from fastapi import FastAPI, Request, HTTPException, Depends
from loguru import logger

from agents import agent
from agents.agent import Agent
from agents.agent_factory import build_agent
from domain.request import AgentPredictionRequest, AgentPredictionResponse, InitRequest, SetTaskRequest


def get_agent(request: Request) -> Agent:
    agent = getattr(request.app.state, "agent", None)
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized.")
    return agent

def get_task(request: Request) -> str:
    task = getattr(request.app.state, "task", None)
    if task is None:
        raise HTTPException(status_code=400, detail="Task not initialized. Call endpoint 'POST /task'")
    return task

def include_routes(app: FastAPI):
    @app.get("/status", status_code=200)
    def status():
        return {"status": "ok"}

    @app.post("/init", status_code=200)
    def init(init_request: InitRequest):
        agent = build_agent(
            agent_type=init_request.agent,
        )
        app.state.agent = agent
        logger.info(f"Initialized agent: '{agent}'")
        agent.reset()
        return agent.get_config()

    @app.post("/task", status_code=200)
    def set_task(set_task_request: SetTaskRequest):
        logger.info(f"Set task to: '{set_task_request.task}'")
        app.state.task = set_task_request.task

    @app.post("/reset", status_code=200)
    def reset(agent = Depends(get_agent)):
        logger.info(f"Reset agent: '{agent}'")
        agent.reset()

        if hasattr(app.state, "task"):
            delattr(app.state, "task")


    @app.post("/predict", status_code=200)
    def predict(prediction_request: AgentPredictionRequest, agent = Depends(get_agent), task = Depends(get_task)) -> AgentPredictionResponse:
        return agent.predict(screenshot=prediction_request.screenshot, task=task)


