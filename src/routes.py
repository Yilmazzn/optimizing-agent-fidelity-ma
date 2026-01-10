import sys
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Depends
from loguru import logger

# Configure loguru to include timestamps
logger.remove()
logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

from agents.agent import Agent
from agents.agent_factory import build_agent
from domain.request import AgentPredictionRequest, AgentPredictionResponse, InitRequest, SetTaskRequest
from utils import fix_pyautogui_script


# Session storage for agents and tasks
sessions: dict[str, dict] = {}

# Reusable session_id dependency
SessionId = Annotated[str, Query(..., description="Unique session identifier")]


def get_session(session_id: SessionId) -> dict:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found. Call 'POST /init?session_id={session_id}' first.")
    return sessions[session_id]


def get_agent(session: dict = Depends(get_session)) -> Agent:
    agent = session.get("agent")
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized.")
    return agent


def get_task(session: dict = Depends(get_session)) -> str:
    task = session.get("task")
    if task is None:
        raise HTTPException(status_code=400, detail="Task not initialized. Call endpoint 'POST /task'")
    return task


def include_routes(app: FastAPI):
    @app.get("/status", status_code=200)
    def status():
        return {"status": "ok"}

    @app.post("/init", status_code=200)
    def init(init_request: InitRequest, session_id: SessionId):
        agent = build_agent(
            agent_type=init_request.agent,
        )
        sessions[session_id] = {"agent": agent, "task": None}
        logger.info(f"Initialized agent: '{agent}' for session: '{session_id}'")
        agent.reset()
        return agent.get_config()

    @app.post("/task", status_code=200)
    def set_task(set_task_request: SetTaskRequest, session: dict = Depends(get_session)):
        logger.info(f"Set task to: '{set_task_request.task}'")
        session["task"] = set_task_request.task

    @app.post("/reset", status_code=200)
    def reset(session: dict = Depends(get_session)):
        agent = session.get("agent")
        if agent is None:
            raise HTTPException(status_code=500, detail="Agent not initialized.")
        logger.info(f"Reset agent: '{agent}'")
        agent.reset()
        session["task"] = None

    @app.post("/predict", status_code=200)
    def predict(prediction_request: AgentPredictionRequest, agent: Agent = Depends(get_agent), task: str = Depends(get_task)) -> AgentPredictionResponse:
        result = agent.predict(screenshot=prediction_request.screenshot, task=task)
        result.pyautogui_actions = fix_pyautogui_script(result.pyautogui_actions) 
        return result

