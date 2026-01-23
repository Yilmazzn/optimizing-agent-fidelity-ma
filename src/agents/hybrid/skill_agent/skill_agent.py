from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from agents.hybrid.agent import Custom2Agent
from agents.hybrid.skill_agent.skill_prompts import SKILLS_REFLECTOR_PROMPT
from agents.hybrid.skill_agent.skill_tools import SkillManager, SkillsToolSet

_EXTEND_PROMPT = """
# Skills

Skills are optional, domain-specific capability packages (e.g., instructions, templates, workflows, or logic) that can complement the assistant's general knowledge. They are loaded dynamically and are not always needed.

The assistant should use its own judgment to decide whether a Skill could improve accuracy, consistency, or efficiency. Skills are often helpful for domain-specific tasks, structured workflows, or situations with explicit standards, but may be unnecessary for simple or well-known problems.

When a Skill seems relevant, the assistant should consult it via the `read-skill` tool and incorporate its guidance as appropriate. Skill content should inform the response, not replace general reasoning unless clearly beneficial.

If no Skill meaningfully adds value, proceed using general knowledge alone.  
Skills and tool usage should remain internal unless explicitly requested.

## Available Skills:
{skills_list}
""".strip()

class SkillAgent(Custom2Agent):
    """Hybrid with coding tools + skill management"""
    def __init__(self, vm_http_server: str, name: str = "skill-agent"):
        super().__init__(name=name, vm_http_server=vm_http_server)
        
        self.skill_manager = SkillManager()
        self.available_skills = self.skill_manager.get_available_skills()
        skills_list = "\n".join([f"- {skill.name}: {skill.description}" for skill in self.available_skills])
        self.system_prompt += "\n\n" + _EXTEND_PROMPT.format(skills_list=skills_list)

        self.tool_set = SkillsToolSet(vm_http_server=vm_http_server)

    def _curate_skill(self):
        ...

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

        _input = [
            termination_tool_result,
            {
                "role": "user",
                "content": [{"type": "input_text", "text": SKILLS_REFLECTOR_PROMPT}]
            }
        ]
        response = self.planner_client.responses.create(
            model="gpt-5.2",
            input=_input,
            previous_response_id=self.previous_response_id,
            tool_choice="none",
        )
        return response.output_text

    def end_task(self):
        reflection = self._learn_from_episode()
        logger.info(f"Reflector learned from episode: \n{reflection}")
        self.skill_manager.learn_from_reflection(reflection)