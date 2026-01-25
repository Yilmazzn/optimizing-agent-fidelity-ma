import copy
import json
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.hybrid.skill_agent.models.skill_catalog_manager import SkillCatalogManager, SkillError
from agents.hybrid.skill_agent.prompts.curator_prompt import SKILLS_CURATOR_PROMPT
from domain.request import TokenUsage
from utils import get_openai_client, get_tool_calls_from_response

class SkillCurator:

    def __init__(self, skill_catalog_manager: SkillCatalogManager):
        self.client = get_openai_client()
        self.skill_catalog_manager = skill_catalog_manager

        self.system_prompt = SKILLS_CURATOR_PROMPT.format(skill_catalogs=self.skill_catalog_manager.list_catalogs_high_level())
        self.backup_skill_catalog = None
        self.max_iterations = 20
        self.action_history = []
    
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=4.0, min=1.0, max=30.0),
    )
    def _make_call(self, user_query: str, tool_results: list = None, previous_response_id: str = None):
        _input = []
        if tool_results:
            _input += tool_results
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
            previous_response_id=previous_response_id,
            input=_input,
            reasoning={"effort": "high"},
            tools=self.get_tools(),
        )
        return response
    
    def learn_from_reflection(self, reflection: str) -> tuple[TokenUsage, str]:
        self.backup_skill_catalog_manager = copy.deepcopy(self.skill_catalog_manager)
        token_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, cached_prompt_tokens=0)

        tool_results = []
        previous_response_id = None
        iteration = 0
        while iteration < self.max_iterations:
            response = self._make_call(reflection, tool_results, previous_response_id)
            token_usage += TokenUsage.from_response(response)
            tool_calls = get_tool_calls_from_response(response)
            
            tool_results = []
            for tool_call in tool_calls:
                self.action_history.append({
                    "name": tool_call.name,
                    "args": json.loads(tool_call.arguments),
                })
                logger.info(f"[Skill Curator] Handling tool call: {tool_call.name} with args: {json.dumps(json.loads(tool_call.arguments), indent=2)}")
                
                try:
                    tool_result = self._handle_tool_call(tool_call)
                except SkillError as e:
                    tool_result = {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": f"ERROR: {str(e)}",
                    }
                tool_results.append(tool_result)
                self.action_history[-1]["result"] = tool_result["output"]
            previous_response_id = response.id

            iteration += 1

            # terminate if agent stopped making tool calls
            if len(tool_calls) == 0:
                break

            if iteration >= self.max_iterations:
                logger.warning("Skill Curator reached maximum iterations without converging.")
                self.skill_catalog_manager = self.backup_skill_catalog_manager
                break
                
        self.skill_catalog_manager.save()
        return token_usage, response.output_text
    
    def _handle_tool_call(self, tool_call) -> dict:
        name = tool_call.name
        args = json.loads(tool_call.arguments)
        tool_result = None

        if name == "read_skill_domain":
            domain_name = args["domain"]
            catalog = self.skill_catalog_manager._ensure_catalog_exists(domain_name)
            tool_result = catalog.to_markdown()
        elif name == "create_new_domain":
            domain_name = args["domain"]
            description = args["description"]
            first_skill_title = args["first_skill_title"]
            first_skill_context = args["first_skill_context"]
            first_skill_content = args["first_skill_content"]

            catalog = self.skill_catalog_manager.create_new_catalog(
                name=domain_name,
                description=description,
                skill_title=first_skill_title,
                skill_context=first_skill_context,
                skill_content=first_skill_content,
            )
            tool_result = f"Created new skill domain '{domain_name}'\n\n{catalog.to_markdown()}."
        elif name == "create_new_skill":
            domain_name = args["domain"]
            title = args["title"]
            context = args["context"]
            content = args["content"]

            skill = self.skill_catalog_manager.create_new_skill(
                catalog_name=domain_name,
                title=title,
                context=context,
                content=content,
            )
            tool_result = f"Created new skill '{title}' in domain '{domain_name}'.\n\n{skill.to_markdown()}"
        elif name == "update_skill":
            domain_name = args["domain"]
            skill_id = args["skill_id"]
            new_title = args.get("new_title", None)
            new_context = args.get("new_context", None)
            new_content = args.get("new_content", None)

            skill = self.skill_catalog_manager.refactor_skill(
                catalog_name=domain_name,
                skill_id=skill_id,
                new_title=new_title,
                new_context=new_context,
                new_content=new_content,
            )
            tool_result = f"Updated skill '{skill.title}' (ID: {skill.id}) in domain '{domain_name}' and removed notes.\n\n{skill.to_markdown()}"
        elif name == "add_note_to_skill":
            domain_name = args["domain"]
            skill_id = args["skill_id"]
            note = args["note"]

            skill = self.skill_catalog_manager.add_note_to_skill(
                catalog_name=domain_name,
                skill_id=skill_id,
                note=note,
            )
            tool_result = f"Added note to skill '{skill.title}' (ID: {skill.id}) in domain '{domain_name}'"
        elif name == "remove_skill":
            domain_name = args["domain"]
            skill_id = args["skill_id"]

            self.skill_catalog_manager.remove_skill(
                catalog_name=domain_name,
                skill_id=skill_id,
            )
        elif name == "reset_all_changes":
            self.skill_catalog_manager = copy.deepcopy(self.backup_skill_catalog_manager)
            tool_result = f"Reset all changes made during the current learning session.\n\n{self.skill_catalog_manager.list_catalogs_structure()}"
        elif name == "move_skill_to_new_domain":
            source_domain = args["source_domain"]
            skill_id = args["skill_id"]
            target_domain = args["target_domain"]

            skill = self.skill_catalog_manager.get_skill(
                catalog_name=source_domain,
                skill_id=skill_id,
            )
            # Remove from source
            self.skill_catalog_manager.remove_skill(
                catalog_name=source_domain,
                skill_id=skill_id,
            )
            # Add to target
            self.skill_catalog_manager.add_skill(target_domain, skill)
            tool_result = f"Moved skill '{skill.title}' (ID: {skill.id}) from domain '{source_domain}' to domain '{target_domain}'."
        
        else:
            raise ValueError(f"Unknown tool call '{name}'.")

        return {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": tool_result,
        }
    
    def get_tools(self) -> list:
        return [
            {
                "type": "function",
                "name": "read_skill_domain",
                "description": "Read the contents of skill domain by its name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": [catalog.name for catalog in self.skill_catalog_manager.skill_catalogs],
                            "description": "The name of the skill domain to request the information for",
                        },
                    },
                    "required": ["domain"],
                },
                "additionalProperties": False
            },
            {
                "type": "function",
                "name": "create_new_domain",
                "description": "Create a new skill domain with the given name and description, along with the first entry.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "The name of the new skill domain to create. Very broad and high-level. (e.g. 'terminal', 'file-management', 'gimp')",
                        },
                        "description": {
                            "type": "string",
                            "description": "A brief description of the new skill domain. e.g. 'Skills for managing files on the computer.'",
                        },
                        "first_skill_title": {
                            "type": "string",
                            "description": "The title of the first skill section entry.",
                        },
                        "first_skill_context": {
                            "type": "string",
                            "description": "The context description of the first skill section entry on when it applies ('trigger').",
                        },
                        "first_skill_content": {
                            "type": "string",
                            "description": "The content of the first skill section entry, including usage instructions and examples.",
                        },
                    },
                    "required": ["domain", "description", "first_skill_title", "first_skill_context", "first_skill_content"],
                },
                "additionalProperties": False
            },
            {
                "type": "function",
                "name": "create_new_skill",
                "description": "Create a new skill entry in an existing skill domain.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": [catalog.name for catalog in self.skill_catalog_manager.skill_catalogs],
                            "description": "The name of the existing skill domain to add the new skill to.",
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the new skill section entry.",
                        },
                        "context": {
                            "type": "string",
                            "description": "The context description of the new skill section entry on when it applies ('trigger').",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content of the new skill section entry, including usage instructions and examples.",
                        },
                    },
                    "required": ["domain", "title", "context", "content"],
                },
                "additionalProperties": False
            },
            {
                "type": "function",
                "name": "update_skill",
                "description": "Update the content of an existing skill entry in a skill domain.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": [catalog.name for catalog in self.skill_catalog_manager.skill_catalogs],
                            "description": "The name of the existing skill domain containing the skill to update.",
                        },
                        "skill_id": {
                            "type": "string",
                            "enum": [skill.id for catalog in self.skill_catalog_manager.skill_catalogs for skill in catalog.get_skills()],
                            "description": "The ID of the skill section entry to update.",
                        },
                        "new_title": {
                            "type": "string",
                            "description": "The new title for the skill section entry. Leave empty to keep unchanged.",
                        },
                        "new_context": {
                            "type": "string",
                            "description": "The new context description for the skill section entry ('trigger'). Leave empty to keep unchanged.",
                        },
                        "new_content": {
                            "type": "string",
                            "description": "The new content for the skill section entry, including usage instructions and examples. Leave empty to keep unchanged.",
                        },
                    },
                    "required": ["domain", "skill_id"],
                },
                "additionalProperties": False
            },
            {
                "type": "function",
                "name": "add_note_to_skill",
                "description": "Add a note, such as a comment, insight, or specification, to an existing skill entry in a skill domain.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": [catalog.name for catalog in self.skill_catalog_manager.skill_catalogs],
                            "description": "The name of the existing skill domain containing the skill to add a note to.",
                        },
                        "skill_id": {
                            "type": "string",
                            "enum": [skill.id for catalog in self.skill_catalog_manager.skill_catalogs for skill in catalog.get_skills()],
                            "description": "The ID of the skill section entry to add a note to.",
                        },
                        "note": {
                            "type": "string",
                            "description": "The note text to add to the skill section entry.",
                        },
                    },
                    "required": ["domain", "skill_id", "note"],
                },
            },
            {
                "type": "function",
                "name": "reset_all_changes",
                "description": "Reset all changes made during the current learning session, restoring the skill catalog to its previous state in case of critical unrecoverable state.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "type": "function",
                "name": "remove_skill",
                "description": "Remove an existing skill entry from a skill domain.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": [catalog.name for catalog in self.skill_catalog_manager.skill_catalogs],
                            "description": "The name of the existing skill domain containing the skill to remove.",
                        },
                        "skill_id": {
                            "type": "string",
                            "enum": [skill.id for catalog in self.skill_catalog_manager.skill_catalogs for skill in catalog.get_skills()],
                            "description": "The ID of the skill section entry to remove.",
                        },
                    },
                    "required": ["domain", "skill_id"],
                },
            },
            {
                "type": "function",
                "name": "move_skill_to_new_domain",
                "description": "Move an existing skill entry from one skill domain to a new skill domain.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_domain": {
                            "type": "string",
                            "enum": [catalog.name for catalog in self.skill_catalog_manager.skill_catalogs],
                            "description": "The name of the existing skill domain containing the skill to move.",
                        },
                        "skill_id": {
                            "type": "string",
                            "enum": [skill.id for catalog in self.skill_catalog_manager.skill_catalogs for skill in catalog.get_skills()],
                            "description": "The ID of the skill section entry to move.",
                        },
                        "target_domain": {
                            "type": "string",
                            "enum": [catalog.name for catalog in self.skill_catalog_manager.skill_catalogs],
                            "description": "The name of the target skill domain to move the skill to. If it does not exist, it will be created.",
                        },
                    },
                    "required": ["source_domain", "skill_id", "target_domain"],
                },
            }
        ]