from dataspeak.validation.repair_pipeline import run_pipeline_with_validation


def test_pipeline_generates_and_executes_city_revenue_query():
    result = run_pipeline_with_validation("统计每个城市的订单总金额，并按金额降序排列")

    assert result["success"] is True
    assert result["logs"]["sql_list"][0]["safety_passed"] is True
    assert "GROUP BY" in result["logs"]["sql_list"][0]["sql"].upper()
    assert result["logs"]["execution_results"][0]["row_count"] >= 1
    assert result["validation_result"]["confidence"] >= 0.6
