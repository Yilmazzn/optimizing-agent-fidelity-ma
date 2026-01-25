
import datetime
from pydantic import BaseModel, Field
import re

_SKILL_MARKDOWN = """
## [{id}] {title}

### 🎯 When is this relevant?
{description}

### 📖 Guide
{content}

### 📝 Field Notes
{notes}
""".strip()

class SkillNote(BaseModel):
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    note: str

class Skill(BaseModel):
    id: str
    title: str
    description: str
    content: str
    notes: list[SkillNote] = Field(default_factory=list)

    def to_markdown(self) -> str:
        notes_md = "<none>"
        if self.notes:
            notes_md = "\n".join([f"- {note.timestamp.isoformat()}: '{note.note}'" for note in self.notes])
        return _SKILL_MARKDOWN.format(
            id=self.id,
            title=self.title,
            description=self.description,
            content=self.content,
            notes=notes_md
        )
    
    def add_note(self, note: str):
        self.notes.append(SkillNote(note=note))

    @classmethod
    def parse_skill_from_markdown(cls, md: str) -> "Skill":
        id_match = re.search(r'^## \[(.*?)\] (.*)$', md, re.MULTILINE)
        description_match = re.search(r'### 🎯 When is this relevant\?\r?\n(.*?)\r?\n### 📖 Guide', md, re.DOTALL)
        content_match = re.search(r'### 📖 Guide\r?\n(.*?)\r?\n### 📝 Field Notes', md, re.DOTALL)
        notes_match = re.search(r'### 📝 Field Notes\r?\n(.*)$', md, re.DOTALL)
        
        if not (id_match and description_match and content_match and notes_match):
            raise ValueError("Invalid skill markdown format.")

        skill_id = id_match.group(1).strip()
        title = id_match.group(2).strip()
        description = description_match.group(1).strip()
        content = content_match.group(1).strip()
        notes_raw = notes_match.group(1).strip()

        notes = []
        if notes_raw and notes_raw != "<none>":
            for line in notes_raw.splitlines():
                note_match = re.match(r'- (.*?): \'(.*)\'', line.strip())
                if note_match:
                    timestamp_str = note_match.group(1).strip()
                    note_text = note_match.group(2).strip()
                    timestamp = datetime.datetime.fromisoformat(timestamp_str)
                    notes.append(SkillNote(timestamp=timestamp, note=note_text))

        return Skill(
            id=skill_id,
            title=title,
            description=description,
            content=content,
            notes=notes
        )

