import json
import traceback
from typing import Union, List, Iterable, Sequence

from loguru import logger
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from qwen_agent.tools.base import BaseTool, register_tool

# https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/utils/agent_function_call.py

@register_tool("computer_use")
class ComputerUse(BaseTool):
    _SLEEP_AFTER_CLICK_S = 0.2
    _SLEEP_SHORT_S = 0.1
    _SLEEP_DRAG_TAP_S = 0.05
    @property
    def description(self):
        return f"""
Use a mouse and keyboard to interact with a computer, and take screenshots.
* This is an interface to a desktop GUI. You do not have access to a terminal or applications menu. You must click on desktop icons to start applications.
* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions. E.g. if you click on Firefox and a window doesn't open, try wait and taking another screenshot.
* The screen's resolution is {self.display_width_px}x{self.display_height_px}.
* Whenever you intend to move the cursor to click on an element like an icon, you should consult a screenshot to determine the coordinates of the element before moving the cursor.
* If you tried clicking on a program or link but it failed to load, even after waiting, try adjusting your cursor position so that the tip of the cursor visually falls on the element that you want to click.
* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges.
* Don't answer explicitly. Just terminate the task if finished with either success, failure or infeasible.
""".strip()

    parameters = {
        "properties": {
            "action": {
                "description": """
The action to perform. The available actions are:
* `key`: Performs key down presses on the arguments passed in order, then performs key releases in reverse order.
* `type`: Type a string of text on the keyboard.
* `mouse_move`: Move the cursor to a specified (x, y) pixel coordinate on the screen.
* `left_click`: Click the left mouse button at a specified (x, y) pixel coordinate on the screen.
* `left_click_drag`: Click and drag the cursor to a specified (x, y) pixel coordinate on the screen.
* `right_click`: Click the right mouse button at a specified (x, y) pixel coordinate on the screen.
* `middle_click`: Click the middle mouse button at a specified (x, y) pixel coordinate on the screen.
* `double_click`: Double-click the left mouse button at a specified (x, y) pixel coordinate on the screen.
* `triple_click`: Triple-click the left mouse button at a specified (x, y) pixel coordinate on the screen (simulated as double-click since it's the closest action).
* `scroll`: Performs a scroll of the mouse scroll wheel.
* `hscroll`: Performs a horizontal scroll (mapped to regular scroll).
* `wait`: Wait specified seconds for the change to happen.
* `terminate`: Terminate the current task and report its completion status.
* `answer`: Answer a question and terminate the task (with status "success").
""".strip(),
                "enum": [
                    "key",
                    "type",
                    "mouse_move",
                    "left_click",
                    "left_click_drag",
                    "right_click",
                    "middle_click",
                    "double_click",
                    "triple_click",
                    "scroll",
                    "hscroll",
                    "wait",
                    "terminate",
                    "answer",
                ],
                "type": "string",
            },
            "keys": {
                "description": "Required only by `action=key`.",
                "type": "array",
            },
            "text": {
                "description": "Required only by `action=type` and `action=answer`.",
                "type": "string",
            },
            "coordinate": {
                "description": "(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to.",
                "type": "array",
            },
            "scroll_amount": {
                "description": "The number of “clicks” on the mouse scroll wheel to scroll. Positive values scroll up, negative values scroll down. Required only by `action=scroll` and `action=hscroll`.",
                "type": "number",
            },
            "time": {
                "description": "The seconds to wait. Required only by `action=wait`.",
                "type": "number",
            },
            "status": {
                "description": "The status of the task. Required only by `action=terminate`.",
                "type": "string",
                "enum": ["success", "failure", "infeasible"],
            },
        },
        "required": ["action"],
        "type": "object",
    }

    def __init__(self, cfg=None):
        self.display_width_px = cfg["display_width_px"]
        self.display_height_px = cfg["display_height_px"]
        super().__init__(cfg)

    def call(self, params: Union[str, dict], **kwargs):
        params = self._verify_json_format_args(params)
        action = params["action"]
        if action in ["left_click", "right_click", "middle_click", "double_click","triple_click"]:
            return self._mouse_click(action, params.get("coordinate"))
        elif action == "key":
            return self._key(params["keys"])
        elif action == "type":
            return self._type(params["text"])
        elif action == "mouse_move":
            return self._mouse_move(params["coordinate"])
        elif action == "left_click_drag":
            return self._left_click_drag(params["coordinate"])
        elif action == "scroll":
            return self._scroll(params["scroll_amount"])
        elif action == "hscroll":
            return self._hscroll(params["scroll_amount"])
        elif action == "wait":
            return self._wait(params["time"])
        elif action == "terminate":
            return self._terminate(params["status"])
        elif action == "answer":
            return self._answer(params["text"])
        else:
            raise ValueError(f"Invalid action: {action}")

    def _script(self, lines: Iterable[str]) -> str:
        return "\n".join([line for line in lines if line is not None and str(line).strip() != ""]).rstrip()

    def _normalize_key(self, key: str) -> str:
        k = key.strip().lower()
        conversion = {
            "page_down": "pagedown",
            "pageup": "pageup",
            "page_up": "pageup",
            "pagedown": "pagedown",
            "super": "win",
            "super_l": "win",
            "escape": "esc",
            "return": "enter",
        }
        return conversion.get(k, k)

    def _mouse_click(self, button: str, coordinate: Sequence[float] | None):
        click_map = {
            "left_click": "click",
            "right_click": "rightClick",
            "middle_click": "middleClick",
            "double_click": "doubleClick",
            "triple_click": "tripleClick",
        }
        fn = click_map.get(button)
        if fn is None:
            raise ValueError(f"Invalid click button/action: {button}")

        lines: list[str] = []
        if coordinate is None:
            lines.append(f"pyautogui.{fn}()")
        else:
            x, y = coordinate
            lines.append(f"pyautogui.{fn}({x}, {y})")

        return self._script(lines)

    def _key(self, keys: List[str]):
        if not isinstance(keys, list) or not keys:
            raise ValueError(f"keys must be a non-empty list, got: {keys}")

        normalized = [self._normalize_key(str(k)) for k in keys if str(k).strip()]
        if not normalized:
            raise ValueError(f"keys must contain at least one key, got: {keys}")

        lines: list[str] = []
        for k in normalized:
            lines.append(f"pyautogui.keyDown({k!r})")
        for k in reversed(normalized):
            lines.append(f"pyautogui.keyUp({k!r})")

        # Small pause to allow shortcuts to take effect.
        lines.append(f"time.sleep({self._SLEEP_SHORT_S})")
        return self._script(lines)

    def _type(self, text: str):
        if not isinstance(text, str):
            raise ValueError(f"text must be a string, got: {type(text)}")

        # Some models send a literal backslash-n sequence ("\\n") instead of an actual newline.
        # In that case, convert it so we press Enter rather than typing backslash + n.
        if "\\n" in text and "\n" not in text:
            text = text.replace("\\r\\n", "\n").replace("\\n", "\n")

        # Same for tab: convert literal "\\t" to actual tab character.
        if "\\t" in text and "\t" not in text:
            text = text.replace("\\t", "\t")

        lines: list[str] = []
        # Split by newlines first, then handle tabs within each line.
        parts = text.split("\n")
        for idx, part in enumerate(parts):
            # Split each part by tabs and press tab key between segments.
            tab_segments = part.split("\t")
            for tab_idx, segment in enumerate(tab_segments):
                if segment:
                    lines.append(f"pyautogui.typewrite({segment!r}, interval=0.05)")
                if tab_idx < len(tab_segments) - 1:
                    lines.append("pyautogui.press('tab')")
            if idx < len(parts) - 1:
                lines.append("pyautogui.press('enter')")

        # Typing itself is paced; add only a small pause after.
        lines.append(f"time.sleep({self._SLEEP_SHORT_S})")
        return self._script(lines)

    def _mouse_move(self, coordinate: Sequence[float]):
        x, y = coordinate
        return self._script([f"pyautogui.moveTo({x}, {y}, duration=0.2)"])

    def _left_click_drag(self, coordinate: Sequence[float]):
        x, y = coordinate
        lines = [
            "pyautogui.mouseDown()",
            f"time.sleep({self._SLEEP_DRAG_TAP_S})",
            f"pyautogui.dragTo({x}, {y}, duration=0.5)",
            "pyautogui.mouseUp()"
        ]
        return self._script(lines)

    def _scroll(self, scroll_amount: int):
        try:
            amt = int(round(float(scroll_amount)))
        except Exception as e:
            raise ValueError(f"scroll_amount must be numeric, got: {scroll_amount}") from e
        # Positive scrolls up, negative scrolls down (pyautogui convention).
        return self._script([f"pyautogui.scroll({amt})"])

    def _hscroll(self, pixels: int):
        # Horizontal scroll isn't consistently supported across platforms; try it, fallback to scroll.
        try:
            amt = int(round(float(pixels)))
        except Exception as e:
            raise ValueError(f"pixels must be numeric, got: {pixels}") from e

        return self._script([
            "try:",
            f"    pyautogui.hscroll({amt})",
            "except Exception:",
            f"    pyautogui.scroll({amt})"
        ])

    def _wait(self, time: int):
        try:
            seconds = float(time)
        except Exception as e:
            raise ValueError(f"time must be numeric seconds, got: {time}") from e

        if seconds < 0:
            raise ValueError(f"time must be >= 0, got: {time}")
        return self._script([f"time.sleep({seconds})"])

    def _answer(self, text: str):
        if not isinstance(text, str):
            raise ValueError(f"text must be a string, got: {type(text)}")
        return "DONE"

    def _terminate(self, status: str):
        if status.lower().strip() == "success":
            return "DONE"
        return "FAIL"


