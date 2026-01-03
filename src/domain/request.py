from typing import Any, Optional

from pydantic import BaseModel

# ===== AGENT PREDICTION =====

class AgentPredictionRequest(BaseModel):
    screenshot: str # base64-encoded

class TokenUsage(BaseModel):
    prompt_tokens: int
    cached_prompt_tokens: Optional[int]
    completion_tokens: int


class AgentPredictionResponse(BaseModel):
    response: Any
    pyautogui_actions: Optional[str]
    usage: TokenUsage

# ===== INIT

class InitRequest(BaseModel):
    task: str
    agent: str
