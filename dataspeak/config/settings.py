"""Central settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for DataSpeak."""

    app_name: str = "DataSpeak"
    api_host: str = _env("DATASPEAK_API_HOST", "127.0.0.1")
    api_port: int = int(_env("DATASPEAK_API_PORT", "18088"))
    web_port: int = int(_env("DATASPEAK_WEB_PORT", "18501"))
    database_url: str = _env(
        "DATASPEAK_DATABASE_URL",
        f"sqlite:///{PROJECT_ROOT / 'demo_data' / 'dataspeak_demo.sqlite'}",
    )
    schema_index_path: str = _env(
        "SCHEMA_INDEX_PATH",
        str(PROJECT_ROOT / "demo_data" / "schema_index.json"),
    )
    llm_provider: str = _env("LLM_PROVIDER", "ollama")
    ollama_base_url: str = _env("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    openai_base_url: str = _env("OPENAI_BASE_URL", "")
    openai_api_key: str = _env("OPENAI_API_KEY", "")
    chat_model: str = _env("CHAT_MODEL", "")
    coder_model: str = _env("CODER_MODEL", "")
    embedding_provider: str = _env("EMBEDDING_PROVIDER", "sentence_transformers")
    rerank_provider: str = _env("RERANK_PROVIDER", "cross_encoder")
    default_sql_limit: int = int(_env("DEFAULT_SQL_LIMIT", "100"))
    max_repair_rounds: int = int(_env("MAX_REPAIR_ROUNDS", "3"))


settings = Settings()
