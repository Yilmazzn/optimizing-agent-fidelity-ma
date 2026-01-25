import json

from agents.grounders.qwen3_vl import Qwen3VLGrounder
from agents.hybrid.skill_agent.models.skill_catalog_manager import SkillCatalogManager
from agents.hybrid.tools import CuaToolSet

class SkillsToolSet(CuaToolSet):
    def __init__(self, vm_http_server: str, skill_catalog_manager: SkillCatalogManager):
        super().__init__(
            grounder=Qwen3VLGrounder(),
            http_server=vm_http_server,
            enable_python_execution_tool=True,
            enable_terminal_command_tool=True,
        )
        self.skill_catalog_manager = skill_catalog_manager
        self.tools.extend(self.get_tools())
        self.used_skill_domains = set()

    def get_used_skill_domains(self) -> list[str]:
        return list(self.used_skill_domains)

    def parse_action(self, tool_call, screenshot: str) -> tuple[str, str, tuple[int, int], bool]:
        name = tool_call.name
        args = json.loads(tool_call.arguments)

        if name == "read_skill_domain":
            domain_name = args.get("domain")
            catalog = self.skill_catalog_manager._ensure_catalog_exists(domain_name)
            tool_result = catalog.to_markdown()
            self.used_skill_domains.add(domain_name)
        else:
            return super().parse_action(tool_call, screenshot)
        
        return tool_result, "", (0, 0), True

    def get_tools(self) -> list[dict]:
        return [{
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
        }]