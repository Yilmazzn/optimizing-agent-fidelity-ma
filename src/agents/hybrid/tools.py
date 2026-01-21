import json
import traceback
from typing import List, Sequence, Tuple

from loguru import logger
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, wait_exponential

from agents.grounders.grounder import Grounder


_computer_use_tools = [
    {
        "type": "function",
        "name": "press_keys",
        "description": "Performs key down presses on the arguments passed in order, then performs key releases in reverse order.",
        "parameters": {
            "type": "object",
            "properties": {
                "keys": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Ordered list of keys to press down sequentially and release in reverse order."
                }
        },
        "required": ["keys"],
        "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "type_text",
        "description": "Types a string of text on the keyboard.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to be typed on the keyboard."
                }
            },
            "required": ["text"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "move_cursor_to_element",
        "description": "Moves/Hovers the cursor to a UI element. The element must be described in a way that makes it uniquely identifiable on the current screen. Important: this function only hovers over the element.",
        "parameters": {
            "type": "object",
            "properties": {
                "element": {
                    "type": "string",
                    "description": "A precise, unambiguous description of exactly one UI element that is uniquely identifiable on the screen. The description must include distinguishing attributes such as visible text, element role or type (e.g., button, input, icon), container or section context, and/or relative position. Vague or generic descriptions are invalid."
                }
            },
            "required": ["element"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "mouse_click",
        "description": "Clicks the mouse at a uniquely identifiable UI element on the screen.",
        "parameters": {
            "type": "object",
            "properties": {
                "element": {
                    "type": "string",
                    "description": "A precise, unambiguous description of exactly one UI element that is uniquely identifiable on the current screen. The description must include distinguishing attributes such as visible text, element role or type (e.g., button, menu item, icon), container or section context, and/or relative position. Vague or generic descriptions are invalid."
                },
                "mouse_button": {
                    "type": "string",
                    "enum": ["left", "right"],
                    "default": "left",
                    "description": "Which mouse button to click. Defaults to 'left'. If 'right' is specified, only a single click is permitted."
                },
                "click_type": {
                    "type": "string",
                    "enum": ["single", "double", "triple"],
                    "default": "single",
                    "description": "Type of clicks to perform. Defaults to 'single'. Values greater than 'single' are only valid when button is 'left', and perform double or triple clicks needed for specific operations."
                }
            },
            "required": ["element"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "scroll",
        "description": "Performs a scroll action using the mouse scroll wheel.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "integer",
                    "description": "The scroll amount equaling 'clicks' on the mousewheel. Positive values scroll up (or right if horizontal is true); negative values scroll down (or left if horizontal is true)."
                },
                "horizontal": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether the scroll is horizontal. Defaults to false (vertical scrolling). If true, the scroll is performed horizontally."
                }
            },
            "required": ["amount"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "wait",
        "description": "Waits for a specified number of seconds to allow a change on the screen or in the system to occur.",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "number",
                    "default": 5,
                    "description": "Number of seconds to wait before continuing. Defaults to 5 seconds."
                }
            },
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "finish",
        "description": "Finishes the current task execution if successful, failed, or infeasible after completing the task or failing to do so, and reports its final status. To be used at last after completing the task.",
        "parameters": {
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
    },
    {
        "type": "function",
        "name": "left_click_drag",
        "description": "Performs a left-click drag from one UI element to another. Both elements must be uniquely identifiable on the screen.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_element": {
                    "type": "string",
                    "description": "A precise, unambiguous description of the UI element where the drag starts. Must include distinguishing attributes such as visible text, element role/type, container context, and/or relative position to ensure it is uniquely identifiable."
                },
                "target_element": {
                    "type": "string",
                    "description": "A precise, unambiguous description of the UI element where the drag ends. Must include distinguishing attributes such as visible text, element role/type, container context, and/or relative position to ensure it is uniquely identifiable."
                }
            },
            "required": ["start_element", "target_element"],
            "additionalProperties": False
        }
    }
]

