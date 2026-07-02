"""Hybrid schema retrieval with RRF fusion."""

from __future__ import annotations

from typing import Any, Dict, List

from dataspeak.retrieval.bm25_retriever import keyword_search
from dataspeak.retrieval.vector_retriever import vector_search
from dataspeak.schema_index.schema_store import load_schema_fields


def get_dynamic_top_k(keyword_count: int) -> int:
    """Return per-route Top-K based on keyword count."""

    if keyword_count <= 2:
        return 30
    if keyword_count <= 5:
        return 20
    return 10


def rrf_fusion(keyword_results: List[Dict[str, Any]], vector_results: List[Dict[str, Any]], rrf_k: int = 60) -> List[Dict[str, Any]]:
    """Fuse ranked keyword and vector results with Reciprocal Rank Fusion."""

    field_map: Dict[str, Dict[str, Any]] = {}
    for source_results in (keyword_results, vector_results):
        for item in source_results:
            field_id = item["field_id"]
            rank = item.get("rank", 999)
            if field_id not in field_map:
                field_map[field_id] = item.copy()
                field_map[field_id]["rrf_score"] = 0.0
                field_map[field_id]["match_sources"] = []
            field_map[field_id]["rrf_score"] += 1 / (rrf_k + rank)
            field_map[field_id]["match_sources"].append(item.get("source", "unknown"))
    return sorted(field_map.values(), key=lambda item: item["rrf_score"], reverse=True)


def hybrid_retrieve(query: str, keywords: List[str], final_top_k: int = 50) -> Dict[str, Any]:
    """Run keyword retrieval, vector retrieval, and RRF fusion."""

    fields = load_schema_fields()
    dynamic_top_k = get_dynamic_top_k(len(keywords))
    keyword_results: List[Dict[str, Any]] = []
    for keyword in keywords:
        keyword_results.extend(keyword_search(keyword, dynamic_top_k, fields))
    vector_results = vector_search(query, dynamic_top_k, fields)
    fused = rrf_fusion(keyword_results, vector_results)[:final_top_k]
    return {
        "keywords": keywords,
        "dynamic_top_k": dynamic_top_k,
        "keyword_result_count": len(keyword_results),
        "vector_result_count": len(vector_results),
        "final_result_count": len(fused),
        "results": fused,
    }
