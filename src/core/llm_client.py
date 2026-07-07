import json
import logging
import time
from typing import Any, Iterator

from openai import OpenAI

from src.core.config import LLMConfig, LLMNotConfiguredError

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI-compatible LLM client with retry, streaming, and audit logging."""

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
            )
        return self._client

    def _ensure_key(self) -> None:
        if not self.config.is_configured:
            raise LLMNotConfiguredError()

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        response_format: dict | None = None,
    ) -> str:
        """Synchronous chat completion with retry."""
        self._ensure_key()

        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.config.temperature,
        }

        if response_format is not None:
            kwargs["response_format"] = response_format

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._get_client().chat.completions.create(**kwargs)
                content = response.choices[0].message.content or ""
                return content
            except LLMNotConfiguredError:
                raise
            except Exception as exc:
                last_error = exc
                logger.warning("LLM call attempt %d failed: %s", attempt + 1, exc)
                if attempt < self.config.max_retries:
                    time.sleep(0.5)

        raise last_error  # type: ignore[misc]

    def chat_stream(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Iterator[str]:
        """Streaming chat completion — yields content chunks."""
        self._ensure_key()

        try:
            stream = self._get_client().chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.config.temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except LLMNotConfiguredError:
            raise
        except Exception as exc:
            logger.error("LLM stream failed: %s", exc)
            raise

    def chat_with_tools(
        self,
        system_prompt: str,
        messages: list[dict],
        tools: list[dict],
    ) -> dict:
        """Chat completion with tool calling — returns the raw response dict."""
        self._ensure_key()

        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *messages,
            ],
            "temperature": self.config.temperature,
            "tools": tools,
        }

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._get_client().chat.completions.create(**kwargs)
                msg = response.choices[0].message
                result: dict = {"content": msg.content}
                if msg.tool_calls:
                    result["tool_calls"] = [
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments),
                        }
                        for tc in msg.tool_calls
                    ]
                return result
            except Exception as exc:
                last_error = exc
                if attempt < self.config.max_retries:
                    time.sleep(0.5)

        raise last_error  # type: ignore[misc]
