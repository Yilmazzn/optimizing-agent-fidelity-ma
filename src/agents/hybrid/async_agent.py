import base64
import json
from typing import Optional, Tuple

from loguru import logger
import requests
from tenacity import retry
from agents.grounders.qwen3_vl import Qwen3VLGrounder
from agents.hybrid.agent import Custom2Agent
from agents.hybrid.tools import CuaToolSet

class AsyncToolSet(CuaToolSet):
    def __init__(self, vm_http_server: str):
        super().__init__(
            grounder=Qwen3VLGrounder(),
            http_server=vm_http_server,
            enable_python_execution_tool=True,
            enable_terminal_command_tool=True,
        )

        self.tools.append({
            "type": "function",
            "name": "screenshot",
            "description": "Take a screenshot of the current screen.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        })

    def parse_action(self, tool_call, screenshot: str) -> tuple[str, str, tuple[int, int], bool]:
        name = tool_call.name
        args = json.loads(tool_call.arguments)

        if name == "screenshot":
            tool_result = [
                {
                    "type": "input_image",
                    "image_url": {"url": "data:image/png;base64," + screenshot},
                }
            ]
        else:
            return super().parse_action(tool_call, screenshot)
        
        retrigger = {
            "screenshot": False,
            "execute_python_code": False,
            "execute_terminal_command": False,
        }.get(name, True)

        return tool_result, "", (0, 0), retrigger



class AsyncCustomAgent(Custom2Agent):
    """ same custom-2, but async """

    def __init__(self, vm_http_server: str, name: str = "async-custom-2"):
        super().__init__(name=name, vm_http_server=vm_http_server)
        self.tool_set = AsyncToolSet(vm_http_server=vm_http_server)
        self.system_prompt += "\n* You have access to an additional tool 'screenshot' to take screenshots of the current screen whenever needed.*"

    def _generate_plan(self, task: str = None, screenshot: str = None) -> Tuple[str, list]: 
        screenshot = screenshot if self.step == 1 else None
        return super()._generate_plan(task=task, screenshot=screenshot)