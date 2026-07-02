"""Rerank candidates with query-document lexical signals."""

from __future__ import annotations

from typing import Any, Dict, List


def rerank_by_model(query: str, candidates: List[Dict[str, Any]], top_k: int = 20) -> List[Dict[str, Any]]:
    """Rerank candidates; acts as local fallback when CrossEncoder is absent."""

    query_chars = set(query.lower())
    ranked = []
    for item in candidates:
        text = (item.get("rerank_text") or item.get("keyword_text") or "").lower()
        lexical = sum(1 for ch in query_chars if ch in text) / max(len(query_chars), 1)
        score = item.get("rrf_score", 0.0) * 10 + lexical
        row = item.copy()
        row["rerank_score"] = round(score, 6)
        ranked.append(row)
    ranked.sort(key=lambda item: item["rerank_score"], reverse=True)
    for rank, item in enumerate(ranked[:top_k], 1):
        item["rank"] = rank
    return ranked[:top_k]
