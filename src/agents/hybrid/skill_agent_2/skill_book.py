import json
import os
from pathlib import Path
from pydantic import BaseModel, Field
import frontmatter

_SKILL_DIR = Path(__file__).parent / ".skills"

class SkillError(Exception):
    pass


class SkillCreationError(SkillError):
    pass


class SkillFetchError(SkillError):
    pass

class SkillMergeError(SkillError):
    pass

class SkillMetrics(BaseModel):
    times_requested: int = 0
    times_followed: int = 0
    positive_impact: int = 0
    negative_impact: int = 0
    neutral_impact: int = 0

class Skill(BaseModel):
    domain: str
    name: str
    description: str
    context: str
    guidance: str
    annotations: list[str] = Field(default_factory=list)
    metrics: SkillMetrics = Field(default_factory=SkillMetrics)
    
    @property
    def title(self) -> str:
        return self.name.replace("-", " ").title()
    
    @property
    def id(self) -> str:
        return f"{self.domain}/{self.name}"

    @property
    def content(self) -> str:
        """Generate markdown content from context and guidance."""
        return f"## Context\n{self.context}\n\n## Guidance\n{self.guidance}"

    def to_markdown(self) -> str:
        annotations_md = "## Annotations\n"
        if len(self.annotations) == 0:
            annotations_md += "<none>"
        else: 
            annotations_md += "\n".join([f"- {note}" for note in self.annotations])
        return f"# [`{self.id}`] {self.title}\n\n{self.content}\n\n{annotations_md}"

    def annotate(self, note: str):
        self.annotations.append(note)


class SkillDomain(BaseModel):
    id: str
    description: str
    skills: dict[str, Skill] = Field(default_factory=dict)

    def add_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    def get_skill(self, skill_name: str) -> Skill:
        if skill_name not in self.skills:
            available = ", ".join(self.skills.keys()) if self.skills else "none"
            raise SkillFetchError(
                f"Skill '{skill_name}' not found in domain '{self.id}'. Available skills: {available}"
            )
        return self.skills[skill_name]

    def list_skills(self) -> str:
        if not self.skills:
            return f"No skills in domain '{self.id}'."
        return "\n".join(
            [f"- `{self.id}/{name}`: {skill.title}" for name, skill in self.skills.items()]
        )

    def get_skill_ids(self) -> list[str]:
        return [f"{self.id}/{name}" for name in self.skills.keys()]


