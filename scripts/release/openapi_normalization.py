"""Semantic normalization helpers for generated OpenAPI comparisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def drop_json_schema_defaults(value: Any) -> Any:
    """Remove explicit JSON Schema defaults that do not change contract semantics."""
    if isinstance(value, dict):
        return {
            key: drop_json_schema_defaults(item)
            for key, item in value.items()
            if not (key == "additionalProperties" and item is True)
        }
    if isinstance(value, list):
        return [drop_json_schema_defaults(item) for item in value]
    return value


def normalized_openapi_json(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    normalized = drop_json_schema_defaults(payload)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))
