"""FastAPI entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from dataspeak.app.api_routes import router

app = FastAPI(title="DataSpeak API", version="0.1.0", description="Private Text2SQL Agent demo")
app.include_router(router)
