import os
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    base_url: str = field(
        default_factory=lambda: os.getenv(
            "LLM_BASE_URL", "https://api.deepseek.com/v1"
        )
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("LLM_API_KEY", "")
    )
    model: str = field(
        default_factory=lambda: os.getenv("LLM_MODEL", "deepseek-chat")
    )
    temperature: float = 0.3
    timeout: float = 30.0
    max_retries: int = 2

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


class LLMNotConfiguredError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "LLM_API_KEY is not configured. "
            "Set the environment variable or configure it in .env."
        )
