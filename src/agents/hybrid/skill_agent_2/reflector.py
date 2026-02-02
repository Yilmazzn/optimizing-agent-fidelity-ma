from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.hybrid.skill_agent_2.skill_book import SkillBook
from domain.request import TokenUsage
from utils import get_openai_client

_USER_PROMPT = """
## Reflect on this trajectory

Review the trajectory you just completed and provide:
1. **Skill Reviews** — feedback on each skill that was retrieved
2. **New Learnings** — guidance that could help a less capable agent

### Skills Retrieved

{skills_section}

Note: You already saw the full content of these skills during the task. The descriptions above are just for reference.

---

## Part 1: Skill Reviews

Provide one review per skill listed above. If no skills were retrieved, return an empty list.

Focus on:
- Did following (or not following) the skill help or hurt?
- Was the guidance accurate and complete?
- What concrete improvement would make this skill better?

---

## Part 2: New Learnings

Extract guidance from:
- **Friction moments**: Where you struggled, retried, or wasted steps before succeeding
- **Discoveries**: Useful knowledge you noticed that wasn't obvious beforehand

**Worth extracting:**
- Non-obvious UI locations (menus, settings, hidden features)
- Keyboard shortcuts or faster workflows
- Gotchas or prerequisites that aren't intuitive
- Correct sequence of steps when order matters

**Not worth extracting:**
- Basic computer knowledge (clicking, scrolling, typing)
- Task-specific details that won't generalize
- Knowledge already covered by a retrieved skill (give feedback instead)

---

## Guidelines

- **Empty is fine**: Not every trajectory has learnings—return empty lists if nothing meaningful
- **Be general**: Guidance should help with many tasks, not just this specific one
- **Be concrete**: Include exact menu paths, shortcuts, UI elements
- **Avoid duplicates**: If a skill already covers something, improve the skill via feedback rather than creating a new learning
""".strip()


class SkillPositive(BaseModel):
    """Skill was followed and helped succeed."""
    
    skill_id: str = Field(
        description="The skill identifier (e.g., 'gimp/transparency')"
    )
    followed: Literal["yes", "partially"] = Field(
        description="'yes' = fully followed, 'partially' = some parts followed"
    )
    impact: Literal["positive"] = Field(
        default="positive",
        description="Skill helped succeed"
    )
    what_helped: str = Field(
        description="Brief description of how the skill contributed to success"
    )


# === Followed: Negative ===

class SkillNegative(BaseModel):
    """Skill was followed but caused friction or errors."""
    
    skill_id: str = Field(
        description="The skill identifier (e.g., 'gimp/transparency')"
    )
    followed: Literal["yes", "partially"] = Field(
        description="'yes' = fully followed, 'partially' = some parts followed"
    )
    impact: Literal["negative"] = Field(
        default="negative",
        description="Skill caused friction or errors"
    )
    issue_type: Literal["incorrect", "incomplete", "unclear"] = Field(
        description="'incorrect' = guidance was wrong, 'incomplete' = missing steps, 'unclear' = confusing or ambiguous"
    )
    what_went_wrong: str = Field(
        description="What specifically failed or caused friction"
    )
    corrected_guidance: str | None = Field(
        default=None,
        description="The correct approach that actually worked, if discovered. Null if still unsolved."
    )


# === Followed: Neutral ===

class SkillNeutral(BaseModel):
    """Skill was followed but had no meaningful effect."""
    
    skill_id: str = Field(
        description="The skill identifier (e.g., 'gimp/transparency')"
    )
    followed: Literal["yes", "partially"] = Field(
        description="'yes' = fully followed, 'partially' = some parts followed"
    )
    impact: Literal["neutral"] = Field(
        default="neutral",
        description="Skill had no meaningful effect"
    )
    reason: Literal["not_needed", "marginal"] = Field(
        description="'not_needed' = task didn't require this, 'marginal' = helped slightly but not significantly"
    )
    suggested_improvement: str | None = Field(
        default=None,
        description="How the skill could have been improved to be more useful if applies to the situation. Null if no suggestions, irrelevant or marginal."
    )


# === Not Followed ===

