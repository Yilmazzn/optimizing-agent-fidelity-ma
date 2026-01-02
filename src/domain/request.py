from typing import Optional

from pydantic import BaseModel

# ===== AGENT PREDICTION =====

class AgentPredictionRequest(BaseModel):
    screenshot: str # base64-encoded

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int


class AgentPredictionResponse(BaseModel):
    response: str
    pyautogui_actions: Optional[str]
    usage: TokenUsage

# ===== INIT

class InitRequest(BaseModel):
    task: str
    agent: str
