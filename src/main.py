import sys
from loguru import logger

# Configure loguru to include timestamps (must be done before other imports)
logger.remove()
logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agents import agent_factory
from routes import include_routes

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

include_routes(app)


if __name__ == "__main__":
    DISABLE_RELOAD = os.getenv("DISABLE_RELOAD", "false").lower() == "true"
    PORT = int(os.getenv("PORT", "9876"))
    
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=not DISABLE_RELOAD)

    # import base64
    # from agents.agent_factory import build_agent

    # agent = build_agent("custom-2", vm_http_server="http://192.168.152.134:5000")

    # img_filepath = r"D:\Projects\OSWorld-MA\results\pyautogui\screenshot\ui-tars-1.5-7b\libreoffice_calc\1d17d234-e39d-4ed7-b46f-4417922a4e7c\step_1_20251220@143713728414.png"
    # with open(img_filepath, "rb") as f:
    #     img_bytes = f.read()
    #     b64_screenshot = base64.b64encode(img_bytes).decode("utf-8")

    # agent.predict(
    #     screenshot=b64_screenshot, 
    #     # task="I want you to write 'Hello World' in B12",
    #     # task="Create a new Sheet and place the heads 'Name', 'Age', 'City' in cells A1, B1, C1 respectively."
    #     task="Run a simple ls -a on the desktop",
    # )

    # agent.predict(
    #     screenshot=b64_screenshot,
    #     task="Move the mouse to the 'New Sheet' button and click it.",
    # )

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

    