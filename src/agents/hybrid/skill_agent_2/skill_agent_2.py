from agents.hybrid.agent import Custom2Agent


class SkillAgent2(Custom2Agent):
    """Hybrid with coding tools + skill management"""
    def __init__(self, vm_http_server: str, name: str = "skill-agent"):
        super().__init__(name=name, vm_http_server=vm_http_server)