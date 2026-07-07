# Security

> Safety controls built into the Agent Skeleton.

## Tool-level controls

### Tool whitelist

Only registered tools can be called. Unknown tool names are rejected.
See `src/core/agent_loop.py` — the agent checks `self.config.tools.get(tool_name)` before executing.

### Pydantic argument validation

All tool arguments are validated by Pydantic models before execution.
Invalid types, missing required fields, or constraint violations are caught before the tool runs.
See `src/core/tool_registry.py`.

### Duplicate call detection

If the same tool is called with identical arguments twice, the agent stops.
This prevents infinite loops from LLM hallucination.
See `src/core/agent_loop.py` — `call_history` tracking.

### Max iteration cap

Default 8 iterations. Configurable per agent.
See `src/core/agent_loop.py` — `self.config.max_iterations`.

## Implementation-level controls

### Safe calculator (AST parser)

The `calculator` tool uses Python's `ast` module to parse expressions, not `eval()`.
Code injection attempts (`__import__`, `open()`, function calls) are rejected as syntax errors.
See `src/tools/builtin/__init__.py` — `_safe_calc()`.

### File path whitelist

The `read_file` tool blocks:
- Absolute paths (Unix `/etc/passwd`, Windows `C:\...`)
- Path traversal (`../secret.txt`)
- Sensitive filenames (`.env`, `.gitignore`, `.gitconfig`)

See `src/tools/builtin/__init__.py` — `_is_safe_path()`.

### No shell execution

Tools cannot execute shell commands. The `calculator` tool specifically blocks `__import__` and function calls through AST whitelist (only `Constant`, `BinOp`, `UnaryOp` nodes allowed).

### No arbitrary HTTP by default

The builtin `web_search` tool is a stub. It returns a static hint to replace with a real API.
Real HTTP tools should be added in `tools/business/` with explicit URL whitelists.

## What is NOT yet defended

| Threat | Current status |
|--------|---------------|
| Prompt injection (user message manipulates agent) | Basic: tool whitelist + Pydantic. Not comprehensive. |
| Prompt injection (JD text contains hidden instructions) | Not defended. JD text is passed as-is to LLM. |
| LLM API key exposure | Key in `.env`, gitignored. No server-side secret management. |
| Memory poisoning (attacker fills conversation buffer) | Conversation buffer is per-session and in-process only. |

## Test coverage

Security controls are tested in:
- `tests/test_builtin_security.py` — 12 tests (AST safety, eval blocking, path whitelist)
- `tests/test_agent_loop.py` — unknown tool rejection, max iterations, duplicate detection