class SkillBook(BaseModel):
    domains: dict[str, SkillDomain] = Field(default_factory=dict)

    @classmethod
    def load(cls, location: Path | str = None) -> "SkillBook":
        location = Path(location) if location else _SKILL_DIR
        domains: dict[str, SkillDomain] = {}

        # Load domain index
        index_path = location / "index.json"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                domains_data = json.load(f)
                for d in domains_data:
                    domains[d["id"]] = SkillDomain(id=d["id"], description=d["description"])

        # Load skills into their domains
        for domain_dir in location.iterdir():
            if domain_dir.is_file():
                continue
            domain_id = domain_dir.name
            if domain_id not in domains:
                domains[domain_id] = SkillDomain(id=domain_id, description="")

            for skill_file in domain_dir.iterdir():
                if skill_file.suffix != ".md":
                    continue
                with open(skill_file, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                    skill_data = post.metadata
                    skill_data["domain"] = domain_id
                    skill = Skill(**skill_data)
                    domains[domain_id].add_skill(skill)

        return cls(domains=domains)

    def save(self, location: Path | str = None):
        location = Path(location) if location else _SKILL_DIR
        os.makedirs(location, exist_ok=True)

        # Save each skill file
        for domain_id, domain in self.domains.items():
            domain_dir = location / domain_id
            os.makedirs(domain_dir, exist_ok=True)

            for skill_name, skill in domain.skills.items():
                skill_path = domain_dir / f"{skill_name}.md"
                metadata = skill.model_dump(mode="json")
                post = frontmatter.Post(content="", **metadata)
                with open(skill_path, "w", encoding="utf-8") as f:
                    f.write(frontmatter.dumps(post))

        # Save domain index
        with open(location / "index.json", "w", encoding="utf-8") as f:
            domains_data = [
                {"id": d.id, "description": d.description} for d in self.domains.values()
            ]
            json.dump(domains_data, f, indent=4)

    def list_domains(self) -> str:
        if not self.domains:
            return "No domains available."
        return "\n".join(
            [f"- `{d.id}`: {d.description}" for d in self.domains.values()]
        )

    def get_domain(self, domain_id: str) -> SkillDomain:
        if domain_id not in self.domains:
            raise SkillFetchError(
                f"Domain '{domain_id}' not found. Available domains:\n{self.list_domains()}"
            )
        return self.domains[domain_id]

    def add_domain(self, domain_id: str, description: str) -> SkillDomain:
        if domain_id in self.domains:
            raise SkillCreationError(f"Domain '{domain_id}' already exists.")
        self.domains[domain_id] = SkillDomain(id=domain_id, description=description)
        return self.domains[domain_id]

    def get_domain_ids(self) -> list[str]:
        return list(self.domains.keys())

    def get_skill(self, skill_id: str) -> Skill:
        """Get a skill by its full ID (domain/skill_name)."""
        if "/" not in skill_id:
            error_msg = f"Skill ID '{skill_id}' is invalid. Must be in format '<domain>/<skill_name>'.\n\n"
            error_msg += f"Available skills:\n{self.list_skills()}"
            raise SkillFetchError(error_msg)
        domain_id, skill_name = skill_id.split("/", 1)
        domain = self.get_domain(domain_id)
        return domain.get_skill(skill_name)

    def add_skill(self, domain_id: str, name: str, description: str, context: str, guidance: str) -> Skill:
        domain = self.get_domain(domain_id)
        
        if domain_id in name: 
            raise SkillCreationError(f"Skill name '{name}' should not include domain prefix '{domain_id}/'.")
        if len(name) < 3 or len(name) > 20:
            raise SkillCreationError("Skill name must be between 3 and 20 characters.")
        if not all(c.islower() or c == '-' for c in name):
            raise SkillCreationError("Skill name must be lowercase and can only contain letters and hyphens.")

        if len(description) < 10 or len(description) > 100:
            raise SkillCreationError("Skill description must be between 10 and 100 characters.")
        if len(context) < 10 or len(context) > 500:
            raise SkillCreationError("Skill context must be between 10 and 500 characters.")
        if len(guidance) < 20 or len(guidance) > 2000:
            raise SkillCreationError("Skill guidance must be between 20 and 2000 characters.")

        skill = Skill(
            domain=domain_id,
            name=name,
            description=description,
            context=context,
            guidance=guidance
        )

        domain.add_skill(skill)
        return skill
    
    def remove_skill(self, skill_id: str):
        domain_id, skill_name = skill_id.split("/", 1)
        domain = self.get_domain(domain_id)
        if skill_name not in domain.skills:
            raise SkillFetchError(f"Skill '{skill_id}' not found.")
        del domain.skills[skill_name]

    def update_skill(
        self,
        skill_id: str,
        description: str = None,
        context: str = None,
        guidance: str = None
    ) -> tuple[Skill, list[str]]:
        """Update a skill's fields. Only non-None fields are updated.
        
        Returns:
            tuple: (updated skill, list of changes made)
        """
        skill = self.get_skill(skill_id)
        changes = []

        if description is not None:
            old_description = skill.description
            skill.description = description
            changes.append(f"Description updated from '{old_description}' to '{skill.description}'")
        
        if context is not None:
            skill.context = context
            changes.append("Context updated")
        
        if guidance is not None:
            skill.guidance = guidance
            changes.append("Guidance updated")
        
        return skill, changes

    def list_skills(self, domain: str = None) -> str:
        if domain:
            domain_obj = self.get_domain(domain)
            return domain_obj.list_skills()
        else:
            all_skills = []
            for domain_obj in self.domains.values():
                all_skills.extend(domain_obj.list_skills())
            return "\n".join(all_skills)

    def get_all_skill_ids(self) -> list[str]:
        """Get all skill IDs in format domain/skill_name."""
        skill_ids = []
        for domain in self.domains.values():
            skill_ids.extend(domain.get_skill_ids())
        return skill_ids

    def find_similar_skills(self, content: str, threshold: float = 0.8) -> list[Skill]:
        raise NotImplementedError("Skill similarity search not implemented yet.")


if __name__ == "__main__":
    # Example usage
    skill_book = SkillBook()
    skill_book.add_domain("browser", "Skills for browser automation")

    skill = Skill(
        name="open-browser",
        description="A skill for opening a web browser.",
        title="Open Web Browser",
        content="Instructions to open a web browser.",
    )

    skill_id = skill_book.add_skill("browser", skill)
    print(f"Added skill: {skill_id}")

    # Retrieve skill by ID
    retrieved = skill_book.get_skill("browser/open-browser")
    print(retrieved.to_markdown())


