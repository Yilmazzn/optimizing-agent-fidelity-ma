from datetime import datetime
import os

from loguru import logger
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from agents.agent import Agent
from domain.request import AgentPredictionResponse, TokenUsage

from anthropic import AnthropicBedrock

from utils import expect_env_var
from dotenv import load_dotenv
load_dotenv()

# https://github.com/anthropics/claude-quickstarts/blob/main/computer-use-demo/computer_use_demo/loop.py#L265

_ANTHROPIC_MODEL_MAP = {
    "claude-sonnet-4.5": "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
}

_SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using x86_64 architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open browser, please just click on the Chrome icon.  Note, Chrome is what is installed on your system.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_editor or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* DO NOT ask users for clarification during task execution. DO NOT stop to request more information from users. Always take action using available tools!!!
* NEVER USE THE SCREENSHOT TOOL. You already get screenshots automatically after every action in the user request. 
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* TASK FEASIBILITY: You can declare a task infeasible at any point during execution - whether at the beginning after taking a screenshot, or later after attempting some actions and discovering barriers. Carefully evaluate whether the task is feasible given the current system state, available applications, and task requirements. If you determine that a task cannot be completed due to:
  - Missing required applications or dependencies that cannot be installed
  - Insufficient permissions or system limitations
  - Contradictory or impossible requirements
  - Any other fundamental barriers that make completion impossible
  Then you MUST output exactly "[INFEASIBLE]" (including the square brackets) anywhere in your response to trigger the fail action. The system will automatically detect this pattern and terminate the task appropriately.
