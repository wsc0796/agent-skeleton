"""Chat endpoints: synchronous and SSE streaming."""

import json
import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from src.agents.personas.job_matcher import build_job_matcher
from src.core.agent_loop import AgentConfig, ReActAgent
from src.core.config import LLMNotConfiguredError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    agent_name: str = Field(default="job_matcher")


class ChatResponse(BaseModel):
    agent_name: str
    answer: str
    steps: list[dict]
    iterations: int
    tools_called: list[str]
    total_latency_ms: int


def _get_agent(agent_name: str) -> ReActAgent:
    persona = build_job_matcher()
    return ReActAgent(
        AgentConfig(
            system_prompt=persona.system_prompt,
            tools=persona.tools,
            max_iterations=persona.max_iterations,
            llm_client=persona.llm_client,
            name=persona.name,
        )
    )


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    try:
        agent = _get_agent(body.agent_name)
    except LLMNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "LLM_NOT_CONFIGURED",
                "message": "LLM_API_KEY is not configured. CRUD and tools still work without a key.",
            },
        )

    try:
        result = agent.run(body.message)
    except Exception as exc:
        logger.error("Agent error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Agent encountered an error processing your request.",
        )

    return ChatResponse(
        agent_name=body.agent_name,
        answer=result.answer,
        steps=[
            {
                "iteration": s.iteration,
                "thought": s.thought,
                "tool_name": s.tool_name,
                "tool_args": s.tool_args,
                "tool_result": str(s.tool_result)[:500] if s.tool_result else None,
                "is_final": s.is_final,
            }
            for s in result.steps
        ],
        iterations=result.iterations,
        tools_called=result.tools_called,
        total_latency_ms=result.total_latency_ms,
    )


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    try:
        agent = _get_agent(body.agent_name)
    except LLMNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "LLM_NOT_CONFIGURED", "message": "LLM_API_KEY is not configured."},
        )

    async def event_generator():
        yield {"event": "agent_started", "data": json.dumps({"agent": body.agent_name})}

        try:
            result = agent.run(body.message)

            for step in result.steps:
                if step.tool_name:
                    yield {
                        "event": "tool_call_started",
                        "data": json.dumps({
                            "iteration": step.iteration,
                            "tool": step.tool_name,
                            "args": step.tool_args,
                        }),
                    }
                    yield {
                        "event": "tool_call_finished",
                        "data": json.dumps({
                            "iteration": step.iteration,
                            "tool": step.tool_name,
                            "result_preview": str(step.tool_result)[:300] if step.tool_result else None,
                        }),
                    }
                if step.is_final:
                    yield {
                        "event": "final_answer",
                        "data": json.dumps({
                            "answer": result.answer,
                            "iterations": result.iterations,
                            "tools_called": result.tools_called,
                            "latency_ms": result.total_latency_ms,
                        }),
                    }
        except Exception as exc:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(exc)}),
            }

    return EventSourceResponse(event_generator())
