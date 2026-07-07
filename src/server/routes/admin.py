"""Admin endpoints: list available tools and agents."""

from fastapi import APIRouter

from src.agents.personas.job_matcher import build_job_matcher
from src.tools.builtin import builtin_tools
from src.tools.business.job_matching.tools import tools as jm_tools

router = APIRouter(tags=["admin"])


@router.get("/tools")
def list_tools() -> dict:
    all_tools: list[dict] = []
    for tool in builtin_tools() + jm_tools():
        all_tools.append({
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
        })
    return {"tools": all_tools}


@router.get("/agents")
def list_agents() -> dict:
    agent = build_job_matcher()
    return {
        "agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "tool_count": len(agent.tools.list_names()),
                "tools": agent.tools.list_names(),
            }
        ]
    }
