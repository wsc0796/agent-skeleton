import pytest
from pydantic import BaseModel, Field

from src.core.tool_registry import ToolRegistry, ToolSpec


class CalcArgs(BaseModel):
    expression: str = Field(..., min_length=1)


def calc(expression: str) -> dict:
    return {"result": eval(expression)}


class EchoArgs(BaseModel):
    message: str


def echo(message: str) -> str:
    return message


class TestToolRegistry:
    def test_register_and_get(self):
        registry = ToolRegistry()
        tool = ToolSpec(
            name="echo",
            description="Echo a message",
            args_model=EchoArgs,
            function=echo,
        )
        registry.register(tool)

        assert registry.get("echo") is tool
        assert "echo" in registry.list_names()

    def test_execute_valid_args(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="calc",
                description="Calculate",
                args_model=CalcArgs,
                function=calc,
            )
        )

        result = registry.get("calc").execute(expression="2 + 3")
        assert result == {"result": 5}

    def test_execute_invalid_args_raises(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="calc",
                description="Calculate",
                args_model=CalcArgs,
                function=calc,
            )
        )

        with pytest.raises(Exception):
            registry.get("calc").execute(wrong_field="2 + 3")

    def test_to_openai_schema(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="echo",
                description="Echo a message",
                args_model=EchoArgs,
                function=echo,
            )
        )

        schema = registry.to_openai_schemas()[0]
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "echo"
        assert "message" in schema["function"]["parameters"]["properties"]

    def test_describe(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(name="a", description="First tool", args_model=EchoArgs, function=echo)
        )
        registry.register(
            ToolSpec(name="b", description="Second tool", args_model=EchoArgs, function=echo)
        )

        desc = registry.describe()
        assert "- a: First tool" in desc
        assert "- b: Second tool" in desc
