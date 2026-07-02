"""Build combined memory context."""

from __future__ import annotations

from dataspeak.memory.long_term import long_term_memory
from dataspeak.memory.short_term import short_term_memory


def build_memory_context(session_id: str, user_id: str, query: str, use_long_term_memory: bool = False) -> dict:
    """Return short-term and optional long-term memory context."""

    short = short_term_memory.get_context(session_id)
    long = long_term_memory.search(user_id, query) if use_long_term_memory else []
    return {"short_term": short, "long_term": long}
