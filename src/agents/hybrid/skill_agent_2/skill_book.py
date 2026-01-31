from datetime import datetime
import json
import os
from pathlib import Path
from pydantic import BaseModel, Field, model_validator
import frontmatter

_SKILL_DIR = Path(__file__).parent / ".skills"

class SkillError(Exception):
    pass

class SkillCreationError(SkillError):
    pass

class SkillFetchError(SkillError):
    pass

class SkillMetrics(BaseModel):
    helpful: int = 0
    harmful: int = 0
    fetch_count: int = 0

class SkillChangelogEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    reason: str
    change: str

class Skill(BaseModel):
    id: str
    description: str
    domain: str
    metrics: SkillMetrics = Field(default_factory=SkillMetrics)
    changelog: list[SkillChangelogEntry] = Field(default_factory=list)
    feedbacks: list[str] = Field(default_factory=list)
    title: str
    content: str

    @property
    def is_core(self) -> bool:
        return self.domain == "core"

    @model_validator(mode="after")
    def sort_changelog(self):
        self.changelog.sort(key=lambda e: e.timestamp)
        return self

    def to_markdown(self) -> str:
        if self.is_core:
            return f"[`{self.id}`] {self.content}"
        return f"# [`{self.id}`] {self.title}\n\n{self.description}\n\n{self.content}"
    
    def save_to_file(self, location: Path | str = None):
        location = location or (_SKILL_DIR / self.domain / f"{self.id}.md")
        os.makedirs(location.parent, exist_ok=True)

        metadata = self.model_dump(exclude={"content"}, mode="json")
        post = frontmatter.Post(content=self.content, **metadata)
        file_content = frontmatter.dumps(post)
        with open(location, "w", encoding="utf-8") as f:
            f.write(file_content)
    
    def change(self, reason: str, change: str):
        entry = SkillChangelogEntry(reason=reason, change=change)
        self.changelog.append(entry)

class SkillDomain(BaseModel):
    id: str
    description: str

class SkillBook(BaseModel):
    skills: list[Skill] = Field(default_factory=list)
    domains: list[SkillDomain] = Field(default_factory=list)

    @classmethod
    def load(cls, location: Path | str = None) -> "SkillBook":
        location = location or _SKILL_DIR
        skills = []
        for domain_dir in Path(location).iterdir():
            if domain_dir.is_file():
                continue
            for skill_file in domain_dir.iterdir():
                if skill_file.suffix != ".md":
                    continue
                with open(skill_file, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                    skill_data = post.metadata
                    skill_data["content"] = post.content
                    skill = Skill(**skill_data)
                    skills.append(skill)

        with open(Path(location) / "index.json", "r", encoding="utf-8") as f:
            domains_data = json.load(f)
            domains = [SkillDomain(**d) for d in domains_data]
        return cls(skills=skills, domains=domains)
    
    def save(self):
        location = location or _SKILL_DIR
        for skill in self.skills:
            skill.save_to_file()
        with open(Path(location) / "index.json", "w", encoding="utf-8") as f:
            domains_data = [domain.model_dump() for domain in self.domains]
            json.dump(domains_data, f, indent=4)

    def list_domains(self) -> str:
        return "\n".join([f"- `{domain.id}`: {domain.description}" for domain in self.domains])
    
    def get_domain(self, domain_id: str) -> SkillDomain:
        for domain in self.domains:
            if domain.id == domain_id:
                return domain
        raise SkillFetchError(f"Domain '{domain_id}' not found in skill book. Available domains:\n{self.list_domains()}")

    def get_domain_names(self) -> list[str]:
        return [domain.id for domain in self.domains]
    
    def get_skill_ids_in_domain(self, domain_id: str) -> list[str]:
        domain = self.get_domain(domain_id)
        skill_ids = [skill.id for skill in self.skills if skill.domain == domain.id]
        return skill_ids
    
    def get_core_skills(self) -> list[Skill]:
        return [skill for skill in self.skills if skill.is_core]
    
    def list_core_skills(self) -> str:
        core_skills = self.get_core_skills()
        if not core_skills:
            return "[no core skills available]"
        return "\n".join([f"- [`{skill.id}`]: {skill.content}" for skill in core_skills])

    def list_skills_in_domain(self, domain_id: str) -> str:
        domain = self.get_domain(domain_id)
        skills_in_domain = [skill for skill in self.skills if skill.domain == domain.id]
        if not skills_in_domain:
            raise SkillFetchError(f"No skills found in domain '{domain_id}'.")
        return "\n".join([f"- [`{skill.id}`]: {skill.title}" for skill in skills_in_domain])
    
    def find_similar_skills(self, content: str, threshold: float = 0.8) -> list[Skill]:
        raise NotImplementedError("Skill similarity search not implemented yet.")

if __name__ == "__main__":
    skill = Skill(
        id="skill-001",
        description="A skill for opening a web browser.",
        domain="browser",
        title="Open Web Browser",
        content="Instructions to open a web browser."
    )
    skill.change(reason="Initial creation", change="Created the skill for opening a web browser.")
    skill.save_to_file()

    skill_book = SkillBook.load()


