from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.release.regenerate_public_release_hashes import expected_manifest
from tools.trust.common import TrustToolError

MANIFEST = Path("data/public/releases/parva-bs-public-demo.manifest.json")


def _manifest_with_path(tmp_path: Path, artifact_path: str) -> Path:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["artifact_hashes"][0]["path"] = artifact_path
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return manifest_path


def test_expected_manifest_rejects_absolute_artifact_path(tmp_path):
    absolute_path = str((tmp_path / "source.json").resolve())
    manifest_path = _manifest_with_path(tmp_path, absolute_path)

    with pytest.raises(TrustToolError, match="repo-relative"):
        expected_manifest(manifest_path)


def test_expected_manifest_rejects_private_artifact_storage(tmp_path):
    manifest_path = _manifest_with_path(tmp_path, "data/future_bs/private/predictions.json")

    with pytest.raises(TrustToolError, match="private/local artifact storage"):
        expected_manifest(manifest_path)


def test_expected_manifest_rejects_directory_traversal(tmp_path):
    manifest_path = _manifest_with_path(tmp_path, "../outside.json")

    with pytest.raises(TrustToolError, match="cannot traverse"):
        expected_manifest(manifest_path)
