from datetime import datetime

from agents.agent import Agent
from domain.request import AgentPredictionResponse

from anthropic import AnthropicBedrock

from utils import expect_env_var
from dotenv import load_dotenv
load_dotenv()

# https://github.com/anthropics/claude-quickstarts/blob/main/computer-use-demo/computer_use_demo/loop.py#L265

_ANTHROPIC_MODEL_MAP = {
    "claude-sonnet-4.5": "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
}

_SYSTEM_PROMPT = """
<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open chrome or any application, please just click on the icon.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {dt}.
</SYSTEM_CAPABILITY>
""".strip().format(dt=datetime.today().strftime("%A, %B %-d, %Y"))


class BaseAnthropicAgent(Agent):

    def __init__(self, model: str, max_images_in_history: int = 3, **kwargs):
        self.model = model
        self.max_images_in_history = max_images_in_history

        super().__init__(name=f"base-anthropic-{model}", *kwargs)

        expect_env_var("AWS_ACCESS_KEY_ID")
        expect_env_var("AWS_SECRET_ACCESS_KEY")
        self.client = AnthropicBedrock(aws_region="eu-central-1")

        self.inference_model = _ANTHROPIC_MODEL_MAP.get(self.model)
        self.history = []

        if self.inference_model is None:
            raise ValueError(f"'{self.model}' is not a valid model")

    # https://platform.claude.com/docs/en/build-with-claude/prompt-caching
    # So in total up to 4 cache breakpoints are supported. Should be used on the most recent. 1 is reserved for the system prompt
    def _inject_prompt_caching(self, messages: list):
        remaining_breakpoints = 3
        for message in reversed(messages):
            if message["role"] != "user":
                continue
            if remaining_breakpoints == 0:
                if "cache_control" in message:
                    del message["cache_control"]
                continue
            message["content"][-1]["cache_control"] = {"type": "ephemeral"}
            remaining_breakpoints -= 1

    def _make_call(self, messages: list, max_tokens=1024):
        return self.client.beta.messages.create(
            max_tokens=max_tokens,
            model=self.inference_model,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                },
            ],
            tools=[
                {"type": "computer_20250124", "name": "computer", "display_width_px": 1024,
                 "display_height_px": 768},
                {"type": "bash_20250124", "name": "bash"}
            ],
            messages=messages,
            betas=["computer-use-2025-01-24"],
        )

    def _build_messages(self) -> list:
        messages = []
        first_image_idx = max(0, len(self.history) - self.max_images_in_history)

        for i, ele in enumerate(self.history):
            ## USER
            content = []
            if i >= first_image_idx:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": ele["screenshot"],
                    },
                })
            content.append({
                "type": "text",
                "text": ele["user_query"]
            })
            messages.append({
                "role": "user",
                "content": content,
            })

            ## ASSISTANT


        return messages

    def run_tool(self, action: dict) -> str:

        return "Tool Result"

    def predict(self, screenshot: str, task: str) -> AgentPredictionResponse:
        user_query = None
        if len(self.history) == 0:
            user_query = task
        else:
            ...

        screenshot = self.resize_screenshot(screenshot)
        self.history.append({
            "screenshot": screenshot,
            "user_query": user_query,
        })

        messages = self._build_messages()
        self._inject_prompt_caching(messages)

        response = self._make_call(messages)
        self.history[-1]["response"] = response.content

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                tool_result = self.run_tool(block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": tool_result,
                })
        self.history[-1]["tool_results"] = tool_results

        return AgentPredictionResponse()




if __name__ == "__main__":
    agent = BaseAnthropicAgent(model="claude-sonnet-4.5")

    import base64

    with open("/Users/YILUZUN/Projects/optimizing-agent-fidelity-ma/data/test-image.png", "rb") as f:
        _image_bytes = f.read()

        # encode base 64
        _image_base64 = base64.b64encode(_image_bytes).decode("utf-8")

    agent.predict(screenshot=_image_base64, task="Click on the 'Log In' Button")
