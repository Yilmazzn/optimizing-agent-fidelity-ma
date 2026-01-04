import openai

from agents.agent import Agent
from domain.request import AgentPredictionResponse

class BaseGPTAgent(Agent):

    def __init__(self, model: str, base_url: str, api_key: str, **kwargs) -> None:
        super().__init__(name=f"base-{model}", *kwargs)

        self.model = model

        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
    def _parse_tool_call(self, tool_call: str) -> tuple[str, str]:
        action = ""
        tool_result = ""

        return action, tool_result
    
    def _build_messages(self) -> list[dict]:
        messages = []
        return messages
    
    def _make_api_call(self, messages: list[dict]) -> dict:
        ...

    def predict(self, screenshot: str, task) -> AgentPredictionResponse:
        self.history.append({"screenshot": screenshot})
        self.history[-1]["user_query"] = task
        


