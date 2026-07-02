"""Typed state carried through the DataSpeak LangGraph workflow."""

from __future__ import annotations

from typing import Any, Dict, List, NotRequired, TypedDict


class DataSpeakGraphState(TypedDict):
    """Shared Agent state for Router, Text2SQL, QA and repair nodes."""

    query: str
    session_id: str
    user_id: str
    use_long_term_memory: bool
    route: Dict[str, Any]
    memory_context: Dict[str, Any]
    schema_context: Dict[str, Any]
    plan: List[Dict[str, Any]]
    sql_list: List[Dict[str, Any]]
    execution_results: List[Dict[str, Any]]
    validation_result: Dict[str, Any]
    repair_round: int
    max_repair_rounds: int
    repair_history: List[Dict[str, Any]]
    final_answer: str
    analysis: str
    success: bool
    error_stage: str
    problem: str
    trace: List[Dict[str, Any]]
    next_node: NotRequired[str]


def initial_state(
    query: str,
    session_id: str = "default",
    user_id: str = "demo_user",
    max_repair_rounds: int = 3,
    use_long_term_memory: bool = False,
) -> DataSpeakGraphState:
    """Build a fully-populated initial state for graph invocation."""

    return {
        "query": query,
        "session_id": session_id,
        "user_id": user_id,
        "use_long_term_memory": use_long_term_memory,
        "route": {},
        "memory_context": {},
        "schema_context": {},
        "plan": [],
        "sql_list": [],
        "execution_results": [],
        "validation_result": {},
        "repair_round": 0,
        "max_repair_rounds": max_repair_rounds,
        "repair_history": [],
        "final_answer": "",
        "analysis": "",
        "success": False,
        "error_stage": "",
        "problem": "",
        "trace": [],
    }
