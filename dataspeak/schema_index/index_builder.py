"""Build local schema index documents."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import List

from dataspeak.schema_index.schema_profiler import profile_column
from dataspeak.schema_index.schema_reader import read_sqlite_schema
from dataspeak.schema_index.schema_store import (
    COLUMN_DESCRIPTIONS,
    TABLE_DESCRIPTIONS,
    SchemaField,
    default_schema_fields,
    save_schema_fields,
)


def build_schema_index(db_path: str | Path | None = None, index_path: str | Path | None = None) -> Path:
    """Build a JSON schema index from SQLite or the built-in demo schema."""

    if db_path is None or not Path(db_path).exists():
        return save_schema_fields(default_schema_fields(), index_path)

    meta = read_sqlite_schema(db_path)
    fields: List[SchemaField] = []
    defaults = {field.field_id: field for field in default_schema_fields()}
    for col in meta:
        table = col["table_name"]
        name = col["column_name"]
        field_id = f"{table}.{name}"
        base = defaults.get(field_id)
        prof = profile_column(db_path, table, name)
        desc = COLUMN_DESCRIPTIONS.get(name, name)
        table_desc = TABLE_DESCRIPTIONS.get(table, f"{table} table")
        if base:
            fields.append(replace(base, column_type=col["column_type"], primary_key=col["primary_key"], **prof))
        else:
            fields.append(
                SchemaField(
                    field_id=field_id,
                    database_name="dataspeak_demo",
                    table_name=table,
                    table_description=table_desc,
                    column_name=name,
                    column_type=col["column_type"],
                    column_description=desc,
                    primary_key=col["primary_key"],
                    foreign_key=None,
                    keyword_text=f"{table} {name} {desc} {table_desc}",
                    vector_text=f"字段 {field_id} 表示{desc}，属于{table_desc}",
                    rerank_text=f"字段名：{name}；所属表：{table}；类型：{col['column_type']}；字段含义：{desc}；表说明：{table_desc}",
                    **prof,
                )
            )
    return save_schema_fields(fields, index_path)
