import pytest
from unittest import mock

from src.core.llm_client import LLMClient
from src.core.config import LLMNotConfiguredError


class TestLLMClientConfig:
    def test_raises_when_key_not_configured(self):
        client = LLMClient()
        client.config.api_key = ""
        with pytest.raises(LLMNotConfiguredError):
            client._ensure_key()

    def test_retries_on_failure(self):
        client = LLMClient()
        with mock.patch.object(client, "_ensure_key", return_value=None):
            with mock.patch.object(client, "_get_client") as mock_get_client:
                mock_client = mock.MagicMock()
                mock_get_client.return_value = mock_client
                mock_client.chat.completions.create.side_effect = [
                    ConnectionError("timeout"),
                    mock.MagicMock(
                        choices=[mock.MagicMock(message=mock.MagicMock(content="success"))]
                    ),
                ]

                result = client.chat("sys", "user")

                assert result == "success"
                assert mock_client.chat.completions.create.call_count == 2

    def test_raises_after_max_retries(self):
        client = LLMClient()
        client.config.max_retries = 1
        with mock.patch.object(client, "_ensure_key", return_value=None):
            with mock.patch.object(client, "_get_client") as mock_get_client:
                mock_client = mock.MagicMock()
                mock_get_client.return_value = mock_client
                mock_client.chat.completions.create.side_effect = ConnectionError("fail")

                with pytest.raises(ConnectionError):
                    client.chat("sys", "user")

                # 1 initial + 1 retry = 2 attempts
                assert mock_client.chat.completions.create.call_count == 2
