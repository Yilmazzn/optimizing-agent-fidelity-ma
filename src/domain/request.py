from typing import Any, Optional

import openai
from pydantic import BaseModel

# ===== AGENT PREDICTION =====

class AgentPredictionRequest(BaseModel):
    screenshot: str # base64-encoded
    task_id: str
    domain: str

class TokenUsage(BaseModel):
    prompt_tokens: int
    cached_prompt_tokens: Optional[int] = 0
    completion_tokens: int

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            cached_prompt_tokens=self.cached_prompt_tokens + other.cached_prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
        )
    
    @classmethod
    def from_response(cls, response) -> "TokenUsage":
        cached_input_tokens = response.usage.input_tokens_details.cached_tokens
        return TokenUsage(
            prompt_tokens=response.usage.input_tokens - cached_input_tokens,
            completion_tokens=response.usage.output_tokens,
            cached_prompt_tokens=cached_input_tokens,
        )

class AgentPredictionResponse(BaseModel):
    response: str
    pyautogui_actions: Optional[str]
    usage: TokenUsage
    status: str = "working" # or "done", "infeasible", "error"

    def __add__(self, other: "AgentPredictionResponse") -> "AgentPredictionResponse":
        return AgentPredictionResponse(
            response=self.response + "\n\n========\n\n" + other.response,
            pyautogui_actions=self.pyautogui_actions + "\n\n# ========\n\n" + other.pyautogui_actions,
            usage=self.usage + other.usage,
            status=other.status,
        )

class AgentPredictionResponseLog(AgentPredictionResponse):
    task_id: str
    task: str
    domain: str
    duration: float # seconds


# ===== INIT
class InitRequest(BaseModel):
    agent: str
    vm_http_server: Optional[str] = None

class SetTaskRequest(BaseModel):
    task: str
