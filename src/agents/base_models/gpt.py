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

    def predict(self, screenshot: str, task) -> AgentPredictionResponse:
        pass


