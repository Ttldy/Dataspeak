"""Long-term memory with local vector-like retrieval."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Dict, List


class LongTermMemory:
    """User-controlled long-term memory store."""

    def __init__(self) -> None:
        self.items: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def save(self, user_id: str, text: str, metadata: Dict[str, Any] | None = None) -> None:
        """Save a summary or preference, stripping raw row payloads by default."""

        clean_meta = {k: v for k, v in (metadata or {}).items() if k != "raw_rows"}
        self.items[user_id].append({"text": text, "metadata": clean_meta})

    def search(self, user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories by token overlap."""

        q_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
        scored = []
        for item in self.items.get(user_id, []):
            terms = set(re.findall(r"[\w\u4e00-\u9fff]+", item["text"].lower()))
            score = len(q_terms & terms)
            if score or any(ch in item["text"] for ch in query):
                row = item.copy()
                row["score"] = score
                scored.append(row)
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]


long_term_memory = LongTermMemory()
