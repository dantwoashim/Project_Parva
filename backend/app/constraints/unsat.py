"""Unsat core helpers."""

from __future__ import annotations


def unsat_core(*reasons: str) -> list[str]:
    return list(reasons)
