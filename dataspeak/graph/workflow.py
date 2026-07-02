"""Build and run the DataSpeak LangGraph workflow."""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from dataspeak.graph.edges import repair_edge, route_edge, validation_edge
from dataspeak.graph.nodes import (
    execute_sql_node,
    final_answer_node,
    generate_plan_node,
    generate_sql_node,
    load_memory_node,
    qa_answer_node,
    repair_router_node,
    retrieve_schema_node,
    route_node,
    validate_result_node,
)
from dataspeak.graph.state import DataSpeakGraphState, initial_state


def build_dataspeak_graph():
    """Build and compile the DataSpeak Agent state machine."""

    graph = StateGraph(DataSpeakGraphState)
    graph.add_node("load_memory", load_memory_node)
    graph.add_node("route", route_node)
    graph.add_node("retrieve_schema", retrieve_schema_node)
    graph.add_node("generate_plan", generate_plan_node)
    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("validate_result", validate_result_node)
    graph.add_node("repair_router", repair_router_node)
    graph.add_node("qa_answer", qa_answer_node)
    graph.add_node("final_answer", final_answer_node)

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "route")
    graph.add_conditional_edges(
        "route",
        route_edge,
        {"retrieve_schema": "retrieve_schema", "qa_answer": "qa_answer"},
    )
    graph.add_edge("retrieve_schema", "generate_plan")
    graph.add_edge("generate_plan", "generate_sql")
    graph.add_edge("generate_sql", "execute_sql")
    graph.add_edge("execute_sql", "validate_result")
    graph.add_conditional_edges(
        "validate_result",
        validation_edge,
        {"final_answer": "final_answer", "repair_router": "repair_router"},
    )
    graph.add_conditional_edges(
        "repair_router",
        repair_edge,
        {
            "retrieve_schema": "retrieve_schema",
            "generate_plan": "generate_plan",
            "generate_sql": "generate_sql",
            "execute_sql": "execute_sql",
        },
    )
    graph.add_edge("qa_answer", "final_answer")
    graph.add_edge("final_answer", END)
    return graph.compile()


def run_dataspeak_graph(
    query: str,
    session_id: str = "default",
    user_id: str = "demo_user",
    max_repair_rounds: int = 3,
    use_long_term_memory: bool = False,
) -> Dict[str, Any]:
    """Run the compiled DataSpeak graph and return the final state."""

    app = build_dataspeak_graph()
    state = initial_state(
        query=query,
        session_id=session_id,
        user_id=user_id,
        max_repair_rounds=max_repair_rounds,
        use_long_term_memory=use_long_term_memory,
    )
    result = app.invoke(state)
    result["logs"] = {
        "query": result.get("query"),
        "schema_context": result.get("schema_context", {}),
        "plan": result.get("plan", []),
        "sql_list": result.get("sql_list", []),
        "execution_results": result.get("execution_results", []),
    }
    return result
