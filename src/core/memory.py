import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import chromadb

logger = logging.getLogger(__name__)


@dataclass
class MemoryConfig:
    persist_dir: str = "./data/chroma"
    collection_name: str = "agent_memory"
    max_recent_messages: int = 20


@dataclass
class ConversationMemory:
    """Sliding-window conversation buffer. Keeps the last N messages."""

    messages: list[dict] = field(default_factory=list)
    max_messages: int = 20

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def add_user(self, content: str) -> None:
        self.add("user", content)

    def add_assistant(self, content: str) -> None:
        self.add("assistant", content)

    def add_tool_result(self, tool_name: str, result: Any) -> None:
        self.add("tool", json.dumps({"tool": tool_name, "result": result}, default=str))

    def as_list(self) -> list[dict]:
        return list(self.messages)

    def clear(self) -> None:
        self.messages.clear()


@dataclass
class LongTermMemory:
    """ChromaDB-backed vector memory for persistent knowledge storage."""

    config: MemoryConfig = field(default_factory=MemoryConfig)
    _collection: Any = None

    def _get_collection(self):
        if self._collection is not None:
            return self._collection

        Path(self.config.persist_dir).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=self.config.persist_dir)
        self._collection = client.get_or_create_collection(
            name=self.config.collection_name
        )
        return self._collection

    def remember(self, text: str, metadata: dict | None = None) -> str:
        """Store a piece of knowledge. Returns the document ID."""
        collection = self._get_collection()
        doc_id = f"mem_{collection.count() + 1}"
        collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[doc_id],
        )
        logger.debug("Stored memory %s: %s", doc_id, text[:80])
        return doc_id

    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant memories."""
        try:
            collection = self._get_collection()
            if collection.count() == 0:
                return []
            results = collection.query(query_texts=[query], n_results=top_k)
            memories: list[dict] = []
            for i, doc_id in enumerate(results.get("ids", [[]])[0]):
                memories.append({
                    "id": doc_id,
                    "text": results.get("documents", [[]])[0][i] if results.get("documents") else "",
                    "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                })
            return memories
        except Exception as exc:
            logger.warning("Memory recall failed: %s", exc)
            return []

    def forget(self, doc_id: str) -> bool:
        """Delete a specific memory."""
        try:
            self._get_collection().delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def clear_all(self) -> None:
        """Delete all memories."""
        try:
            client = chromadb.PersistentClient(path=self.config.persist_dir)
            client.delete_collection(name=self.config.collection_name)
            self._collection = None
        except Exception:
            pass
