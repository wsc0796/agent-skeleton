# Platform Mapping

> How concepts in agent-skeleton map to popular Agent platforms.
> This shows understanding of the underlying abstractions, not competition.

## Concept mapping

| agent-skeleton | Dify | n8n AI Agent | LangChain/LangGraph |
|---------------|------|-------------|-------------------|
| `AgentPersona` | Agent node config | AI Agent node | `AgentExecutor` / `create_react_agent` |
| `ToolRegistry` | Tools panel | Tools / HTTP Request nodes | `@tool` decorator / `StructuredTool` |
| `ReActAgent.run()` | Workflow execution | Node execution | Agent loop (`agent.invoke()`) |
| `AgentStep` (SSE trace) | Run history / logs | Execution history | Callbacks / LangSmith traces |
| `src/tools/business/` | Custom tools / API tools | Custom nodes / Function nodes | Custom tools |
| `src/agents/personas/` | Agent templates | Workflow templates | Agent configurations |
| `LLMClient` | Model provider settings | AI Agent model config | `ChatOpenAI` / `ChatDeepSeek` |
| `Memory` | Conversation variables | Workflow data / $json | `BaseChatMemory` / `RunnableWithMessageHistory` |

## What each platform is best for

| Platform | Best for |
|----------|---------|
| **agent-skeleton** | Learning Agent internals; interview portfolio; quick business-tool prototypes |
| **Dify** | Visual agentic workflow building; RAG pipelines; non-developer users |
| **n8n** | Automation workflows connecting many services; AI Agent as one node in a larger flow |
| **LangChain / LangGraph** | Production Python agent systems with ecosystem support (tracing, evals, hub) |

## Why I started with a hand-written version

1. **Understand the internals**: Before using a framework, I wanted to know
   exactly how a ReAct loop works — the JSON parsing, tool dispatch, result
   injection, and iteration control.
2. **Debug control**: With my own loop, I can log every step and see exactly
   where a tool call fails, rather than digging through framework traces.
3. **No dependency lock-in**: My core abstractions (AgentPersona, ToolRegistry,
   ReActAgent) can be adapted to run on LangChain or Spring AI if needed.
4. **Interview readiness**: I can explain ReAct from scratch, not just "I called
   `agent.run()`".

## When I would use a platform instead

- **Dify/n8n**: When a non-technical stakeholder needs to build or modify agent
  workflows without writing code.
- **LangChain**: When I need production features (LangSmith tracing, LangGraph
  state management, built-in tool integrations) that would take too long to
  build from scratch.
- **Spring AI**: When working in a Java/Spring Boot ecosystem where the rest of
  the stack expects Spring-based AI components.
