#!/usr/bin/env python3
"""Verify a public Parva offline bundle."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/parva_offline_verify.py dist/parva-offline-bundle")
        return 2
    root = Path(sys.argv[1])
    manifest_path = root / "bundle-manifest.json"
    if not manifest_path.exists():
        print(json.dumps({"ok": False, "error": "bundle-manifest.json missing"}, indent=2))
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues = []
    for relative, expected in manifest.get("checksums", {}).items():
        path = root / relative
        if not path.exists():
            issues.append(f"missing:{relative}")
            continue
        if _sha256(path) != expected:
            issues.append(f"checksum_mismatch:{relative}")
    print(json.dumps({"ok": not issues, "issues": issues, "checked": len(manifest.get("checksums", {}))}, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
