# Agent Evaluation

> How to assess whether the agent is working correctly.

## Current evaluation approach

This project uses **behavioral testing** — verifying specific agent behaviors through pytest,
not relying on LLM-as-judge or human scoring.

## What we test today

| Category | What we check | Test file |
|----------|-------------|-----------|
| Tool selection | Agent chooses correct tool for a task | `test_agent_loop.py` |
| Invalid tool rejection | Unknown tool names are rejected, not executed | `test_agent_loop.py` |
| Max iteration safety | Agent stops after reaching iteration limit | `test_agent_loop.py` |
| Duplicate call detection | Same tool + same args twice → agent stops | `test_agent_loop.py` |
| JSON parse resilience | Malformed LLM output → retry, not crash | `test_agent_loop.py` |
| Tool argument validation | Pydantic catches invalid args before execution | `test_tool_registry.py` |
| Security: AST calculator | Code injection blocked, valid math works | `test_builtin_security.py` |
| Security: file path whitelist | .env, absolute paths, .. traversal blocked | `test_builtin_security.py` |
| Job matching accuracy | Known JD → expected skills extracted | `test_job_matching_tools.py` |
| API error handling | 503 when key missing, 422 for invalid input | `test_chat_api.py` |

## How many tests pass?

44 tests. All pass on every push (GitHub Actions CI).

## What we can't fully test without real LLM calls

| Limitation | Current workaround |
|-----------|-------------------|
| LLM output quality varies by model | Mock LLM in tests for deterministic behavior |
| Tool selection accuracy depends on prompt quality | Test with controlled prompts, not open-ended |
| Multi-turn conversation coherence | Not yet systematically tested |
| RAG retrieval quality | ChromaDB is optional and not yet in eval suite |

## Future improvements

For a more rigorous evaluation:

1. **Golden dataset**: 10 JD/resume pairs with known expected match scores.
   Run the agent and compare output against ground truth.
2. **Tool selection accuracy benchmark**: 20 prompts where the correct tool is known.
   Measure how often the agent picks the right tool.
3. **Latency budget**: Track p50/p95/p99 latency for agent runs.
4. **LLM-as-judge**: Use a separate LLM call to score answer quality against rubrics.
   (Note: adds cost and is not deterministic.)
5. **Regression test suite**: Re-run the full test suite after any core change.

## Interview answer

> "I use behavioral testing — each safety control and tool has specific pytest cases.
> For LLM-dependent behavior, I mock the LLM to test the agent's decision logic
> deterministically. I know real evaluation would require a golden dataset and
> possibly LLM-as-judge, which I'd add if this were production-facing."
