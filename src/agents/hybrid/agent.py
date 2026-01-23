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
from utils import expect_env_var, fix_pyautogui_script, get_tool_calls_from_response


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

        # managing responses api state
        self.last_tool_results = None
        self.previous_response_id = None

    @retry(
       reraise=True,
       stop=stop_after_attempt(4),
       wait=wait_exponential(multiplier=1.0, min=1.0, max=8.0),
    )
    def _generate_plan(self, task: str = None, screenshot: str = None) -> Tuple[str, list]: 
        # only pass task for very first request
        user_query = f"Complete the following task: '{task}'\n\n" if task else "Execute the next action."
        instructions = self.system_prompt if task else None
        
        _input = []

        if task is None:
            if self.last_tool_results is None or len(self.last_tool_results) == 0:
                raise ValueError("No tool results from previous step to inform the planner.")
            _input += self.last_tool_results
        
        user_content = []
        if screenshot:
            user_content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{screenshot}"
            })
        user_content.append({"type": "input_text", "text": user_query})
        _input.append({
            "role": "user",
            "content": user_content
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
            previous_response_id=self.previous_response_id,
            tool_choice="required",
        )
        self.previous_response_id = response.id
        return response

    def end_task(self):
        pass

    def iterate(self, screenshot: str = None, task: str = None) -> tuple[AgentPredictionResponse, bool]:
        response = self._generate_plan(task=task, screenshot=screenshot)
        regenerate_plan = False

        token_usage = TokenUsage.from_response(response)

        reasoning_summaries = [] 
        for output in response.output:
            if output.type == "summary_text" or output.type == "reasoning":
                for summary in output.summary:
                    summary_text = summary.text.strip() if summary.text else None
                    if summary_text:
                        reasoning_summaries.append(summary_text)
        reasoning_summary = "\n\n".join(reasoning_summaries)
        logger.info(f"Reasoning Summary: {reasoning_summary}")

        tool_calls = get_tool_calls_from_response(response)
        executed_actions = []
        pyautogui_scripts = []
        self.last_tool_results = []

        for tool_call in tool_calls:
            executed_action, pyautogui_script, _token_usage, _regenerate_plan = self.tool_set.parse_action(
                tool_call=tool_call,
                screenshot=screenshot,
            )
            regenerate_plan = _regenerate_plan or regenerate_plan
            
            token_usage.prompt_tokens += _token_usage[0]
            token_usage.completion_tokens += _token_usage[1]

            executed_actions.append(executed_action)
            pyautogui_scripts.append(pyautogui_script)

            self.last_tool_results.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": executed_action,
            })

        pyautogui_script = "\n\n".join(pyautogui_scripts)
        pyautogui_script = fix_pyautogui_script(pyautogui_script)

        agent_response = reasoning_summary
        if response.output_text:
            agent_response += "\n\n#Output\n" + response.output_text

        agent_response += "\n\n# Tool Calls"
        for i, tc in enumerate(tool_calls):
            executed_action = executed_actions[i]
            tc_name, tc_args = tc.name, tc.arguments
            agent_response += f"\n\n# Tool Call {i+1}:\n"
            agent_response += f"Called tool: {tc_name}\n"
            agent_response += f"## Arguments\n{json.dumps(tc_args, indent=2)}\n"
            agent_response += f"## Result\n{executed_action}"

        return AgentPredictionResponse(
            pyautogui_actions=pyautogui_script,
            response=agent_response,
            usage=token_usage,
        ), regenerate_plan

    def predict(self, screenshot: str, task) -> AgentPredictionResponse:
        task = task if self.step == 1 else None

        agent_response, retrigger = self.iterate(screenshot=screenshot, task=task)
        while retrigger:
            logger.info("Regenerating plan based on tool call result.")
            additional_response, retrigger = self.iterate(screenshot=None, task=None)

            agent_response += additional_response

        self.step += 1
        return agent_response
    
class Custom2Agent(Custom1Agent):
    """ same custom-1, however has coding tools (python/terminal)"""
    def __init__(self, vm_http_server: str, name: str = "custom-2"):
        super().__init__(name=name)
        self.system_prompt = PLANNER_SYSTEM_PROMPT_V2
        self.grounder = Qwen3VLGrounder(model="qwen/qwen3-vl-32b-instruct")
        self.tool_set = CuaToolSet(grounder=self.grounder, enable_python_execution_tool=True, enable_terminal_command_tool=True, http_server=vm_http_server)
    