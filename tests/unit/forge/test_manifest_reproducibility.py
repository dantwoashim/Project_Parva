from __future__ import annotations

from app.forge.manifest import build_manifest
from app.forge.static_bundle import build_year_bundle
from app.forge.verify import verify_manifest


def test_static_bundle_manifest_is_reproducible(tmp_path) -> None:
    build_year_bundle(2082, tmp_path)
    first = build_manifest(tmp_path)
    build_year_bundle(2082, tmp_path)
    second = build_manifest(tmp_path)
    assert first == second
    assert verify_manifest(tmp_path)
