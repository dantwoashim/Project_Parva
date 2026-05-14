#!/usr/bin/env python3
"""Regenerate deterministic public release manifest artifact hashes."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from tools.trust.common import (  # noqa: E402
    DEFAULT_MANIFEST_PATH,
    DEFAULT_SIGNATURE_PATH,
    TrustToolError,
    build_alpha_signature_payload,
    load_json,
    sha256_file,
)

FORBIDDEN_PUBLIC_ARTIFACT_PREFIXES = (
    "data/source_archive/",
    "data/future_bs/private/",
    "data/ephemeris/",
    "private/",
)
FORBIDDEN_PUBLIC_ARTIFACT_TOKENS = (
    "/.env",
    "/credentials",
    "/secrets",
    "/private_credentials",
)


def _dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _public_artifact_path(artifact: dict[str, Any]) -> Path:
    raw_path = artifact.get("path")
    artifact_id = str(artifact.get("artifact_id") or "<unknown>")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise TrustToolError(f"artifact {artifact_id}: path is missing")

    if Path(raw_path).is_absolute() or PureWindowsPath(raw_path).is_absolute():
        raise TrustToolError(f"artifact {artifact_id}: public release path must be repo-relative")

    normalized = raw_path.replace("\\", "/").strip()
    if normalized.startswith("../") or "/../" in normalized or normalized == "..":
        raise TrustToolError(f"artifact {artifact_id}: public release path cannot traverse directories")

    normalized_lower = normalized.lower().lstrip("./")
    if any(normalized_lower.startswith(prefix) for prefix in FORBIDDEN_PUBLIC_ARTIFACT_PREFIXES):
        raise TrustToolError(
            f"artifact {artifact_id}: public release path references private/local artifact storage"
        )
    token_scan = "/" + normalized_lower
    if any(token in token_scan for token in FORBIDDEN_PUBLIC_ARTIFACT_TOKENS):
        raise TrustToolError(
            f"artifact {artifact_id}: public release path references private credentials or secrets"
        )

    artifact_path = (PROJECT_ROOT / normalized).resolve()
    try:
        artifact_path.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise TrustToolError(f"artifact {artifact_id}: path escapes repository root") from exc
    return artifact_path


def expected_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    manifest = deepcopy(load_json(manifest_path))
    for artifact in manifest.get("artifact_hashes", []):
        if not isinstance(artifact, dict):
            continue
        artifact_path = _public_artifact_path(artifact)
        artifact["sha256"] = sha256_file(artifact_path)
    return manifest


def expected_signature(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    signature_path: Path = DEFAULT_SIGNATURE_PATH,
) -> dict[str, Any]:
    signed_at = None
    if signature_path.exists():
        existing = load_json(signature_path)
        signed_at = str(existing.get("signed_at") or "") or None
    if signed_at is None:
        manifest = load_json(manifest_path)
        signed_at = str(manifest.get("generated_at") or "") or None
    return build_alpha_signature_payload(manifest_path, signed_at=signed_at)


def check_release_hashes(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    signature_path: Path = DEFAULT_SIGNATURE_PATH,
) -> dict[str, Any]:
    current_manifest = load_json(manifest_path)
    next_manifest = expected_manifest(manifest_path)
    manifest_ok = current_manifest == next_manifest

    current_signature = load_json(signature_path) if signature_path.exists() else {}
    next_signature = expected_signature(manifest_path, signature_path)
    signature_ok = current_signature == next_signature

    return {
        "ok": manifest_ok and signature_ok,
        "manifest_ok": manifest_ok,
        "signature_ok": signature_ok,
        "manifest_path": str(manifest_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "signature_path": str(signature_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }


def write_release_hashes(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    signature_path: Path = DEFAULT_SIGNATURE_PATH,
) -> dict[str, Any]:
    next_manifest = expected_manifest(manifest_path)
    _dump_json(manifest_path, next_manifest)
    next_signature = expected_signature(manifest_path, signature_path)
    _dump_json(signature_path, next_signature)
    return check_release_hashes(manifest_path, signature_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Fail if hashes are stale.")
    mode.add_argument("--write", action="store_true", help="Rewrite stale public release hashes.")
    args = parser.parse_args()

    result = write_release_hashes() if args.write else check_release_hashes()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
