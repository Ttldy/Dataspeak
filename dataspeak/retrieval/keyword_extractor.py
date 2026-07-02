"""Keyword extraction for schema retrieval."""

from __future__ import annotations

import re
from typing import List


DOMAIN_TERMS = [
    "城市",
    "订单总金额",
    "总金额",
    "订单金额",
    "退款率",
    "退款",
    "产品",
    "客户等级",
    "客单价",
    "评分",
    "反馈",
    "营销活动",
    "近60天",
    "最近30天",
    "订单数量",
    "平均值",
    "支付",
    "渠道",
    "品类",
]


def extract_keywords(query: str) -> List[str]:
    """Extract core business terms using deterministic fallback rules."""

    keywords = [term for term in DOMAIN_TERMS if term in query]
    ascii_words = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", query)
    keywords.extend(ascii_words)
    if "每个城市" in query and "城市" not in keywords:
        keywords.append("城市")
    if "平均客单价" in query:
        keywords.extend(["客户等级", "订单总金额"])
    if not keywords:
        keywords = [query.strip()]
    seen: set[str] = set()
    return [item for item in keywords if item and not (item in seen or seen.add(item))]
