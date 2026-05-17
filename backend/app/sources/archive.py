"""Immutable source archive writer."""

from __future__ import annotations

from pathlib import Path


def write_raw_source(path: Path, data: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"raw source artifact already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
