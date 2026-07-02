from dataspeak.retrieval.hybrid_retriever import get_dynamic_top_k, rrf_fusion
from dataspeak.retrieval.retrieval_pipeline import retrieve_schema_context


def test_dynamic_top_k_rules():
    assert get_dynamic_top_k(2) == 30
    assert get_dynamic_top_k(4) == 20
    assert get_dynamic_top_k(6) == 10


def test_rrf_fusion_merges_sources():
    keyword_results = [{"field_id": "orders.total_amount", "rank": 1, "source": "keyword"}]
    vector_results = [{"field_id": "orders.total_amount", "rank": 3, "source": "vector"}]

    fused = rrf_fusion(keyword_results, vector_results)

    assert fused[0]["field_id"] == "orders.total_amount"
    assert set(fused[0]["match_sources"]) == {"keyword", "vector"}


def test_retrieve_schema_context_returns_schema_graph():
    result = retrieve_schema_context("统计每个城市的订单总金额")

    assert "customers" in result["schema_graph_text"]
    assert "orders" in result["schema_graph_text"]
    assert result["keywords"]
    assert result["rerank_results"]
