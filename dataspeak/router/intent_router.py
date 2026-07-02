"""Dynamic route selection for DataSpeak."""

from __future__ import annotations

from typing import Dict


TEXT2SQL_TERMS = (
    "统计",
    "查询",
    "多少",
    "前",
    "排名",
    "总金额",
    "平均",
    "退款率",
    "订单",
    "客户",
    "产品",
    "城市",
    "销售",
    "金额",
    "数量",
    "近",
    "最近",
    "分组",
    "排序",
)
FOLLOWUP_TERMS = ("刚才", "上面", "结果", "解释", "为什么", "继续", "这些", "这个")
METRIC_TERMS = ("口径", "指标", "含义", "定义", "字段")


def route_query(query: str) -> Dict[str, object]:
    """Classify a user query into a stable structured route."""

    q = query.strip()
    if any(term in q for term in FOLLOWUP_TERMS) and any(term in q for term in ("结果", "解释", "为什么", "刚才")):
        return {
            "route": "result_followup",
            "reason": "用户在追问或解释历史执行结果，需要读取短期记忆。",
            "need_memory": True,
        }
    if any(term in q for term in METRIC_TERMS) and not any(term in q for term in ("查询", "统计", "列出")):
        return {
            "route": "data_qa",
            "reason": "用户询问指标或字段口径，可由数据问答链路回答。",
            "need_memory": True,
        }
    if any(term in q for term in TEXT2SQL_TERMS):
        return {
            "route": "text2sql",
            "reason": "用户需要查询、统计、筛选或排序实时业务数据。",
            "need_memory": True,
        }
    return {
        "route": "chitchat",
        "reason": "用户输入不需要访问数据库。",
        "need_memory": False,
    }
