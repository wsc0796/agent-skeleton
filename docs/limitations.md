# Limitations

> Honest boundaries. This project is an internship portfolio piece, not a production framework.

## What this project IS

- A readable, testable Agent skeleton for learning and interview discussion
- A demonstration of ReAct loop, tool registry, Pydantic validation, and SSE execution trace
- A template for quickly prototyping business-tool agents

## What this project is NOT

- Production-ready
- A framework competing with LangChain, Dify, or n8n
- Secure against all prompt injection or adversarial inputs
- Multi-tenant or authenticated
- Performance-optimized for high concurrency

## Current limitations

| Area | Limitation |
|------|-----------|
| Authentication | None. No user login, no API keys for endpoints. |
| Authorization | None. Any caller can invoke any tool. |
| Rate limiting | None. AI endpoints have no request caps. |
| Persistent storage | Conversation memory is in-process. ChromaDB integration is optional and demo-level. |
| Prompt injection | Basic tool whitelist and Pydantic validation, but no dedicated prompt-injection defense. |
| Multi-agent | Not implemented. Single ReAct agent only. |
| Observability | Basic logging. No structured trace storage or monitoring dashboard. |
| Concurrency | SQLite would need migration to PostgreSQL for multi-user scenarios. |
| Business tools | Job matching tools are rule-based examples. Real CRM/DB/API integration requires additional engineering. |

## What I would add for production

If evolving toward production:

1. Authentication (OAuth2 / API keys)
2. Rate limiting on AI endpoints
3. Persistent execution trace storage (PostgreSQL)
4. Structured logging + metrics (Prometheus)
5. Prompt-injection defense layer
6. Tool permission model (read-only vs. side-effect tools)
7. Agent evaluation harness (scoring tool selection accuracy)
8. CI/CD pipeline with integration tests against real LLM

## Interview answer

> "This is a learning project that shows I understand Agent internals:
> ReAct loop, tool validation, execution tracing, and safety controls.
> I know what it would take to productionize it — auth, rate limiting,
> trace persistence, and prompt-injection defense — which is why I
> explicitly document the boundaries."
