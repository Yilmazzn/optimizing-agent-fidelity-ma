import sys
from loguru import logger

from agents.hybrid.skill_agent.models.skill_catalog_manager import SkillCatalogManager

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
    
    # manager = SkillCatalogManager()
    # manager.create_new_catalog(name="default", description="Default skill catalog", skill_title="Initial Skill", trigger="This is the initial skill in the default catalog.", content="Use this skill as an example.")
    # manager.create_new_skill(
    #     catalog_name="default",
    #     title="Test Skill",
    #     trigger="This is a test skill.",
    #     content="Use this skill to test the skill catalog manager.",
    # )
    
    # manager.save()

    # import base64
    # from agents.agent_factory import build_agent

    # agent = build_agent("custom-3", vm_http_server="http://192.168.152.134:5000")

    # img_filepath = r"D:\Projects\OSWorld-MA\results\pyautogui\screenshot\ui-tars-1.5-7b\libreoffice_calc\1d17d234-e39d-4ed7-b46f-4417922a4e7c\step_1_20251220@143713728414.png"
    # with open(img_filepath, "rb") as f:
    #     img_bytes = f.read()
    #     b64_screenshot = base64.b64encode(img_bytes).decode("utf-8")
    
    # with open(r"d:\Projects\OSWorld-MA\results\pyautogui\screenshot\ui-tars-1.5-7b\libreoffice_calc\1d17d234-e39d-4ed7-b46f-4417922a4e7c\step_2_20251220@143720591582.png", "rb") as f:
    #     img_bytes = f.read()
    #     b64_screenshot_2 = base64.b64encode(img_bytes).decode("utf-8")

    # agent.predict(
    #     screenshot=b64_screenshot, 
    #     task="Select A1:B12 using the cell input box top left.",
    # )

    # agent.predict(
    #     screenshot=b64_screenshot_2, 
    #     task="Execute the next action",
    # )

    # agent.predict(
    #     screenshot=b64_screenshot, 
    #     task="Execute the next action",
    # )

    # agent.predict(
    #     screenshot=b64_screenshot_2, 
    #     task="Execute the next action",
    # )

    # agent.end_task()

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

    