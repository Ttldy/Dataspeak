"""Build schema index from local demo database."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dataspeak.schema_index.index_builder import build_schema_index
from dataspeak.sql_agent.sql_executor import ensure_demo_sqlite


def main() -> None:
    """Script entrypoint."""

    db_path = ensure_demo_sqlite()
    index_path = build_schema_index(db_path)
    print(f"schema index built: {index_path}")


if __name__ == "__main__":
    main()
