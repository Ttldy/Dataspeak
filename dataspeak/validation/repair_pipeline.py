"""Closed-loop Text2SQL pipeline with callback repair."""

from __future__ import annotations

from typing import Any, Dict, List

from dataspeak.config.settings import settings
from dataspeak.planning.plan_generator import generate_plan
from dataspeak.retrieval.retrieval_pipeline import retrieve_schema_context
from dataspeak.sql_agent.sql_executor import execute_sql_steps
from dataspeak.sql_agent.sql_generator import generate_sql_list
from dataspeak.validation.result_validator import validate_execution_result


def run_full_pipeline_once(query: str, memory: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Run retrieval, planning, SQL generation, and execution once."""

    memory = memory or {}
    schema_context = memory.get("schema_context") or retrieve_schema_context(query)
    plan = memory.get("plan") or generate_plan(query, schema_context["schema_graph"])
    sql_list = memory.get("sql_list") or generate_sql_list(query, plan, schema_context["schema_graph"])
    execution_results = memory.get("execution_results") or execute_sql_steps(sql_list)
    return {
        "query": query,
        "schema_context": schema_context,
        "plan": plan,
        "sql_list": sql_list,
        "execution_results": execution_results,
    }


def reset_memory_by_callback_module(memory: Dict[str, Any], callback_module: str) -> Dict[str, Any]:
    """Reset downstream stages based on a validator callback module."""

    new_memory = memory.copy()
    if callback_module == "schema_retrieval":
        for key in ("schema_context", "plan", "sql_list", "execution_results"):
            new_memory.pop(key, None)
    elif callback_module == "cot_generation":
        for key in ("plan", "sql_list", "execution_results"):
            new_memory.pop(key, None)
    elif callback_module == "sql_generation":
        for key in ("sql_list", "execution_results"):
            new_memory.pop(key, None)
    elif callback_module == "sql_execution":
        new_memory.pop("execution_results", None)
    else:
        new_memory.clear()
    return new_memory


def run_pipeline_with_validation(query: str, max_repair_rounds: int | None = None) -> Dict[str, Any]:
    """Run the LangGraph workflow while preserving the legacy response shape."""

    from dataspeak.graph.workflow import run_dataspeak_graph

    max_rounds = settings.max_repair_rounds if max_repair_rounds is None else max_repair_rounds
    result = run_dataspeak_graph(query=query, max_repair_rounds=max_rounds)
    result.setdefault("round", result.get("repair_round", 0))
    return result
