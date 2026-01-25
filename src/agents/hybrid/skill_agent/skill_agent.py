import datetime
import os
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed
from agents.hybrid.agent import Custom2Agent
from agents.hybrid.skill_agent.models.skill_catalog_manager import SkillCatalogManager
from agents.hybrid.skill_agent.models.skill_curator import SkillCurator
from agents.hybrid.skill_agent.prompts.agent_prompt import SKILL_AGENT_PROMPT
from agents.hybrid.skill_agent.prompts.reflector_prompt import SKILLS_REFLECTOR_PROMPT
from agents.hybrid.skill_agent.skill_tools import SkillsToolSet

class SkillAgent(Custom2Agent):
    """Hybrid with coding tools + skill management"""
    def __init__(self, vm_http_server: str, name: str = "skill-agent"):
        super().__init__(name=name, vm_http_server=vm_http_server)
        
        self.skill_manager = SkillCatalogManager()
        self.skill_curator = SkillCurator(skill_catalog_manager=self.skill_manager)

        self.system_prompt = self.generate_system_prompt()
        self.tool_set = SkillsToolSet(vm_http_server=vm_http_server, skill_catalog_manager=self.skill_manager)

    def generate_system_prompt(self) -> str:
        system_prompt = SKILL_AGENT_PROMPT.format(
            datetime=datetime.datetime.today().strftime('%A, %B %d, %Y'),
            skill_catalog_summary=self.skill_manager.list_catalogs_high_level(),
            sudo_password=os.getenv("VM_SUDO_PASSWORD"),
        )
        return system_prompt 

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(5),
        reraise=True,
    )
    def _learn_from_episode(self):
        # reuse planner with its own system prompt
        # might be suboptimal, but reasoning traces are elsewise hidden and lost which can lead to insights being missed
        # also utilize prefix caching this way to reduce costs and latency

        # overwrite tool result to move over to "evaluation" phase
        termination_tool_result = self.last_tool_results[-1]
        termination_tool_result["output"] = "TASK COMPLETED\n\nTransitioning to reflection phase."

        _prompt = SKILLS_REFLECTOR_PROMPT.format(
            skill_catalog_structure=self.skill_manager.list_catalogs_structure()
        )

        _input = [
            termination_tool_result,
            {
                "role": "user",
                "content": [{"type": "input_text", "text": _prompt}]
            }
        ]
        response = self.planner_client.responses.create(
            model="gpt-5.2",
            input=_input,
            previous_response_id=self.previous_response_id,
            tool_choice="none",
        )
        return response.output_text

    def end_task(self, task_id: str):
        reflection = self._learn_from_episode()
        logger.info(f"Reflector learned from episode: \n{reflection}")
        token_usage, agent_output = self.skill_curator.learn_from_reflection(reflection)
        self.skill_manager.archive_skill_catalogs(
            token_usage=token_usage, 
            summary=agent_output, 
            action_history=self.skill_curator.action_history,
            task_id=task_id
        )