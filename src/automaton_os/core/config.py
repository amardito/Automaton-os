from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            return os.getenv(key, "")

        return _ENV_PATTERN.sub(replace, value)

    if isinstance(value, dict):
        return {key: _expand_env(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_expand_env(item) for item in value]

    return value


def load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    return _expand_env(data)


def load_settings(path: str | Path = "configs/settings.yaml") -> dict:
    return load_yaml(path)


def load_agents(path: str | Path = "configs/agents.yaml") -> dict:
    return load_yaml(path)


def load_missions(path: str | Path = "configs/missions.yaml") -> dict:
    return load_yaml(path)
