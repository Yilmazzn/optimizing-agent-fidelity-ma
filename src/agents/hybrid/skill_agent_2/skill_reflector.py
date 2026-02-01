from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.hybrid.skill_agent_2.skill_book import SkillBook
from domain.request import TokenUsage


_USER_PROMPT = """
## Reflect on the skills used previously.

During this task, the following skills were retrieved from the skillbook:

## Skills 

{skills}

## Task

Review each skill and evaluate how it impacted the trajectory separated by `---`.

For each skill, assess:
- **followed**: Did the agent follow this skill's guidance? (yes | no | partially)
- **impact**: Did this skill help the agent succeed (positive), mislead or cause friction (negative), or have no meaningful effect (neutral)?
- **reason**: Why did it have this impact? Tie your explanation to what actually happened in the trace.
- **feedback**: What would make this skill better? Concrete suggestions. Use null if the skill worked well as-is.

### Guidelines

- **Be specific**: Reference what actually happened in the trace
- **Be constructive**: Feedback should suggest improvements
- **Judge impact by outcome**: 
  - positive = skill contributed to success
  - negative = skill caused confusion, errors, or wasted steps
  - neutral = skill had no meaningful effect (irrelevant to task, or agent already knew this)
- **Include all skills**: Every retrieved skill needs a reflection

Think carefully and thoroughly in your internal reasoning. Analyze each skill's usage against the trace, consider the agent's actions, and evaluate the outcomes.
""".strip()

class SkillReflection(BaseModel):
    """Reflection on a single skill's usage during the task."""
    skill_id: str = Field(description="The skill identifier (e.g., 'domain/skill-name')")
    followed: Literal["yes", "no", "partially"] = Field(description="Whether the agent followed this skill's guidance")
    impact: Literal["positive", "negative", "neutral"] = Field(description="Whether this skill helped, hindered, or had no effect")
    reason: str = Field(description="Brief explanation tied to the trace")
    feedback: str | None = Field(description="Concrete suggestion for improvement, or null if none needed")


class SkillReflections(BaseModel):
    """Collection of reflections on all skills used during the task."""
    reflections: list[SkillReflection]


class SkillReflector:
    def __init__(self, skill_book: SkillBook):
        self.skill_book = skill_book   

    @retry(
       reraise=True,
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    )
    def _make_call(self, previous_response_id, prompt: str):
        response = self.client.responses.parse(
            model="gpt-5.2",
            reasoning={"effort": "high"},
            input=prompt,
            previous_response_id=previous_response_id,
            text_format=SkillReflections,
        )
        return response
    
    def _format_skill_to_markdown(self, skill_id: str) -> str:
        skill = self.skill_book.get_skill(skill_id)
        return f"- `{skill_id}`: {skill.description}"
    
    def _handle_reflection(self, reflection: SkillReflection) -> bool:
        """ Bool return variable determines if skill should be further analyzed by skill manager """
        skill = self.skill_book.get_skill(reflection.skill_id)
        skill.metrics.times_requested += 1
        
        if reflection.feedback:
            skill.annotate(reflection.feedback)

        skill.metrics.negative_impact += 1 if reflection.impact == "negative" else 0
        skill.metrics.positive_impact += 1 if reflection.impact == "positive" else 0
        skill.metrics.neutral_impact += 1 if reflection.impact == "neutral" or reflection.followed == "no" else 0

        return reflection.feedback is not None or reflection.impact == "negative"
        
    async def reflect_on_skill_usage(self, previous_response_id: str, used_skill_ids: list[str]) -> tuple[list[SkillReflection], TokenUsage]:
        skills_list = [self._format_skill_to_markdown(skill_id) for skill_id in used_skill_ids]

        response = self._make_call(
            previous_response_id,
            prompt=_USER_PROMPT.format(skills="\n".join(skills_list))
        )
        token_usage = TokenUsage.from_response(response)
        parsed_response: SkillReflections = response.output_parsed

        skills_to_process = []
        for reflection in parsed_response.reflections:
            needs_review = self._handle_reflection(reflection)
            if needs_review:
                skills_to_process.append(reflection)
        return skills_to_process, token_usage
    