from datetime import datetime
import json
import os
from pathlib import Path
import re

from agents.hybrid.skill_agent.models.catalog import SkillCatalog
from agents.hybrid.skill_agent.models.skill import Skill
from domain.request import TokenUsage

_SKILLS_DIR = Path(__file__).parent.parent / ".skills"
os.makedirs(_SKILLS_DIR, exist_ok=True)

_SKILL_ARCHIVE_DIR = _SKILLS_DIR.parent  / ".skills-archive"
os.makedirs(_SKILL_ARCHIVE_DIR, exist_ok=True)

class SkillError(Exception):
    pass

class SkillTitleTooLongError(SkillError):
    pass

class SkillAlreadyExists(SkillError):
    pass

class SkillCatalogAlreadyExists(SkillError):
    pass

class SkillDoesNotExist(SkillError):
    pass

class SkillCatalogDoesNotExist(SkillError):
    pass

class SkillUpdateError(SkillError):
    pass

class SkillCatalogManager:

    def __init__(self):
        self.skill_catalogs: list[SkillCatalog] = []
        self.refresh_catalog()

    def list_catalogs_structure(self) -> str:
        domain_structure = ""
        for catalog in self.skill_catalogs:
            domain_structure += f"### `{catalog.name}`: {catalog.description}\n\n"
            for skill in catalog.skills:
                domain_structure += f"- [{skill.id}] {skill.title}\n"
            domain_structure += "\n"
        return domain_structure

    def list_catalogs_high_level(self) -> str:
        if not self.skill_catalogs:
            return "<no skill domains currently exist>"
        domain_summary = ""
        for catalog in self.skill_catalogs:
            domain_summary += f"- `{catalog.name}`: {catalog.description}\n"
        return domain_summary

    def _ensure_catalog_exists(self, catalog_name: str) -> SkillCatalog:
        for catalog in self.skill_catalogs:
            if catalog.name == catalog_name:
                return catalog
        raise SkillCatalogDoesNotExist(
            f"Skill catalog with name '{catalog_name}' does not exist.\n\n Current Structure: \n{self.list_catalogs_high_level()}"
        )

    def refresh_catalog(self):
        self.skill_catalogs = []
        for catalog_file in _SKILLS_DIR.glob("*.md"):
            catalog = SkillCatalog.load(catalog_file)
            self.skill_catalogs.append(catalog)

    def _generate_unique_id(self, title: str):
        existing_ids = {skill.id for catalog in self.skill_catalogs for skill in catalog.skills}
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug) # Remove special chars
        slug = re.sub(r'[\s-]+', '-', slug).strip('-') # Spaces to dashes

        if slug in existing_ids:
            raise SkillAlreadyExists(f"Skill with ID '{slug}' already exists.")
        
        return slug
    
    def _validate_title(self, title: str):
        if len(title) > 50:
            raise SkillTitleTooLongError("Skill title exceeds maximum length of 50 characters.")

    def _clean_markdown(self, text: str) -> str:
        return text.replace("#", "").replace("---", "").strip()

    def save(self, location: Path | str = None):
        save_location = location if location else _SKILLS_DIR
        for catalog in self.skill_catalogs:
            catalog.save(save_location / f"{catalog.name}.md")

    def create_new_catalog(self, name: str, description: str, skill_title: str, skill_context: str, skill_content: str) -> SkillCatalog:
        for catalog in self.skill_catalogs:
            if catalog.name == name:
                raise SkillCatalogAlreadyExists(f"Skill catalog with name '{name}' already exists.")

        new_catalog = SkillCatalog(name=name, description=description)
        self.skill_catalogs.append(new_catalog)
        self.create_new_skill(
            catalog_name=name,
            title=skill_title,
            context=skill_context,
            content=skill_content,
        )
        return new_catalog
    
    def create_new_skill(self, catalog_name: str, title: str, context: str, content: str) -> Skill:
        self._validate_title(title)
        catalog = self._ensure_catalog_exists(catalog_name)
        new_skill = Skill(
            id=self._generate_unique_id(title),
            title=title,
            description=self._clean_markdown(context),
            content=self._clean_markdown(content),
        )
        catalog.add_skill(new_skill)
        return new_skill
    
    def get_skill(self, catalog_name: str, skill_id: str) -> Skill:
        catalog = self._ensure_catalog_exists(catalog_name)
        skill = catalog.get_skill(skill_id)
        if skill is None:
            raise SkillDoesNotExist(
                f"Skill with ID '{skill_id}' does not exist in domain '{catalog_name}'.\n\nCurrent Skills in domain '{catalog_name}': \n" +
                "\n".join([f"- [{s.id}] {s.title}" for s in catalog.skills])
            )
        return skill
    
    def add_skill(self, catalog_name: str, skill: str) -> Skill:
        catalog = self._ensure_catalog_exists(catalog_name)
        parsed_skill = Skill.parse_skill_from_markdown(skill)
        self._validate_title(parsed_skill.title)
        if catalog.get_skill(parsed_skill.id):
            raise SkillAlreadyExists(f"Skill with ID '{parsed_skill.id}' already exists in domain '{catalog_name}'.")
        catalog.add_skill(parsed_skill)
        return parsed_skill

    def add_note_to_skill(self, catalog_name: str, skill_id: str, note: str) -> Skill:
        skill = self.get_skill(catalog_name, skill_id)
        skill.add_note(note)
        return skill
    
    def refactor_skill(self, catalog_name: str, skill_id: str, new_title: str = None, new_context: str = None, new_content: str = None) -> Skill:
        skill = self.get_skill(catalog_name, skill_id)

        if new_title is None and new_context is None and new_content is None:
            raise SkillUpdateError(f"No title, context, or content provided for the update of '{skill_id}' in domain '{catalog_name}'.")

        if new_title:
            self._validate_title(new_title)
            skill.id = self._generate_unique_id(new_title)
            skill.title = new_title
        if new_context:
            skill.description = self._clean_markdown(new_context)
        if new_content:
            skill.content = self._clean_markdown(new_content)
        skill.notes = []  # Clear notes on refactor
        return skill
    
    def remove_skill(self, catalog_name: str, skill_id: str):
        catalog = self._ensure_catalog_exists(catalog_name)
        success = catalog.remove_skill(skill_id)
        if not success:
            raise SkillDoesNotExist(
                f"Skill with ID '{skill_id}' does not exist in domain '{catalog_name}'.\n\nCurrent Skills in domain '{catalog_name}': \n" +
                "\n".join([f"- [{s.id}] {s.title}" for s in catalog.skills])
            )
    
    def archive_skill_catalogs(self, summary: str, token_usage: TokenUsage, action_history: list[dict], task_id: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_obj = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "token_usage": token_usage.model_dump(),
            "action_history": action_history,
            "task_id": task_id,
        }

        with open(_SKILL_ARCHIVE_DIR / f"{timestamp}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(archive_obj, indent=4))

        archive_dir = _SKILL_ARCHIVE_DIR / task_id
        os.makedirs(archive_dir, exist_ok=True)

        self.save(location=archive_dir)