class SkillNotFollowed(BaseModel):
    """Skill was retrieved but not followed."""
    
    skill_id: str = Field(
        description="The skill identifier (e.g., 'gimp/transparency')"
    )
    followed: Literal["no"] = Field(
        default="no",
        description="Skill was not followed"
    )
    reason: Literal["irrelevant", "chose_alternative", "seemed_wrong"] = Field(
        description="'irrelevant' = didn't apply to task, 'chose_alternative' = preferred different approach, 'seemed_wrong' = didn't trust the guidance"
    )
    explanation: str = Field(
        description="Brief explanation why the skill was not followed. If 'seemed_wrong' or 'chose_alternative', describe what was wrong or what alternative was chosen."
    )


SkillReview = SkillPositive | SkillNegative | SkillNeutral | SkillNotFollowed


class FrictionLearning(BaseModel):
    """Knowledge extracted from a friction moment—where the agent struggled before succeeding."""
    
    type: Literal["friction"] = Field(
        default="friction",
        description="Indicates this learning came from struggling before succeeding"
    )
    what_happened: str = Field(
        description="Brief factual description of what occurred in the trace"
    )
    why_it_matters: str = Field(
        description="What made this hard? Why would a less capable agent struggle here?"
    )
    scope: str = Field(
        description="Where this applies: 'general', 'os', or application name (e.g., 'gimp', 'chrome', 'libreoffice-calc')"
    )
    situation: str = Field(
        description="When is this relevant? Describe the general context, not the specific task"
    )
    guidance: str = Field(
        description="Clear, actionable instructions—what TO do. Use numbered steps for procedures. Include exact menu paths, shortcuts, or UI elements."
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Certainty level: 'high' = correct and generalizable, 'medium' = fairly sure, 'low' = might be situational"
    )
    steps_wasted: int = Field(
        ge=1,
        description="Approximately how many actions were spent struggling before finding the solution"
    )


class DiscoveredLearning(BaseModel):
    """Knowledge discovered without struggling—noticed something useful."""
    
    type: Literal["discovered"] = Field(
        default="discovered",
        description="Indicates this learning was discovered without friction"
    )
    what_happened: str = Field(
        description="Brief factual description of what was discovered"
    )
    why_it_matters: str = Field(
        description="Why is this useful? How was it discovered?"
    )
    scope: str = Field(
        description="Where this applies: 'general', 'os', or application name (e.g., 'gimp', 'chrome', 'libreoffice-calc')"
    )
    situation: str = Field(
        description="When is this relevant? Describe the general context, not the specific task"
    )
    guidance: str = Field(
        description="Clear, actionable instructions—what TO do. Use numbered steps for procedures. Include exact menu paths, shortcuts, or UI elements."
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Certainty level: 'high' = correct and generalizable, 'medium' = fairly sure, 'low' = might be situational"
    )

Learning = FrictionLearning | DiscoveredLearning


class TrajectoryReflection(BaseModel):
    """Complete reflection on a trajectory: skill reviews and new learnings."""
    
    skill_reviews: list[SkillReview] = Field(
        default_factory=list,
        description="One review per skill that was retrieved during the task. Empty list if no skills were used."
    )
    new_learnings: list[Learning] = Field(
        default_factory=list,
        description="New guidance extracted from friction moments or discoveries. Empty list if no meaningful learnings."
    )


class SkillsReflector:
    def __init__(self, skill_book: SkillBook):
        self.skill_book = skill_book   
        self.client = get_openai_client()

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
            text_format=TrajectoryReflection,
        )
        return response
    
    def _list_skills_md(self, skill_ids: list[str]) -> str:
        if len(skill_ids) == 0:
            return "<No skills were retrieved>"

        skills_list = [self.skill_book.get_skill(skill_id) for skill_id in skill_ids]
        md_lines = []
        for skill in skills_list:
            md_lines.append(f"- `{skill.skill_id}`: {skill.description}")
        return "\n".join(md_lines)
        
    def reflect(self, previous_response_id: str, used_skill_ids: list[str]) -> tuple[TrajectoryReflection, TokenUsage, str]:
        
        skills_md = self._list_skills_md(used_skill_ids)

        response = self._make_call(
            previous_response_id,
            prompt=_USER_PROMPT.format(skills_section=skills_md)
        )
        token_usage = TokenUsage.from_response(response)
        parsed_response: TrajectoryReflection = response.output_parsed

        return parsed_response, token_usage
    