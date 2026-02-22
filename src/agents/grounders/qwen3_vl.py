import json
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.grounders.grounder import Grounder, GroundingError
from utils import convert_to_base64_image_url, expect_env_var

_QWEN3_VL_ACTION_SPACE_SIZE = (1000, 1000)
_SYSTEM_PROMPT = """
You are an AI model specialized in locating UI elements within screenshots. Given a GUI screenshot and a description of a UI element, your task is to accurately identify and return the (x, y) coordinates of the specified UI element within the image

The screen's resolution is 1000x1000

You may think step by step to locate the element.

# Rules
- The response MUST include a pixel coordinate
- Do not output more than one coordinate
- Make sure to locate any buttons, links, icons, etc with the cursor tip in the center of the element. Don't provide coordinates to boxes on their edges unless asked.


# Example
User Query: 'Locate the "Submit" button on the screen.'
Output: 'I see the blue "Submit" button at coordinates (450, 300)'.
"""

class Qwen3VLGrounder(Grounder):
    def __init__(self, model: str = "qwen/qwen3-vl-235b-a22b-instruct"):
        super().__init__(action_space_size=_QWEN3_VL_ACTION_SPACE_SIZE)
        self.model = model
        self.client = openai.OpenAI(
            base_url=expect_env_var("OPENROUTER_BASE_URL"),
            api_key=expect_env_var("OPENROUTER_API_KEY")
        )
        
    @retry(
       reraise=True,
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=3.0, min=1.0, max=60.0),
    )
    def _make_call(self, messages: list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        if response is None:
            raise ValueError("No response from the grounding model.")
        return response
    
    # def _extract_tool_calls(self, text: str) -> list[dict]:
    #     blocks: list[str] = []
    #     open_tag = "<tool_call>"
    #     close_tag = "</tool_call>"

    #     i = 0
    #     while True:
    #         start = text.find(open_tag, i)
    #         if start == -1:
    #             break
    #         end = text.find(close_tag, start + len(open_tag))
    #         if end == -1:
    #             raise ValueError("No </tool_call> found for a <tool_call> block.")
    #         raw = text[start + len(open_tag):end].strip()
    #         if raw:
    #             blocks.append(raw)
    #         i = end + len(close_tag)

    #     tool_calls = []
    #     for block in blocks:
    #         try:
    #             tool_call = json.loads(block)
    #         except json.JSONDecodeError as e:
    #             raise ValueError(f"Failed to parse tool call JSON: {e}")
    #         tool_calls.append(tool_call)
    #     return tool_calls

    def _extract_coords_from_response(self, text: str) -> tuple[int, int]:
        import re
        match = re.search(r'\((\d+),\s*(\d+)\)', text)
        if match:
            x = int(match.group(1))
            y = int(match.group(2))
            return (x, y)
        else:
            raise GroundingError(text)
    
    def _locate_ui_element_coords_raw(self, screenshot: str, ui_element: str) -> tuple[int, int]:
        messages = [
            {
                "role": "system",
                "content": _SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": convert_to_base64_image_url(screenshot)},
                    },
                    {
                        "type": "text",
                        "text": f"Locate the UI element described as: '{ui_element}'"
                    }
                ]
            }
        ]
        response = self._make_call(messages)
        text = response.choices[0].message.content
        usage = (response.usage.prompt_tokens, response.usage.completion_tokens)
        coords = self._extract_coords_from_response(text)
        return coords, usage
    