from pydantic import BaseModel
from agents.hybrid.skill_agent_2.skill_book import SkillBook





class SkillReflector:
    def __init__(self, skill_book: SkillBook):
        self.skill_book = skill_book   

    def _make_call(self, previous_response_id: str):
        ...

    def reflect_on_skill_usage(self, previous_response_id: str, used_skill_ids: list[str]) -> str:
        ...

    