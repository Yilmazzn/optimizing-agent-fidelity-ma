from agents.agent import Agent
from agents.base_models.anthropic.claude_agent import BaseAnthropicAgent


def build_agent(agent_type: str) -> Agent:
    if agent_type == "anthropic-claude-sonnet-4.5":
        return BaseAnthropicAgent(model="claude-sonnet-4.5")
    elif agent_type == "qwen3-vl-32b-thinking":
        from agents.base_models.qwen_3_vl.qwen_vl_agent import QwenAgent
        return QwenAgent()
    elif agent_type == "qwen3-vl-32b-thinking-v2":
        from agents.base_models.qwen_3_vl.qwen_vl_agent import QwenAgentV2
        return QwenAgentV2()
    raise ValueError(f"Unknown agent type: {agent_type}")