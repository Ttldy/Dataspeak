"""Schema graph construction and formatting."""

from __future__ import annotations

from typing import Any, Dict, List

from dataspeak.schema_index.schema_store import RELATIONS, TABLE_DESCRIPTIONS, load_schema_fields


def build_schema_graph(rerank_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build table-field-relation graph from reranked field results."""

    all_fields = {field.field_id: field for field in load_schema_fields()}
    selected_ids = {item["field_id"] for item in rerank_results}
    table_names = {item["table_name"] for item in rerank_results}
    expanded = [field for field in all_fields.values() if field.table_name in table_names and (field.field_id in selected_ids or field.primary_key or field.foreign_key)]
    relations = [
        {
            "source_table": src,
            "source_field": src_f,
            "target_table": dst,
            "target_field": dst_f,
            "relation_type": typ,
            "relation_description": desc,
        }
        for src, src_f, dst, dst_f, typ, desc in RELATIONS
        if src in table_names and dst in table_names
    ]
    return {
        "tables": [
            {"database_name": "dataspeak_demo", "table_name": table, "table_description": TABLE_DESCRIPTIONS.get(table, table)}
            for table in sorted(table_names)
        ],
        "fields": [field.__dict__ for field in expanded],
        "relations": relations,
    }


def format_schema_graph(schema_graph: Dict[str, Any]) -> str:
    """Format schema graph text for planning and SQL generation."""

    lines: List[str] = []
    by_table: Dict[str, List[Dict[str, Any]]] = {}
    for field in schema_graph["fields"]:
        by_table.setdefault(field["table_name"], []).append(field)
    table_desc = {table["table_name"]: table["table_description"] for table in schema_graph["tables"]}
    for table, fields in by_table.items():
        lines.append(f"表名：{table}")
        lines.append(f"表格摘要：{table_desc.get(table, '')}")
        for field in fields:
            lines.append(f"- 字段：{field['column_name']} | 类型：{field['column_type']} | 含义：{field['column_description']} | 样例值：{field['sample_values']}")
        lines.append("")
    lines.append("表关联关系：")
    if not schema_graph["relations"]:
        lines.append("无明确表关联关系")
    for rel in schema_graph["relations"]:
        lines.append(f"{rel['source_table']}.{rel['source_field']} ↔ {rel['target_table']}.{rel['target_field']}；{rel['relation_description']}")
    return "\n".join(lines)
