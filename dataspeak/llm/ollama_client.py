"""Ollama HTTP chat adapter."""

from __future__ import annotations

import json
import urllib.request

from dataspeak.config.settings import settings
from dataspeak.llm.fallback import FallbackChatModel


class OllamaChatModel:
    """Small Ollama Chat API client."""

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        self.model = model or settings.chat_model
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    def complete(self, prompt: str) -> str:
        """Call Ollama when configured, otherwise fallback."""

        if not self.model:
            return FallbackChatModel().complete(prompt)
        body = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False}).encode("utf-8")
        try:
            req = urllib.request.Request(f"{self.base_url}/api/chat", data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("message", {}).get("content", "")
        except Exception:
            return FallbackChatModel().complete(prompt)
