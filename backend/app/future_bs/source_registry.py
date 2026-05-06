"""Source registry helpers for future BS corpus provenance."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_REGISTRY_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "source_registry.json"


@lru_cache(maxsize=1)
def load_source_registry() -> dict[str, Any]:
    if not SOURCE_REGISTRY_PATH.exists():
        return {
            "corpus_id": "missing_registry",
            "status": "registry_missing",
            "warning": "Source registry file is not present.",
            "sources": {},
        }
    return json.loads(SOURCE_REGISTRY_PATH.read_text(encoding="utf-8"))


def source_payload(source_reference: str) -> dict[str, Any]:
    registry = load_source_registry()
    sources = registry.get("sources", {})
    if source_reference not in sources:
        return {
            "source_reference": source_reference,
            "source_type": "unknown",
            "verification_status": "needs_review",
        }
    payload = dict(sources[source_reference])
    payload["source_reference"] = source_reference
    return payload
