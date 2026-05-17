"""Deterministic canonical query normalization."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any

from app.canonicalization.spec import CANONICALIZATION_VERSION, DEFAULT_CONTEXT

DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
MONTH_ALIASES = {
    "baishakh": "baishakh",
    "baisakh": "baishakh",
    "बैशाख": "baishakh",
}
FESTIVAL_ALIASES = {
    "dashain": "dashain",
    "dasain": "dashain",
    "दशैं": "dashain",
    "दशैँ": "dashain",
}


def normalize_scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = re.sub(r"\s+", " ", value.translate(DEVANAGARI_DIGITS).strip().lower())
    if text in MONTH_ALIASES:
        return MONTH_ALIASES[text]
    if text in FESTIVAL_ALIASES:
        return FESTIVAL_ALIASES[text]
    return text


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return normalize_scalar(value)


def canonicalize_query(query: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(query)
    context = {**DEFAULT_CONTEXT, **payload.get("context", {})}
    normalized = {
        "canonicalization_version": CANONICALIZATION_VERSION,
        "operation": normalize_scalar(payload.get("operation", "unknown")),
        "input": _normalize(payload.get("input", {})),
        "context": _normalize(context),
    }
    return normalized


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def identity_hash(query: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(canonicalize_query(query)).encode("utf-8")).hexdigest()
    return f"parva:id:v1:sha256:{digest}"
