from dataclasses import dataclass, field

from src.core.llm_client import LLMClient
from src.core.tool_registry import ToolRegistry


@dataclass
class AgentPersona:
    """An agent's identity: what it knows, what tools it has, how it behaves."""

    name: str
    description: str
    system_prompt: str
    tools: ToolRegistry = field(default_factory=ToolRegistry)
    model: str = "deepseek-chat"
    temperature: float = 0.3
    max_iterations: int = 8
    llm_client: LLMClient | None = None
