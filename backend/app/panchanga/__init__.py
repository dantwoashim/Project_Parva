"""Proof-carrying Panchanga engine helpers."""

from __future__ import annotations

from typing import Any


def build_panchanga_summary_capsule(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from app.panchanga.proof import build_panchanga_summary_capsule as _build

    return _build(*args, **kwargs)

__all__ = ["build_panchanga_summary_capsule"]
