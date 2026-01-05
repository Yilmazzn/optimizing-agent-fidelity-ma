import json
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.agent import Agent
from agents.base_models.qwen_3_vl.prompts import QWEN_SYSTEM_PROMPT
from agents.base_models.qwen_3_vl.tools import ComputerUse
from domain.request import AgentPredictionResponse

from transformers.models.qwen2_vl.image_processing_qwen2_vl_fast import smart_resize

from qwen_agent.llm.fncall_prompts.nous_fncall_prompt import (
    NousFnCallPrompt,
    Message,
    ContentItem
)

from utils import expect_env_var

_INFERENCE_MODEL_MAP = {
    "qwen3-vl": "qwen/qwen3-vl-235b-a22b-thinking",
}

# https://github.com/QwenLM/Qwen3-VL/blob/main/cookbooks/computer_use.ipynb

class QwenAgent(Agent):

    def __init__(self, model: str, image_size=(1000, 1000), **kwargs) -> None:
        super().__init__(name=model, **kwargs)
        self.model = model
        self.image_size = image_size
        self.computer_use_tool = ComputerUse(
            cfg={
                "display_width_px": self.image_size[0],
                "display_height_px": self.image_size[1],
            }
        )
        
        openrouter_api_key = expect_env_var("OPENROUTER_API_KEY")
        openrouter_base_url = expect_env_var("OPENROUTER_BASE_URL")
        self.client = openai.OpenAI(
            base_url=openrouter_base_url,
            api_key=openrouter_api_key,
        )

        self.inference_model = _INFERENCE_MODEL_MAP.get(model, model)

    def _get_system_message(self):
        system_message = NousFnCallPrompt().preprocess_fncall_messages(
            messages = [
                Message(role="system", content=[ContentItem(text=QWEN_SYSTEM_PROMPT)]),
            ],
            functions=[self.computer_use_tool.function]
        )
        system_message = system_message[0].model_dump()
        return system_message
    
    @retry(
        reraise=True,
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    )
    def _make_call(self, messages: list[dict]):
        return self.client.chat.completions.create(
            model=self.inference_model,
            messages=messages,
        )


    def predict(self, screenshot: str, task: str) -> AgentPredictionResponse:
        resized_image = self.resize_screenshot(screenshot)

        self.history.append({
            "screenshot": resized_image,
        })

        resized_height, resized_width = smart_resize(
            width=self.image_size[0],
            height=self.image_size[1],
            factor=32,      # Qwen VL 3 factor
            min_pixels=3136,
            max_pixels=12845056,
        )

        system_message = self._get_system_message()
        
        messages = [
            {
                "role": "system",
                "content": [
                    { "type": "text", "text": msg["text"]} for msg in system_message["content"]
                ]
            },
        ]


        first_image_index = max(0, len(self.history) - self.max_images_in_history)
        for i in range(len(self.history)):
            user_content = []
            if i >= first_image_index:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{self.history[i]['screenshot']}",
                    }
                })
            if i == 0:
                user_content.append({
                    "type": "text",
                    "text": task,
                })
            
            messages.append({
                "role": "user",
                "content": user_content,
            })

            agent_content = self.history[i].get("agent_response", None)
            if agent_content:
                messages.append({
                        "role": "assistant",
                        "content": [
                            { "type": "text", "text": agent_content}
                        ]
                    })
                
        # make API call
        result = self._make_call(messages=messages)
        output_text = result.choices[0].message.content
    
        # handle tool calls in output text
        action = json.loads(output_text.split('<tool_call>\n')[1].split('\n</tool_call>')[0])
        coordinate_raw = action.get("arguments", {}).get("coordinate")
        coordinate_absolute = [coordinate_raw[0] / self.image_size[0] * resized_width, coordinate_raw[1] / self.image_size[1] * resized_height]

