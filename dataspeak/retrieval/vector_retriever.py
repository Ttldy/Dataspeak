"""Local vector fallback using token overlap."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List

from dataspeak.schema_index.schema_store import SchemaField, load_schema_fields


def _tokens(text: str) -> List[str]:
    return re.findall(r"[\w\u4e00-\u9fff]+", text.lower())


def _cosine(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def vector_search(query: str, top_k: int = 20, fields: List[SchemaField] | None = None) -> List[Dict]:
    """Return semantic-ish matches without requiring FAISS or Milvus."""

    fields = fields or load_schema_fields()
    qv = Counter(_tokens(query))
    results = []
    for field in fields:
        score = _cosine(qv, Counter(_tokens(field.vector_text + " " + field.keyword_text)))
        if score:
            row = field.__dict__.copy()
            row.update({"rank": 0, "score": score, "source": "vector"})
            results.append(row)
    results.sort(key=lambda item: item["score"], reverse=True)
    for rank, item in enumerate(results[:top_k], 1):
        item["rank"] = rank
    return results[:top_k]
