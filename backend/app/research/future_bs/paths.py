"""Path helpers for Future BS research modules."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the repository root from the research package location."""

    return Path(__file__).resolve().parents[4]
