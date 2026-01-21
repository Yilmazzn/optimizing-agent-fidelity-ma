import json
from typing import Tuple

from loguru import logger
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
from agents.agent import Agent
from agents.hybrid.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT_V2
from agents.hybrid.tools import CuaToolSet
from agents.grounders.qwen3_vl import Qwen3VLGrounder
from domain.request import AgentPredictionResponse, TokenUsage
from utils import expect_env_var, fix_pyautogui_script


class Custom1Agent(Agent):
    """
    This uses a custom agent based on planning separately and GUI grounding for coordinate-based tasks
    
    Follows https://arxiv.org/pdf/2505.13227
    """

    def __init__(self, name: str = "custom-1"):
        super().__init__(name=name)

        self.grounding_model = "Qwen/Qwen3-VL-32B-Instruct"
        self.planner_client = openai.OpenAI(
            base_url=expect_env_var("AZURE_OPENAI_BASE_URL"),
            api_key=expect_env_var("AZURE_OPENAI_API_KEY"),
        )
        self.tool_set = CuaToolSet(
            grounder=Qwen3VLGrounder(model=self.grounding_model),
        )
        self.system_prompt = PLANNER_SYSTEM_PROMPT

    @retry(
       reraise=True,
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    )
    def _generate_plan(self, task: str) -> Tuple[str, list]: 
        instructions=None
        user_query = "Execute the next action."
        previous_response_id = None
        tool_results = []

        # include system prompt only on first step
        if len(self.history) <= 1:
            instructions = self.system_prompt
            user_query = f"Complete the following task: '{task}'\n\n"
        else:
            previous_response_id =self.history[-2].get("response_id", None)
            tool_results = self.history[-2].get("tool_results", None)

        screenshot = self.history[-1]["screenshot"]

        _input = []

        if tool_results:
            _input += tool_results

        _input.append({
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{screenshot}"
                },
                {"type": "input_text", "text": user_query},
            ]
        })

        response = self.planner_client.responses.create(
            model="gpt-5.2",
            instructions=instructions,
            tools=self.tool_set.tools,
            reasoning={
                "effort": "high",
                "summary": "auto",
            },
            input=_input,
            previous_response_id=previous_response_id,
            tool_choice="required",
        )

        self.history[-1]["response_id"] = response.id

        return response


    def predict(self, screenshot: str, task) -> AgentPredictionResponse:
        token_usage = TokenUsage(
            prompt_tokens=0,
            completion_tokens=0,
        )
        self.history.append({
            "screenshot": screenshot,
        })

        response = self._generate_plan(task)

        # calculate token usage
        cached_input_tokens = response.usage.input_tokens_details.cached_tokens
        token_usage.prompt_tokens += response.usage.input_tokens - cached_input_tokens
        token_usage.completion_tokens += response.usage.output_tokens
        token_usage.cached_prompt_tokens += cached_input_tokens

        # reasoning summary
        reasoning_summaries = [] 
        for output in response.output:
            if output.type == "summary_text" or output.type == "reasoning":
                for summary in output.summary:
                    summary_text = summary.text.strip() if summary.text else None
                    if summary_text:
                        reasoning_summaries.append(summary_text)
        reasoning_summary = "\n\n".join(reasoning_summaries)
        logger.info(f"Reasoning Summary: {reasoning_summary}")

        tool_calls = list(filter(lambda o: o.type == "function_call", response.output))

        self.history[-1]["reasoning_summary"] = reasoning_summary
        self.history[-1]["agent_output"] = response.output
        self.history[-1]["tool_calls"] = tool_calls

        executed_actions = []
        pyautogui_scripts = []
        tool_results = []
        for tool_call in tool_calls:
            executed_action, pyautogui_script, _token_usage = self.tool_set.parse_action(tool_call, screenshot)
            
            token_usage.prompt_tokens += _token_usage[0]
            token_usage.completion_tokens += _token_usage[1]

            executed_actions.append(executed_action)
            pyautogui_scripts.append(pyautogui_script)

            tool_results.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": executed_action,
            })

        self.history[-1]["tool_results"] = tool_results

        pyautogui_script = "\n\n".join(pyautogui_scripts)
        pyautogui_script = fix_pyautogui_script(pyautogui_script)

        agent_response = reasoning_summary
        if response.output_text:
            agent_response += "\n\n#Output\n" + response.output_text

        agent_response += "\n\n# Tool Calls\n\n"
        for i, tc in enumerate(tool_calls):
            executed_action = executed_actions[i]
            tc_name, tc_args = tc.name, tc.arguments
            agent_response += f"Called tool: {tc_name} with arguments: {json.dumps(tc_args)}\n"
            agent_response += f"Result: {executed_action}\n\n"

        return AgentPredictionResponse(
            pyautogui_actions=pyautogui_script,
            response=agent_response,
            usage=token_usage,
        )
    
class Custom2Agent(Custom1Agent):
    """ same custom-1, however has coding tools (python/terminal)"""
    def __init__(self, vm_http_server: str, name: str = "custom-2"):
        super().__init__(name=name)
        self.system_prompt = PLANNER_SYSTEM_PROMPT_V2
        self.grounder = Qwen3VLGrounder(model="qwen/qwen3-vl-32b-instruct")
        self.tool_set = CuaToolSet(grounder=self.grounder, enable_python_execution_tool=True, enable_terminal_command_tool=True, http_server=vm_http_server)
    