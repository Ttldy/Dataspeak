"""Generate auditable structured plans without exposing hidden reasoning."""

from __future__ import annotations

from typing import Any, Dict, List


def generate_plan(query: str, schema_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate a JSON plan consumed by SQL generation."""

    fields = [f"{field['table_name']}.{field['column_name']}" for field in schema_graph.get("fields", [])]
    lower = query.lower()
    instruction = "根据用户问题从候选表中筛选、关联、聚合并排序，输出可审计结果。"
    if "退款率" in query:
        instruction = "先关联订单明细、产品和退款记录；再按产品分组计算退款笔数/订单明细笔数作为退款率；最后按退款率降序取前N。"
    elif "营销" in query and ("没有下单" in query or "未下单" in query):
        instruction = "先筛选参加营销活动的客户；再排除近60天有订单的客户；最后输出客户信息与活动信息。"
    elif "客户等级" in query or "客单价" in query:
        instruction = "先关联客户与订单；再按客户等级分组；然后计算平均订单金额作为平均客单价。"
    elif "评分" in query and "平均值" in query:
        instruction = "先计算订单平均金额；再关联反馈与订单；最后筛选低评分且订单金额高于平均值的反馈。"
    elif "城市" in query:
        instruction = "先关联客户和订单；再按城市分组统计订单总金额；最后按金额降序排序。"
    return [
        {
            "step": 1,
            "database": "dataspeak_demo",
            "objects": fields,
            "instruction": instruction,
            "output": _infer_output(query),
        }
    ]


def _infer_output(query: str) -> str:
    if "城市" in query:
        return "city, order_total_amount"
    if "退款率" in query:
        return "product_name, order_item_count, refund_count, refund_rate"
    if "营销" in query:
        return "customer_id, customer_name, city, event_name"
    if "客户等级" in query or "客单价" in query:
        return "customer_level, avg_order_value"
    if "评分" in query:
        return "feedback_id, customer_id, order_id, rating, total_amount, feedback_text"
    return "query_result"
