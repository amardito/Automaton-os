from __future__ import annotations

from abc import ABC, abstractmethod


Message = dict[str, str]


class ModelProvider(ABC):
    @abstractmethod
    def chat(self, model: str, messages: list[Message], temperature: float = 0.2) -> str:
        """Return text response from a chat model."""
        raise NotImplementedError
