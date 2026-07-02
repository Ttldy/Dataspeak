"""Full schema retrieval pipeline."""

from __future__ import annotations

from typing import Any, Dict

from dataspeak.retrieval.hybrid_retriever import hybrid_retrieve
from dataspeak.retrieval.keyword_extractor import extract_keywords
from dataspeak.retrieval.reranker import rerank_by_model
from dataspeak.retrieval.schema_graph import build_schema_graph, format_schema_graph


def retrieve_schema_context(query: str) -> Dict[str, Any]:
    """Retrieve schema candidates and build a schema graph."""

    keywords = extract_keywords(query)
    hybrid_result = hybrid_retrieve(query=query, keywords=keywords, final_top_k=50)
    rerank_results = rerank_by_model(query=query, candidates=hybrid_result["results"], top_k=20)
    schema_graph = build_schema_graph(rerank_results)
    return {
        "query": query,
        "keywords": keywords,
        "dynamic_top_k": hybrid_result["dynamic_top_k"],
        "candidates": hybrid_result["results"],
        "rerank_results": rerank_results,
        "schema_graph": schema_graph,
        "schema_graph_text": format_schema_graph(schema_graph),
    }
