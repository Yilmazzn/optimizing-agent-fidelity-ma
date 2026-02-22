import json

from loguru import logger
from agents.hybrid.skill_agent_2.skill_book import SkillBook, SkillFetchError, SkillMergeError, SkillError


class SkillManagerTools:
    def __init__(self, skill_book: SkillBook):
        self.skill_book = skill_book

    def get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "name": "fetch_similar_skills",
                "description": "Find skills in the given domain that relate to the situation. Returns full content of top matches. Use this to check for duplicates or find skills to extend.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": self.skill_book.get_domain_ids(),
                            "description": "The domain to search within (e.g., 'gimp', 'chrome', 'os')."
                        },
                        "skill_description": {
                            "type": "string",
                            "description": "Description of when the guidance applies. Used for similarity matching."
                        }
                    },
                    "required": ["domain", "skill_description"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "read_skills",
                "description": "Read the full content of the specific skills. Use this to see current content before updating.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_ids": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": self.skill_book.get_all_skill_ids()
                            },
                            "description": "The list of skill IDs to read (e.g. ['libreoffice-calc/select-cells', 'gimp/transparency'])."
                        },
                    },
                    "required": ["skill_ids"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "create_domain",
                "description": "Create a new domain in the skillbook. Use when a learning references an application that doesn't have a domain yet.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "The name for the new domain. Must be lowercase with hyphens, specific to an application (e.g., 'libreoffice-calc', 'visual-studio-code', 'firefox')."
                        }
                    },
                    "required": ["domain"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "create_skill",
                "description": "Create a new skill. Use when no existing skill covers this knowledge.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "enum": self.skill_book.get_domain_ids(),
                            "description": "The domain for the new skill (e.g., 'gimp', 'chrome', 'os')."
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "The name for the new skill (e.g., 'transparency', 'cell-selection'). Use lowercase with hyphens."
                        },
                        "description": {
                            "type": "string",
                            "description": "A brief description of the skill's purpose. Used for triggering skill retrieval."
                        },
                        "body": {
                            "type": "string", 
                            "description": "The complete skill content in markdown format. Contains all instructions, cases, and guidance."
                        }
                    },
                    "required": ["domain", "skill_name", "description", "body"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "update_skill",
                "description": "Replace a skill's content. Use when extending or fixing an existing skill.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "enum": self.skill_book.get_all_skill_ids(),
                            "description": "The skill ID to update (e.g., 'gimp/transparency', 'chrome/tabs')."
                        },
                        "description": {
                            "type": "string",
                            "description": "A brief one-line description of the skill's purpose. Only provide if the description needs to be changed."
                        },
                        "body": {
                            "type": "string",
                            "description": "The complete skill content in markdown. Omit to keep existing."
                        },
                        "dismiss_annotations": {
                            "type": "boolean",
                            "description": "If true, clears all annotations from the skill if does not apply to new content anymore. Defaults to True."
                        }
                    },
                    "required": ["skill_id"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "annotate_skill",
                "description": "Add a note to a skill for future review. Use when uncertain or for minor observations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "enum": self.skill_book.get_all_skill_ids(),
                            "description": "The skill ID to annotate (e.g., 'gimp/transparency', 'chrome/tabs')."
                        },
                        "annotation": {
                            "type": "string",
                            "description": "The note to add to the skill's Annotations section."
                        },
                    },
                    "required": ["skill_id", "annotation"],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "delete_skill",
                "description": "Remove a skill entirely. Use sparingly—only when a skill is harmful or obsolete.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "enum": self.skill_book.get_all_skill_ids(),
                            "description": "The skill ID to delete (e.g., 'gimp/transparency', 'chrome/tabs')."
                        }
                    },
                    "required": ["skill_id"],
                    "additionalProperties": False
                }
            },
            {
            "type": "function",
            "name": "merge_skills",
            "description": "Merge two skills in the same domain into one. The target skill is updated with given fields; the source skill is deleted. Use when two skills cover overlapping knowledge that belongs together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_skill_id": {
                        "type": "string",
                        "enum": self.skill_book.get_all_skill_ids(),
                        "description": "The skill to merge FROM (will be deleted)."
                    },
                    "target_skill_id": {
                        "type": "string",
                        "enum": self.skill_book.get_all_skill_ids(),
                        "description": "The skill to merge INTO (will be updated)."
                    },
                    "description": {
                        "type": "string",
                        "description": "One-line summary for the merged skill."
                    },
                    "body": {
                        "type": "string",
                        "description": "Combined skill content in markdown (should cover both original skills)."
                    },
                    "dismiss_annotations": {
                        "type": "boolean",
                        "description": "If true, clears all annotations from the target skill. Defaults to True. But keep if at least one annotation might still apply"
                    }
                },
                "required": ["source_skill_id", "target_skill_id", "description", "body"],
                "additionalProperties": False
            }
        }
        ]
    
    def parse_action(self, tool_call) -> dict:
        logger.info(f"Parsing tool call: {tool_call.name} with args: \n{json.dumps(json.loads(tool_call.arguments), indent=2)}")
        try:
            return self._parse_action(tool_call)
        except SkillError as e:
            return {
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(e)
            }
    
    def _parse_action(self, tool_call) -> dict:
        name = tool_call.name
        args = json.loads(tool_call.arguments)
        tool_result = ""

        if name == "fetch_similar_skills":
            domain = args["domain"]
            skill_description = args["skill_description"]
            tool_result = self.skill_book.find_similar_skills(
                description=skill_description,
                domain=domain,
                threshold=0.4,
                max_skills=3
            )
        
        elif name == "read_skills":
            skill_ids = args["skill_ids"]
            if len(skill_ids) > 4:
                raise SkillFetchError(f"Too many skills requested: {len(skill_ids)}. Maximum at a time is 4.")
            skills_content = []
            for skill_id in skill_ids:
                skill = self.skill_book.get_skill(skill_id)
                skills_content.append(skill.to_evaluation_markdown())
            tool_result = "\n\n---\n\n".join(skills_content)
        
        elif name == "create_domain":
            domain_id = args["domain"]
            self.skill_book.add_domain(domain_id)
            self.skill_book.save()
            tool_result = f"Domain '{domain_id}' created successfully."
        
        elif name == "create_skill":
            domain = args["domain"]
            skill_name = args["skill_name"]

            skill = self.skill_book.add_skill(
                domain_id=domain,
                name=skill_name,
                description=args["description"],
                body=args["body"]
            )
            tool_result = f"Skill `{domain}/{skill_name}` created successfully.\n\n{skill.to_markdown()}"
        
        elif name == "update_skill":
            skill_id = args["skill_id"]
            skill, changes = self.skill_book.update_skill(
                skill_id=skill_id,
                description=args.get("description"),
                body=args.get("body"),
                dismiss_annotations=args.get("dismiss_annotations", True)
            )
            self.skill_book.save()
            changes_str = "; ".join(changes) if changes else "No changes made"
            tool_result = f"Skill '{skill_id}' updated. {changes_str}.\n\n{skill.to_markdown()}"
        
        elif name == "annotate_skill":
            skill_id = args["skill_id"]
            skill = self.skill_book.get_skill(skill_id)
            skill.annotate(args["annotation"])
            tool_result = f"Annotation added to skill '{skill_id}'."
        
        elif name == "delete_skill":
            skill_id = args["skill_id"]
            self.skill_book.remove_skill(skill_id)
            tool_result = f"Skill '{skill_id}' deleted successfully."

        elif name == "merge_skills":
            source_skill_id = args["source_skill_id"]
            target_skill_id = args["target_skill_id"]
            source_domain = source_skill_id.split("/")[0]
            target_domain = target_skill_id.split("/")[0]

            if source_skill_id == target_skill_id:
                raise SkillMergeError("Source and target skill IDs cannot be the same.")

            if source_domain != target_domain:
                raise SkillMergeError("Cannot merge skills from different domains.")
            
            target_skill, _ = self.skill_book.update_skill(
                skill_id=target_skill_id,
                description=args["description"],
                body=args["body"],
                dismiss_annotations=args.get("dismiss_annotations", True)
            )
            self.skill_book.remove_skill(source_skill_id)
            self.skill_book.save()
            tool_result = f"Skills '{source_skill_id}' merged into '{target_skill_id}'.\n\n{target_skill.to_markdown()}"
            
        else:
            raise ValueError(f"Unknown tool name: {name}")

        return {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": tool_result
        }