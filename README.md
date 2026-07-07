# Agent Skeleton

**Reusable Agent project skeleton — plug in business tools, swap agent personas, core stays unchanged.**

Built for internship job-seeking: customize per-company JD requirements in minutes.

## Architecture

```
src/
├── core/                    # 🔒 NEVER CHANGES — reusable across all projects
│   ├── llm_client.py        # OpenAI-compatible client (DeepSeek/OpenAI, retry, streaming)
│   ├── agent_loop.py        # ReAct agent loop with visible thinking chain
│   ├── tool_registry.py     # Tool registration + Pydantic validation + OpenAI schema
│   └── memory.py            # Conversation buffer + ChromaDB long-term memory
│
├── tools/                   # 🔧 CUSTOMIZE per project
│   ├── builtin/             # Generic tools (search, calculator, time, file, store)
│   └── business/            # 🎯 Business-specific tools (replace per JD)
│
├── agents/                  # 🎯 CUSTOMIZE per project
│   └── personas/            # Agent configs (system prompt + tools + model)
│
├── server/                  # 🔒 STABLE — FastAPI + SSE
└── ui/                      # 🔒 STABLE — React Agent Chat
```

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

## Documentation

| Doc | For |
|-----|-----|
| [Architecture](docs/architecture.md) | Request flow diagram, layer responsibility, SSE event trace |
| [Resume Evidence](docs/resume_evidence.md) | STAR bullets, interview Q&A, test coverage map, demo commands |
| [Customization Guide](docs/customize.md) | 30-min guide: add business tools for any company JD |

## How It Works

```text
User: "Search for Python Agent frameworks"
  → Agent thinks: "I need web search"
  → Tool call: web_search("Python Agent frameworks")
  → Agent analyzes results
  → Final answer with citations
```

## Customize per JD

| Company wants | You change |
|---------------|-----------|
| Customer support agent | `tools/business/` ← CRM + ticket tools |
| Code review agent | `tools/business/` ← git + lint + test tools |
| Job matching agent | `tools/business/` ← JD analysis + resume matching |
| Data analysis agent | `tools/business/` ← SQL + pandas + viz tools |

**`src/core/` never changes.** Only swap tools and personas.

## Test

```bash
pytest -v                          # 19 tests
ruff check .                       # Code quality
```

## Tech Stack

- **LLM**: OpenAI-compatible API (DeepSeek default)
- **Agent**: Hand-written ReAct loop (no framework lock-in)
- **Memory**: ChromaDB (vector) + conversation buffer
- **Validation**: Pydantic for all tool arguments
- **Server** (coming): FastAPI + SSE streaming
- **UI** (coming): React + Vite Agent Chat

## Current Status

**All 3 weeks complete — 44 tests, ruff clean, CI green.**

| Week | Delivered |
|------|-----------|
| Week 1 | Core engine: LLM client, ReAct loop, tool registry, memory, 6 built-in tools |
| Week 2 | FastAPI server + SSE streaming + job matcher persona + 4 business tools |
| Week 3 | React Agent Chat UI + calculator safety fix (AST parser, no eval) + sample data |

## Comparison

| Feature | agent-skeleton | LangChain | Dify |
|---------|---------------|-----------|------|
| Hand-written | ✅ | ❌ | ❌ |
| No framework lock-in | ✅ | ❌ | ❌ |
| Customizable per JD | ✅ | ✅ | ❌ |
| Learnable in 1 day | ✅ | ❌ | ✅ |

## License

MIT
