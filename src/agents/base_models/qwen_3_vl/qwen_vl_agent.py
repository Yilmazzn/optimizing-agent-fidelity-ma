import json
import openai
import base64
import shutil
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.agent import Agent
from agents.base_models.qwen_3_vl.prompts import QWEN_SYSTEM_PROMPT
from agents.base_models.qwen_3_vl.tools import ComputerUse
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

_INFERENCE_MODEL_MAP = {
    "qwen3-vl": "qwen3-vl-32b-thinking",
}

# https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/computer_use.ipynb

class QwenAgent(Agent):

    def __init__(self, model: str, image_size=(1920, 1080), **kwargs) -> None:
        super().__init__(name=model, **kwargs)
        self.model = model

        # qwen 3 vl trained on 1000x1000 coordinate system
        self.computer_use_tool = ComputerUse(
            cfg={
                "display_width_px": 1000,
                "display_height_px": 1000,
            }
        )

        self.image_size = (1000, 1000) # for rescaling coordinates (dont scale image before)
    
    
        self.inference_model = _INFERENCE_MODEL_MAP.get(model, model)
        self.enable_thinking = True
        self.thinking_budget = 4096
        self.system_prompt = QWEN_SYSTEM_PROMPT
        
        _base_url = expect_env_var("ALIBABA_BASE_URL")
        _api_key = expect_env_var("ALIBABA_API_KEY")
        self.client = openai.OpenAI(
            base_url=expect_env_var("ALIBABA_BASE_URL"),
            api_key=expect_env_var("ALIBABA_API_KEY")
        )

    def _get_system_message(self):
        system_message = NousFnCallPrompt().preprocess_fncall_messages(
            messages = [
                Message(role="system", content=[ContentItem(text="QWEN_SYSTEM_PROMPT")]),
            ],
            functions=[self.computer_use_tool.function]
        )
        system_message = system_message[0].model_dump()
        return system_message
    
    #@retry(
    #    reraise=True,
    #    stop=stop_after_attempt(4),
    #    wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    #)
    def _make_call(self, messages: list[dict]):
        result = self.client.chat.completions.create(
            model = self.inference_model,
            messages = messages,   
        )
        return result


    def predict(self, screenshot: str, task: str) -> AgentPredictionResponse:
        self.history.append({
            "screenshot": screenshot,
        })

        resized_height, resized_width = qwen_utils.smart_resize(
            width=1920,
            height=1080,
            factor=32,      # Qwen VL 3 factor
            min_pixels=1000*1000,
            max_pixels=2000*1200,
        )

        # system message
        system_message = NousFnCallPrompt().preprocess_fncall_messages(
            messages=[
                    Message(role="system", content=[ContentItem(text=self.system_prompt)]),
                ],
                functions=[self.computer_use_tool.function],
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
                user_content.append({"type": "text", "text": task})
            else: 
                tool_result = self.history[i-1].get("tool_result", None)
                user_content.append({
                    "type": "text",
                    "text": f"<tool_result>\n{tool_result}\n</tool_result>",
                })

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
        cached_tokens = result.usage.prompt_tokens_details.cached_tokens
        token_usage = TokenUsage(
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            cached_prompt_tokens=cached_tokens if cached_tokens else 0,
        )
        
    
        # handle tool calls in output text
        if "<tool_call>" not in output_text:
            raise ValueError("No <tool_call> found in the model output.")
        if "</tool_call>" not in output_text:
            raise ValueError("No </tool_call> found in the model output.")
        
        try:
            action = json.loads(output_text.split('<tool_call>\n')[1].split('\n</tool_call>')[0])
        except json.JSONDecodeError as e:
            return AgentPredictionResponse(
                pyautogui_actions="FAIL",
                usage=token_usage,
                response=output_text + "\nFailed to parse tool_call JSON.",
                status="fail"
            )
        
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

        try:
            pyautogui_actions = self.computer_use_tool.call(action["arguments"])
        except Exception as e:
            return AgentPredictionResponse(
                pyautogui_actions="FAIL",
                usage=token_usage,
                response=output_text + f"\nFailed to perform tool call: {str(e)}",
                status="fail"
            )

        self.history[-1]["agent_response"] = output_text
        self.history[-1]["tool_result"] = f"Performed {action['arguments']}"


        return AgentPredictionResponse(
            pyautogui_actions=pyautogui_actions,
            usage=token_usage,
            response=output_text
        )
