from agents.agent import Agent
from agents.base_models.claude import BaseAnthropicAgent


def build_agent(agent_type: str) -> Agent:
    if agent_type == "anthropic":
        return BaseAnthropicAgent(model="claude-sonnet-4.5")
    raise ValueError(f"Unknown agent type: {agent_type}")