"""Small BM25-like keyword retriever."""

from __future__ import annotations

from typing import Dict, List

from dataspeak.schema_index.schema_store import SchemaField, load_schema_fields


SYNONYMS = {
    "订单总金额": ["total_amount", "line_amount", "paid_amount"],
    "总金额": ["total_amount", "line_amount", "paid_amount"],
    "订单金额": ["total_amount", "line_amount"],
    "城市": ["city"],
    "退款率": ["refund_amount", "refund_status", "order_id", "product_id"],
    "产品": ["product_id", "product_name", "category"],
    "客户等级": ["customer_level"],
    "客单价": ["total_amount", "customer_level"],
    "评分": ["rating"],
    "反馈": ["customer_feedback", "feedback_text"],
    "营销活动": ["marketing_events", "event_name", "event_date", "converted"],
    "支付": ["payments", "paid_amount", "payment_status"],
}


def keyword_search(keyword: str, top_k: int = 20, fields: List[SchemaField] | None = None) -> List[Dict]:
    """Search fields by keyword overlap and curated synonyms."""

    fields = fields or load_schema_fields()
    needles = [keyword, *SYNONYMS.get(keyword, [])]
    results = []
    for field in fields:
        text = field.keyword_text.lower()
        score = 0.0
        for needle in needles:
            n = str(needle).lower()
            if n in text or n == field.column_name.lower() or n == field.table_name.lower():
                score += 3.0 if n in (field.column_name.lower(), field.table_name.lower()) else 1.0
        if score:
            row = field.__dict__.copy()
            row.update({"rank": 0, "score": score, "source": "keyword"})
            results.append(row)
    results.sort(key=lambda item: item["score"], reverse=True)
    for rank, item in enumerate(results[:top_k], 1):
        item["rank"] = rank
    return results[:top_k]
