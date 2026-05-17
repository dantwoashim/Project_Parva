"""Verify static bundle manifests."""

from __future__ import annotations

import json
from pathlib import Path

from app.sources.hashing import sha256_file


def verify_manifest(root: Path) -> bool:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = root / entry["path"]
        if not path.exists() or sha256_file(path) != entry["sha256"]:
            return False
    return True
