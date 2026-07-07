"""FastAPI server for agent-skeleton — REST + SSE chat endpoints."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server.routes.admin import router as admin_router
from src.server.routes.chat import router as chat_router

app = FastAPI(
    title="Agent Skeleton API",
    description="Reusable Agent project — FastAPI + SSE chat with tool-calling agents.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
