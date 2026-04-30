from __future__ import annotations

from automaton_os.core.config import load_settings
from automaton_os.providers.ollama import OllamaProvider
from automaton_os.providers.openai_compatible import OpenAICompatibleProvider
from automaton_os.providers.base import Message, ModelProvider


class ModelRouter:
    def __init__(self, settings: dict | None = None) -> None:
        self.settings = settings or load_settings()
        self.providers = self._build_providers()

    def _build_providers(self) -> dict[str, ModelProvider]:
        providers_config = self.settings.get("providers", {})
        providers: dict[str, ModelProvider] = {}

        if "ollama" in providers_config:
            providers["ollama"] = OllamaProvider(
                base_url=providers_config["ollama"].get("base_url", "http://localhost:11434")
            )

        if "cloudflare" in providers_config:
            cloudflare = providers_config["cloudflare"]
            if cloudflare.get("base_url"):
                providers["cloudflare"] = OpenAICompatibleProvider(
                    base_url=cloudflare.get("base_url", ""),
                    api_key=cloudflare.get("api_key", ""),
                )

        if "openai_compatible" in providers_config:
            openai_compatible = providers_config["openai_compatible"]
            if openai_compatible.get("base_url"):
                providers["openai_compatible"] = OpenAICompatibleProvider(
                    base_url=openai_compatible.get("base_url", ""),
                    api_key=openai_compatible.get("api_key", ""),
                )

        return providers

    def chat(self, profile: str, messages: list[Message], temperature: float = 0.2) -> str:
        model_config = self.settings.get("models", {}).get(profile)
        if not model_config:
            model_config = self.settings["models"]["default"]

        provider_name = model_config["provider"]
        model_name = model_config["model"]

        provider = self.providers.get(provider_name)
        if not provider:
            raise RuntimeError(f"Provider is not configured or unavailable: {provider_name}")

        return provider.chat(model=model_name, messages=messages, temperature=temperature)
