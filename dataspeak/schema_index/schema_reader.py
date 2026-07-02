"""Read schema metadata from SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List


def read_sqlite_schema(db_path: str | Path) -> List[Dict[str, Any]]:
    """Read table and column metadata from a SQLite database."""

    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(f"SQLite database not found: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        tables = [
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        ]
        rows: List[Dict[str, Any]] = []
        for table in tables:
            for col in conn.execute(f"PRAGMA table_info({table})"):
                rows.append(
                    {
                        "table_name": table,
                        "column_name": col["name"],
                        "column_type": col["type"],
                        "primary_key": bool(col["pk"]),
                    }
                )
        return rows
    finally:
        conn.close()
