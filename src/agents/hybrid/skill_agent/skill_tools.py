from datetime import datetime
import json
import os
from pathlib import Path
from pydantic import BaseModel, Field

from tenacity import stop_after_attempt
from tenacity import retry
import yaml

from agents.grounders.qwen3_vl import Qwen3VLGrounder
from agents.hybrid.skill_agent.skill_prompts import _SKILLS_MANAGER_PROMPT
from agents.hybrid.tools import CuaToolSet, ToolNotFoundError
from domain.request import TokenUsage
from utils import get_openai_client, get_tool_calls_from_response


_SKILLS_FOLDER = Path(__file__).parent / ".skills"
_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

os.makedirs(_SKILLS_FOLDER, exist_ok=True)

_read_skill_tool = {
    "type": "function",
    "name": "read-skill",
    "description": "Reads the content of a specified skill.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the skill to be read."
            }
        },
        "required": ["name"],
        "additionalProperties": False
    }
}

_write_skill_tool = {
    "type": "function",
    "name": "write-skill",
    "description": "Creates or overwrites a skill with the given name, description, and content.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the skill to be created or updated. Must be unique, lower-case, and use hyphens instead of spaces. If it does not exist, a new skill will be created."
            },
            "description": {
                "type": "string",
                "description": "A brief description of the skill, specifying its purpose and when to use it."
            },
            "content": {
                "type": "string",
                "description": "The full content of the skill, including instructions and workflows."
            }
        },
        "required": ["name"],
        "additionalProperties": False
    }
}
_deprecate_skill_tool = {
    "type": "function",
    "name": "deprecate-skill",
    "description": "Permanently removes a skill with the given name.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the skill to be deprecated."
            }
        },
        "required": ["name"],
        "additionalProperties": False
    }
}


class SkillDoesNotExistError(Exception):
    pass

class SkillMeta(BaseModel):
    name: str
    description: str

    def __str__(self):
        return f"- {self.name}: {self.description}"

class Skill(SkillMeta):
    last_updated: str = Field(default_factory=lambda: datetime.now().strftime(_DATETIME_FORMAT))
    content: str

    @classmethod
    def from_file(cls, filepath: str) -> "Skill":
        with open(filepath, "r") as f:
            file_content = f.read()

        parts = file_content.split('---')
        
        if len(parts) < 3:
            raise ValueError("Invalid format: missing frontmatter delimiters")
        
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()
        
        return Skill.model_validate(frontmatter | {"content": body})
    
    def persist_to_file(self):
        filepath = f"{_SKILLS_FOLDER}/{self.name}.md"
        self.last_updated = datetime.now().strftime(_DATETIME_FORMAT)

        yaml_str = yaml.dump(self.model_dump(exclude={"content"}), default_flow_style=False)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write('---\n')
            f.write(yaml_str)
            f.write('---\n')
            f.write(self.content)

    def update(self, description: str, content: str):
        if description:
            self.description = description
        if content:
            self.content = content
        self.last_updated = datetime.now().strftime(_DATETIME_FORMAT)
        self.persist_to_file()