* The current date is {datetime.today().strftime('%A, %B %d, %Y')}.
* Home directory of this Ubuntu system is '/home/user'.
* If you need a password for sudo, the password of the computer is '{os.getenv("VM_SUDO_PASSWORD")}'. 
</SYSTEM_CAPABILITY>
"""

_finish_tool = {
    "name": "finish",
    "description": "Finishes the current task execution if successful, failed, or infeasible after completing the task or failing to do so, and reports its final status. To be used at last after completing the task.",
    "input_schema": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["success", "failure", "infeasible"],
                "description": "Final execution status of the task."
            }
        },
        "required": ["status"],
        "additionalProperties": False
    }
}

def _is_retriable_anthropic_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None)

    # If it's a client-side error (4xx) that isn't typically transient, do not retry.
    # Common transient 4xx cases: timeout/conflict/ratelimit.
    if isinstance(status_code, int) and 400 <= status_code < 500:
        return status_code in (408, 409, 429)

    return True


class BaseAnthropicAgent(Agent):

    def __init__(self, model: str, max_images_in_history: int = 3, image_size = (1280, 720), **kwargs):
        self.model = model

        super().__init__(
            name=f"anthropic-{model}", 
            image_size=image_size, 
            max_images_in_history=max_images_in_history,
            **kwargs
        )

        expect_env_var("AWS_ACCESS_KEY_ID")
        expect_env_var("AWS_SECRET_ACCESS_KEY")
        self.client = AnthropicBedrock(aws_region="eu-central-1")

        self.inference_model = _ANTHROPIC_MODEL_MAP.get(self.model)
        self.history = []

        if self.inference_model is None:
            raise ValueError(f"'{self.model}' is not a valid model")
        
        self.tools = [
            {"type": "computer_20250124", "name": "computer", "display_width_px": self.image_size[0],
                "display_height_px": self.image_size[1]},
            _finish_tool,
        ]
        self.enable_prompt_caching = True
        self.thinking_enabled = True
        self.thinking_budget_tokens = 2048
        self.beta_flags = ["computer-use-2025-01-24"]

    # https://platform.claude.com/docs/en/build-with-claude/prompt-caching
    # So in total up to 4 cache breakpoints are supported. Should be used on the most recent. 1 is reserved for the system prompt
    def _inject_prompt_caching(self, messages: list):
        if not self.enable_prompt_caching:
            return
        remaining_breakpoints = 3
        for message in reversed(messages):
            if message["role"] != "user":
                continue
            if remaining_breakpoints == 0:
                if "cache_control" in message:
                    del message["cache_control"]
                continue
            message["content"][-1]["cache_control"] = {"type": "ephemeral"}
            remaining_breakpoints -= 1

    @retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
        retry=retry_if_exception(_is_retriable_anthropic_error),
    )
    def _make_call(self, messages: list, max_tokens=4096):
        thinking = None
        if self.thinking_enabled:
            thinking = {
                "type": "enabled",
                "budget_tokens": self.thinking_budget_tokens,
            }

        return self.client.beta.messages.create(
            max_tokens=max_tokens,
            model=self.inference_model,
            thinking=thinking,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                },
            ],
            tools=self.tools,
            messages=messages,
            betas=self.beta_flags,
        )

    def _build_messages(self) -> list:
        messages = []
        first_image_idx = max(0, len(self.history) - self.max_images_in_history)

        for i, ele in enumerate(self.history):
            ## USER
            content = []
            
            # add tool result from previous step. Must come first as per https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use#handling-results-from-client-tools
            if i > 0: 
                content.extend(self.history[i-1].get("tool_results", []))

            if i >= first_image_idx:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": ele["screenshot"],
                    },
                })
            if "user_query" in ele and ele["user_query"] is not None:
                content.append({
                    "type": "text",
                    "text": ele["user_query"]
                })
            messages.append({
                "role": "user",
                "content": content,
            })

            ## ASSISTANT (if not last message)
            if "response" in ele:
                messages.append({
                    "role": "assistant",
                    "content": ele["response"]
                })

        return messages

    def end_task(self):
        pass

    def predict(self, screenshot: str, task: str) -> AgentPredictionResponse:
        user_query = None
        if len(self.history) == 0:
            user_query = task

        screenshot = self.resize_screenshot(screenshot)
        self.history.append({
            "screenshot": screenshot,
            "user_query": user_query,
        })

        messages = self._build_messages()
        self._inject_prompt_caching(messages)

        response = self._make_call(messages)
        self.history[-1]["response"] = response.content

        tool_results = []
        actions = []

        logger.info(f"Anthropic response: {response}")
        for block in response.content:
            if block.type == "tool_use":
                pyautogui_actions, tool_result = self.parse_actions_from_tool_call(block)
                actions.append(pyautogui_actions)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": tool_result,
                })
        
        self.history[-1]["tool_results"] = tool_results

        responses = []
        for block in response.content:
            if block.type == "text":
                responses.append(block.text)

        status = "working"
        status = status if len(tool_results) > 0 else "done"

        return AgentPredictionResponse(
            response="\n\n".join(responses).strip(),
            pyautogui_actions="\n".join(actions).strip(),
            usage=TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                cached_prompt_tokens=response.usage.cache_read_input_tokens,
            ),
            status=status
        )
    
    def parse_actions_from_bash_tool(self, function_args) -> tuple[str, str]:
        command = function_args.get("command")
        restart = function_args.get("restart", False)
        
        _pyautogui_actions_bash = ""
        if restart:
            _pyautogui_actions_bash += (
                "pyautogui.hotkey('ctrl', 'alt', 't')\n"
                "time.sleep(3)\n"
                "pyautogui.write('pkill gnome-terminal', interval=0.05)\n"
                "pyautogui.press('enter')\n"
                "time.sleep(2)\n"
                "pyautogui.hotkey('ctrl', 'alt', 't')\n"
            )

        return None, None

    def parse_actions_from_tool_call(self, tool_call) -> tuple[str, str]:
        result = ""
        function_args = tool_call.input

        if tool_call.name not in ["computer", "finish"]:
            raise ValueError(f"Invalid tool call name: {tool_call}")

        if tool_call.name == "finish":
            status = function_args.get("status")
            if status == "success":
                return "DONE", "Task completed successfully."
            else:  # failure or infeasible
                return "FAIL", f"Task ended with status: {status}"

        if tool_call.name == "bash":
            return self.parse_actions_from_bash_tool(function_args)


        action = function_args.get("action")
        if action is None:
            raise ValueError(f"action is required in function_args, got: {tool_call.input}")
        action_conversion = {
            "left click": "left_click",
            "right click": "right_click"
        }
        action = action_conversion.get(action, action)
        
        text = function_args.get("text")
        coordinate = function_args.get("coordinate")
        start_coordinate = function_args.get("start_coordinate")
        scroll_direction = function_args.get("scroll_direction")
        scroll_amount = function_args.get("scroll_amount")
        duration = function_args.get("duration")
        
        # resize coordinates if resize_factor is set

        if action == "left_mouse_down":
            result += "pyautogui.mouseDown()\n"
        elif action == "left_mouse_up":
            result += "pyautogui.mouseUp()\n"
        
        elif action == "hold_key":
            if not isinstance(text, str):
                raise ValueError(f"{text} must be a string")
            
            keys = text.split('+')
            for key in keys:
                key = key.strip().lower()
                result += f"pyautogui.keyDown('{key}')\n"
            expected_outcome = f"Keys {text} held down."

        # Handle mouse move and drag actions
        elif action in ("mouse_move", "left_click_drag"):
            if coordinate is None:
                raise ValueError(f"coordinate is required for {action}")
            if text is not None:
                raise ValueError(f"text is not accepted for {action}")
            if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 2:
                raise ValueError(f"{coordinate} must be a tuple of length 2")
            if not all(isinstance(i, int) for i in coordinate):
                raise ValueError(f"{coordinate} must be a tuple of ints")
            
            x, y = self.resize_coords_to_original(coordinate)
            if action == "mouse_move":
                result += (
                    f"pyautogui.moveTo({x}, {y}, duration={duration or 0.5})\n"
                )
                expected_outcome = f"Mouse moved to {coordinate}."
            elif action == "left_click_drag":
                # If start_coordinate is provided, validate and move to start before dragging
                if start_coordinate:
                    if not isinstance(start_coordinate, (list, tuple)) or len(start_coordinate) != 2:
                        raise ValueError(f"{start_coordinate} must be a tuple of length 2")
                    if not all(isinstance(i, int) for i in start_coordinate):
                        raise ValueError(f"{start_coordinate} must be a tuple of ints")
                    start_x, start_y = self.resize_coords_to_original(start_coordinate)
                    result += (
                        f"pyautogui.moveTo({start_x}, {start_y}, duration={duration or 0.5})\n"
                    )
                result += (
                    f"pyautogui.dragTo({x}, {y}, duration={duration or 0.5})\n"
                )
                expected_outcome = f"Cursor dragged {f'from {start_coordinate} ' if start_coordinate else ''}to {coordinate}."

        # Handle keyboard actions
        elif action in ("key", "type"):
            if text is None:
                raise ValueError(f"text is required for {action}")
            if coordinate is not None:
                raise ValueError(f"coordinate is not accepted for {action}")
            if not isinstance(text, str):
                raise ValueError(f"{text} must be a string")

            if action == "key":
                key_conversion = {
                    "page_down": "pagedown",
                    "page_up": "pageup",
                    "super_l": "win",
                    "super": "command",
                    "escape": "esc"
                }
                keys = text.split('+')
                for key in keys:
                    key = key.strip().lower()
                    key = key_conversion.get(key, key)
                    result += (f"pyautogui.keyDown('{key}')\n")
                for key in reversed(keys):
                    key = key.strip().lower()
                    key = key_conversion.get(key, key)
                    result += (f"pyautogui.keyUp('{key}')\n")
                expected_outcome = f"Keys '{text}' pressed."
            elif action == "type":
                lines = text.split('\n')
                code = []

                for i, line in enumerate(lines):
                    if line:
                        code.append(f"pyautogui.write({repr(line)}, interval=0.05)")
                    if i < len(lines) - 1:
                        code.append("pyautogui.press('enter')")

                result += "\n".join(code) + "\n"
                expected_outcome = f"Text {text} written."

        # Handle scroll actions
        elif action == "scroll":
            if text is not None:
                result += (f"pyautogui.keyDown('{text.lower()}')\n")
            if coordinate is None:
                if scroll_direction in ("up", "down"):
                    result += (
                        f"pyautogui.scroll({scroll_amount if scroll_direction == 'up' else -scroll_amount})\n"
                    )
                elif scroll_direction in ("left", "right"):
                    result += (
                        f"pyautogui.hscroll({scroll_amount if scroll_direction == 'right' else -scroll_amount})\n"
                    )
            else:
                x, y = self.resize_coords_to_original(coordinate)
                if scroll_direction in ("up", "down"):
                    result += (
                        f"pyautogui.scroll({scroll_amount if scroll_direction == 'up' else -scroll_amount}, {x}, {y})\n"
                    )
                elif scroll_direction in ("left", "right"):
                    result += (
                        f"pyautogui.hscroll({scroll_amount if scroll_direction == 'right' else -scroll_amount}, {x}, {y})\n"
                    )
            if text is not None:
                result += (f"pyautogui.keyUp('{text.lower()}')\n")

            expected_outcome = f"Scrolled {scroll_direction}"

        # Handle click actions
        elif action in ("left_click", "right_click", "double_click", "middle_click", "left_press", "triple_click"):
            # Handle modifier keys during click if specified
            if text:
                keys = text.split('+')
                for key in keys:
                    key = key.strip().lower()
                    result += f"pyautogui.keyDown('{key}')\n"
            if coordinate is not None:
                x, y = self.resize_coords_to_original(coordinate)
                if action == "left_click":
                    result += (f"pyautogui.click({x}, {y})\n")
                elif action == "right_click":
                    result += (f"pyautogui.rightClick({x}, {y})\n")
                elif action == "double_click":
                    result += (f"pyautogui.doubleClick({x}, {y})\n")
                elif action == "middle_click":
                    result += (f"pyautogui.middleClick({x}, {y})\n")
                elif action == "left_press":
                    result += (f"pyautogui.mouseDown({x}, {y})\n")
                    result += ("time.sleep(1)\n")
                    result += (f"pyautogui.mouseUp({x}, {y})\n")
                elif action == "triple_click":
                    result += (f"pyautogui.tripleClick({x}, {y})\n")

            else:
                if action == "left_click":
                    result += ("pyautogui.click()\n")
                elif action == "right_click":
                    result += ("pyautogui.rightClick()\n")
                elif action == "double_click":
                    result += ("pyautogui.doubleClick()\n")
                elif action == "middle_click":
                    result += ("pyautogui.middleClick()\n")
                elif action == "left_press":
                    result += ("pyautogui.mouseDown()\n")
                    result += ("time.sleep(1)\n")
                    result += ("pyautogui.mouseUp()\n")
                elif action == "triple_click":
                    result += ("pyautogui.tripleClick()\n")
            # Release modifier keys after click
            if text:
                keys = text.split('+')
                for key in reversed(keys):
                    key = key.strip().lower()
                    result += f"pyautogui.keyUp('{key}')\n"
            
            expected_outcome = f"Performed {action}"
            if coordinate:
                expected_outcome += f" at {coordinate}"
            if text:
                expected_outcome += f" with modifiers '{text}'"
            
        elif action == "wait":
            if duration is None:
                duration = 5
            result += f"pyautogui.sleep({duration})\n"
            expected_outcome = f"Waited for {duration} seconds"
        elif action == "fail":
            result += "FAIL"
            expected_outcome = "Finished"
        elif action == "done":
            result += "DONE"
            expected_outcome = "Finished"
        elif action == "call_user":
            result += "CALL_USER"
            expected_outcome = "Call user"
        elif action == "screenshot":
            result += "pyautogui.sleep(0.1)\n"
            expected_outcome = "Screenshot taken"
        else:
            raise ValueError(f"Invalid action: {action}")
        
        return result, expected_outcome




if __name__ == "__main__":
    agent = BaseAnthropicAgent(model="claude-sonnet-4.5")

    import base64

    with open("/Users/YILUZUN/Projects/optimizing-agent-fidelity-ma/data/test-image.png", "rb") as f:
        _image_bytes = f.read()

        # encode base 64
        _image_base64 = base64.b64encode(_image_bytes).decode("utf-8")

    #agent.predict(screenshot=_image_base64, task="Click on the 'Log In' Button")
    agent.predict(screenshot=_image_base64, task="You are done. There is no tusk")
