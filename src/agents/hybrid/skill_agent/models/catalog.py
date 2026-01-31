import re
import re
from pydantic import BaseModel, Field
import yaml

from agents.hybrid.skill_agent.models.skill import Skill

class SkillCatalog(BaseModel):
    name: str               # Name of skill cataloge respective the domain, e.g. 'chrome', 'file-system', 'excel', ...
    description: str        # Short description 
    skills: list[Skill] = Field(default_factory=list)

    def get_short_description(self) -> str:
        return f"{self.name}: {self.description} ({len(self.skills)} entries available)"
    
    def get_skill(self, skill_id: str) -> Skill | None:
        for skill in self.skills:
            if skill.id == skill_id:
                return skill
        return None

    def to_markdown(self) -> str:
        md = f"# Skill Catalog: `{self.name}`\n\n> {self.description}\n\n---\n\n"
        for skill in self.skills:
            md += skill.to_markdown() + "\n\n---\n\n"
        return md
    
    def add_skill(self, skill: Skill):
        self.skills.append(skill)

    def remove_skill(self, skill_id: str) -> bool:
        skill_to_remove = next((skill for skill in self.skills if skill.id == skill_id), None)
        if skill_to_remove is None:
            return False
        self.skills.remove(skill_to_remove)
        return True
    
    def get_skills(self) -> list[Skill]:
        return self.skills

    def get_domain_description(self) -> str:
        raise NotImplementedError("Domain description retrieval not implemented yet.")
    
    def deduplicate_skills(self):
        # deduplicate skills by the their context description
        raise NotImplementedError("Deduplication not implemented yet.")
    
    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(self.model_dump(exclude={"skills"}), f, encoding="utf-8")
            f.write("---")
            for i, skill in enumerate(self.skills):
                if i == 0:
                    f.write("\n\n")
                else:
                    f.write("\n\n---\n\n")
                f.write(skill.to_markdown())
    
    @classmethod
    def load(cls, filepath) -> "SkillCatalog":
        with open(filepath, "r", encoding="utf-8") as f:
            raw_md = f.read()

        parts = raw_md.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Invalid skill catalog format. Missing YAML front matter.")
        
        frontmatter = yaml.safe_load(parts[1])
        catalog = cls(name=frontmatter["name"], description=frontmatter["description"], skills=[])

        sections = re.split(r'\n---\n', parts[2])
        for section in sections:
            section = section.strip()
            skill = Skill.parse_skill_from_markdown(section)
            catalog.add_skill(skill)
        
        return catalog