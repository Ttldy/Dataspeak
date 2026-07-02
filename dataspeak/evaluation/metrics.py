"""Evaluation metric helpers."""

from __future__ import annotations


def safe_ratio(numerator: float, denominator: float) -> float:
    """Return a rounded ratio with zero-division safety."""

    return round(numerator / denominator, 4) if denominator else 0.0
