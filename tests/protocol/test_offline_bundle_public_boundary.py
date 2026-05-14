from __future__ import annotations

from app.services.protocol_service import offline_bundle_manifest_payload


def test_offline_bundle_manifest_excludes_private_artifacts() -> None:
    manifest = offline_bundle_manifest_payload()
    paths = [item["path"] for item in manifest["contents"]]

    assert manifest["signature_status"] == "unsigned_preview"
    assert manifest["signature"] is None
    assert paths
    assert all("source_archive" not in path for path in paths)
    assert all("private" not in path for path in paths)
    assert all(path in manifest["checksums"] for path in paths)