_python_tool = {
    "type": "function",
    "name": "execute_python_code",
    "description": "Executes a snippet of Python code in a secure sandboxed environment and returns the output or any errors encountered during execution." +
                    "The Python should be the raw complete code snippet ('python -c' is not required).",
    "parameters": {
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
    "type": "function",
    "name": "execute_terminal_command",
    "description": "Executes a temporary terminal command on the system and returns the command output or any errors encountered during execution.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The terminal command to be executed."
            },
            "working_dir": {
                "type": "string",
                "description": "The working directory in which to execute the command. If not specified, uses the default working dir."
            }
        },
        "required": ["command"],
        "additionalProperties": False
    }
}

def _normalize_key(key: str) -> str:
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
        "arrowup": "up",
        "arrowdown": "down",
        "arrowleft": "left",
        "arrowright": "right",
        "meta": "win",
    }
    return conversion.get(k, k)

class ToolNotFoundError(Exception):
    pass

class CuaToolSet:

    def __init__(self, 
                 grounder: Grounder, 
                 http_server: str = None, 
                 enable_python_execution_tool: bool = False,
                 enable_terminal_command_tool: bool = False
        ):
        self.tools = _computer_use_tools
        self.http_server = http_server
        self.enable_python_execution_tool = enable_python_execution_tool
        self.enable_terminal_command_tool = enable_terminal_command_tool
        self.grounder = grounder

        if self.enable_python_execution_tool or self.enable_terminal_command_tool:
            if not self.http_server:
                raise ValueError("http_server must be provided when coding tools are enabled.")

        if self.enable_python_execution_tool:
            self.tools.append(_python_tool)
        if self.enable_terminal_command_tool:
            self.tools.append(_terminal_tool)

    def parse_action(self, tool_call: dict, screenshot: str) -> Tuple[str, str, tuple[int, int]]:
        name = tool_call.name
        args = json.loads(tool_call.arguments)

        tool_result = ""
        pyautogui_actions = []
        usage = (0, 0)

        element = args.get("element")
        mouse_button = args.get("mouse_button", "left")
        click_type = args.get("click_type", "single")
        keys = args.get("keys")
        text = args.get("text")
        status = args.get("status")
        start_element = args.get("start_element")
        target_element = args.get("target_element")
        amount = args.get("amount")
        horizontal = args.get("horizontal", False)

        if name == "mouse_click":
            if element is None:
                raise ValueError(f"mouse_click requires 'element' argument. Got arguments {args}")
            if mouse_button not in ["left", "right"]:
                raise ValueError(f"mouse_button must be 'left' or 'right'. Got: {mouse_button}")
            if click_type not in ["single", "double", "triple"]:
                raise ValueError(f"click_type must be 'single', 'double', or 'triple'. Got: {click_type}")
            
            clicks = {
                "single": 1,
                "double": 2,
                "triple": 3
            }.get(click_type, 1)

            coords, usage = self.grounder.locate_ui_element_coords(ui_element=element, screenshot=screenshot)
            pyautogui_actions.append(f"pyautogui.click({coords[0]}, {coords[1]}, clicks={clicks}, button='{mouse_button}', interval=0.1)")
            tool_result = f"{click_type} clicked {mouse_button} button at {coords}."
        elif name == "move_cursor_to_element":
            if element is None:
                raise ValueError(f"move_cursor_to_element requires 'element' argument. Got arguments {args}")
            
            coords, usage  = self.grounder.locate_ui_element_coords(ui_element=element, screenshot=screenshot)
            pyautogui_actions.append(f"pyautogui.moveTo({coords[0]}, {coords[1]}, duration=0.2)")
            tool_result = f"Moved cursor to {coords}."

        elif name == "left_click_drag":
            if start_element is None or target_element is None:
                raise ValueError(f"left_click_drag requires 'start_element' and 'target_element' arguments. Got arguments {args}")
            
            start_coords, usage_start = self.grounder.locate_ui_element_coords(ui_element=start_element, screenshot=screenshot)
            target_coords, usage_target = self.grounder.locate_ui_element_coords(ui_element=target_element, screenshot=screenshot)
            usage = (usage_start[0] + usage_target[0], usage_start[1] + usage_target[1])

            pyautogui_actions.append(f"pyautogui.moveTo({start_coords[0]}, {start_coords[1]}, duration=0.2)")
            pyautogui_actions.append("pyautogui.mouseDown(button='left')")
            pyautogui_actions.append(f"pyautogui.moveTo({target_coords[0]}, {target_coords[1]}, duration=0.5)")
            pyautogui_actions.append("pyautogui.mouseUp(button='left')")
            tool_result = f"Dragged left click from {start_coords} to {target_coords}."

        elif name == "press_keys":
            if keys is None:
                raise ValueError(f"press_keys requires 'keys' argument. Got arguments {args}")
            
            normalized_keys = [_normalize_key(str(k)) for k in keys if str(k).strip()]
            for k in normalized_keys:
                pyautogui_actions.append(f"pyautogui.keyDown({k!r})")
            pyautogui_actions.append("time.sleep(0.3)")  # small pause
            for k in reversed(normalized_keys):
                pyautogui_actions.append(f"pyautogui.keyUp({k!r})")
            tool_result = f"Pressed keys: {', '.join(keys)}"

        elif name == "type_text":
            # Some models send a literal backslash-n sequence ("\\n") instead of an actual newline.
            # In that case, convert it so we press Enter rather than typing backslash + n.
            if "\\n" in text and "\n" not in text:
                text = text.replace("\\r\\n", "\n").replace("\\n", "\n")

            # Same for tab: convert literal "\\t" to actual tab character.
            if "\\t" in text and "\t" not in text:
                text = text.replace("\\t", "\t")

            # Split by newlines first, then handle tabs within each line.
            parts = text.split("\n")
            for idx, part in enumerate(parts):
                # Split each part by tabs and press tab key between segments.
                tab_segments = part.split("\t")
                for tab_idx, segment in enumerate(tab_segments):
                    if segment:
                        pyautogui_actions.append(f"pyautogui.typewrite({segment!r}, interval=0.05)")
                    if tab_idx < len(tab_segments) - 1:
                        pyautogui_actions.append("pyautogui.press('tab')")
                if idx < len(parts) - 1:
                    pyautogui_actions.append("pyautogui.press('enter')")
            tool_result = f"Typed text: {text!r}"

        elif name == "scroll":
            if amount is None:
                raise ValueError(f"scroll requires 'amount' argument. Got arguments {args}")
            if horizontal:
                pyautogui_actions.append(f"pyautogui.hscroll({amount})")
                tool_result = f"Scrolled horizontally by {amount} units."
            else:
                pyautogui_actions.append(f"pyautogui.scroll({amount})")
                tool_result = f"Scrolled vertically by {amount} units."

        elif name == "wait":
            seconds = args.get("seconds", 5)
            try:
                sec_float = float(seconds)
            except Exception as e:
                raise ValueError(f"seconds must be numeric, got: {seconds}") from e
            if sec_float < 0:
                raise ValueError(f"seconds must be >= 0, got: {seconds}")
            pyautogui_actions.append(f"time.sleep({sec_float})")
            tool_result = f"Waited for {sec_float} seconds."
        elif name == "finish":
            _status = {
                "success": "DONE",
                "failure": "FAIL",
                "infeasible": "FAIL",
            }.get(status.lower().strip(), "FAIL")
            pyautogui_actions.append(_status)
            tool_result = f"Finished with status: {status}."
        
        elif self.enable_python_execution_tool and name == "execute_python_code":
            code = args.get("code")
            if code is None:
                raise ValueError(f"execute_python_code requires 'code' argument. Got arguments {args}")
            
            result = self._execute_python_code(code=code)
            if result["status"] == "error":
                logs = result["output"]
            else:
                logs = result["message"]
            tool_result = json.dumps({
                "status": result["status"],
                "output": logs,
            }, indent=2)

        elif self.enable_terminal_command_tool and name == "execute_terminal_command":
            command = args.get("command")
            working_dir = args.get("working_dir")
            if command is None:
                raise ValueError(f"execute_terminal_command requires 'command' argument. Got arguments {args}")
            
            result = self._execute_terminal_command(command=command, working_dir=working_dir)
            tool_result = json.dumps(result, indent=2)

        else:
            raise ToolNotFoundError(f"Unknown tool call: {name}")
    
        return tool_result, "\n".join(pyautogui_actions), usage
    
        
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
    def _execute_terminal_command(self, command: str, working_dir: str = None, timeout: int = 300) -> dict:
        payload = json.dumps({
            "script": command,
            "timeout": timeout,
            "working_dir": working_dir
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


