from pydantic import BaseModel, Field
from typing import Literal
from tenacity import retry, stop_after_attempt, wait_exponential

from domain.request import TokenUsage
from utils import get_openai_client


class FrictionLearning(BaseModel):
    """Knowledge extracted from a friction moment."""
    type: Literal["friction"] = "friction"
    what_happened: str
    why_it_matters: str
    scope: str
    situation: str
    guidance: str
    confidence: Literal["low", "medium", "high"]
    steps_wasted: int = Field(ge=1)


class DiscoveredLearning(BaseModel):
    """Knowledge discovered without struggling."""
    type: Literal["discovered"] = "discovered"
    what_happened: str
    why_it_matters: str
    scope: str
    situation: str
    guidance: str
    confidence: Literal["low", "medium", "high"]


Learning = FrictionLearning | DiscoveredLearning


class TrajectoryReflection(BaseModel):
    """Output from reflecting on a trajectory."""
    learnings: list[Learning] = Field(default_factory=list)


_USER_PROMPT = """
## Reflect on this trajectory

You have just completed a task. Review the trajectory above and extract any guidance that could help a less capable agent succeed in similar situations.

Look for:

1. **Friction moments**: Where did you struggle, retry, or take multiple attempts before succeeding? What knowledge would have helped you succeed faster?
2. **Discovered knowledge**: Did you learn or notice anything useful that wasn't obvious beforehand?

### Guidelines

- **Be general**: Guidance should help with many tasks, not just this specific one
- **Be positive**: Describe what to do, not what to avoid
- **Be honest**: Only extract learnings where you're reasonably confident
- **Be selective**: Not every trace has learnings—return an empty list if nothing meaningful

### Field guidance

- **scope**: Use lowercase. Either 'general', 'os', or a specific application name like 'gimp', 'chrome', 'libreoffice-calc'
- **situation**: Describe WHEN this applies in general terms, not the specific task
- **guidance**: Concrete, actionable steps. Include exact menu paths, shortcuts, or UI elements
- **confidence**: 'high' = certain and generalizable; 'medium' = fairly sure; 'low' = might be situational
- **steps_wasted** (friction only): Count of actions spent before finding the solution
""".strip()


class TrajectoryReflector:
    def __init__(self):
        self.client = get_openai_client()

    @retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    )
    def _make_call(self, previous_response_id: str) -> TrajectoryReflection:
        response = self.client.responses.parse(
            model="gpt-5.2",
            reasoning={"effort": "high"},
            input=_USER_PROMPT,
            previous_response_id=previous_response_id,
            text_format=TrajectoryReflection,
        )
        return response.output_parsed

    def reflect_on_trajectory(self, previous_response_id: str) -> tuple[list[Learning], TokenUsage]:
        response = self._make_call(previous_response_id)
        token_usage = TokenUsage.from_response(response)
        return response.learnings, token_usage