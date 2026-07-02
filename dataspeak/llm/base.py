"""Common LLM adapter interfaces."""

from __future__ import annotations

from typing import Protocol


class ChatModel(Protocol):
    """Minimal chat model protocol."""

    def complete(self, prompt: str) -> str:
        """Return model text for a prompt."""
