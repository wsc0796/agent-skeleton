from dataclasses import dataclass, field
from typing import Any, Callable

from pydantic import BaseModel


@dataclass
class ToolSpec:
    """A tool the agent can call. args_model validates input with Pydantic."""

    name: str
    description: str
    args_model: type[BaseModel]
    function: Callable[..., Any]
    category: str = "general"

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI function calling schema."""
        props = self.args_model.model_json_schema().get("properties", {})
        required = self.args_model.model_json_schema().get("required", list(props.keys()))
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                },
            },
        }

    def execute(self, **kwargs: Any) -> Any:
        validated = self.args_model(**kwargs)
        return self.function(**validated.model_dump())


@dataclass
class ToolRegistry:
    """Manages registered tools with category grouping and safety controls."""

    tools: dict[str, ToolSpec] = field(default_factory=dict)

    def register(self, tool: ToolSpec) -> None:
        self.tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec | None:
        return self.tools.get(name)

    def list_names(self) -> list[str]:
        return list(self.tools.keys())

    def list_by_category(self, category: str) -> list[ToolSpec]:
        return [t for t in self.tools.values() if t.category == category]

    def to_openai_schemas(self) -> list[dict]:
        return [t.to_openai_schema() for t in self.tools.values()]

    def describe(self) -> str:
        lines: list[str] = []
        for t in self.tools.values():
            lines.append(f"- {t.name}: {t.description}")
        return "\n".join(lines)
