"""Read versioned package data without depending on the source checkout."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any, Literal, overload


@overload
def read_data(name: str, *, missing_ok: Literal[False] = False) -> dict[str, Any]: ...


@overload
def read_data(name: str, *, missing_ok: Literal[True]) -> dict[str, Any] | None: ...


def read_data(name: str, *, missing_ok: bool = False) -> dict[str, Any] | None:
    path = files("parva") / "data" / name
    if missing_ok and not path.is_file():
        return None
    value: dict[str, Any] = json.loads(path.read_text("utf-8"))
    return value
