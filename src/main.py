"""CLI entry point for the Agent Skeleton.

Usage:
    python -m src.main "Your question here"
    python -m src.main "What is 15 * 7?"
    python -m src.main "Search for Python Agent frameworks"

The CLI provides quick verification that your agent works end-to-end.
"""

import json
import logging
import sys

from src.core.agent_loop import AgentConfig, ReActAgent
from src.core.config import LLMNotConfiguredError
from src.core.llm_client import LLMClient
from src.core.tool_registry import ToolRegistry
from src.tools.builtin import builtin_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


def build_default_agent() -> ReActAgent:
    tools = ToolRegistry()
    for tool in builtin_tools():
        tools.register(tool)

    return ReActAgent(
        AgentConfig(
            system_prompt="You are a helpful assistant. Use tools to answer questions accurately.",
            tools=tools,
            max_iterations=8,
            llm_client=LLMClient(),
            name="default",
        )
    )


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <question>")
        print("Example: python -m src.main 'What is 15 * 7?'")
        sys.exit(1)

    user_message = " ".join(sys.argv[1:])

    try:
        agent = build_default_agent()
    except LLMNotConfiguredError:
        print("Error: LLM_API_KEY is not configured.")
        print("Create a .env file with your API key (see .env.example).")
        print("CRUD and tool execution work without an API key.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"User: {user_message}")
    print(f"{'='*60}\n")

    result = agent.run(user_message)

    for step in result.steps:
        if step.tool_name:
            print(f"\n[Step {step.iteration}] 💭 {step.thought}")
            print(f"  🔧 Calling: {step.tool_name}")
            print(f"  📥 Args: {json.dumps(step.tool_args, ensure_ascii=False)}")
            print(f"  📤 Result: {json.dumps(step.tool_result, ensure_ascii=False, default=str)[:200]}")
        elif step.is_final:
            print(f"\n[Step {step.iteration}] 💭 {step.thought}")

    print(f"\n{'='*60}")
    print(f"Answer: {result.answer}")
    print(f"Iterations: {result.iterations} | Tools called: {len(result.tools_called)} | Latency: {result.total_latency_ms}ms")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
