"""Run a small local benchmark for DataSpeak."""

from __future__ import annotations

import json
import time
from pathlib import Path

from dataspeak.config.settings import PROJECT_ROOT
from dataspeak.evaluation.metrics import safe_ratio
from dataspeak.retrieval.retrieval_pipeline import retrieve_schema_context
from dataspeak.validation.repair_pipeline import run_pipeline_with_validation


def load_queries() -> list[dict]:
    """Load benchmark samples."""

    path = PROJECT_ROOT / "dataspeak" / "evaluation" / "sample_queries.json"
    return json.loads(path.read_text(encoding="utf-8"))


def run_benchmark() -> dict:
    """Evaluate schema recall, precision, execution accuracy, repair and latency."""

    samples = load_queries()
    recall_hits = precision_hits = target_total = retrieved_total = exec_ok = repair_ok = 0
    latencies = []
    for sample in samples:
        start = time.perf_counter()
        ctx = retrieve_schema_context(sample["query"])
        retrieved = {item["field_id"] for item in ctx["rerank_results"]}
        targets = set(sample["target_fields"])
        recall_hits += len(targets & retrieved)
        precision_hits += len(targets & retrieved)
        target_total += len(targets)
        retrieved_total += max(len(retrieved), 1)
        result = run_pipeline_with_validation(sample["query"])
        exec_ok += int(result["success"])
        repair_ok += int(result["success"] and result["round"] > 0)
        latencies.append((time.perf_counter() - start) * 1000)
    return {
        "schema_recall": safe_ratio(recall_hits, target_total),
        "schema_precision": safe_ratio(precision_hits, retrieved_total),
        "sql_execution_accuracy": safe_ratio(exec_ok, len(samples)),
        "repair_success_rate": safe_ratio(repair_ok, len(samples)),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
    }


def main() -> None:
    """CLI entrypoint."""

    print(json.dumps(run_benchmark(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
