"""Schema metadata and local index storage."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

from dataspeak.config.settings import PROJECT_ROOT, settings


TABLE_DESCRIPTIONS = {
    "customers": "客户基础信息表，包含客户等级、城市、注册时间等画像字段。",
    "products": "产品信息表，包含产品品类、价格、成本和上架状态。",
    "orders": "订单主表，记录订单客户、时间、状态和订单总金额。",
    "order_items": "订单明细表，记录订单中每个产品的数量、单价和行金额。",
    "payments": "支付表，记录订单支付渠道、支付金额和支付状态。",
    "refunds": "退款表，记录订单明细退款金额、原因和退款状态。",
    "marketing_events": "营销活动触达表，记录客户参加活动、渠道和转化状态。",
    "customer_feedback": "客户反馈表，记录评分、反馈文本和关联订单。",
}

COLUMN_DESCRIPTIONS = {
    "customer_id": "客户唯一标识",
    "customer_name": "客户姓名",
    "city": "客户所在城市",
    "customer_level": "客户等级",
    "registered_at": "注册日期",
    "product_id": "产品唯一标识",
    "product_name": "产品名称",
    "category": "产品品类",
    "list_price": "标价",
    "unit_cost": "单位成本",
    "is_active": "是否上架",
    "order_id": "订单唯一标识",
    "order_date": "订单日期",
    "status": "订单状态",
    "total_amount": "订单总金额",
    "item_id": "订单明细唯一标识",
    "quantity": "购买数量",
    "unit_price": "成交单价",
    "line_amount": "明细成交金额",
    "payment_id": "支付唯一标识",
    "payment_method": "支付方式",
    "paid_amount": "支付金额",
    "payment_status": "支付状态",
    "refund_id": "退款唯一标识",
    "refund_amount": "退款金额",
    "refund_reason": "退款原因",
    "refund_status": "退款状态",
    "event_id": "营销活动唯一标识",
    "event_name": "营销活动名称",
    "channel": "营销渠道",
    "event_date": "营销触达日期",
    "converted": "是否转化",
    "feedback_id": "反馈唯一标识",
    "rating": "客户评分",
    "feedback_text": "反馈内容",
    "created_at": "创建时间",
}

RELATIONS = [
    ("orders", "customer_id", "customers", "customer_id", "many_to_one", "订单通过客户ID关联客户信息。"),
    ("order_items", "order_id", "orders", "order_id", "many_to_one", "订单明细通过订单ID关联订单主表。"),
    ("order_items", "product_id", "products", "product_id", "many_to_one", "订单明细通过产品ID关联产品信息。"),
    ("payments", "order_id", "orders", "order_id", "one_to_one", "支付记录通过订单ID关联订单。"),
    ("refunds", "item_id", "order_items", "item_id", "many_to_one", "退款通过订单明细ID关联具体产品。"),
    ("marketing_events", "customer_id", "customers", "customer_id", "many_to_one", "营销活动通过客户ID关联客户。"),
    ("customer_feedback", "customer_id", "customers", "customer_id", "many_to_one", "反馈通过客户ID关联客户。"),
    ("customer_feedback", "order_id", "orders", "order_id", "many_to_one", "反馈可通过订单ID关联订单金额。"),
]


@dataclass
class SchemaField:
    """Field-level schema document."""

    field_id: str
    database_name: str
    table_name: str
    table_description: str
    column_name: str
    column_type: str
    column_description: str
    primary_key: bool
    foreign_key: str | None
    sample_values: List[Any]
    min: Any | None
    max: Any | None
    avg: float | None
    null_ratio: float
    enum_distribution: Dict[str, int]
    keyword_text: str
    vector_text: str
    rerank_text: str


def default_schema_fields() -> List[SchemaField]:
    """Return built-in field documents used before a DB index is built."""

    cols = {
        "customers": [
            ("customer_id", "INTEGER", True, None, [1, 2, 3]),
            ("customer_name", "TEXT", False, None, ["Alice", "Bob"]),
            ("city", "TEXT", False, None, ["北京", "上海", "深圳"]),
            ("customer_level", "TEXT", False, None, ["gold", "silver"]),
            ("registered_at", "DATE", False, None, ["2026-01-01"]),
        ],
        "products": [
            ("product_id", "INTEGER", True, None, [1, 2, 3]),
            ("product_name", "TEXT", False, None, ["智能音箱", "AI会员"]),
            ("category", "TEXT", False, None, ["硬件", "订阅"]),
            ("list_price", "DECIMAL", False, None, [99.0, 299.0]),
            ("unit_cost", "DECIMAL", False, None, [35.0, 120.0]),
            ("is_active", "INTEGER", False, None, [1, 0]),
        ],
        "orders": [
            ("order_id", "INTEGER", True, None, [1001, 1002]),
            ("customer_id", "INTEGER", False, "customers.customer_id", [1, 2]),
            ("order_date", "DATE", False, None, ["2026-06-01"]),
            ("status", "TEXT", False, None, ["paid", "refunded"]),
            ("total_amount", "DECIMAL", False, None, [128.0, 799.0]),
        ],
        "order_items": [
            ("item_id", "INTEGER", True, None, [1, 2]),
            ("order_id", "INTEGER", False, "orders.order_id", [1001, 1002]),
            ("product_id", "INTEGER", False, "products.product_id", [1, 2]),
            ("quantity", "INTEGER", False, None, [1, 3]),
            ("unit_price", "DECIMAL", False, None, [99.0, 199.0]),
            ("line_amount", "DECIMAL", False, None, [99.0, 597.0]),
        ],
        "payments": [
            ("payment_id", "INTEGER", True, None, [1, 2]),
            ("order_id", "INTEGER", False, "orders.order_id", [1001, 1002]),
            ("payment_method", "TEXT", False, None, ["alipay", "card"]),
            ("paid_amount", "DECIMAL", False, None, [128.0, 799.0]),
            ("payment_status", "TEXT", False, None, ["success", "failed"]),
        ],
        "refunds": [
            ("refund_id", "INTEGER", True, None, [1, 2]),
            ("item_id", "INTEGER", False, "order_items.item_id", [1, 2]),
            ("refund_amount", "DECIMAL", False, None, [30.0, 199.0]),
            ("refund_reason", "TEXT", False, None, ["质量问题", "不喜欢"]),
            ("refund_status", "TEXT", False, None, ["approved", "rejected"]),
        ],
        "marketing_events": [
            ("event_id", "INTEGER", True, None, [1, 2]),
            ("customer_id", "INTEGER", False, "customers.customer_id", [1, 2]),
            ("event_name", "TEXT", False, None, ["618促销", "新品试用"]),
            ("channel", "TEXT", False, None, ["短信", "公众号"]),
            ("event_date", "DATE", False, None, ["2026-05-20"]),
            ("converted", "INTEGER", False, None, [0, 1]),
        ],
        "customer_feedback": [
            ("feedback_id", "INTEGER", True, None, [1, 2]),
            ("customer_id", "INTEGER", False, "customers.customer_id", [1, 2]),
            ("order_id", "INTEGER", False, "orders.order_id", [1001, 1002]),
            ("rating", "INTEGER", False, None, [2, 5]),
            ("feedback_text", "TEXT", False, None, ["物流慢", "体验好"]),
            ("created_at", "DATE", False, None, ["2026-06-10"]),
        ],
    }
    fields: List[SchemaField] = []
    for table, rows in cols.items():
        for name, typ, pk, fk, samples in rows:
            desc = COLUMN_DESCRIPTIONS.get(name, name)
            keyword_text = " ".join([table, name, desc, TABLE_DESCRIPTIONS[table], *map(str, samples)])
            vector_text = f"字段 {table}.{name} 表示{desc}，属于{TABLE_DESCRIPTIONS[table]}"
            rerank_text = f"字段名：{name}；所属表：{table}；类型：{typ}；字段含义：{desc}；样例值：{samples}；表说明：{TABLE_DESCRIPTIONS[table]}"
            fields.append(
                SchemaField(
                    field_id=f"{table}.{name}",
                    database_name="dataspeak_demo",
                    table_name=table,
                    table_description=TABLE_DESCRIPTIONS[table],
                    column_name=name,
                    column_type=typ,
                    column_description=desc,
                    primary_key=pk,
                    foreign_key=fk,
                    sample_values=samples,
                    min=None,
                    max=None,
                    avg=None,
                    null_ratio=0.0,
                    enum_distribution={str(s): 1 for s in samples if isinstance(s, str)},
                    keyword_text=keyword_text,
                    vector_text=vector_text,
                    rerank_text=rerank_text,
                )
            )
    return fields


def load_schema_fields(index_path: str | Path | None = None) -> List[SchemaField]:
    """Load field documents from JSON, falling back to built-in demo schema."""

    path = Path(index_path or settings.schema_index_path)
    if not path.exists():
        return default_schema_fields()
    data = json.loads(path.read_text(encoding="utf-8"))
    return [SchemaField(**item) for item in data["fields"]]


def save_schema_fields(fields: Iterable[SchemaField], index_path: str | Path | None = None) -> Path:
    """Persist schema fields as the local fallback index."""

    path = Path(index_path or settings.schema_index_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fields": [asdict(field) for field in fields],
        "relations": [
            {
                "source_table": src,
                "source_field": src_f,
                "target_table": dst,
                "target_field": dst_f,
                "relation_type": typ,
                "relation_description": desc,
            }
            for src, src_f, dst, dst_f, typ, desc in RELATIONS
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def project_sqlite_path() -> Path:
    """Return the demo SQLite DB path."""

    if settings.database_url.startswith("sqlite:///"):
        return Path(settings.database_url.removeprefix("sqlite:///"))
    return PROJECT_ROOT / "demo_data" / "dataspeak_demo.sqlite"
