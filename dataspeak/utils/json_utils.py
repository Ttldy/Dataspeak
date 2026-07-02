"""JSON helper functions."""

from __future__ import annotations

import json
from typing import Any


def dumps(data: Any) -> str:
    """Serialize data with deterministic UTF-8 friendly formatting."""

    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, default=str)
