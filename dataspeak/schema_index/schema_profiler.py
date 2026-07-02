"""Profile sample values and distributions for schema columns."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict


def profile_column(db_path: str | Path, table: str, column: str) -> Dict[str, Any]:
    """Compute lightweight profiling stats for a single column."""

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        total = conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"] or 0
        nulls = conn.execute(f"SELECT COUNT(*) AS n FROM {table} WHERE {column} IS NULL").fetchone()["n"] or 0
        samples = [row[0] for row in conn.execute(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL LIMIT 5")]
        stats = conn.execute(f"SELECT MIN({column}), MAX({column}), AVG({column}) FROM {table}").fetchone()
        enum_rows = conn.execute(
            f"SELECT {column}, COUNT(*) AS n FROM {table} WHERE {column} IS NOT NULL GROUP BY {column} ORDER BY n DESC LIMIT 10"
        ).fetchall()
        return {
            "sample_values": samples,
            "min": stats[0],
            "max": stats[1],
            "avg": stats[2] if isinstance(stats[2], (int, float)) else None,
            "null_ratio": nulls / total if total else 0.0,
            "enum_distribution": {str(row[0]): row["n"] for row in enum_rows},
        }
    except sqlite3.OperationalError:
        return {"sample_values": [], "min": None, "max": None, "avg": None, "null_ratio": 0.0, "enum_distribution": {}}
    finally:
        conn.close()
