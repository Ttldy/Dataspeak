"""Conditional edges for the DataSpeak LangGraph workflow."""

from __future__ import annotations

from dataspeak.graph.state import DataSpeakGraphState


def route_edge(state: DataSpeakGraphState) -> str:
    """Route Text2SQL requests to retrieval, all others to QA."""

    if state.get("route", {}).get("route") == "text2sql":
        return "retrieve_schema"
    return "qa_answer"


def validation_edge(state: DataSpeakGraphState) -> str:
    """Choose final answer or repair based on validation status."""

    if state.get("validation_result", {}).get("success"):
        return "final_answer"
    if state.get("repair_round", 0) >= state.get("max_repair_rounds", 3):
        return "final_answer"
    return "repair_router"


def repair_edge(state: DataSpeakGraphState) -> str:
    """Route repair back to the earliest stage that must be recomputed."""

    callback_module = state.get("validation_result", {}).get("callback_module", "")
    if callback_module == "schema_retrieval":
        return "retrieve_schema"
    if callback_module in {"cot_generation", "plan_generation"}:
        return "generate_plan"
    if callback_module == "sql_generation":
        return "generate_sql"
    if callback_module == "sql_execution":
        return "execute_sql"
    return "retrieve_schema"
