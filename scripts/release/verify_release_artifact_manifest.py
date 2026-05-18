#!/usr/bin/env python3
"""Verify the public release artifact manifest hashes."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = PROJECT_ROOT / "data" / "public" / "release-artifact-manifest.json"


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit("release artifact manifest missing; run scripts/release/build_release_artifact_manifest.py")
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload.get("schema") != "parva-release-artifact-manifest-v1":
        raise SystemExit("release artifact manifest schema mismatch")
    issues: list[str] = []
    for artifact in payload.get("artifacts", []):
        rel = artifact.get("path")
        expected = artifact.get("sha256")
        path = PROJECT_ROOT / str(rel)
        if not path.exists():
            issues.append(f"{rel}: missing")
            continue
        actual = _sha256(path)
        if actual != expected:
            issues.append(f"{rel}: hash mismatch expected {expected} actual {actual}")
        if path.stat().st_size != artifact.get("bytes"):
            issues.append(f"{rel}: byte size mismatch")
    if issues:
        for issue in issues:
            print(f"[release-manifest] {issue}")
        return 1
    print("Release artifact manifest verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
