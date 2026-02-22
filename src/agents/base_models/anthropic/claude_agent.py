from datetime import datetime
import json
import os
import traceback

from fastapi import requests
from loguru import logger
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from agents.agent import Agent
from agents.hybrid.skill_agent_2.skill_book import SkillBook
from domain.request import AgentPredictionResponse, TokenUsage

from anthropic import AnthropicBedrock

from utils import expect_env_var
from dotenv import load_dotenv
load_dotenv()

# https://github.com/anthropics/claude-quickstarts/blob/main/computer-use-demo/computer_use_demo/loop.py#L265

_ANTHROPIC_MODEL_MAP = {
    "claude-sonnet-4.5": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "claude-haiku-4.5": "global.anthropic.claude-haiku-4-5-20251001-v1:0"
}

_SYSTEM_PROMPT = f"""
You are an Advanced Computer Control Agent. Your goal is to execute complex tasks by navigating a GUI/CLI environment. You operate with a high degree of autonomy, rigorous self-criticism, and strategic planning.

You will be provided with most recent screenshot of the computer interface at each step. 

# Environment Context
* Date: {datetime.today().strftime('%A, %B %d, %Y')} | Home: '/home/user' | OS: Linux/Ubuntu | Language: 'English'
* If Sudo access is required for any operation, the sudo password is '{os.getenv("VM_SUDO_PASSWORD")}'.
* **CRITICAL:** DO NOT ask for clarification. Proceed with available tools. If the goal is ambiguous, make a logical assumption and state it in your reasoning.
* **Precision:** Click the visual **center** of elements.
* **Latency:** Use 'wait' if an app is loading or the screen is settling; do not click blindly.
* **Termination:** Save your work if inside an application. Finish by calling action=terminate.
* **Visibility:** When viewing a page it can be helpful to zoom out and/or scroll and scan, so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.

# Cognitive Process
* Maintain a clear internal reasoning trace.
* Describe relevant aspects and information in the screenshot which could guide you in the completion of the task.
* Clarify the user intent based on task description, context, and screenshot, DO NOT ask the user.
* Carefully plan and think before taking an action at each step.
* Always refer to the latest screenshot to understand the current state of the computer
* Reflect on the previous action and its effects. Ensure that the current state and previous action reflect your expected outcome before proceeding as they might be have been executed incorrectly.
* Break down complex tasks into smaller, manageable steps.
* If uncertain about the next step, take a moment to analyze the current screenshot.
* Reflect on the previous plan, adjusting it if necessary based on the current state of the computer.
* Use the provided tools to interact with the computer GUI.
* Some applications may take time to start or process actions, so you may need to see the results of your actions. E.g. if you click on Firefox and a window doesn't open, try waiting.

# Error Recovery Patterns
When things go wrong, follow this decision tree:
- Diagnose why it failed. Is the element not clickable? Wrong location? App not responding? Plan is invalid?
- You must:
   - Switch to an alternative approach (if GUI fails, try CLI; if one menu path fails, try another)
   - If no alternatives exist, assess whether:
     * The entire goal approach is flawed → Re-plan from last successful milestone
     * Go back to a previous step and try a new approach.
     * The system is in an unrecoverable state → Document the issue and explain what went wrong, terminate with failure
     * A precondition is missing → Take a step back and address the precondition first (e.g. Information missing, application not running)   

# Finishing with 'INFEASIBLE'
* TASK FEASIBILITY: You can declare a task infeasible at any point during execution - whether at the beginning after taking a screenshot, or later after attempting some actions and discovering barriers. Carefully evaluate whether the task is feasible given the current system state, available applications, and task requirements. If you determine that a task cannot be completed due to:
  - Missing required applications or dependencies that cannot be installed
  - Insufficient permissions or system limitations
  - Contradictory or impossible requirements
  - Any other fundamental barriers that make completion impossible

# Rules
* Only use 'finish' tool when the task is completed and you are sure of it, or cannot be completed given the current state.
* You DO NOT require the action 'screenshot', because screenshots are provided at each step automatically. 
* If you need a fundamental workaround to complete the specified task, which deviates from the task description, you must declare the task infeasible.
* Precisely follow the task instructions. If the user asks for something very specific, follow it exactly (e.g. show me ..., do not assume alternatives unless absolutely necessary).
* Use negative values for scroll to scroll down. The range should be between -10 and 10 for most cases.
* Before finishing, ensure that the task has been completed, and it is shown to the user (on the screen).
* You **CAN** combine multiple tool calls into a single turn when feasible, provided they do not require intermediate visual feedback.
""".strip()

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
_python_tool = {
    "name": "execute_python_code",
    "description": "Executes a snippet of Python code in a secure sandboxed environment and returns the output or any errors encountered during execution." +
                    "The Python should be the raw complete code snippet ('python -c' is not required).",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code snippet to be executed."
            }
        },
        "required": ["code"],
        "additionalProperties": False
    }
}
_terminal_tool =  {
    "name": "execute_terminal_command",
    "description": "Executes a temporary non-stateful terminal command on the system and returns the command output or any errors encountered during execution.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The terminal command to be executed."
            }
        },
        "required": ["command"],
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

    def __init__(self, model: str, http_server: str, max_images_in_history: int = 5, image_size = (1280, 720), **kwargs):
        self.model = model
        self.http_server = http_server

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
            _python_tool,
            _terminal_tool,
        ]
        self.enable_prompt_caching = True
        self.thinking_enabled = True
        self.thinking_budget_tokens = 10000
        self.beta_flags = ["computer-use-2025-01-24"]
        self.system_prompt = _SYSTEM_PROMPT

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
    def _make_call(self, messages: list, max_tokens=10000):
        thinking = None
        if self.thinking_enabled:
            thinking = {
                "type": "enabled",
                "budget_tokens": 6000,
            }

        return self.client.beta.messages.create(
            max_tokens=max_tokens,
            model=self.inference_model,
            thinking=thinking,
            system=self.system_prompt,
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

    def end_task(self, task_id: str = None):
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
            elif block.type == "tool_use":
                responses.append(f"### Tool Call: `{block.name}`\n\n{json.dumps(block.input, indent=2)}\n\n")

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

    def parse_actions_from_tool_call(self, tool_call) -> tuple[str, str]:
        result = ""
        function_args = tool_call.input


        if tool_call.name not in ["computer", "finish", "execute_terminal_command", "execute_python_code"]:
            raise ValueError(f"Invalid tool call name: {tool_call}")

        if tool_call.name == "finish":
            status = function_args.get("status")
            if status == "success":
                return "DONE", "Task completed successfully."
            else:  # failure or infeasible
                return "FAIL", f"Task ended with status: {status}"

        if tool_call.name == "execute_terminal_command":
            command = function_args.get("command")
            if command is None:
                raise ValueError(f"execute_terminal_command requires 'command' argument. Got arguments {function_args}")

            result = self._execute_terminal_command(command=command)
            tool_result = json.dumps(result, indent=2)
            return "", tool_result

        if tool_call.name == "execute_python_code":
            code = function_args.get("code")
            if code is None:
                raise ValueError(f"execute_python_code requires 'code' argument. Got arguments {function_args}")

            result = self._execute_python_code(code=code)
            if result["status"] == "error":
                logs = result["output"]
            else:
                logs = result["message"]
            tool_result = json.dumps({
                "status": result["status"],
                "output": logs,
            }, indent=2)
            return "", tool_result
        
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
        elif action in ("done", "finish"):
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

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0)
    )
    def _execute_python_code(self, code: str) -> dict:
        prefixes_to_strip = ["python -c", "python3 -c"]
        for prefix in prefixes_to_strip:
            if code.startswith(prefix):
                code = code[len(prefix):].strip()

        payload = json.dumps({"code": code})

        try:
            response = requests.post(self.http_server + "/run_python", headers={'Content-Type': 'application/json'},
                                        data=payload, timeout=300)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": "Failed to execute command.", "output": None, "error": response.json()["error"]}
        except Exception as e:
            logger.error(f"An error occurred while trying to execute the command: {traceback.format_exc()}")
            raise e
        
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0)
    )
    def _execute_terminal_command(self, command: str, timeout: int = 300) -> dict:
        payload = json.dumps({
            "script": command,
            "timeout": timeout
        })
        try:
            response = requests.post(
                self.http_server + "/run_bash_script", 
                headers={'Content-Type': 'application/json'},
                data=payload, 
                timeout=timeout,
            )
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Bash script executed successfully with return code: {result.get('returncode', -1)}")
                return result
            elif response.status_code == 400:
                return {
                    "status": "error",
                    "output": "",
                    "error": f"Scipt execution failed with status code : {response.status_code}, error: {response.text}",
                    "returncode": -1
                }
            else:
                logger.error(f"Failed to execute bash script. Status code: {response.status_code}, response: {response.text}")
                raise Exception("Failed to execute bash script.")
            
        except requests.exceptions.ReadTimeout:
            logger.error("Bash script execution timed out")
            return {
                "status": "error",
                "output": "",
                "error": f"Script execution timed out after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"An error occurred while trying to execute the bash script: {e}")
            raise e


SKILLS_PROMPT = """
You are an Advanced Computer Control Agent. Your goal is to execute complex tasks by navigating a GUI/CLI environment. You operate with a high degree of autonomy, rigorous self-criticism, and strategic planning.

You will be provided with most recent screenshot of the computer interface at each step. 

# Environment Context
* Date: {dt} | Home: '/home/user' | OS: Linux/Ubuntu | Language: 'English'
* If Sudo access is required for any operation, the sudo password is '{sudo_pw}'.
* **CRITICAL:** DO NOT ask for clarification. Proceed with available tools. If the goal is ambiguous, make a logical assumption and state it in your reasoning.
* **Precision:** Click the visual **center** of elements.
* **Latency:** Use 'wait' if an app is loading or the screen is settling; do not click blindly.
* **Termination:** Save your work if inside an application. Finish by calling action=terminate.
* **Visibility:** When viewing a page it can be helpful to zoom out and/or scroll and scan, so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.

# ⚠️ MANDATORY FIRST STEP: READ SKILLS BEFORE ACTING

**ON EVERY NEW TASK, BEFORE TAKING ANY ACTIONS:**
1. Examine the task description and screenshot to identify which domain(s) are involved
2. Call `get_domain_skills(domain)` for EACH relevant domain to see available skills
3. Call `read_skills([skill_ids])` to read ALL skills that could possibly be relevant

**This is NOT optional.** Skills contain critical non-obvious knowledge (menu locations, correct procedures, shortcuts, prerequisites) that prevents errors and wasted effort. Even if you think you know how to do something, CHECK SKILLS FIRST.

**If you skip reading skills and encounter problems later, you have failed to follow instructions.**

# Cognitive Process
* Maintain a clear internal reasoning trace.
* Describe relevant aspects and information in the screenshot which could guide you in the completion of the task.
* Clarify the user intent based on task description, context, and screenshot, DO NOT ask the user.
* Carefully plan and think before taking an action at each step.
* Always refer to the latest screenshot to understand the current state of the computer
* Reflect on the previous action and its effects. Ensure that the current state and previous action reflect your expected outcome before proceeding as they might be have been executed incorrectly.
* Break down complex tasks into smaller, manageable steps.
* If uncertain about the next step, take a moment to analyze the current screenshot.
* Reflect on the previous plan, adjusting it if necessary based on the current state of the computer.
* Use the provided tools to interact with the computer GUI.
* Some applications may take time to start or process actions, so you may need to see the results of your actions. E.g. if you click on Firefox and a window doesn't open, try waiting.

# Error Recovery Patterns
When things go wrong, follow this decision tree:
- Diagnose why it failed. Is the element not clickable? Wrong location? App not responding? Plan is invalid?
- You must:
   - Switch to an alternative approach (if GUI fails, try CLI; if one menu path fails, try another)
   - If no alternatives exist, assess whether:
     * The entire goal approach is flawed → Re-plan from last successful milestone
     * Go back to a previous step and try a new approach.
     * The system is in an unrecoverable state → Document the issue and explain what went wrong, terminate with failure
     * A precondition is missing → Take a step back and address the precondition first (e.g. Information missing, application not running)   

# Finishing with 'INFEASIBLE'
* TASK FEASIBILITY: You can declare a task infeasible at any point during execution - whether at the beginning after taking a screenshot, or later after attempting some actions and discovering barriers. Carefully evaluate whether the task is feasible given the current system state, available applications, and task requirements. If you determine that a task cannot be completed due to:
  - Missing required applications or dependencies that cannot be installed
  - Insufficient permissions or system limitations
  - Contradictory or impossible requirements
  - Any other fundamental barriers that make completion impossible


# Skills System

You have access to a skillbook containing proven guidance from past agents—non-obvious knowledge like hidden menu locations, correct procedures, shortcuts, and prerequisites.

## How Skills Work

**Two-step process (MANDATORY at task start):**
1. **Discover:** `get_domain_skills(domain)` → Returns list of skill IDs and descriptions for the domain
2. **Read:** `read_skills([skill_ids])` → Returns full detailed guidance for those skills

**Available domains:**

{domains_list}

## When to Read Skills

**REQUIRED - At task start:**
- Identify ALL domains related to your task (e.g., task mentions "Chrome bookmarks" → check 'chrome' domain)
- Call `get_domain_skills` for EACH relevant domain
- Read ALL skills that seem even remotely relevant (be liberal, not conservative)
- If unsure whether a domain is relevant, CHECK IT ANYWAY

**Recommended - During execution:**
- When you encounter unexpected behavior or errors
- When you can't find a feature or menu item
- Before trying an action you're uncertain about
- After any failure or confusion

## Important Notes

- Skills contain non-obvious knowledge that ISN'T visible in screenshots
- Reading an irrelevant skill costs little; missing a relevant one costs everything
- Skills are guidance based on past experience—use judgment if something seems outdated
- Better to read 5 skills (with 3 irrelevant) than to miss 1 critical skill  

# Rules
* Only use 'finish' tool when the task is completed and you are sure of it, or cannot be completed given the current state.
* You DO NOT require the action 'screenshot', because screenshots are provided at each step automatically. 
* If you need a fundamental workaround to complete the specified task, which deviates from the task description, you must declare the task infeasible.
* Precisely follow the task instructions. If the user asks for something very specific, follow it exactly (e.g. show me ..., do not assume alternatives unless absolutely necessary).
* Use negative values for scroll to scroll down. The range should be between -10 and 10 for most cases.
* Before finishing, ensure that the task has been completed, and it is shown to the user (on the screen).
* You **CAN** combine multiple tool calls into a single turn when feasible, provided they do not require intermediate visual feedback.
""".strip()

class SkillAnthropicAgent(BaseAnthropicAgent):
    def __init__(self, model, http_server, max_images_in_history = 5, image_size=(1280, 720), **kwargs):
        super().__init__(model, http_server, max_images_in_history, image_size, **kwargs)
        self.skill_book = SkillBook.load()
        self.system_prompt = SKILLS_PROMPT.format(
            dt=datetime.today().strftime('%A, %B %d, %Y'),
            domains_list=self.skill_book.list_domains(),
            sudo_pw=os.getenv("VM_SUDO_PASSWORD"),
        )
        self.tools.extend([
            {
                "name": "get_domain_skills",
                "description": "**CALL THIS FIRST on every new task!** Discovers available skills for a domain/application. Returns skill IDs and descriptions. This reveals what proven guidance exists from past agents. Always call this before taking actions in any application.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": self.skill_book.get_domain_ids(),
                            "description": "The domain/application name (e.g. 'chrome', 'gimp', 'libreoffice-calc'). Check ALL relevant domains."
                        }
                    },
                    "required": ["domain"],
                    "additionalProperties": False
                }
            },
            {
                "name": "read_skills",
                "description": "**CALL THIS to read full skill content** after discovering skills with get_domain_skills. Returns detailed step-by-step guidance including menu locations, shortcuts, prerequisites, and correct procedures that aren't obvious from screenshots. Read ALL potentially relevant skills before proceeding.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "skill_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": self.skill_book.get_all_skill_ids()
                            },
                            "description": "List of skill IDs to read (e.g. ['chrome/bookmarks-manager', 'gimp/transparency']). Include ALL skills that might be relevant—better to read too many than miss one."
                        },
                    },
                    "required": ["skill_ids"],
                    "additionalProperties": False
                }
            }
        ])

    def parse_actions_from_tool_call(self, tool_call):
        if tool_call.name not in ["get_domain_skills", "read_skills"]:
            return super().parse_actions_from_tool_call(tool_call)
        
        function_args = tool_call.input
        if tool_call.name == "get_domain_skills":
            domain_id = function_args.get("domain")
            domain_skills = self.skill_book.list_skills(domain_id)
            return "", domain_skills
        elif tool_call.name == "read_skills": 
            skill_ids = function_args.get("skill_ids")
            skills_content = []
            for skill_id in skill_ids:
                skill = self.skill_book.get_skill(skill_id)
                skills_content.append(skill.to_markdown())
            tool_result = "\n\n---\n\n".join(skills_content)
            return "", tool_result
        else:
            raise ValueError(f"Function call not found '{tool_call.name}'")



if __name__ == "__main__":
    agent = BaseAnthropicAgent(model="claude-sonnet-4.5")

    import base64

    with open("/Users/YILUZUN/Projects/optimizing-agent-fidelity-ma/data/test-image.png", "rb") as f:
        _image_bytes = f.read()

        # encode base 64
        _image_base64 = base64.b64encode(_image_bytes).decode("utf-8")

    #agent.predict(screenshot=_image_base64, task="Click on the 'Log In' Button")
    agent.predict(screenshot=_image_base64, task="You are done. There is no tusk")
