"""Deterministic fallback model."""

from __future__ import annotations


class FallbackChatModel:
    """A no-network model used for demos and tests."""

    def complete(self, prompt: str) -> str:
        """Return a compact deterministic answer."""

        return "DataSpeak fallback: 当前未配置可用大模型，已使用规则链路完成演示。"