@register_tool("get_domain_skills")
class GetDomainSkills(BaseTool):
    description = (
        "**CALL THIS FIRST on every new task!** Discovers available skills for a domain/application. "
        "Returns skill IDs and descriptions. This reveals what proven guidance exists from past agents. "
        "Always call this before taking actions in any application."
    )

    parameters = {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "The domain/application name (e.g. 'chrome', 'gimp', 'libreoffice-calc'). Check ALL relevant domains.",
            }
        },
        "required": ["domain"],
    }

    def __init__(self, cfg=None):
        self.skill_book = cfg["skill_book"]
        super().__init__(cfg)

    def call(self, params: Union[str, dict], **kwargs) -> str:
        params = self._verify_json_format_args(params)
        domain_id = params["domain"]
        return self.skill_book.list_skills(domain_id)


@register_tool("read_skills")
class ReadSkills(BaseTool):
    description = (
        "**CALL THIS to read full skill content** after discovering skills with get_domain_skills. "
        "Returns detailed step-by-step guidance including menu locations, shortcuts, prerequisites, "
        "and correct procedures that aren't obvious from screenshots. Read ALL potentially relevant skills before proceeding."
    )

    parameters = {
        "type": "object",
        "properties": {
            "skill_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of skill IDs to read (e.g. ['chrome/bookmarks-manager', 'gimp/transparency']). "
                               "Include ALL skills that might be relevant—better to read too many than miss one.",
            }
        },
        "required": ["skill_ids"],
    }

    def __init__(self, cfg=None):
        self.skill_book = cfg["skill_book"]
        super().__init__(cfg)

    def call(self, params: Union[str, dict], **kwargs) -> str:
        params = self._verify_json_format_args(params)
        skill_ids = params["skill_ids"]
        skills_content = []
        for skill_id in skill_ids:
            skill = self.skill_book.get_skill(skill_id)
            skills_content.append(skill.to_markdown())
        return "\n\n---\n\n".join(skills_content)


