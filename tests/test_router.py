from dataspeak.router.intent_router import route_query


def test_route_text2sql_for_business_aggregation():
    result = route_query("统计最近30天每个城市的订单总金额")

    assert result["route"] == "text2sql"
    assert result["need_memory"] is True
    assert "统计" in result["reason"] or "查询" in result["reason"]


def test_route_result_followup_uses_memory():
    result = route_query("把刚才的结果解释一下，退款率为什么这么高？")

    assert result["route"] == "result_followup"
    assert result["need_memory"] is True


def test_route_chitchat_without_memory_requirement():
    result = route_query("你好，今天状态怎么样？")

    assert result["route"] == "chitchat"
    assert result["need_memory"] is False
