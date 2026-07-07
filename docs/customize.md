# How to Add Business Tools

> Build a minimal business-tool prototype in ~30 minutes.
> Production integration with real CRM/DB/APIs requires additional engineering.

## Overview

Most business adaptation happens in two directories:

```text
src/tools/business/    ← swap in your tools
src/agents/personas/   ← swap in your agent config
```

`src/core/`, `src/server/`, `src/ui/` are designed as stable layers — most changes happen in `tools/` and `agents/`.

## Step 1: Define Your Tools

Create `src/tools/business/my_domain/tools.py`:

```python
from pydantic import BaseModel, Field
from src.core.tool_registry import ToolSpec

# 1. Define argument models
class MyToolArgs(BaseModel):
    input_field: str = Field(..., min_length=1)

# 2. Implement the function
def my_tool(input_field: str) -> dict:
    return {"result": f"Processed: {input_field}"}

# 3. Export as tool list
def tools() -> list[ToolSpec]:
    return [
        ToolSpec(
            name="my_tool",
            description="What this tool does — shown to the LLM.",
            args_model=MyToolArgs,
            function=my_tool,
            category="business",
        ),
    ]
```

## Step 2: Define Your Agent Persona

Create `src/agents/personas/my_agent.py`:

```python
from src.agents.base import AgentPersona
from src.core.tool_registry import ToolRegistry
from src.tools.business.my_domain.tools import tools as my_tools

SYSTEM_PROMPT = """You are a [ROLE]. Your mission: [WHAT YOU DO].
Respond in JSON with action_type: "tool_call" or "final"."""

def build_my_agent() -> AgentPersona:
    registry = ToolRegistry()
    for tool in my_tools():
        registry.register(tool)
    return AgentPersona(
        name="my_agent",
        description="[ONE-LINE DESCRIPTION]",
        system_prompt=SYSTEM_PROMPT,
        tools=registry,
    )
```

## Step 3: Register the Agent

In `src/server/routes/chat.py`, add your agent to `_get_agent()`:

```python
def _get_agent(agent_name: str) -> ReActAgent:
    if agent_name == "my_agent":
        persona = build_my_agent()
    else:
        persona = build_job_matcher()  # default
    # ... rest unchanged
```

## Step 4: Write Tests

Create `tests/test_my_tools.py`:

```python
from src.tools.business.my_domain.tools import my_tool

def test_my_tool_works():
    result = my_tool("test input")
    assert "result" in result
```

## Step 5: Add Sample Data

Create `examples/my_domain/sample_data/` with realistic test inputs.

## Example: Customer Support Agent

```text
src/tools/business/
└── customer_support/
    └── tools.py        ← lookup_ticket, create_ticket, search_kb, escalate

src/agents/personas/
└── support_agent.py    ← system_prompt: "You are a Tier 1 support agent..."

examples/
└── customer_support/
    └── sample_data/
        ├── sample_ticket.txt
        └── sample_kb_article.txt
```

**Time: ~30 minutes for a minimal prototype.**

## What this covers vs. what's missing

| Covered by this guide | Requires additional engineering |
|-----------------------|--------------------------------|
| New tool definitions | Real CRM/DB/API authentication |
| Agent persona config | Production error handling |
| Test scaffolding | Performance tuning |
| Server registration | Rate limiting & monitoring |
| Sample data | Data migration & persistence |

This guide produces a working prototype you can demo. Production integration
with company-specific systems requires additional work on auth, reliability,
and data integration.
