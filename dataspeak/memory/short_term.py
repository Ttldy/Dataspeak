"""Short-term sliding window memory with summary compression."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Deque, Dict


class ShortTermMemory:
    """Session-local sliding window memory."""

    def __init__(self, window_size: int = 6) -> None:
        self.window_size = window_size
        self.windows: Dict[str, Deque[Dict[str, Any]]] = defaultdict(deque)
        self.summaries: Dict[str, str] = defaultdict(str)

    def add_turn(self, session_id: str, user_query: str, assistant_answer: str, metadata: Dict[str, Any] | None = None) -> None:
        """Add a turn and compress overflow into a summary."""

        window = self.windows[session_id]
        window.append({"user": user_query, "assistant": assistant_answer, "metadata": metadata or {}})
        while len(window) > self.window_size:
            old = window.popleft()
            self.summaries[session_id] = (self.summaries[session_id] + f"\n用户：{old['user']}；回答摘要：{old['assistant']}").strip()

    def get_context(self, session_id: str) -> Dict[str, str]:
        """Return summary plus recent window text."""

        window_text = "\n".join(f"用户：{turn['user']}\n助手：{turn['assistant']}" for turn in self.windows[session_id])
        return {"summary": self.summaries[session_id], "window_text": window_text}


short_term_memory = ShortTermMemory()
