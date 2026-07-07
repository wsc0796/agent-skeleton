import pytest
from unittest import mock

from src.core.agent_loop import AgentConfig, ReActAgent
from src.core.tool_registry import ToolRegistry, ToolSpec


class EchoArgs(pytest.importorskip("pydantic").BaseModel):
    message: str


def echo(message: str) -> str:
    return f"Echo: {message}"


def make_agent() -> ReActAgent:
    tools = ToolRegistry()
    tools.register(
        ToolSpec(
            name="echo",
            description="Echo a message back",
            args_model=EchoArgs,
            function=echo,
        )
    )
    return ReActAgent(
        AgentConfig(
            system_prompt="You are a test agent. Use tools when needed.",
            tools=tools,
            max_iterations=5,
            name="test",
        )
    )


class TestReActAgent:
    def test_agent_returns_final_answer(self):
        agent = make_agent()

        final_response = '{"action_type": "final", "reasoning": "User said hi", "answer": "Hello!"}'
        with mock.patch.object(agent.llm, "chat", return_value=final_response):
            result = agent.run("Hi!")

        assert result.answer == "Hello!"
        assert result.iterations == 1

    def test_agent_calls_tool_then_answers(self):
        agent = make_agent()

        tool_response = '{"action_type": "tool_call", "reasoning": "I need to echo", "tool_name": "echo", "tool_args": {"message": "hello"}}'
        final_response = '{"action_type": "final", "reasoning": "Done", "answer": "Echo: hello"}'

        with mock.patch.object(agent.llm, "chat", side_effect=[tool_response, final_response]):
            result = agent.run("Echo hello")

        assert "echo" in result.tools_called
        assert len(result.steps) == 2
        assert result.steps[0].tool_name == "echo"
        assert result.steps[1].is_final

    def test_agent_handles_unknown_tool(self):
        agent = make_agent()

        bad_tool = '{"action_type": "tool_call", "reasoning": "Try bad tool", "tool_name": "nonexistent", "tool_args": {}}'
        final_response = '{"action_type": "final", "reasoning": "Tool failed", "answer": "Cannot help"}'

        with mock.patch.object(agent.llm, "chat", side_effect=[bad_tool, final_response]):
            result = agent.run("Do something")

        assert result.iterations == 2
        assert len(result.tools_called) == 0  # bad tool doesn't count

    def test_agent_stops_on_repeated_calls(self):
        agent = make_agent()

        # Same tool call 3 times
        tool_response = '{"action_type": "tool_call", "reasoning": "Need echo", "tool_name": "echo", "tool_args": {"message": "test"}}'
        with mock.patch.object(agent.llm, "chat", return_value=tool_response):
            result = agent.run("Test")

        assert "repeated tool calls" in result.answer.lower()
        assert result.iterations <= 5

    def test_agent_max_iterations(self):
        agent = make_agent()
        agent.config.max_iterations = 3

        # Use unique tool calls each time to avoid "repeated calls" early stop
        def unique_tool_response(iteration):
            # Each call is unique (different message), avoids repeat detection
            return mock.MagicMock()

        # Mock chat to always return tool_call but with different args each time
        responses = []
        for i in range(3):
            responses.append(
                f'{{"action_type": "tool_call", "reasoning": "step {i}", "tool_name": "echo", "tool_args": {{"message": "msg{i}"}}}}'
            )

        with mock.patch.object(agent.llm, "chat", side_effect=responses):
            result = agent.run("Loop forever")

        assert "maximum iterations" in result.answer.lower()
        assert result.iterations == 3

    def test_invalid_json_retry(self):
        agent = make_agent()

        bad_json = "not valid json"
        final_response = '{"action_type": "final", "reasoning": "ok", "answer": "Recovered"}'

        with mock.patch.object(agent.llm, "chat", side_effect=[bad_json, final_response]):
            result = agent.run("Test")

        assert result.answer == "Recovered"
        assert result.iterations == 2
