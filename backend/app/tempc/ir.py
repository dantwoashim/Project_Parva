"""TempC IR."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TempCProgram:
    name: str
    operation: str
    parameters: dict