@register_tool("execute_python_code")
class ExecutePythonCode(BaseTool):
    description = (
        "Executes a snippet of Python code in a secure sandboxed environment and returns the output or any errors encountered during execution. "
        "The Python should be the raw complete code snippet ('python -c' is not required)."
    )

    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code snippet to be executed.",
            }
        },
        "required": ["code"],
    }

    def __init__(self, cfg=None):
        self.http_server = cfg["http_server"]
        super().__init__(cfg)

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0))
    def call(self, params: Union[str, dict], **kwargs) -> str:
        params = self._verify_json_format_args(params)
        code = params["code"]

        prefixes_to_strip = ["python -c", "python3 -c"]
        for prefix in prefixes_to_strip:
            if code.startswith(prefix):
                code = code[len(prefix):].strip()

        payload = json.dumps({"code": code})
        try:
            response = requests.post(
                self.http_server + "/run_python",
                headers={"Content-Type": "application/json"},
                data=payload,
                timeout=300,
            )
            if response.status_code == 200:
                result = response.json()
            else:
                result = {"status": "error", "message": "Failed to execute command.", "output": None, "error": response.json().get("error")}
        except Exception as e:
            logger.error(f"Error executing python code: {traceback.format_exc()}")
            raise e

        if result.get("status") == "error":
            logs = result.get("output") or result.get("error", "Unknown error")
        else:
            logs = result.get("message", "")

        return json.dumps({"status": result.get("status"), "output": logs}, indent=2)


@register_tool("execute_terminal_command")
class ExecuteTerminalCommand(BaseTool):
    description = "Executes a temporary non-stateful terminal command on the system and returns the command output or any errors encountered during execution."

    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The terminal command to be executed.",
            }
        },
        "required": ["command"],
    }

    def __init__(self, cfg=None):
        self.http_server = cfg["http_server"]
        super().__init__(cfg)

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0))
    def call(self, params: Union[str, dict], **kwargs) -> str:
        params = self._verify_json_format_args(params)
        command = params["command"]
        timeout = 300

        payload = json.dumps({"script": command, "timeout": timeout})
        try:
            response = requests.post(
                self.http_server + "/run_bash_script",
                headers={"Content-Type": "application/json"},
                data=payload,
                timeout=timeout,
            )
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Bash script executed successfully with return code: {result.get('returncode', -1)}")
                return json.dumps(result, indent=2)
            elif response.status_code == 400:
                return json.dumps({
                    "status": "error",
                    "output": "",
                    "error": f"Script execution failed with status code: {response.status_code}, error: {response.text}",
                    "returncode": -1,
                }, indent=2)
            else:
                logger.error(f"Failed to execute bash script. Status code: {response.status_code}, response: {response.text}")
                raise Exception("Failed to execute bash script.")
        except requests.exceptions.ReadTimeout:
            logger.error("Bash script execution timed out")
            return json.dumps({
                "status": "error",
                "output": "",
                "error": f"Script execution timed out after {timeout} seconds",
                "returncode": -1,
            }, indent=2)
        except Exception as e:
            logger.error(f"Error executing bash script: {e}")
            raise e