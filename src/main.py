from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agents import agent_factory
from routes import include_routes

from dotenv import load_dotenv
load_dotenv()

AGENT_CONFIG = {
    "agent_type": "anthropic",
    "model": "claude-sonnet-4.5"
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    agent = agent_factory.build_agent(*AGENT_CONFIG)
    app.state.agent = agent
    yield

include_routes(app)


if __name__ == "__main__":
    DISABLE_RELOAD = os.getenv("DISABLE_RELOAD", "false").lower() == "true"
    PORT = int(os.getenv("PORT", "9876"))
    
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=not DISABLE_RELOAD)


    # import base64
    # from agents.agent_factory import build_agent

    # agent = build_agent("qwen3-vl-32b-thinking")
    # img_filepath = r"C:\Users\yilma\Desktop\Projects\OSWorld-MA\results\pyautogui\screenshot\anthropic-claude-sonnet-4.5\chrome\da46d875-6b82-4681-9284-653b0c7ae241\step_1_20260104@210922089788.png"
    # with open(img_filepath, "rb") as f:
    #     img_bytes = f.read()
    #     b64_screenshot = base64.b64encode(img_bytes).decode("utf-8")

    # # coordinates = (1893, 88)
    # # # coordinates = (999, 89)
    # # resized_coords = agent.map_cords_to_orig_cords(coordinates)
    # # print("Original coordinates:", coordinates)
    # # print("Resized coordinates:", resized_coords)
    # # coordinates = resized_coords

    # # draw a red dot at the coordinates
    # # from PIL import Image, ImageDraw

    # # img = Image.open(img_filepath)
    # # draw = ImageDraw.Draw(img)
    # # r = 5
    # # x, y = coordinates
    # # draw.ellipse((x - r, y - r, x + r, y + r), fill="red", outline="red")
    # # img.show()

    # response = agent.predict(
    #     screenshot=b64_screenshot,
    #     task="Move the mouse on the top right and click on the three dots to open the menu.",
    # )

    