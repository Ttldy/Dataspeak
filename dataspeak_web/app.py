"""Streamlit demo UI for DataSpeak."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dataspeak.graph.workflow import run_dataspeak_graph

st.set_page_config(page_title="DataSpeak", layout="wide")
st.title("DataSpeak 智能问数 Agent")

query = st.text_input("自然语言问题", value="统计最近30天每个城市的订单总金额，并按金额降序排列")
if st.button("运行问数", type="primary"):
    result = run_dataspeak_graph(query)
    st.subheader("路由结果")
    st.json(result.get("route", {}))
    if result.get("route", {}).get("route") == "text2sql":
        logs = result["logs"]
        st.subheader("LangGraph Trace")
        st.json(result.get("trace", []))
        st.subheader("Schema 检索结果")
        st.json(
            {
                "keywords": logs["schema_context"].get("keywords", []),
                "dynamic_top_k": logs["schema_context"].get("dynamic_top_k"),
                "rerank_results": logs["schema_context"].get("rerank_results", [])[:8],
            }
        )
        st.subheader("Schema Graph")
        st.code(logs["schema_context"].get("schema_graph_text", ""))
        st.subheader("结构化 Plan")
        st.json(logs["plan"])
        st.subheader("SQL")
        for item in logs["sql_list"]:
            st.code(item["sql"], language="sql")
            st.json({"safety_passed": item["safety_passed"], "error_message": item["error_message"]})
        st.subheader("执行结果")
        rows = logs["execution_results"][0]["preview_rows"] if logs["execution_results"] else []
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        st.subheader("最终分析")
        st.success(result["final_answer"])
        st.subheader("修正过程")
        st.json(result.get("repair_history", []))
    else:
        st.subheader("LangGraph Trace")
        st.json(result.get("trace", []))
        st.info(result.get("final_answer", "当前问题进入 QA/Fallback 链路。"))
