"""Built-in tools that ship with the agent skeleton. Replace or extend for business use."""

import json
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from src.core.tool_registry import ToolSpec


# ── Web Search ──────────────────────────────────────

class WebSearchArgs(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")


def web_search(query: str) -> dict:
    """Stub: replace with real search API (SerpAPI, Tavily, etc.)."""
    return {
        "query": query,
        "results": [],
        "hint": "Replace this with a real search API like Tavily or SerpAPI.",
    }


# ── Current Time ────────────────────────────────────

class GetCurrentTimeArgs(BaseModel):
    timezone_offset: str = Field(default="UTC", description="Timezone, e.g. 'Asia/Shanghai'")


def get_current_time(timezone_offset: str = "UTC") -> dict:
    return {
        "utc_time": datetime.now(timezone.utc).isoformat(),
        "timezone": timezone_offset,
    }


# ── Calculator ──────────────────────────────────────

class CalculatorArgs(BaseModel):
    expression: str = Field(..., min_length=1, description="Math expression, e.g. '2 + 3 * 4'")


def calculator(expression: str) -> dict:
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"expression": expression, "result": result}
    except Exception as exc:
        return {"expression": expression, "error": str(exc)}


# ── File Reader ─────────────────────────────────────

class ReadFileArgs(BaseModel):
    path: str = Field(..., min_length=1, description="Path to the file")
    max_chars: int = Field(default=5000, description="Max characters to read")


def read_file(path: str, max_chars: int = 5000) -> dict:
    try:
        content = open(path, encoding="utf-8").read()[:max_chars]
        return {"path": path, "chars_read": len(content), "content": content}
    except FileNotFoundError:
        return {"path": path, "error": "File not found"}
    except PermissionError:
        return {"path": path, "error": "Permission denied"}


# ── JSON Store (simple key-value) ───────────────────

class StoreJsonArgs(BaseModel):
    key: str = Field(..., min_length=1, description="Storage key")
    value: str = Field(..., description="Value to store")


class GetJsonArgs(BaseModel):
    key: str = Field(..., min_length=1, description="Storage key")


_store: dict[str, str] = {}


def store_json(key: str, value: str) -> dict:
    try:
        parsed = json.loads(value)
        _store[key] = json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        _store[key] = value
    return {"key": key, "stored": True}


def get_json(key: str) -> dict:
    value = _store.get(key)
    if value is None:
        return {"key": key, "found": False}
    try:
        return {"key": key, "found": True, "value": json.loads(value)}
    except json.JSONDecodeError:
        return {"key": key, "found": True, "value": value}


# ── Registry ────────────────────────────────────────

def builtin_tools() -> list[ToolSpec]:
    return [
        ToolSpec(
            name="web_search",
            description="Search the web for information. Returns search results.",
            args_model=WebSearchArgs,
            function=web_search,
            category="builtin",
        ),
        ToolSpec(
            name="get_current_time",
            description="Get the current time in a specified timezone.",
            args_model=GetCurrentTimeArgs,
            function=get_current_time,
            category="builtin",
        ),
        ToolSpec(
            name="calculator",
            description="Evaluate a mathematical expression. Use for calculations.",
            args_model=CalculatorArgs,
            function=calculator,
            category="builtin",
        ),
        ToolSpec(
            name="read_file",
            description="Read the contents of a file from disk.",
            args_model=ReadFileArgs,
            function=read_file,
            category="builtin",
        ),
        ToolSpec(
            name="store_json",
            description="Store a key-value pair in the agent's memory.",
            args_model=StoreJsonArgs,
            function=store_json,
            category="builtin",
        ),
        ToolSpec(
            name="get_json",
            description="Retrieve a stored value by key from the agent's memory.",
            args_model=GetJsonArgs,
            function=get_json,
            category="builtin",
        ),
    ]
