"""Compile TempC source into IR."""

from __future__ import annotations

from app.tempc.ir import TempCProgram
from app.tempc.parser import parse_tempc


def compile_tempc(source: str) -> TempCProgram:
    return parse_tempc(source)
