#!/usr/bin/env python3
"""Build a public release artifact manifest with pinned hashes."""

from __future__ import annotations

import json
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT = PROJECT_ROOT / "data" / "public" / "release-artifact-manifest.json"

ARTIFACT_PATHS = [
    "docs/api-docs/openapi.public-reference.json",
    "packages/parva-local-kernel/package.json",
    "packages/parva-python/pyproject.toml",
    "packages/parva-js/package.json",
    "reports/source_coverage/coverage_matrix.json",
    "reports/source_coverage/coverage_matrix.md",
    "examples/external/reviewer-bundle/manifest.json",
]

ARTIFACT_DIRS = [
    "tests/fixtures/proof",
    "examples/external/proofpacks",
    "examples/external/timepacks",
]


def _sha256(path: Path) -> str:
    payload = _portable_artifact_bytes(path)
    digest = sha256()
    digest.update(payload)
    return f"sha256:{digest.hexdigest()}"


def _portable_artifact_bytes(path: Path) -> bytes:
    """Hash text artifacts after Git-style EOL normalization for CI parity."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "git_unavailable"


def _iter_artifacts() -> list[Path]:
    paths = [PROJECT_ROOT / rel for rel in ARTIFACT_PATHS]
    for rel in ARTIFACT_DIRS:
        root = PROJECT_ROOT / rel
        if root.exists():
            paths.extend(path for path in root.rglob("*") if path.is_file())
    return sorted(set(paths), key=lambda path: path.relative_to(PROJECT_ROOT).as_posix())


def build_manifest() -> dict[str, Any]:
    artifacts = []
    for path in _iter_artifacts():
        if not path.exists():
            raise SystemExit(f"required release artifact missing: {path.relative_to(PROJECT_ROOT)}")
        artifacts.append(
            {
                "path": path.relative_to(PROJECT_ROOT).as_posix(),
                "sha256": _sha256(path),
                "bytes": len(_portable_artifact_bytes(path)),
            }
        )
    return {
        "schema": "parva-release-artifact-manifest-v1",
        "git_commit_at_generation": _git_head(),
        "generated_at": "reproducible",
        "claim_boundary": "release_artifact_manifest_not_external_validation",
        "not_authority": True,
        "artifacts": artifacts,
        "verification_summary": {
            "public_gate": "scripts/release/verify_public.py",
            "local_kernel_package": "scripts/release/check_local_kernel_package.py",
            "source_coverage": "scripts/release/generate_source_coverage_report.py --check",
        },
    }


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = build_manifest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(PROJECT_ROOT)} with {len(payload['artifacts'])} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
