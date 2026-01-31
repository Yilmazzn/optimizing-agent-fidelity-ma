from pydantic import BaseModel
from enum import Enum

class SkillFeedbackType(str, Enum):
    HELPFUL = "helpful"
    HARMFUL = "harmful"
    NEUTRAL = "neutral"

class SkillImpact(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class SkillFeedbackTicket(BaseModel):
    skill_id: str
    impact_analysis: str
    feedback_type: SkillFeedbackType
    impact: SkillImpact
    feedback: str

class SkillCreationTicket(BaseModel):
    observation: str
    root_cause_analysis: str
    insight: str

