"""SQL safety audit for read-only execution."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

FORBIDDEN = re.compile(r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|REPLACE|MERGE|CALL|EXEC)\b", re.I)


@dataclass
class SQLSafetyResult:
    """Safety audit result."""

    sql: str
    safety_passed: bool
    error_message: str | None = None


def ensure_limit(sql: str, default_limit: int = 100) -> str:
    """Append a LIMIT clause if a SELECT query lacks one."""

    stripped = sql.strip().rstrip(";")
    if re.search(r"\blimit\s+\d+\b", stripped, flags=re.I):
        return stripped
    return f"{stripped} LIMIT {default_limit}"


def referenced_tables(sql: str) -> set[str]:
    """Extract table names after FROM and JOIN."""

    return set(re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)", sql, flags=re.I))


def validate_select_sql(sql: str, allowed_tables: Iterable[str] | None = None) -> SQLSafetyResult:
    """Validate that SQL is a read-only SELECT using allowed tables."""

    cleaned = sql.strip().rstrip(";")
    if not re.match(r"^\s*(WITH\b.*?\bSELECT\b|SELECT\b)", cleaned, flags=re.I | re.S):
        return SQLSafetyResult(cleaned, False, "Only SELECT queries are allowed.")
    if FORBIDDEN.search(cleaned):
        return SQLSafetyResult(cleaned, False, "Forbidden SQL keyword detected.")
    tables = referenced_tables(cleaned)
    allowed = set(allowed_tables or [])
    if allowed and not tables.issubset(allowed):
        unknown = sorted(tables - allowed)
        return SQLSafetyResult(cleaned, False, f"SQL references tables outside schema graph: {unknown}")
    return SQLSafetyResult(cleaned, True)
