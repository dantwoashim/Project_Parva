"""Append-only JSONL transparency log verification."""

from __future__ import annotations

import json
from pathlib import Path

from app.sources.hashing import canonical_json_hash


def append_log_entry(path: Path, entry: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = ""
    if path.exists():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            previous = json.loads(lines[-1])["entry_hash"]
    payload = {**entry, "previous_hash": previous}
    payload["entry_hash"] = f"sha256:{canonical_json_hash(payload)}"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return payload


def verify_log(path: Path) -> bool:
    previous = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        entry_hash = entry.pop("entry_hash")
        if entry.get("previous_hash") != previous:
            return False
        if f"sha256:{canonical_json_hash(entry)}" != entry_hash:
            return False
        previous = entry_hash
    return True
