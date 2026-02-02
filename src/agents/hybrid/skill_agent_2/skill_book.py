import hashlib
import json
import os
from pathlib import Path
from pydantic import BaseModel, Field
import frontmatter
from loguru import logger

from utils import create_embeddings


_SKILL_DIR = Path(__file__).parent / ".skills"
os.makedirs(_SKILL_DIR, exist_ok=True)


def _hash_description(description: str) -> str:
    """Create a hash of the description for change detection."""
    return hashlib.sha256(description.encode()).hexdigest()[:16]

class SkillError(Exception):
    pass


class SkillCreationError(SkillError):
    pass

class SkillFetchError(SkillError):
    pass

class SkillMergeError(SkillError):
    pass

class SkillDomainNotFoundError(SkillError):
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
    embedding: list[float] | None = Field(default=None, exclude=True)
    description_hash: str | None = Field(default=None, exclude=True)
    
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
    
    def save(self, domain_dir: Path):
        """Save the skill as a markdown file with YAML frontmatter."""
        metadata = {
            "name": self.name,
            "description": self.description,
            "context": self.context,
            "guidance": self.guidance,
            "annotations": self.annotations,
            "metrics": self.metrics.model_dump(),
        }
        
        # Create frontmatter post with metadata and content
        post = frontmatter.Post(self.to_markdown(), **metadata)
        
        skill_path = domain_dir / f"{self.name}.md"
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
    
    def needs_embedding_update(self) -> bool:
        """Check if the embedding needs to be updated."""
        if self.embedding is None or self.description_hash is None:
            return True
        return self.description_hash != _hash_description(self.description)
    
    def set_embedding(self, embedding: list[float]):
        """Set the embedding and update the description hash."""
        self.embedding = embedding
        self.description_hash = _hash_description(self.description)
    
    def to_evaluation_markdown(self) -> str:
        annotations_md = "## Annotations\n"
        if len(self.annotations) == 0:
            annotations_md += "<none>"
        else: 
            annotations_md += "\n".join([f"- {note}" for note in self.annotations])

        metrics_md = (
            "## Skill Usage Metrics\n"
            f"- Requested by Agent {self.metrics.times_requested} times, Actually followed {self.metrics.times_followed} times\n"
            f"- Positive Impact: {self.metrics.positive_impact}\n"
            f"- Negative Impact: {self.metrics.negative_impact}\n"
            f"- Neutral Impact: {self.metrics.neutral_impact}\n"
        )

        return (
            f"# [`{self.id}`] {self.title}\n\n"
            f"## Description\n{self.description}\n\n"
            f"{self.content}\n\n"
            f"{annotations_md}\n\n"
            f"{metrics_md}"
        )

    def to_markdown(self, evaluation_format: bool = False) -> str:
        if evaluation_format:
            return self.to_evaluation_markdown()
        
        annotations_md = ""
        if len(self.annotations) > 0:
            annotations_md = "\n\n## Annotations\n"
            annotations_md += "\n".join([f"- {note}" for note in self.annotations])
        
        return f"# [`{self.id}`] {self.title}\n\n{self.content}{annotations_md}"

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
        embeddings_cache: dict[str, dict] = {}

        # Load domain index
        index_path = location / "index.json"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                domains_data = json.load(f)
                for d in domains_data:
                    domains[d["id"]] = SkillDomain(id=d["id"], description=d["description"])

        # Load existing embeddings cache
        embeddings_path = location / "embeddings.json"
        if embeddings_path.exists():
            with open(embeddings_path, "r", encoding="utf-8") as f:
                embeddings_cache = json.load(f)

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
                    
                    # Restore embedding from cache if available
                    if skill.id in embeddings_cache:
                        cached = embeddings_cache[skill.id]
                        skill.embedding = cached.get("embedding")
                        skill.description_hash = cached.get("description_hash")
                    
                    domains[domain_id].add_skill(skill)

        skill_book = cls(domains=domains)
        
        # Generate embeddings for skills that need them
        skill_book._ensure_embeddings(location)
        
        return skill_book
    
    def _ensure_embeddings(self, location: Path = None):
        """Generate embeddings for skills that don't have them or have changed descriptions."""
        location = location or _SKILL_DIR
        all_skills = self.get_all_skills()
        
        skills_needing_embeddings = [
            skill for skill in all_skills if skill.needs_embedding_update()
        ]
        
        for skill in skills_needing_embeddings:
            if skill.embedding is not None:
                logger.info(f"Description changed for skill '{skill.id}', regenerating embedding")
        
        if not skills_needing_embeddings:
            return
        
        logger.info(f"Generating embeddings for {len(skills_needing_embeddings)} skills...")
        
        descriptions = [skill.description for skill in skills_needing_embeddings]
        new_embeddings = create_embeddings(descriptions)
        
        for skill, embedding in zip(skills_needing_embeddings, new_embeddings):
            skill.set_embedding(embedding)
            logger.debug(f"Created embedding for skill: {skill.id}")
        
        # Save updated embeddings
        self._save_embeddings(location)

    def _save_embeddings(self, location: Path = None):
        """Save embeddings to file."""
        location = location or _SKILL_DIR
        embeddings_path = location / "embeddings.json"
        
        embeddings_data = {}
        for skill in self.get_all_skills():
            if skill.embedding is not None:
                embeddings_data[skill.id] = {
                    "description_hash": skill.description_hash,
                    "embedding": skill.embedding
                }
        
        with open(embeddings_path, "w", encoding="utf-8") as f:
            json.dump(embeddings_data, f)
        logger.info(f"Saved embeddings to {embeddings_path}")

    def save(self, location: Path | str = None):
        location = Path(location) if location else _SKILL_DIR
        os.makedirs(location, exist_ok=True)

        # Save each skill file
        for domain_id, domain in self.domains.items():
            domain_dir = location / domain_id
            os.makedirs(domain_dir, exist_ok=True)

            for skill_name, skill in domain.skills.items():
                skill.save(domain_dir)

        # Save domain index
        with open(location / "index.json", "w", encoding="utf-8") as f:
            domains_data = [
                {"id": d.id, "description": d.description} for d in self.domains.values()
            ]
            json.dump(domains_data, f, indent=4)
        
        # Save embeddings
        self._save_embeddings(location)

    def list_domains(self) -> str:
        if not self.domains:
            return "No domains available."
        return "\n".join(
            [f"- `{d.id}`: {d.description}" for d in self.domains.values()]
        )

    def get_domain(self, domain_id: str) -> SkillDomain:
        if domain_id not in self.domains:
            raise SkillDomainNotFoundError(
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
        guidance: str = None,
        dismiss_annotations: bool = False
    ) -> tuple[Skill, list[str]]:
        
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
        
        if dismiss_annotations:
            skill.annotations = []
            changes.append("Annotations cleared")
        
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

    def find_similar_skills(
        self, 
        description: str, 
        domain: str,
        threshold: float = 0.85
    ) -> str:
        """
        Find skills similar to the given description within a domain.
        
        Args:
            description: The description to search for similar skills.
            domain: The domain to search within.
            threshold: Similarity threshold (default 0.85).
            
        Returns:
            Markdown formatted string of similar skills separated by ---, 
            or a message if no similar skills are found.
        """
        domain_obj = self.get_domain(domain)
        skills = list(domain_obj.skills.values())
        
        if not skills:
            return f"No skills found in domain '{domain}'."
        
        # Filter skills that have embeddings
        skills_with_embeddings = [s for s in skills if s.embedding is not None]
        if not skills_with_embeddings:
            return f"No skills with embeddings found in domain '{domain}'."
        
        # Create embedding for the description
        logger.info(f"Creating embedding for similarity search in domain '{domain}'")
        query_embedding = create_embeddings(description)[0]
        
        # Calculate cosine similarity
        def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            return dot_product / (magnitude1 * magnitude2)
        
        # Find similar skills
        similar_skills: list[tuple[Skill, float]] = []
        for skill in skills_with_embeddings:
            similarity = cosine_similarity(query_embedding, skill.embedding)
            if similarity >= threshold:
                similar_skills.append((skill, similarity))
        
        if not similar_skills:
            return f"No similar skills found in domain '{domain}'."
        
        # Sort by similarity (highest first)
        similar_skills.sort(key=lambda x: x[1], reverse=True)
        
        # Format as markdown separated by ---
        markdown_parts = []
        for skill, similarity in similar_skills:
            markdown_parts.append(
                f"{skill.to_markdown()}\n\n*Similarity: {similarity:.2%}*"
            )
        
        return "\n\n---\n\n".join(markdown_parts)
    
    def get_all_skills(self) -> list[Skill]:
        skills = []
        for domain in self.domains.values():
            skills.extend(domain.skills.values())
        return skills


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


