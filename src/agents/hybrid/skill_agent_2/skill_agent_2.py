import json
import os
from datetime import datetime
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.grounders.qwen3_vl import Qwen3VLGrounder
from agents.hybrid.agent import Custom3Agent
from agents.hybrid.skill_agent_2.skill_book import SkillBook
from agents.hybrid.skill_agent_2.reflector import SkillsReflector
from agents.hybrid.skill_agent_2.skill_manager import SkillManager
import asyncio

from agents.hybrid.tools import CuaToolSet
from domain.request import TokenUsage

class SkillTools(CuaToolSet):
    def __init__(self, vm_http_server: str, skill_book: SkillBook):
        super().__init__(
            enable_python_execution_tool=True, 
            enable_terminal_command_tool=True, 
            http_server=vm_http_server,
            grounder=Qwen3VLGrounder()
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
        else: 
            return super().parse_action(tool_call, screenshot)
    
    def get_requested_skill_ids(self) -> list[str]:
        return list(self.requested_skill_ids)


class SkillAgent2(Custom3Agent):
    """Hybrid with coding tools + skill management"""
    def __init__(self, vm_http_server: str, name: str = "skill-agent-2"):
        super().__init__(name=name, vm_http_server=vm_http_server)
        self.skill_book = SkillBook.load()
        self.skill_manager = SkillManager(skill_book=self.skill_book)
        self.reflector = SkillsReflector(skill_book=self.skill_book)
        self.tool_set = SkillTools(vm_http_server=vm_http_server, skill_book=self.skill_book)


    @retry(
       reraise=True,
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    )
    def _make_checkpoint(self):
        self.history.append({
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": "Terminated the turn, and will transition now to reflection phase. Reply only with 'ACK' to confirm."
            }]
        })

        response = self.planner_client.responses.create(
            model="gpt-5.2",
            # instructions=instructions,
            tools=self.tool_set.tools,
            reasoning={"effort": "none"},
            input=self.history,
            prompt_cache_key=self.prompt_cache_key,
            tool_choice="none",
            max_output_tokens=20,
        )
        self.last_response_id = response.id
        return response
    
    def _learn(self) -> dict:
        reflection, token_usage = self.reflector.reflect(self.last_response_id, self.tool_set.get_requested_skill_ids())
        skill_manager_history = self.skill_manager.learn(reviews=reflection.skill_reviews, learnings=reflection.new_learnings)
        
        learning_log = {
            "reflection": {
                "reflections": json.dumps(json.loads(reflection.model_dump_json(indent=4)), indent=4, ensure_ascii=False),
                "token_usage": json.dumps(json.loads(token_usage.model_dump_json(indent=4)), indent=4, ensure_ascii=False),
            },
            "skill_manager_history": skill_manager_history,
        }
        return learning_log

    def end_task(self, task_id: str) -> None:
        self._remove_screenshots_from_history(remove_all=True)
        self._make_checkpoint()

        learning_log = self._learn()
        learning_log["task_id"] = task_id

        self.skill_book.save()

        # persist learning log
        log_dir = ".learning_logs"
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_path = os.path.join(log_dir, f"{timestamp}.json")
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(learning_log, f, indent=4, ensure_ascii=False)
        logger.info(f"Learning log persisted to {log_path}")   