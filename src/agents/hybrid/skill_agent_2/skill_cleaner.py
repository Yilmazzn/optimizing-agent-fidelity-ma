from typing import Literal
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.hybrid.skill_agent_2.skill_book import Skill, SkillBook
from agents.hybrid.skill_agent_2.skill_manager_tools import SkillManagerTools

NEGATIVE_RATIO_THRESHOLD = 0.5
FOLLOW_RATE_THRESHOLD = 0.1

class SkillCleanup(BaseModel):
    """Skill flagged for cleanup evaluation."""
    type: Literal["skill_cleanup"] = "skill_cleanup"
    skill_markdown: str  # Output of to_evaluation_markdown()
    cleanup_reason: Literal["high_negative", "low_follow_rate", "similar_to_other"]
    similar_skill_id: str | None = None  # Only if cleanup_reason == "similar_to_other"

class SkillCleaner:
    def __init__(self, skill_book: SkillBook):
        self.skill_book = skill_book
        self.tools = SkillManagerTools(skill_book=skill_book)
        self.last_response_id = None

    def find_negative_heavy_skills(self) -> list[SkillCleanup]:
        flagged = []
        for skill in self.skill_book.get_all_skills():
            total = skill.metrics.positive_impact + skill.metrics.negative_impact
            if total < 3:
                continue
            if skill.metrics.negative_impact == 0:
                continue
            negative_ratio = skill.metrics.negative_impact / total
            if negative_ratio >= NEGATIVE_RATIO_THRESHOLD:
                flagged.append(
                    SkillCleanup(
                        skill_markdown=skill.to_evaluation_markdown(),
                        cleanup_reason="high_negative"
                    )
                )
        return flagged
    
    def find_low_follow_rate_skills(self) -> list[SkillCleanup]:
        flagged = []
        for skill in self.skill_book.get_all_skills():
            if skill.metrics.times_requested < 5:
                continue
            follow_rate = skill.metrics.times_followed / skill.metrics.times_requested
            if follow_rate < FOLLOW_RATE_THRESHOLD:
                flagged.append(
                    SkillCleanup(
                        skill_markdown=skill.to_evaluation_markdown(),
                        cleanup_reason="low_follow_rate"
                    )
                )
        return flagged
