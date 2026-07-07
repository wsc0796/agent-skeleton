# Agent Skeleton Architecture

## Request Flow

```
Browser (React UI)                curl / Postman
       │                                │
       │  POST /api/v1/chat             │
       ▼                                ▼
┌──────────────────────────────────────────┐
│  FastAPI Server (src/server/)            │
│  ┌────────────┐  ┌───────────────────┐  │
│  │ REST /chat  │  │ SSE /chat/stream  │  │
│  └─────┬───────┘  └────────┬──────────┘  │
│        │                   │              │
│        ▼                   ▼              │
│  ┌──────────────────────────────────┐    │
│  │       AgentPersona               │    │
│  │  (system_prompt + tools + model) │    │
│  └──────────────┬───────────────────┘    │
│                 │                        │
│                 ▼                        │
│  ┌──────────────────────────────────┐    │
│  │       ReActAgent.run()           │    │
│  │  ┌──────────────────────────┐    │    │
│  │  │ 1. LLM returns structured│    │    │
│  │  │    action JSON           │    │    │
│  │  │ 2. "tool_call" → execute │    │    │
│  │  │ 3. Tool result → LLM     │    │    │
│  │  │ 4. "final" → answer      │    │    │
│  │  └──────────────────────────┘    │    │
│  └──────────────┬───────────────────┘    │
│                 │                        │
│                 ▼                        │
│  ┌──────────────────────────────────┐    │
│  │       ToolRegistry               │    │
│  │  ┌──────────┐ ┌───────────────┐  │    │
│  │  │ builtin  │ │   business    │  │    │
│  │  │ (6 tools)│ │ (4 job_match) │  │    │
│  │  └──────────┘ └───────────────┘  │    │
│  └──────────────────────────────────┘    │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │       Memory                     │    │
│  │  ┌────────────────┐ ┌─────────┐  │    │
│  │  │ ConvBuffer(20) │ │ChromaDB │  │    │
│  │  └────────────────┘ └─────────┘  │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
```

## Layer Responsibility

| Layer | Directory | Rule |
|-------|-----------|------|
| Core | `src/core/` | Stable reusable core; changes should be rare and reviewed |
| Tools | `src/tools/` | Most business adaptation should happen in tools/personas/examples |
| Agents | `src/agents/` | Most business adaptation should happen in tools/personas/examples |
| Server | `src/server/` | REST + SSE patterns |
| UI | `src/ui/` | Agent Chat interface |

## Agent Step Trace (SSE Events)

```
POST /api/v1/chat/stream {"message": "Analyze JD: Python, FastAPI"}
  │
  ├─ event: agent_started
  │    data: {"agent": "job_matcher"}
  │
  ├─ event: tool_call_started
  │    data: {"iteration": 1, "tool": "analyze_jd", "args": {...}}
  │
  ├─ event: tool_call_finished
  │    data: {"iteration": 1, "tool": "analyze_jd", "result_preview": "..."}
  │
  ├─ event: tool_call_started
  │    data: {"iteration": 2, "tool": "match_resume", "args": {...}}
  │
  ├─ event: tool_call_finished
  │    data: {"iteration": 2, "tool": "match_resume", "result_preview": "..."}
  │
  └─ event: final_answer
       data: {"answer": "75% match, missing: LLM, RAG", "tools_called": [...]}
```

## Customization Points

To adapt for a different company/role:

1. Write new tools in `src/tools/business/` (copy `job_matching/` as template)
2. Write a new persona in `src/agents/personas/` (copy `job_matcher.py`)
3. Register the persona in `src/server/routes/chat.py`
4. Add sample data in `examples/`
5. Most business adaptation should happen in tools/personas/examples
