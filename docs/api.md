# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Health

```text
GET /health
```

Response: `{"status": "ok"}`

---

### List Tools

```text
GET /api/v1/tools
```

Response:

```json
{
  "tools": [
    {"name": "web_search", "description": "...", "category": "builtin"},
    {"name": "analyze_jd", "description": "...", "category": "business"}
  ]
}
```

---

### List Agents

```text
GET /api/v1/agents
```

Response:

```json
{
  "agents": [
    {"name": "job_matcher", "description": "...", "tool_count": 4, "tools": ["analyze_jd", "match_resume", "generate_gap_report", "generate_study_plan"]}
  ]
}
```

---

### Chat (REST)

```text
POST /api/v1/chat
Content-Type: application/json
```

Request:

```json
{
  "message": "Analyze this JD: AI Agent intern, requires Python, LLM",
  "agent_name": "job_matcher"
}
```

`agent_name` is optional, defaults to `"job_matcher"`.

Success (200):

```json
{
  "agent_name": "job_matcher",
  "answer": "I analyzed the JD...",
  "steps": [
    {
      "iteration": 1,
      "thought": "Need to analyze the JD",
      "tool_name": "analyze_jd",
      "tool_args": {"jd_text": "..."},
      "tool_result": "{'job_type': 'ai_agent', ...}",
      "is_final": false
    }
  ],
  "iterations": 2,
  "tools_called": ["analyze_jd"],
  "total_latency_ms": 1200
}
```

Errors:

| Status | Code | Meaning |
|--------|------|---------|
| 422 | — | `message` is empty or missing |
| 502 | — | Agent processing error |
| 503 | `LLM_NOT_CONFIGURED` | API key not set |

---

### Chat (SSE Stream)

```text
POST /api/v1/chat/stream
Content-Type: application/json
```

Request: same as REST chat.

SSE Events:

| Event | Data |
|-------|------|
| `agent_started` | `{"agent": "job_matcher"}` |
| `tool_call_started` | `{"iteration": N, "tool": "name", "args": {...}}` |
| `tool_call_finished` | `{"iteration": N, "tool": "name", "result_preview": "..."}` |
| `final_answer` | `{"answer": "...", "iterations": N, "tools_called": [...], "latency_ms": N}` |
| `error` | `{"error": "error message"}` |

Example curl:

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze JD: Python, FastAPI"}'
```
