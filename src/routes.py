from datetime import datetime
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Depends
from loguru import logger

from agents.agent import Agent
from agents.agent_factory import build_agent
from domain.request import AgentPredictionRequest, AgentPredictionResponse, AgentPredictionResponseLog, InitRequest, SetTaskRequest
from utils import fix_pyautogui_script, log_agent_response


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
            vm_http_server=init_request.vm_http_server,
        )
        sessions[session_id] = {
            "agent": agent,
            "agent_type": init_request.agent,
            "vm_http_server": init_request.vm_http_server,
            "task": None,
            "predict_count": 0
        }
        logger.info(f"Initialized agent: '{agent.name}' for session: '{session_id}'")
        # return agent.get_config()

    @app.post("/task", status_code=200)
    def set_task(set_task_request: SetTaskRequest, session: dict = Depends(get_session)):
        logger.info(f"Set task to: '{set_task_request.task}'")
        session["task"] = set_task_request.task

    @app.post("/reset", status_code=200)
    def reset(session: dict = Depends(get_session)):
        agent_type = session.get("agent_type")
        vm_http_server = session.get("vm_http_server")
        if agent_type is None:
            raise HTTPException(status_code=500, detail="Agent not initialized.")
        
        # Create a new agent instance instead of calling reset()
        new_agent = build_agent(
            agent_type=agent_type,
            vm_http_server=vm_http_server,
        )
        logger.info(f"Reset agent: '{new_agent.name}' (reinitialized)")
        session["agent"] = new_agent
        session["task"] = None
        session["predict_count"] = 0

    @app.post("/predict", status_code=200)
    def predict(prediction_request: AgentPredictionRequest, agent: Agent = Depends(get_agent), task: str = Depends(get_task), session: dict = Depends(get_session)) -> AgentPredictionResponse:
        session["predict_count"] += 1
        start_time = datetime.now()
        result = agent.predict(screenshot=prediction_request.screenshot, task=task)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result.pyautogui_actions = fix_pyautogui_script(result.pyautogui_actions) 

        agent_response_log = AgentPredictionResponseLog(
            **result.model_dump(),
            duration=duration,
            task_id=prediction_request.task_id,
            task=task,
            domain=prediction_request.domain,
        )
        log_agent_response(agent_name=agent.name, agent_response_log=agent_response_log, start_new=(session["predict_count"] == 1))

        result.time_thinking = duration
        return result

    @app.post("/end_task", status_code=200)
    def end_task(session: dict = Depends(get_session)):
        agent = session.get("agent")
        agent.end_task()