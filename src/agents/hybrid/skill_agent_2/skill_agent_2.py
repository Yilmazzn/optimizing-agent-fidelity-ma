import json
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.hybrid.agent import Custom3Agent
from agents.hybrid.skill_agent_2.skill_book import SkillBook
from agents.hybrid.skill_agent_2.skill_reflector import SkillReflector
from agents.hybrid.skill_agent_2.trajectory_reflector import TrajectoryReflector
import asyncio

from agents.hybrid.tools import CuaToolSet

class SkillTools(CuaToolSet):
    def __init__(self, vm_http_server: str, skill_book: SkillBook):
        super().__init__(
            enable_python_execution_tool=True, 
            enable_code_interpreter_tool=True, 
            http_server=vm_http_server
        )
        self.skill_book = skill_book
        self.tools = self.tools + [
            {
                "type": "function",
                "name": "read_skills",
                "description": "Read the full content of the specific skills. Use this to see current content before updating.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": self.skill_book.get_all_skill_ids()
                            },
                            "description": "The list of skill IDs to read (e.g. ['libreoffice-calc/select-cells', 'gimp/transparency'])."
                        },
                    },
                    "required": ["skill_ids"],
                    "additionalProperties": False
                }
            },
        ]
        self.requested_skill_ids = set()

    def parse_action(self, tool_call, screenshot: str):
        name = tool_call.name
        args = json.loads(tool_call.arguments)

        if name == "read_skills":
            skill_ids = args["skill_ids"]
            self.requested_skill_ids.update(skill_ids)
            skills_content = []
            for skill_id in skill_ids:
                skill = self.skill_book.get_skill(skill_id)
                skills_content.append(skill.to_markdown())
            tool_result = "\n\n---\n\n".join(skills_content)
            return tool_result, "", (0, 0), True
        if name == "finish":
            results = super().parse_action(tool_call, screenshot)
            results[0] = "Terminated the turn, and will transition now to reflection phase."
            return results
        else: 
            return super().parse_action(tool_call, screenshot)
    
    def get_requested_skill_ids(self) -> list[str]:
        return list(self.requested_skill_ids)


class SkillAgent2(Custom3Agent):
    """Hybrid with coding tools + skill management"""
    def __init__(self, vm_http_server: str, name: str = "skill-agent-2"):
        super().__init__(name=name, vm_http_server=vm_http_server)
        self.skill_book = SkillBook()
        self.trajectory_reflector = TrajectoryReflector()
        self.skill_reflector = SkillReflector(skill_book=self.skill_book)
        self.tool_set = SkillTools(vm_http_server=vm_http_server, skill_book=self.skill_book)
    
    async def _learn(self) -> None:
        return await asyncio.gather(
            self.trajectory_reflector.reflect_on_trajectory(self.last_response_id),
            self.skill_reflector.reflect_on_skill_usage(self.last_response_id, self.tool_set.get_requested_skill_ids()),
        )

    def end_task(self) -> None:
        self._remove_screenshots_from_history(remove_all=True)
        results = asyncio.run(self._learn())

        logger.info(f"Trajectory Reflector extracted learnings: {results}")
