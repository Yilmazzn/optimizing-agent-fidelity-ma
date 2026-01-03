from datetime import datetime

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

_SYSTEM_PROMPT = """
<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open chrome or any application, please just click on the icon.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {dt}.
</SYSTEM_CAPABILITY>
""".strip().format(dt=datetime.today().strftime("%A, %B %d, %Y"))


class BaseAnthropicAgent(Agent):

    def __init__(self, model: str, max_images_in_history: int = 3, **kwargs):
        self.model = model
        self.max_images_in_history = max_images_in_history

        super().__init__(name=f"base-anthropic-{model}", *kwargs)

        expect_env_var("AWS_ACCESS_KEY_ID")
        expect_env_var("AWS_SECRET_ACCESS_KEY")
        self.client = AnthropicBedrock(aws_region="eu-central-1")

        self.inference_model = _ANTHROPIC_MODEL_MAP.get(self.model)
        self.history = []

        if self.inference_model is None:
            raise ValueError(f"'{self.model}' is not a valid model")

    # https://platform.claude.com/docs/en/build-with-claude/prompt-caching
    # So in total up to 4 cache breakpoints are supported. Should be used on the most recent. 1 is reserved for the system prompt
    def _inject_prompt_caching(self, messages: list):
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

    def _make_call(self, messages: list, max_tokens=1024):
        return self.client.beta.messages.create(
            max_tokens=max_tokens,
            model=self.inference_model,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                },
            ],
            tools=[
                {"type": "computer_20250124", "name": "computer", "display_width_px": 1024,
                 "display_height_px": 768},
                {"type": "bash_20250124", "name": "bash"}
            ],
            messages=messages,
            betas=["computer-use-2025-01-24"],
        )

    def _build_messages(self) -> list:
        messages = []
        first_image_idx = max(0, len(self.history) - self.max_images_in_history)

        for i, ele in enumerate(self.history):
            ## USER
            content = []
            if i >= first_image_idx:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": ele["screenshot"],
                    },
                })
            content.append({
                "type": "text",
                "text": ele["user_query"]
            })
            messages.append({
                "role": "user",
                "content": content,
            })

            ## ASSISTANT
            messages.append({
                "rolwe": "assistant",
                "content": ele["response"]
            })


        return messages

    def predict(self, screenshot: str, task: str) -> AgentPredictionResponse:
        user_query = None
        if len(self.history) == 0:
            user_query = task
        else:
            user_query = self.history[-1]["tool_result"] # get text result from previous step

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
        for block in response.content:
            if block.type == "tool_use":
                pyautogui_actions, tool_result = self.parse_actions_from_tool_call(block.input)
                actions = actions.append(pyautogui_actions)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": tool_result,
                })
        self.history[-1]["tool_results"] = tool_results

        response_str = ""
        for block in response.content:
            if block.type == "text":
                response_str += block.text + "\n\n"

        return AgentPredictionResponse(
            response=response_str.strip(),
            pyautogui_actions="\n".join(actions),
            usage=TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                cached_prompt_tokens=response.usage.cache_read_input_tokens,
            )
        )

    def parse_actions_from_tool_call(self, tool_call: dict) -> tuple[str, str]:
        result = ""
        function_args = (
            tool_call["input"]
        )
        
        action = function_args.get("action")
        if not action:
            action = tool_call.function.name
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
            result += "pyautogui.sleep(1)\n"
            expected_outcome = "Waited for 1 seconds"
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
