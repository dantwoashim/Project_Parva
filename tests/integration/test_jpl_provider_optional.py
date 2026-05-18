from __future__ import annotations

import os
from pathlib import Path

import pytest
from app.panchanga.ephemeris_provider import JplEphemerisProvider


def test_jpl_provider_reports_unavailable_without_kernel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PARVA_JPL_KERNEL_PATH", raising=False)
    monkeypatch.delenv("PARVA_JPL_DE440_KERNEL", raising=False)
    metadata = JplEphemerisProvider().metadata()

    assert metadata["available"] is False
    assert metadata["kernel_hash"] is None
    assert metadata["boundary_vector"]["not_authority"] is True


def test_jpl_provider_verifies_configured_kernel_hash(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    kernel = tmp_path / "tiny-test-kernel.bsp"
    kernel.write_bytes(b"not-a-real-jpl-kernel-test-fixture")
    monkeypatch.setenv("PARVA_JPL_KERNEL_PATH", str(kernel))
    metadata = JplEphemerisProvider().metadata()
    monkeypatch.setenv("PARVA_JPL_KERNEL_SHA256", metadata["kernel_hash"])

    verified = JplEphemerisProvider().metadata()

    assert verified["available"] is True
    assert verified["kernel_hash"] == metadata["kernel_hash"]
    assert verified["jpl_backed"] is True


def test_jpl_provider_rejects_hash_mismatch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    kernel = tmp_path / "tiny-test-kernel.bsp"
    kernel.write_bytes(b"not-a-real-jpl-kernel-test-fixture")
    monkeypatch.setenv("PARVA_JPL_KERNEL_PATH", str(kernel))
    monkeypatch.setenv("PARVA_JPL_KERNEL_SHA256", "sha256:bad")

    with pytest.raises(ValueError, match="kernel hash"):
        JplEphemerisProvider().metadata()


@pytest.mark.skipif(not os.getenv("PARVA_JPL_KERNEL_PATH"), reason="optional JPL kernel path is not configured")
def test_optional_jpl_kernel_metadata_lane() -> None:
    metadata = JplEphemerisProvider().metadata()

    assert metadata["available"] is True
    assert metadata["kernel_hash"].startswith("sha256:")
    assert metadata["boundary_vector"]["not_authority"] is True
