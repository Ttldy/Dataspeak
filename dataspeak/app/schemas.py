"""Pydantic request and response models."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat API request."""

    query: str
    session_id: str = "default"
    user_id: str = "demo_user"
    use_long_term_memory: bool = False


class ChatResponse(BaseModel):
    """Chat API response."""

    session_id: str
    route: Dict[str, Any]
    result: Dict[str, Any]
    trace: List[Dict[str, Any]] = Field(default_factory=list)


class Text2SQLRequest(BaseModel):
    """Text2SQL direct API request."""

    query: str
    session_id: str = "default"


class BuildIndexResponse(BaseModel):
    """Schema index build response."""

    index_path: str
    message: str
