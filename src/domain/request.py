from typing import Any, Optional

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

class AgentPredictionResponse(BaseModel):
    response: Any
    pyautogui_actions: Optional[str]
    usage: TokenUsage
    status: str = "working" # or "done", "infeasible", "error"

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
