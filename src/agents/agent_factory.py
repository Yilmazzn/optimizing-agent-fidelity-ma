from agents.agent import Agent
from agents.base_models.anthropic.claude_agent import BaseAnthropicAgent


def build_agent(agent_type: str, vm_http_server: str = None) -> Agent:
    if agent_type == "anthropic-claude-sonnet-4.5":
        return BaseAnthropicAgent(model="claude-sonnet-4.5")
    elif agent_type == "qwen3-vl-32b-thinking":
        from agents.base_models.qwen_3_vl.qwen_vl_agent import QwenAgent
        return QwenAgent()
    elif agent_type == "qwen3-vl-32b-thinking-v2":
        from agents.base_models.qwen_3_vl.qwen_vl_agent import QwenAgentV2
        return QwenAgentV2()
    elif agent_type == "custom-1":
        from agents.hybrid.agent import Custom1Agent
        return Custom1Agent()
    elif agent_type == "custom-2":
        from agents.hybrid.agent import Custom2Agent
        if vm_http_server is None:
            raise ValueError("vm_http_server must be provided for custom-2 agent.")
        return Custom2Agent(vm_http_server=vm_http_server)
    elif agent_type == "skill-agent":
        from agents.hybrid.skill_agent.skill_agent import SkillAgent
        if vm_http_server is None:
            raise ValueError("vm_http_server must be provided for skill-agent.")
        return SkillAgent(vm_http_server=vm_http_server)
    elif agent_type == "custom-3":
        from agents.hybrid.agent import Custom3Agent
        if vm_http_server is None:
            raise ValueError("vm_http_server must be provided for custom-3 agent.")
        return Custom3Agent(vm_http_server=vm_http_server)
    elif agent_type == "async-agent":
        from agents.hybrid.async_agent import AsyncCustomAgent
        if vm_http_server is None:
            raise ValueError("vm_http_server must be provided for async-agent.")
        return AsyncCustomAgent(vm_http_server=vm_http_server)
    raise ValueError(f"Unknown agent type: {agent_type}")