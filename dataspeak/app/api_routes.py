"""FastAPI route definitions."""

from __future__ import annotations

from fastapi import APIRouter

from dataspeak.app.schemas import BuildIndexResponse, ChatRequest, ChatResponse, Text2SQLRequest
from dataspeak.graph.workflow import run_dataspeak_graph
from dataspeak.memory.short_term import short_term_memory
from dataspeak.schema_index.index_builder import build_schema_index
from dataspeak.sql_agent.sql_executor import ensure_demo_sqlite
from dataspeak.utils.trace import trace_store

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    """Health check endpoint."""

    return {"status": "ok", "service": "dataspeak", "version": "0.1.0", "workflow": "langgraph"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Run the LangGraph Agent workflow for chat requests."""

    result = run_dataspeak_graph(
        query=request.query,
        session_id=request.session_id,
        user_id=request.user_id,
        use_long_term_memory=request.use_long_term_memory,
    )
    trace_store.add(request.session_id, "langgraph", {"route": result.get("route"), "success": result.get("success")})
    short_term_memory.add_turn(request.session_id, request.query, result.get("final_answer", result.get("analysis", "")))
    return ChatResponse(
        session_id=request.session_id,
        route=result.get("route", {}),
        result=result,
        trace=result.get("trace", []),
    )


@router.post("/text2sql")
def text2sql(request: Text2SQLRequest) -> dict:
    """Run the LangGraph Text2SQL branch directly."""

    result = run_dataspeak_graph(query=request.query, session_id=request.session_id)
    trace_store.add(request.session_id, "text2sql_graph", {"success": result.get("success")})
    return result


@router.post("/schema/index/build", response_model=BuildIndexResponse)
def schema_index_build() -> BuildIndexResponse:
    """Initialize demo DB and build the schema index."""

    db_path = ensure_demo_sqlite()
    index_path = build_schema_index(db_path)
    return BuildIndexResponse(index_path=str(index_path), message="schema index built")


@router.get("/sessions/{session_id}/trace")
def get_trace(session_id: str) -> dict:
    """Return a session trace."""

    return {"session_id": session_id, "trace": trace_store.get(session_id)}
