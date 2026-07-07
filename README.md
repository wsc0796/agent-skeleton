# Agent Skeleton

**A lightweight, reusable Agent backend skeleton for tool-calling agents.**

Built for internship job-seeking: demonstrate core Agent engineering patterns
(ReAct loop, tool registry, SSE execution trace, business tool customization)
in a readable, testable, interviewer-friendly codebase.

## Status

| Item | Status |
|------|--------|
| Agent loop (ReAct) | ✅ |
| Tool registry (Pydantic) | ✅ |
| LLM client (DeepSeek/OpenAI) | ✅ |
| Builtin tools (6) | ✅ |
| FastAPI + SSE | ✅ |
| React Agent Chat UI | ✅ |
| Business example (Job Matching) | ✅ |
| Tests | ✅ 44 passed |
| CI | ✅ GitHub Actions |

**Not production-grade.** This is a learning project and internship portfolio piece.
See [Limitations](docs/limitations.md).

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set LLM_API_KEY=your-deepseek-key

# CLI
python -m src.main "What is 15 * 7?"

# API Server
uvicorn src.server.main:app --reload
# → http://localhost:8000/docs

# React UI
cd src/ui && npm install && npm run dev
# → http://localhost:5173
```

## Architecture

```
src/
├── core/                    # Stable reusable core
│   ├── llm_client.py        # OpenAI-compatible (DeepSeek/OpenAI, retry, streaming)
│   ├── agent_loop.py        # ReAct loop with step-by-step execution trace
│   ├── tool_registry.py     # Tool registration + Pydantic validation + OpenAI schema
│   └── memory.py            # Conversation buffer + optional ChromaDB memory
│
├── tools/
│   ├── builtin/             # Generic tools (search, calculator, time, file, store)
│   └── business/            # 🎯 Swap per company JD (job_matching reference included)
│
├── agents/
│   └── personas/            # 🎯 Swap per use case (job_matcher reference included)
│
├── server/                  # FastAPI REST + SSE streaming
└── ui/                      # React Agent Chat (Vite + TypeScript)
```

## Demo (3 minutes)

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

## Customize per JD

`src/core/` is designed as a stable base. Most business adaptation happens in two directories:

| Company wants | You swap |
|---------------|----------|
| Customer support agent | `tools/business/` ← CRM lookup + ticket tools |
| Code review agent | `tools/business/` ← git diff + lint runner |
| Job matching agent | `tools/business/` ← JD analysis + resume matching (included) |
| Data analysis agent | `tools/business/` ← SQL query + chart tools |

Guide: [docs/customize.md](docs/customize.md)

## Documentation

| Doc | Audience |
|-----|----------|
| [Architecture](docs/architecture.md) | Request flow, SSE event trace, layer design |
| [Resume Evidence](docs/resume_evidence.md) | STAR bullets, interview Q&A, test coverage |
| [Customization Guide](docs/customize.md) | How to add business tools in 30 minutes |
| [Demo Guide](docs/demo.md) | 3-minute demo script with expected output |
| [API Reference](docs/api.md) | Endpoints, request/response schemas, error format |
| [Security](docs/security.md) | Tool whitelist, AST calculator, path whitelist |
| [Limitations](docs/limitations.md) | What this project is NOT |

## How It Works

```text
User: "Analyze this JD: Python, FastAPI required"
  → Agent decides: "I need to analyze the JD first"
  → Tool call: analyze_jd("Python, FastAPI required")
  → Agent reviews result: "job_type=ai_agent, skills=[Python, FastAPI, Docker, Git]"
  → Agent: "Now let me match against your resume"
  → Tool call: match_resume(...)
  → Agent: "match_score=75%, missing=[LLM, RAG]"
  → Final answer with gap report
```

The agent *decides* which tools to call and in what order. Each step is visible
in the execution trace returned by the API.

## Positioning

| Tool | Best for | This project |
|------|----------|-------------|
| LangChain / LangGraph | Production orchestration ecosystem | Learning: I implement the internal loop here |
| Dify / n8n | Low-code agent workflow building | Learning: I understand what happens under the UI |
| **agent-skeleton** | Interview-facing lightweight skeleton | Readable code, tool validation, execution trace |

## Tech Stack

- **LLM**: OpenAI-compatible API (DeepSeek default)
- **Agent**: Hand-written ReAct loop
- **Memory**: Conversation buffer + optional ChromaDB
- **Validation**: Pydantic for all tool arguments
- **Server**: FastAPI + SSE streaming
- **UI**: React 19 + Vite + TypeScript
- **Test**: pytest (44 cases), ruff

## License

MIT