class SkillManager:

    def __init__(self):
        self.client = get_openai_client()
        self.previous_response_id = None

        skill_catalog = "\n".join([str(skill) for skill in self.get_available_skills()])
        self.system_prompt = _SKILLS_MANAGER_PROMPT.format(skill_catalog=skill_catalog)
        self.last_tool_results = None

    def _get_skill(self, name: str) -> Skill:
        skill_file = _SKILLS_FOLDER / f"{name}.md"
        if not skill_file.exists():
            raise SkillDoesNotExistError(f"Skill '{name}' does not exist.")
        
        skill = Skill.from_file(skill_file)
        return skill

    def get_available_skills(self) -> list[SkillMeta]:
        skills = []
    
        for skill_file in _SKILLS_FOLDER.glob("*.md"):
            skill = Skill.from_file(skill_file)
            skills.append(SkillMeta(name=skill.name, description=skill.description))
        
        return skills
    
    def _update_skill(self, name: str, description: str = None, content: str = None):
        skill = self._get_skill(name)
        skill.update(description, content)

    def deprecate_skill(self, name: str):
        skill_file = _SKILLS_FOLDER / f"{name}.md"

        if skill_file.exists():
            skill_file.unlink()
    
    def add_skill(self, name: str, description: str, content: str):
        skill = Skill(
            name=name,
            description=description,
            content=content
        )
        skill.persist_to_file()

    def read_skill_content(self, name: str) -> str:
        skill = self._get_skill(name)
        return skill.content
    
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
    )
    def _make_call(self, user_query: str):
        _input = []
        if self.last_tool_results:
            _input += self.last_tool_results
        _input += [{
            "role": "user",
            "content": [{
                "type": "input_text", 
                "text": user_query
            }]
        }]

        response = self.client.responses.create(
            model="gpt-5.2",
            instructions=self.system_prompt,
            previous_response_id=self.previous_response_id,
            input=_input,
            reasoning={"effort": "high"},
            tools=[
                _read_skill_tool,
                _write_skill_tool,
                _deprecate_skill_tool
            ]
        )
        self.previous_response_id = response.id
        return response
    
    def _handle_tool_call(self, tool_call) -> dict:
        name = tool_call.name
        args = json.loads(tool_call.arguments)
        tool_result = None

        skill_name = args.get("name")
        description = args.get("description")
        content = args.get("content")

        if not skill_name:
            raise ValueError(f"Skill name is required for {name} tool. Received args: {args}")

        if name == "read-skill":
            tool_result = self.read_skill_content(skill_name)
        elif name == "write-skill":
            try: 
                skill = self._get_skill(skill_name)
                skill.update(description=description, content=content)
            except SkillDoesNotExistError:
                if not description or not content:
                    raise ValueError(f"Description and content are required to create a new skill '{skill_name}'.")
                self.add_skill(name=skill_name, description=description, content=content)
            tool_result = f"Skill '{skill_name}' has been created successfully."
        elif name == "deprecate-skill":
            self.deprecate_skill(skill_name)
            tool_result = f"Skill '{skill_name}' has been deprecated successfully."

        return {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": tool_result,
        }
    
    def learn_from_reflection(self, reflection: str) -> TokenUsage:
        token_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, cached_prompt_tokens=0)

        while True:
            response = self._make_call(reflection)
            token_usage += TokenUsage.from_response(response)
            tool_calls = get_tool_calls_from_response(response)

            tool_results = [self._handle_tool_call(tool_call) for tool_call in tool_calls]
            self.last_tool_results = tool_results
            
            # terminate if agent stopped making tool calls
            if len(tool_calls) == 0:
                break

        return token_usage  

    
class SkillsToolSet(CuaToolSet):
    def __init__(self, vm_http_server: str):
        super().__init__(
            grounder=Qwen3VLGrounder(),
            http_server=vm_http_server,
            enable_python_execution_tool=True,
            enable_terminal_command_tool=True,
        )
        self.skill_manager = SkillManager()
        self.tools.extend(self._get_tools())

    def list_skills(self) -> list[SkillMeta]:
        return self.skill_manager.get_available_skills()
    
    def read_skill(self, skill_name: str) -> str:
        try: 
            content = self.skill_manager.read_skill_content(skill_name)
        except SkillDoesNotExistError:
            available_skills = self.skill_manager.get_available_skills()
            error_msg = f"Error: Skill '{skill_name}' does not exist."
            error_msg += "\n\nAvailable skills:\n"
            for skill in available_skills:
                error_msg += f"- {skill.name}: {skill.description}\n"
            return error_msg
        return content
    
    def parse_action(self, tool_call, screenshot: str) -> tuple[str, str, tuple[int, int], bool]:
        name = tool_call.name
        args = json.loads(tool_call.arguments)

        if name == "read-skill":
            skill_name = args.get("name")
            tool_result = self.read_skill(skill_name)
        else:
            return super().parse_action(tool_call, screenshot)
        
        return tool_result, "", (0, 0), True

    def _get_tools(self):
        return [{
            "type": "function",
            "name": "read-skill",
            "description": "Reads the content of a specified skill.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "The name of the skill to be read."
                    }
                },
                "required": ["skill_name"],
                "additionalProperties": False
            }
        }]