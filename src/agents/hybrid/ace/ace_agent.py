import uuid
from pydantic import BaseModel
from agents.hybrid.ace.ace_skills import ACEManager
from agents.hybrid.agent import Custom2Agent
from domain.request import AgentPredictionResponse


class AceAgent(Custom2Agent):
    """uses ACE https://arxiv.org/pdf/2510.04618"""
    def __init__(self, vm_http_server: str, name: str = "ace-agent"):
        super().__init__(name=name, vm_http_server=vm_http_server)

        self.ace_manager = ACEManager()
        
    def predict(self, screenshot: str, task: str) -> AgentPredictionResponse:
        result = super().predict(screenshot=screenshot, task=task)

    def end_task(self):
        ...