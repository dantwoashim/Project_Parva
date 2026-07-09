"""Compatibility namespace for the Future BS research package.

The implementation lives in :mod:`app.research.future_bs`. This package keeps
the historical ``app.future_bs.*`` import path working for existing scripts,
tests, and compatibility surfaces while the repository adopts physical research
lanes.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

_implementation = import_module("app.research.future_bs")
__all__ = getattr(_implementation, "__all__", [])
__path__ = [str(Path(__file__).resolve().parents[1] / "research" / "future_bs")]
