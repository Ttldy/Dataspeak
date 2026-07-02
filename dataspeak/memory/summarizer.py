"""Summary helpers."""

from __future__ import annotations


def summarize_text(text: str, max_chars: int = 500) -> str:
    """Compress text by keeping a bounded prefix for local demos."""

    text = " ".join(text.split())
    return text[:max_chars]
