from __future__ import annotations

import requests

from automaton_os.providers.base import Message, ModelProvider


class OllamaProvider(ModelProvider):
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        self.base_url = base_url.rstrip("/")

    def chat(self, model: str, messages: list[Message], temperature: float = 0.2) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")
