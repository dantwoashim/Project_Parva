"""Fold and unfold membrane proof packs."""

from __future__ import annotations

from app.membranes.timepack import build_timepack


def unfold(membrane: dict, level: str) -> dict:
    return build_timepack(membrane, level)
