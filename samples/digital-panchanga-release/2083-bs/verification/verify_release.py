#!/usr/bin/env python3
"""Verify the sample digital Panchanga release checksums."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    checksum_file = ROOT / "checksums.txt"
    failures: list[str] = []
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(None, 1)
        target = ROOT / relative.strip()
        if not target.exists():
            failures.append(f"missing {relative.strip()}")
            continue
        actual = sha256(target)
        if actual != expected:
            failures.append(f"{relative.strip()}: expected {expected}, got {actual}")
    if failures:
        print("Sample release verification failed:")
        print("\n".join(failures))
        return 1
    print("Sample digital Panchanga release verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
