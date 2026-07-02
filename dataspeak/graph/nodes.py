"""LangGraph nodes that wrap the existing DataSpeak modules."""

from __future__ import annotations

from typing import Any, Dict

from dataspeak.graph.state import DataSpeakGraphState
from dataspeak.memory.memory_retriever import build_memory_context
from dataspeak.planning.plan_generator import generate_plan
from dataspeak.retrieval.retrieval_pipeline import retrieve_schema_context
from dataspeak.router.intent_router import route_query
from dataspeak.sql_agent.sql_executor import execute_sql_steps
from dataspeak.sql_agent.sql_generator import generate_sql_list
from dataspeak.validation.result_validator import validate_execution_result


def _trace(state: DataSpeakGraphState, node: str, payload: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Append a compact trace event to state."""

    trace = list(state.get("trace", []))
    trace.append({"node": node, "payload": payload})
    return trace


def load_memory_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Load short-term and optional long-term memory context."""

    memory_context = build_memory_context(
        session_id=state["session_id"],
        user_id=state["user_id"],
        query=state["query"],
        use_long_term_memory=state.get("use_long_term_memory", False),
    )
    return {"memory_context": memory_context, "trace": _trace(state, "load_memory", {"has_memory": bool(memory_context)})}


def route_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Route the request to Text2SQL or QA branches."""

    route = route_query(state["query"])
    return {"route": route, "trace": _trace(state, "route", route)}


def retrieve_schema_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Retrieve Schema context and build Schema Graph."""

    schema_context = state.get("schema_context") or retrieve_schema_context(state["query"])
    return {
        "schema_context": schema_context,
        "trace": _trace(
            state,
            "retrieve_schema",
            {"keywords": schema_context.get("keywords", []), "dynamic_top_k": schema_context.get("dynamic_top_k")},
        ),
    }


def generate_plan_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Generate structured auditable plan."""

    plan = state.get("plan") or generate_plan(state["query"], state["schema_context"]["schema_graph"])
    return {"plan": plan, "trace": _trace(state, "generate_plan", {"step_count": len(plan)})}


def generate_sql_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Generate SQL list from plan and schema graph."""

    sql_list = state.get("sql_list") or generate_sql_list(state["query"], state["plan"], state["schema_context"]["schema_graph"])
    return {
        "sql_list": sql_list,
        "trace": _trace(
            state,
            "generate_sql",
            {"sql_count": len(sql_list), "safety_passed": all(item.get("safety_passed") for item in sql_list)},
        ),
    }


def execute_sql_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Execute generated SQL through the existing tool layer."""

    execution_results = state.get("execution_results") or execute_sql_steps(state["sql_list"])
    return {
        "execution_results": execution_results,
        "trace": _trace(
            state,
            "execute_sql",
            {"result_count": len(execution_results), "all_success": all(item.get("success") for item in execution_results)},
        ),
    }


def validate_result_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Validate execution result and produce success/failure structure."""

    validation_result = validate_execution_result(
        query=state["query"],
        schema_retrieval_result=state["schema_context"],
        schema_graph=state["schema_context"].get("schema_graph_text", ""),
        plan=state["plan"],
        sql_list=state["sql_list"],
        execution_results=state["execution_results"],
        repair_history=state.get("repair_history", []),
    )
    return {
        "validation_result": validation_result,
        "trace": _trace(state, "validate_result", validation_result),
    }


def repair_router_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Record repair metadata and clear downstream state for the next loop."""

    validation = state.get("validation_result", {})
    callback_module = validation.get("callback_module", "schema_retrieval")
    repair_round = state.get("repair_round", 0) + 1
    repair_history = list(state.get("repair_history", []))
    repair_history.append(
        {
            "round": repair_round,
            "error_stage": validation.get("error_stage"),
            "problem": validation.get("problem"),
            "callback_module": callback_module,
            "repair_advice": validation.get("repair_advice"),
        }
    )
    update: Dict[str, Any] = {
        "repair_round": repair_round,
        "repair_history": repair_history,
        "trace": _trace(state, "repair_router", {"repair_round": repair_round, "callback_module": callback_module}),
    }
    if callback_module == "schema_retrieval":
        update.update({"schema_context": {}, "plan": [], "sql_list": [], "execution_results": []})
    elif callback_module in {"cot_generation", "plan_generation"}:
        update.update({"plan": [], "sql_list": [], "execution_results": []})
    elif callback_module == "sql_generation":
        update.update({"sql_list": [], "execution_results": []})
    elif callback_module == "sql_execution":
        update.update({"execution_results": []})
    else:
        update.update({"schema_context": {}, "plan": [], "sql_list": [], "execution_results": []})
    return update


def qa_answer_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Answer result follow-up, data QA, or chitchat with memory-aware fallback."""

    route = state.get("route", {}).get("route", "chitchat")
    if route == "result_followup":
        answer = "这是结果追问链路：当前可结合短期记忆中的最近查询、SQL 和分析结论继续解释。"
    elif route == "data_qa":
        answer = "这是数据问答链路：当前 Demo 可解释指标口径、字段含义和已保存的查询偏好。"
    else:
        answer = "你好，我是 DataSpeak，可以帮你把自然语言问题转成安全的只读 SQL 并解释结果。"
    return {
        "success": True,
        "final_answer": answer,
        "analysis": answer,
        "trace": _trace(state, "qa_answer", {"route": route}),
    }


def final_answer_node(state: DataSpeakGraphState) -> Dict[str, Any]:
    """Normalize final success/failure fields before END."""

    validation = state.get("validation_result", {})
    if validation.get("success"):
        final_answer = validation.get("final_answer") or validation.get("analysis", "")
        return {
            "success": True,
            "final_answer": final_answer,
            "analysis": validation.get("analysis", final_answer),
            "trace": _trace(state, "final_answer", {"success": True}),
        }
    if state.get("success") and state.get("final_answer"):
        return {"trace": _trace(state, "final_answer", {"success": True})}
    problem = validation.get("problem") or state.get("problem") or "达到最大修复轮次后仍未得到有效结果。"
    return {
        "success": False,
        "error_stage": validation.get("error_stage", state.get("error_stage", "unknown")),
        "problem": problem,
        "final_answer": f"查询失败：{problem}",
        "analysis": problem,
        "trace": _trace(state, "final_answer", {"success": False, "problem": problem}),
    }
