from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.release.verify_release import ReleaseVerificationError, verify_release


MANIFEST = Path("data/public/releases/parva-bs-public-demo.manifest.json")


def test_public_demo_release_verifies():
    messages = verify_release(MANIFEST.resolve())

    assert any("source-registry" in message for message in messages)
    assert any("calculation-trace-schema" in message for message in messages)


def test_release_verifier_fails_on_hash_mismatch(tmp_path):
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload["artifact_hashes"][0]["sha256"] = "0" * 64
    bad_manifest = tmp_path / "bad.manifest.json"
    bad_manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with pytest.raises(ReleaseVerificationError, match="hash mismatch"):
        verify_release(bad_manifest.resolve())
