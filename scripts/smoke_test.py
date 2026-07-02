"""Smoke test for DataSpeak full LangGraph pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dataspeak.graph.workflow import run_dataspeak_graph


def main() -> None:
    """Run a representative Text2SQL query without requiring a server."""

    result = run_dataspeak_graph("统计最近30天每个城市的订单总金额，并按金额降序排列")
    summary = {
        "success": result["success"],
        "workflow": "langgraph",
        "route": result["route"]["route"],
        "sql": result["logs"]["sql_list"][0]["sql"],
        "row_count": result["logs"]["execution_results"][0]["row_count"],
        "final_answer": result["final_answer"],
        "trace_nodes": [item["node"] for item in result["trace"]],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not result["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
