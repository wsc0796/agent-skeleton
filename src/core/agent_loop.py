import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from src.core.llm_client import LLMClient
from src.core.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class AgentStep:
    """One step in the agent's thinking process — visible to the user."""

    iteration: int
    thought: str = ""
    tool_name: str | None = None
    tool_args: dict | None = None
    tool_result: Any = None
    is_final: bool = False


@dataclass
class AgentResult:
    answer: str
    steps: list[AgentStep] = field(default_factory=list)
    iterations: int = 0
    tools_called: list[str] = field(default_factory=list)
    total_latency_ms: int = 0


@dataclass
class AgentConfig:
    """Configuration for an agent instance — this is what you customize per JD."""

    system_prompt: str
    tools: ToolRegistry = field(default_factory=ToolRegistry)
    max_iterations: int = 8
    llm_client: LLMClient | None = None
    temperature: float = 0.3
    name: str = "agent"


class ReActAgent:
    """ReAct (Reasoning + Acting) agent loop.

    The key improvement over the internship-tracker-api version:
    - Visible thinking chain (AgentStep records every thought)
    - Structured tool-call JSON format
    - Step-by-step trace for UI rendering
    """

    SYSTEM_TEMPLATE = """You are an AI assistant with access to tools. Follow this pattern:

1. THINK about what the user needs
2. If you can answer directly, set action_type to "final"
3. If you need a tool, set action_type to "tool_call" and choose the right tool

Available tools:
{tool_descriptions}

Respond ONLY in this JSON format:
If calling a tool:
{{"action_type": "tool_call", "reasoning": "why you need this tool", "tool_name": "name", "tool_args": {{...}}}}

If giving the final answer:
{{"action_type": "final", "reasoning": "summary of your analysis", "answer": "your final answer to the user"}}
"""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.llm = config.llm_client or LLMClient()

    def run(self, user_message: str) -> AgentResult:
        start_ms = int(time.time() * 1000)
        steps: list[AgentStep] = []
        tools_called: list[str] = []
        call_history: list[tuple[str, str]] = []

        system = self.SYSTEM_TEMPLATE.format(
            tool_descriptions=self.config.tools.describe()
        )

        messages: list[dict] = [{"role": "user", "content": user_message}]

        for iteration in range(1, self.config.max_iterations + 1):
            try:
                raw = self.llm.chat(
                    system_prompt=system,
                    user_prompt=json.dumps(messages, ensure_ascii=False),
                )
            except Exception as exc:
                logger.error("LLM error at iteration %d: %s", iteration, exc)
                steps.append(
                    AgentStep(
                        iteration=iteration,
                        thought=f"LLM error: {exc}",
                        is_final=True,
                    )
                )
                return AgentResult(
                    answer=f"Agent encountered an error: {exc}",
                    steps=steps,
                    iterations=iteration,
                    tools_called=tools_called,
                    total_latency_ms=int(time.time() * 1000) - start_ms,
                )

            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Could not parse agent output as JSON")
                steps.append(
                    AgentStep(
                        iteration=iteration,
                        thought="Could not parse response, retrying...",
                    )
                )
                messages.append(
                    {
                        "role": "assistant",
                        "content": "Please respond in valid JSON format.",
                    }
                )
                continue

            action_type = parsed.get("action_type", "")
            reasoning = parsed.get("reasoning", "")

            if action_type == "final":
                steps.append(
                    AgentStep(
                        iteration=iteration,
                        thought=reasoning,
                        is_final=True,
                    )
                )
                return AgentResult(
                    answer=parsed.get("answer", ""),
                    steps=steps,
                    iterations=iteration,
                    tools_called=tools_called,
                    total_latency_ms=int(time.time() * 1000) - start_ms,
                )

            if action_type == "tool_call":
                tool_name = parsed.get("tool_name", "")
                tool_args = parsed.get("tool_args", {})

                tool = self.config.tools.get(tool_name)
                if tool is None:
                    messages.append(
                        {
                            "role": "tool",
                            "content": f"Unknown tool: {tool_name}. Available: {self.config.tools.list_names()}",
                        }
                    )
                    steps.append(
                        AgentStep(
                            iteration=iteration,
                            thought=f"Tried unknown tool: {tool_name}",
                        )
                    )
                    continue

                call_key = (tool_name, json.dumps(tool_args, sort_keys=True))
                if call_history.count(call_key) >= 2:
                    return AgentResult(
                        answer="Detected repeated tool calls. Stopping to avoid infinite loop.",
                        steps=steps,
                        iterations=iteration,
                        tools_called=tools_called,
                        total_latency_ms=int(time.time() * 1000) - start_ms,
                    )

                call_history.append(call_key)
                tools_called.append(tool_name)

                try:
                    result = tool.execute(**tool_args)
                except Exception as exc:
                    result = f"Error executing tool: {exc}"

                step = AgentStep(
                    iteration=iteration,
                    thought=reasoning,
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_result=result,
                )
                steps.append(step)

                observation = {
                    "tool": tool_name,
                    "result": result,
                }
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(observation, ensure_ascii=False, default=str),
                    }
                )
                continue

            messages.append(
                {
                    "role": "assistant",
                    "content": f"Invalid action_type: {action_type}. Use 'tool_call' or 'final'.",
                }
            )

        return AgentResult(
            answer="Reached maximum iterations without a final answer.",
            steps=steps,
            iterations=self.config.max_iterations,
            tools_called=tools_called,
            total_latency_ms=int(time.time() * 1000) - start_ms,
        )
