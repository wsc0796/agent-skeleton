# Demo Guide

> 3-minute demo script for interview or portfolio showcase.

## Prerequisites

```bash
pip install -r requirements.txt
cp .env.example .env
# Set LLM_API_KEY=your-deepseek-key in .env
```

## 1. Start the server

```bash
uvicorn src.server.main:app --reload
```

Open http://localhost:8000/docs for Swagger UI.

## 2. Health check

```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

## 3. List available tools and agents

```bash
curl http://localhost:8000/api/v1/tools
# → {"tools": [{"name":"analyze_jd",...}, {"name":"calculator",...}, ...]}

curl http://localhost:8000/api/v1/agents
# → {"agents": [{"name":"job_matcher","tool_count":4,...}]}
```

## 4. REST chat — analyze a JD

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze this JD: AI Agent intern, requires Python, LLM, FastAPI, Docker"}'
```

**Expected response:**

```json
{
  "agent_name": "job_matcher",
  "answer": "I analyzed the JD...",
  "steps": [
    {
      "iteration": 1,
      "thought": "I need to analyze the JD first",
      "tool_name": "analyze_jd",
      "tool_args": {"jd_text": "AI Agent intern..."},
      "is_final": false
    },
    {
      "iteration": 2,
      "thought": "Analysis complete, here is the result",
      "is_final": true
    }
  ],
  "tools_called": ["analyze_jd"],
  "total_latency_ms": 1200
}
```

## 5. SSE stream — watch the agent work step by step

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Match my skills: Python, FastAPI, Docker against JD: AI Agent intern"}'
```

**Expected SSE events:**

```text
event: agent_started
data: {"agent":"job_matcher"}

event: tool_call_started
data: {"iteration":1,"tool":"analyze_jd","args":{"jd_text":"AI Agent intern"}}

event: tool_call_finished
data: {"iteration":1,"tool":"analyze_jd","result_preview":"{'job_type': 'ai_agent'...}"}

event: tool_call_started
data: {"iteration":2,"tool":"match_resume","args":{"resume_skills":["Python","FastAPI","Docker"],"jd_text":"AI Agent intern"}}

event: tool_call_finished
data: {"iteration":2,"tool":"match_resume","result_preview":"{'match_score': 75...}"}

event: final_answer
data: {"answer":"75% match for ai_agent role...","tools_called":["analyze_jd","match_resume"],"latency_ms":2500}
```

## 6. React UI (optional)

```bash
cd src/ui
npm install
npm run dev
# → http://localhost:5173
```

Type a question or paste a JD. Watch the tool-call panels expand as the agent works.

## No API key?

Without `LLM_API_KEY`, CRUD endpoints and tool listing still work. AI chat returns 503 with error code `LLM_NOT_CONFIGURED`.
