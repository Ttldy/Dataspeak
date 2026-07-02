"""In-memory trace store for Agent execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class TraceStore:
    """Simple process-local trace storage."""

    traces: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def add(self, session_id: str, stage: str, payload: Dict[str, Any]) -> None:
        """Append a trace event."""

        self.traces.setdefault(session_id, []).append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "stage": stage,
                "payload": payload,
            }
        )

    def get(self, session_id: str) -> List[Dict[str, Any]]:
        """Return trace events for a session."""

        return self.traces.get(session_id, [])


trace_store = TraceStore()
