"""Conservative PII and trace scrubbing helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

REDACTION = "[redacted]"

DENYLIST_FIELD_HINTS = frozenset(
    {
        "address",
        "citizenship",
        "citizenship_id",
        "client_name",
        "cooperative_member_id",
        "customer_email",
        "email",
        "full_name",
        "member_id",
        "name",
        "phone",
        "provider_reference",
        "raw_payload",
        "raw_payload_json",
        "tax_id",
    }
)
ALLOWLIST_FIELD_HINTS = frozenset(
    {
        "action_type",
        "artifact_id",
        "bs_date",
        "claim_boundary",
        "confidence",
        "dataset_hash",
        "entry_hash",
        "event",
        "event_type",
        "fact_id",
        "fact_ids",
        "invoice_id",
        "key_id",
        "key_prefix",
        "method",
        "object_id",
        "packet_id",
        "profile_id",
        "release_id",
        "request_id",
        "route",
        "rules_hash",
        "source_id",
        "source_ids",
        "status",
        "subscription_id",
        "timestamp",
        "trace_id",
    }
)

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?977[-\s]?)?(?:9[78]\d{8}|\d{2,4}[-\s]?\d{6,8})(?!\d)")
CITIZENSHIP_RE = re.compile(r"\b\d{2,3}[-/]\d{2,4}[-/]\d{4,8}\b")
ACCOUNT_RE = re.compile(r"\b(?:account|acct|a/c)\s*[:#-]?\s*[A-Z0-9-]{6,24}\b", re.IGNORECASE)
PRECISE_ADDRESS_RE = re.compile(
    r"\b(?:ward|tole|street|marg|road|municipality|gaupalika|province)\s*[:#-]?\s*[^,;]{3,80}",
    re.IGNORECASE,
)


def _field_name_requires_redaction(field_name: str) -> bool:
    normalized = field_name.strip().lower()
    if normalized in ALLOWLIST_FIELD_HINTS:
        return False
    return normalized in DENYLIST_FIELD_HINTS or any(
        hint in normalized for hint in DENYLIST_FIELD_HINTS
    )


def redact_text(value: str) -> str:
    text = str(value)
    text = EMAIL_RE.sub(REDACTION, text)
    text = PHONE_RE.sub(REDACTION, text)
    text = CITIZENSHIP_RE.sub(REDACTION, text)
    text = ACCOUNT_RE.sub(REDACTION, text)
    text = PRECISE_ADDRESS_RE.sub(REDACTION, text)
    return text


def scrub_value(value: Any, *, field_name: str | None = None) -> Any:
    if field_name and _field_name_requires_redaction(field_name):
        return REDACTION
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [scrub_value(item, field_name=field_name) for item in value]
    if isinstance(value, tuple):
        return [scrub_value(item, field_name=field_name) for item in value]
    if isinstance(value, Mapping):
        return scrub_structured_trace(value)
    return value


def scrub_structured_trace(payload: Mapping[str, Any]) -> dict[str, Any]:
    scrubbed: dict[str, Any] = {}
    for key, value in payload.items():
        text_key = str(key)
        scrubbed[text_key] = scrub_value(value, field_name=text_key)
    return scrubbed

