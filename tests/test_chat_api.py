from unittest import mock
from fastapi.testclient import TestClient

from src.server.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAdminEndpoints:
    def test_list_tools(self):
        response = client.get("/api/v1/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) >= 8  # 6 builtin + 4 job matching - 2 overlap

    def test_list_agents(self):
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert len(data["agents"]) == 1
        assert data["agents"][0]["name"] == "job_matcher"


class TestChatEndpoint:
    def test_chat_missing_message_422(self):
        response = client.post("/api/v1/chat", json={})
        assert response.status_code == 422

    def test_chat_empty_message_422(self):
        response = client.post("/api/v1/chat", json={"message": ""})
        assert response.status_code == 422

    def test_chat_returns_503_when_key_missing(self):
        from src.core.config import LLMNotConfiguredError

        with mock.patch(
            "src.server.routes.chat._get_agent",
            side_effect=LLMNotConfiguredError(),
        ):
            response = client.post(
                "/api/v1/chat",
                json={"message": "Analyze this JD"},
            )
        assert response.status_code == 503
        body = response.json()
        detail = body.get("detail", body)
        assert detail["code"] == "LLM_NOT_CONFIGURED"

    def test_chat_returns_response_with_mocked_llm(self):
        final_response = '{"action_type": "final", "reasoning": "JD analyzed", "answer": "Matched 75%"}'

        with mock.patch.object(
            __import__("src.core.llm_client", fromlist=["LLMClient"]).LLMClient,
            "chat",
            return_value=final_response,
        ):
            response = client.post(
                "/api/v1/chat",
                json={"message": "Analyze JD: Python, FastAPI"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["agent_name"] == "job_matcher"
        assert "answer" in data
        assert data["answer"] == "Matched 75%"
        assert "steps" in data
        assert "tools_called" in data
