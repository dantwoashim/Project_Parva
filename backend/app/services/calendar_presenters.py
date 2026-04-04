"""Calendar response presenters."""

from __future__ import annotations

from typing import Any


def present_calendar_payload(*, body: dict[str, Any], trust: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(body)
    payload.update(trust)
    if extra:
        payload.update(extra)
    return payload
