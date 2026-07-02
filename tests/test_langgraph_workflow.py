from dataspeak.graph.nodes import repair_router_node
from dataspeak.graph.workflow import run_dataspeak_graph


def test_langgraph_text2sql_query_runs_full_chain_successfully():
    result = run_dataspeak_graph("统计最近30天每个城市的订单总金额，并按金额降序排列")

    assert result["success"] is True
    assert result["route"]["route"] == "text2sql"
    assert result["schema_context"]["schema_graph_text"]
    assert result["plan"]
    assert result["sql_list"]
    assert result["execution_results"][0]["row_count"] >= 1
    assert result["validation_result"]["success"] is True
    assert result["final_answer"]
    assert any(item["node"] == "validate_result" for item in result["trace"])


def test_langgraph_chitchat_uses_qa_branch_without_sql_generation():
    result = run_dataspeak_graph("你好，随便聊两句")

    assert result["success"] is True
    assert result["route"]["route"] == "chitchat"
    assert result["final_answer"]
    assert result["sql_list"] == []
    assert any(item["node"] == "qa_answer" for item in result["trace"])


def test_repair_router_records_history_and_respects_round_limit_shape():
    state = {
        "validation_result": {
            "success": False,
            "error_stage": "sql_execution",
            "problem": "syntax error",
            "callback_module": "sql_generation",
            "repair_advice": "regenerate SQL",
        },
        "repair_round": 2,
        "repair_history": [],
        "sql_list": [{"sql": "bad"}],
        "execution_results": [{"success": False}],
        "trace": [],
    }

    update = repair_router_node(state)

    assert update["repair_round"] == 3
    assert update["repair_history"][0]["callback_module"] == "sql_generation"
    assert update["sql_list"] == []
    assert update["execution_results"] == []


def test_langgraph_output_contains_display_fields():
    result = run_dataspeak_graph("统计不同客户等级的平均客单价")

    for key in (
        "route",
        "schema_context",
        "plan",
        "sql_list",
        "execution_results",
        "validation_result",
        "final_answer",
    ):
        assert key in result
