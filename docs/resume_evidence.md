# Resume Evidence — Agent Skeleton

> Use this page to prepare for interviews. Every claim maps to a file you can open.

## STAR Resume Bullets

### Bullet 1: Agent Architecture (Backend Engineering)

> **Designed and implemented a lightweight Agent Skeleton with a hand-written ReAct loop**
> (44 pytest cases, 6 builtin tools, 4 job matching tools), Pydantic-based Tool Registry,
> OpenAI-compatible LLM client, and memory module. Added safety controls: tool whitelist,
> max-iteration cap, duplicate-call detection, AST-based calculator, and file path whitelist.
> Built FastAPI REST + SSE dual interface for agent communication, and a React + Vite
> Agent Chat UI for execution trace visualization. GitHub Actions CI with ruff + pytest.

**Evidence files:**
- `src/core/agent_loop.py` — ReAct loop with execution trace
- `src/core/tool_registry.py` — Pydantic-validated tool registration
- `src/core/llm_client.py` — OpenAI-compatible client with retry + streaming
- `src/tools/builtin/__init__.py` — Safe calculator (AST parser, not eval)

### Bullet 2: API + SSE Streaming (Full-Stack)

> **Built job matching business example** with 4 tools (analyze_jd → match_resume →
> generate_gap_report → generate_study_plan) covering 15 tech keywords across 4 job types.
> Tools are independently testable (rule engine, no LLM required). Documented customization
> guide for adapting to other business domains (customer support, code review, data analysis).

**Evidence files:**
- `src/server/main.py` — FastAPI app with CORS
- `src/server/routes/chat.py` — Chat + SSE endpoints
- `src/server/routes/admin.py` — Tools/agents listing
- `src/ui/src/hooks/useAgentChat.ts` — Frontend SSE consumer

### Bullet 3: Business Domain — Job Matching

> **Implemented a complete JD analysis pipeline as a showcase business domain.**
> Four tools (analyze_jd → match_resume → generate_gap_report → generate_study_plan)
> form a closed loop from job description to actionable study plan. The skill rule engine
> covers 15 tech keywords across 4 job types (AI Agent, Java Backend, Fullstack, Test Dev).
> Each tool is independently testable without an LLM — the rule engine provides instant
> results, and LLM can be added for deeper analysis.

**Evidence files:**
- `src/tools/business/job_matching/tools.py` — 4 business tools
- `src/agents/personas/job_matcher.py` — Agent persona config
- `examples/job_matching/sample_data/` — Real JD + resume samples

## Interview Deep-Dive Questions (with Answers)

### Q1: Why hand-written ReAct instead of LangChain?

> "I started with LangChain's AgentExecutor but found it hard to debug when
> tool calls failed. Writing my own ReAct loop gave me full control over:
> 1) the JSON format the LLM must follow,
> 2) tool argument validation (Pydantic),
> 3) safety controls (duplicate detection, max iterations).
> I can now explain ReAct to an interviewer, and I can switch to LangChain
> when I need its ecosystem integrations — I know what it does under the hood."

### Q2: How do you prevent the agent from calling tools infinitely?

> "Three layers: 1) max_iterations cap (default 8),
> 2) duplicate-call detection — if the same tool is called with the same
> arguments twice, the agent stops,
> 3) tool whitelist — unknown tool names are rejected. File at `src/core/agent_loop.py:64-80`."

### Q3: How do you keep this secure?

> "Calculator uses AST parsing, not eval — code injection is impossible.
> File reader blocks absolute paths, `..` traversal, and sensitive filenames like `.env`.
> Agent tools are whitelist-only, no filesystem/shell/URL access by default.
> AI call logs store only hash and truncated summaries. See `docs/security.md`."

### Q4: Is this production-ready?

> "No. This is an internship-facing learning project and reusable skeleton.
> It demonstrates core Agent patterns: ReAct loop, tool registry, validation,
> SSE execution trace, and pluggable business tools. For production, I would add
> authentication, rate limiting, persistent trace storage, prompt-injection defense,
> and observability. I documented all current limitations in `docs/limitations.md`."

### Q5: How would you adapt this for a different company?

> "Swap `src/tools/business/` and `src/agents/personas/`. Most adaptation stays within
> those two directories. For a customer support agent: replace job_matching tools with
> CRM lookup, ticket creation, knowledge base search. A minimal prototype takes ~30 minutes;
> production integration with real CRM/DB/APIs requires additional engineering."

## Test Coverage Map

| Module | Tests | Coverage Focus |
|--------|-------|---------------|
| Agent loop | 6 | Final answer, tool calls, unknown tools, iterations, retry |
| LLM client | 3 | Key check, retry, max retries |
| Tool registry | 5 | Register, execute, schema, describe, invalid args |
| Builtin tools | 5 | Schema validation, calculator, time |
| Builtin security | 12 | AST safety, eval blocking, path whitelist, dotdot, env |
| Job matching | 6 | JD analysis, resume match, gap report, study plan |
| Chat API | 6 | Health, tools list, agents list, chat, 503, mock LLM |
| **Total** | **44** | ruff clean, CI green |

## Quick Demo Commands

```bash
# Start server
uvicorn src.server.main:app --reload

# Health
curl http://localhost:8000/health

# List tools
curl http://localhost:8000/api/v1/tools

# Analyze a JD
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze: AI Agent intern, requires Python, LLM, FastAPI"}'

# Stream agent thinking
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Match my skills: Python, FastAPI, Docker"}'
```
