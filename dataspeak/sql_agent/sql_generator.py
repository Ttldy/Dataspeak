"""SQL generation with local rule fallback."""

from __future__ import annotations

from typing import Any, Dict, List

from dataspeak.config.settings import settings
from dataspeak.sql_agent.sql_safety import ensure_limit, validate_select_sql


def generate_sql_list(query: str, plan: List[Dict[str, Any]], schema_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate SQL for each structured plan step."""

    allowed_tables = {table["table_name"] for table in schema_graph.get("tables", [])}
    sql = _rule_sql(query)
    sql = ensure_limit(sql, settings.default_sql_limit)
    safety = validate_select_sql(sql, allowed_tables=allowed_tables or None)
    return [
        {
            "step": step["step"],
            "database": step["database"],
            "sql": safety.sql,
            "safety_passed": safety.safety_passed,
            "error_message": safety.error_message,
            "plan_step": step,
        }
        for step in plan
    ]


def _rule_sql(query: str) -> str:
    """Generate deterministic SQL for the built-in commerce dataset."""

    if "退款率" in query:
        return """
        SELECT p.product_name,
               COUNT(DISTINCT oi.item_id) AS order_item_count,
               COUNT(DISTINCT r.refund_id) AS refund_count,
               ROUND(COUNT(DISTINCT r.refund_id) * 1.0 / NULLIF(COUNT(DISTINCT oi.item_id), 0), 4) AS refund_rate
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN refunds r ON oi.item_id = r.item_id AND r.refund_status = 'approved'
        GROUP BY p.product_id, p.product_name
        ORDER BY refund_rate DESC, order_item_count DESC
        LIMIT 5
        """
    if "营销" in query and ("没有下单" in query or "未下单" in query):
        return """
        SELECT DISTINCT c.customer_id, c.customer_name, c.city, me.event_name, me.event_date
        FROM marketing_events me
        JOIN customers c ON me.customer_id = c.customer_id
        WHERE NOT EXISTS (
            SELECT 1 FROM orders o
            WHERE o.customer_id = c.customer_id
              AND o.order_date >= date('now', '-60 day')
        )
        ORDER BY me.event_date DESC
        """
    if "客户等级" in query or "客单价" in query:
        return """
        SELECT c.customer_level,
               ROUND(AVG(o.total_amount), 2) AS avg_order_value,
               COUNT(o.order_id) AS order_count
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status IN ('paid', 'completed', 'refunded')
        GROUP BY c.customer_level
        ORDER BY avg_order_value DESC
        """
    if "评分" in query and ("平均值" in query or "平均" in query):
        return """
        SELECT f.feedback_id, c.customer_name, f.order_id, f.rating, o.total_amount, f.feedback_text
        FROM customer_feedback f
        JOIN orders o ON f.order_id = o.order_id
        JOIN customers c ON f.customer_id = c.customer_id
        WHERE f.rating < 3
          AND o.total_amount > (SELECT AVG(total_amount) FROM orders)
        ORDER BY o.total_amount DESC
        """
    if "城市" in query:
        return """
        SELECT c.city,
               ROUND(SUM(o.total_amount), 2) AS order_total_amount,
               COUNT(o.order_id) AS order_count
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_date >= date('now', '-30 day')
        GROUP BY c.city
        ORDER BY order_total_amount DESC
        """
    if "产品" in query:
        return """
        SELECT p.product_name, p.category, SUM(oi.quantity) AS sold_quantity, ROUND(SUM(oi.line_amount), 2) AS sales_amount
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY sales_amount DESC
        """
    return "SELECT order_id, customer_id, order_date, status, total_amount FROM orders ORDER BY order_date DESC"
