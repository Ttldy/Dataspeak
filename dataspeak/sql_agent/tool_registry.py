"""FastAPI-internal tool registry inspired by MCP tools."""

from __future__ import annotations

from typing import Any, Callable, Dict

from dataspeak.retrieval.retrieval_pipeline import retrieve_schema_context
from dataspeak.sql_agent.sql_executor import execute_sql, explain_sql


class ToolRegistry:
    """Register and invoke local agent tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]) -> None:
        """Register a callable tool."""

        self._tools[name] = func

    def call(self, name: str, **kwargs: Any) -> Any:
        """Call a registered tool."""

        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name](**kwargs)

    def names(self) -> list[str]:
        """Return registered tool names."""

        return sorted(self._tools)


LAST_RESULTS: Dict[str, Any] = {}


def get_last_result(session_id: str = "default") -> Any:
    """Return the last execution result for a session."""

    return LAST_RESULTS.get(session_id)


tool_registry = ToolRegistry()
tool_registry.register("execute_sql", execute_sql)
tool_registry.register("inspect_schema", retrieve_schema_context)
tool_registry.register("explain_sql", explain_sql)
tool_registry.register("get_last_result", get_last_result)
