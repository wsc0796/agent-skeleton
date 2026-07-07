# Agent Skeleton

A lightweight, interview-facing Agent project skeleton with a reusable ReAct loop, Pydantic Tool Registry, FastAPI REST/SSE API, React Agent Chat UI, and pluggable business tools.

## Status

| Area | Status |
|---|---|
| Core Agent Loop | ✅ Done |
| Tool Registry | ✅ Done |
| Memory | ✅ Conversation buffer + optional demo-level ChromaDB |
| FastAPI REST API | ✅ Done |
| SSE execution trace | ✅ Done |
| React UI | ✅ Done |
| Business Example | ✅ Job Matching |
| Tests | ✅ 44 passed |
| CI | ✅ GitHub Actions green |

## Docs

- Demo: [docs/demo.md](docs/demo.md)
- API: [docs/api.md](docs/api.md)
- Security: [docs/security.md](docs/security.md)
- Limitations: [docs/limitations.md](docs/limitations.md)
- Evaluation: [docs/evaluation.md](docs/evaluation.md)
- Platform Mapping: [docs/platform_mapping.md](docs/platform_mapping.md)
- Resume Evidence: [docs/resume_evidence.md](docs/resume_evidence.md)

## Positioning

| Tool | Best for | This project focuses on |
|---|---|---|
| LangChain / LangGraph | Production Python agent orchestration ecosystem | Learning and demonstrating core Agent internals |
| Dify / n8n | Low-code workflow building and service integration | Understanding what happens behind workflow nodes |
| agent-skeleton | Interview-facing lightweight skeleton | Readable ReAct loop, tool validation, execution trace, and business customization |

**Not production-grade.** This is a learning project and internship portfolio piece.
See [Limitations](docs/limitations.md).

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set LLM_API_KEY=your-deepseek-key

# CLI
python -m src.main "What is 15 * 7?"

# API server
uvicorn src.server.main:app --reload
# http://localhost:8000/docs

# React UI
cd src/ui && npm install && npm run dev
# http://localhost:5173
```

## Architecture

```text
src/
├── core/                    # Stable reusable core
│   ├── llm_client.py        # OpenAI-compatible DeepSeek/OpenAI client
│   ├── agent_loop.py        # ReAct loop with step-by-step execution trace
│   ├── tool_registry.py     # Tool registration + Pydantic validation + OpenAI schema
│   └── memory.py            # Conversation buffer + optional demo-level ChromaDB memory
│
├── tools/
│   ├── builtin/             # Generic tools: calculator, time, file, store, search stub
│   └── business/            # Business tools; job_matching reference included
│
├── agents/
│   └── personas/            # Persona configs; job_matcher reference included
│
├── server/                  # FastAPI REST + SSE streaming
└── ui/                      # React Agent Chat UI
```

## Demo

```bash
# 1. Start server
uvicorn src.server.main:app --reload

# 2. Health
curl http://localhost:8000/health

# 3. Analyze a JD
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze: AI Agent intern, requires Python, LLM, FastAPI"}'

# 4. See agent execution trace via SSE
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Match my skills: Python, FastAPI, Docker"}'
```

Full demo guide: [docs/demo.md](docs/demo.md)

## Customize

`src/core/` is designed as a stable base. Most business adaptation happens in tools, personas, and examples:

| Use case | Typical adaptation point |
|---|---|
| Customer support agent | `tools/business/` for CRM lookup and ticket tools |
| Code review agent | `tools/business/` for git diff and lint tools |
| Job matching agent | `tools/business/` for JD analysis and resume matching |
| Data analysis agent | `tools/business/` for SQL query and chart tools |

Guide: [docs/customize.md](docs/customize.md)

## How It Works

```text
User: "Analyze this JD: Python, FastAPI required"
  -> Agent returns structured action JSON for analyze_jd
  -> Tool call: analyze_jd("Python, FastAPI required")
  -> Tool result: job_type=ai_agent, skills=[Python, FastAPI, Docker, Git]
  -> Agent returns structured action JSON for match_resume
  -> Tool call: match_resume(...)
  -> Tool result: match_score=75%, missing=[LLM, RAG]
  -> Final answer with gap report
```

The agent chooses which registered tools to call and in what order. Each step is visible in the execution trace returned by the API.

## Tech Stack

- **LLM**: OpenAI-compatible API, DeepSeek by default
- **Agent**: Hand-written ReAct loop
- **Memory**: Conversation buffer + optional demo-level ChromaDB
- **Validation**: Pydantic for all tool arguments
- **Server**: FastAPI + SSE streaming
- **UI**: React 19 + Vite + TypeScript
- **Test**: pytest, ruff

## License

MIT
