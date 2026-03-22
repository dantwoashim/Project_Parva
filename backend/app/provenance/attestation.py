"""Cryptographic attestation helpers for provenance records."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _read_text_file(path: Path | None) -> str | None:
    if not path or not path.exists():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    return raw or None


def _attestation_key_path() -> Path | None:
    configured = os.getenv("PARVA_PROVENANCE_ATTESTATION_KEY_FILE", "").strip()
    if configured:
        path = Path(configured)
        return path if path.exists() else None
    return None


def _attestation_key() -> bytes | None:
    raw = os.getenv("PARVA_PROVENANCE_ATTESTATION_KEY", "").strip()
    if raw:
        return raw.encode("utf-8")

    file_value = _read_text_file(_attestation_key_path())
    if not file_value:
        return None
    return file_value.encode("utf-8")


def attestation_key_configured() -> bool:
    return _attestation_key() is not None


def _attestation_key_id() -> str | None:
    raw = os.getenv("PARVA_PROVENANCE_ATTESTATION_KEY_ID", "").strip()
    if raw:
        return raw

    configured = os.getenv("PARVA_PROVENANCE_ATTESTATION_KEY_ID_FILE", "").strip()
    if configured:
        return _read_text_file(Path(configured))

    return None


def build_attestation(payload: dict[str, Any]) -> dict[str, Any]:
    key = _attestation_key()
    if not key:
        return {
            "mode": "unsigned",
            "algorithm": None,
            "key_id": None,
            "value": None,
        }

    value = hmac.new(key, canonical_json(payload).encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "mode": "hmac-sha256",
        "algorithm": "hmac-sha256",
        "key_id": _attestation_key_id() or "local-hmac",
        "value": value,
    }


def verify_attestation(payload: dict[str, Any], attestation: dict[str, Any] | None) -> bool:
    if not isinstance(attestation, dict):
        return False

    mode = attestation.get("mode")
    if mode == "unsigned":
        return attestation.get("value") is None

    if mode != "hmac-sha256":
        return False

    key = _attestation_key()
    value = attestation.get("value")
    if not key or not isinstance(value, str):
        return False

    expected = build_attestation(payload)
    return hmac.compare_digest(value, str(expected.get("value") or ""))
