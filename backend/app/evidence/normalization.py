"""Normalize extracted public evidence rows."""

from __future__ import annotations

from typing import Any


def normalize_source_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        cleaned = {str(key).strip(): value for key, value in row.items() if str(key).strip()}
        cleaned.setdefault("row_id", f"row_{index:04d}")
        cleaned.setdefault("review_required", True)
        cleaned.setdefault("authority_boundary", "source_backed_not_authority")
        normalized.append(cleaned)
    return normalized

