import json
from loguru import logger
import openai
import base64
import shutil
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.agent import Agent
from datetime import datetime
import os

from agents.base_models.qwen_3_vl.prompts import QWEN_SYSTEM_PROMPT, QWEN_SYSTEM_PROMPT_V2, QWEN_SKILLS_PROMPT
from agents.base_models.qwen_3_vl.tools import ComputerUse, ExecutePythonCode, ExecuteTerminalCommand, GetDomainSkills, ReadSkills
from agents.base_models.qwen_3_vl import utils as qwen_utils
from domain.request import AgentPredictionResponse, TokenUsage

from qwen_agent.llm.fncall_prompts.nous_fncall_prompt import (
    NousFnCallPrompt,
    Message,
    ContentItem
)

from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print, multimodal_typewriter_print

from utils import VIEWPORT_SIZE, expect_env_var, map_coords_to_screen

class ToolCallExtractionError(Exception):
    pass

# https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/computer_use.ipynb

class QwenAgent(Agent):

    def __init__(
        self,
        http_server: str = None,
        enable_python_tool: bool = False,
        enable_terminal_tool: bool = False,
        **kwargs
    ) -> None:
        super().__init__(name="qwen3-vl", **kwargs)

        self.http_server = http_server

        # qwen 3 vl trained on 1000x1000 coordinate system
        self.computer_use_tool = ComputerUse(
            cfg={
                "display_width_px": 1000,
                "display_height_px": 1000,
            }
        )

        self.image_size = (1000, 1000) # for rescaling coordinates (dont scale image before)

        self.inference_model = "qwen/qwen3-vl-235b-a22b-thinking"
        self.system_prompt = QWEN_SYSTEM_PROMPT

        self.client = openai.OpenAI(
            base_url=expect_env_var("OPENROUTER_BASE_URL"),
            api_key=expect_env_var("OPENROUTER_API_KEY")
        )

        # tool registry: name -> tool instance
        self.tool_registry = {
            "computer_use": self.computer_use_tool,
        }

        if enable_python_tool or enable_terminal_tool:
            if not self.http_server:
                raise ValueError("http_server must be provided when coding tools are enabled.")

        if enable_python_tool:
            self.python_tool = ExecutePythonCode(cfg={"http_server": self.http_server})
            self.tool_registry["execute_python_code"] = self.python_tool
        if enable_terminal_tool:
            self.terminal_tool = ExecuteTerminalCommand(cfg={"http_server": self.http_server})
            self.tool_registry["execute_terminal_command"] = self.terminal_tool

    def _get_tool_functions(self) -> list[dict]:
        return [tool.function for tool in self.tool_registry.values()]

    def _get_system_message(self):
        system_message = NousFnCallPrompt().preprocess_fncall_messages(
            messages = [
                Message(role="system", content=[ContentItem(text="QWEN_SYSTEM_PROMPT")]),
            ],
            functions=self._get_tool_functions()
        )
        system_message = system_message[0].model_dump()
        return system_message
    
    @retry(
       reraise=True,
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=4.0, min=1.0, max=60.0),
    )
    def _make_call(self, messages: list[dict]):
        result = self.client.chat.completions.create(
            model = self.inference_model,
            messages = messages,   
        )
        return result

    def _extract_tool_calls(self, text: str) -> list[dict]:
        blocks: list[str] = []
        open_tag = "<tool_call>"
        close_tag = "</tool_call>"

        i = 0
        while True:
            start = text.find(open_tag, i)
            if start == -1:
                break
            end = text.find(close_tag, start + len(open_tag))
            if end == -1:
                raise ToolCallExtractionError("No </tool_call> found for a <tool_call> block.")
            raw = text[start + len(open_tag):end].strip()
            if raw:
                blocks.append(raw)
            i = end + len(close_tag)

        tool_calls = []
        for block in blocks:
            try:
                tool_call = json.loads(block)
            except json.JSONDecodeError as e:
                raise ToolCallExtractionError(f"Failed to parse tool call JSON: {e}")
            tool_calls.append(tool_call)
        return tool_calls
    
    # to reduce load on RAM hopefully
    def _clean_history_from_images(self):
        amount_images_kept = 0
        for i in reversed(range(len(self.history))):
            if "screenshot" not in self.history[i]:
                continue
            if amount_images_kept < self.max_images_in_history:
                amount_images_kept += 1
                continue
            del self.history[i]["screenshot"]

    def end_task(self, task_id: str):
        pass

    def predict(self, screenshot: str, task: str) -> AgentPredictionResponse:
        self.history.append({
            "screenshot": screenshot,
        })
        self._clean_history_from_images()

        resized_height, resized_width = qwen_utils.smart_resize(
            width=1920,
            height=1080,
            factor=32,
            min_pixels=3136,
            max_pixels=12845056,
        )

        # system message
        system_message = NousFnCallPrompt().preprocess_fncall_messages(
            messages=[
                    Message(role="system", content=[ContentItem(text=self.system_prompt)]),
                ],
                functions=self._get_tool_functions(),
                lang=None,
            )
        system_message = system_message[0].model_dump()
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": msg["text"]} for msg in system_message["content"]
                ],
            },
        ] 


        first_image_index = max(0, len(self.history) - self.max_images_in_history)
        for i in range(len(self.history)):
            user_content = []
            if i >= first_image_index:
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{self.history[i]['screenshot']}"},
                })
            if i == 0:
                user_content.append({"type": "text", "text": f"/think {task}"})

            if user_content:
                messages.append({
                    "role": "user",
                    "content": user_content,
                })

            agent_response = self.history[i].get("agent_response", None)
            if agent_response:
                messages.append({
                    "role": "assistant",
                    "content": [
                        { "type": "text", "text": agent_response}
                    ]
                })
                
        # make API call
        result = self._make_call(messages=messages)
        output_text = result.choices[0].message.content
        model_reasoning = result.choices[0].message.model_extra["reasoning"]
        agent_response = f"<think>\n{model_reasoning}\n</think>\n\n{output_text}"
        
        cached_tokens = 0
        if hasattr(result.usage, "prompt_tokens_details") and hasattr(result.usage.prompt_tokens_details, "cached_tokens"):
            cached_tokens = result.usage.prompt_tokens_details.cached_tokens

        token_usage = TokenUsage(
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            cached_prompt_tokens=cached_tokens if cached_tokens else 0,
        )

        
        
        try:
            actions = self._extract_tool_calls(output_text)
        except ToolCallExtractionError as e:
            logger.error(f"Tool call extraction error: {e}")
            return AgentPredictionResponse(
                pyautogui_actions="FAIL",
                usage=token_usage,
                response=agent_response + "\nFailed to parse tool_call JSON.",
                status="fail"
            )
        
        # scale back coordinates
        for action in actions:
            coordinate = action.get("arguments", {}).get("coordinate")
            if coordinate: 
                coordinate = map_coords_to_screen(
                    coords=tuple(coordinate),
                    scr_size=(1000, 1000),
                    target_size=(resized_width, resized_height)
                )
                coordinate = map_coords_to_screen(
                    coords=tuple(coordinate),
                    scr_size=(resized_width, resized_height),
                    target_size=VIEWPORT_SIZE
                )
                action["arguments"]["coordinate"] = list(coordinate)

        pyautogui_actions = []
        try:
            for action in actions:
                tool_name = action["name"]
                tool = self.tool_registry.get(tool_name)
                if tool is None:
                    raise ValueError(f"Unknown tool: {tool_name}")

                result = tool.call(action["arguments"])

                if tool_name == "computer_use":
                    pyautogui_actions.append(result)

        except Exception as e:
            return AgentPredictionResponse(
                pyautogui_actions="FAIL",
                usage=token_usage,
                response=agent_response + f"\n\nFailed to perform tool call: {str(e)}",
                status="fail"
            )
        pyautogui_actions = "\n\n".join(pyautogui_actions)

        self.history[-1]["agent_response"] = agent_response


        return AgentPredictionResponse(
            pyautogui_actions=pyautogui_actions,
            usage=token_usage,
            response=agent_response
        )


class QwenAgentV2(QwenAgent):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.system_prompt = QWEN_SYSTEM_PROMPT_V2


class SkillQwenAgent(QwenAgent):
    """QwenAgent with skill book integration, mirroring SkillAnthropicAgent."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        from agents.hybrid.skill_agent_2.skill_book import SkillBook
        self.skill_book = SkillBook.load()

        self.system_prompt = QWEN_SKILLS_PROMPT.format(
            dt=datetime.today().strftime('%A, %B %d, %Y'),
            sudo_pw=os.getenv("VM_SUDO_PASSWORD"),
            domains_list=self.skill_book.list_domains(),
        )

        # Register skill tools
        self.tool_registry["get_domain_skills"] = GetDomainSkills(
            cfg={"skill_book": self.skill_book}
        )
        self.tool_registry["read_skills"] = ReadSkills(
            cfg={"skill_book": self.skill_book}
        )