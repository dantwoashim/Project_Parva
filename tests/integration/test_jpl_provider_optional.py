from __future__ import annotations

import hashlib
import os
import struct
from pathlib import Path

import pytest
from app.panchanga.ephemeris_provider import JplEphemerisProvider, provider_from_id


def _write_structural_spk(path: Path) -> str:
    payload = bytearray(4 * 1024)
    payload[:8] = b"DAF/SPK "
    struct.pack_into("<ii", payload, 8, 2, 6)
    payload[16:76] = b"PARVA PROVIDER TEST".ljust(60)
    struct.pack_into("<iii", payload, 76, 2, 2, 513)
    payload[88:96] = b"LTL-IEEE"
    ftp_marker = b"FTPSTR:\r:\n:\r\n:\r\x00:\x81:\x10\xce:ENDFTP"
    payload[699 : 699 + len(ftp_marker)] = ftp_marker
    segments = ((3, 0), (10, 0), (301, 3), (399, 3))
    struct.pack_into("<ddd", payload, 1024, 0.0, 0.0, float(len(segments)))
    for index, (target, center) in enumerate(segments):
        offset = 1024 + 24 + index * 40
        start_address = 385 + index * 2
        struct.pack_into(
            "<dd6i",
            payload,
            offset,
            -1_000.0,
            1_000.0,
            target,
            center,
            1,
            2,
            start_address,
            start_address + 1,
        )
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_jpl_provider_reports_unavailable_without_kernel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PARVA_JPL_KERNEL_PATH", raising=False)
    monkeypatch.delenv("PARVA_JPL_DE440_KERNEL", raising=False)
    metadata = JplEphemerisProvider().metadata()

    assert metadata["available"] is False
    assert metadata["kernel_hash"] is None
    assert metadata["boundary_vector"]["not_authority"] is True


def test_jpl_provider_requires_configured_kernel_hash(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    kernel = tmp_path / "tiny-test-kernel.bsp"
    kernel.write_bytes(b"not-a-real-jpl-kernel-test-fixture")
    monkeypatch.setenv("PARVA_JPL_KERNEL_PATH", str(kernel))
    monkeypatch.delenv("PARVA_JPL_KERNEL_SHA256", raising=False)

    with pytest.raises(ValueError, match="PARVA_JPL_KERNEL_SHA256 is required"):
        JplEphemerisProvider().metadata()


def test_jpl_provider_rejects_non_spk_with_matching_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    kernel = tmp_path / "tiny-test-kernel.bsp"
    payload = b"not-a-real-jpl-kernel-test-fixture"
    kernel.write_bytes(payload)
    monkeypatch.setenv("PARVA_JPL_KERNEL_PATH", str(kernel))
    monkeypatch.setenv("PARVA_JPL_KERNEL_SHA256", hashlib.sha256(payload).hexdigest())

    with pytest.raises(ValueError, match="DAF record sequence"):
        JplEphemerisProvider().metadata()


def test_jpl_provider_reports_verified_kernel_as_metadata_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    kernel = tmp_path / "structural-test-kernel.bsp"
    digest = _write_structural_spk(kernel)
    monkeypatch.setenv("PARVA_JPL_KERNEL_PATH", str(kernel))
    monkeypatch.setenv("PARVA_JPL_KERNEL_SHA256", digest)
    monkeypatch.setenv("PARVA_JPL_KERNEL_SIZE", str(kernel.stat().st_size))

    metadata = JplEphemerisProvider().metadata()

    assert metadata["available"] is True
    assert metadata["calculation_available"] is False
    assert metadata["jpl_backed"] is False
    assert metadata["provider_kind"] == "verified_kernel_metadata_only"
    assert metadata["kernel_hash"] == f"sha256:{digest}"


def test_jpl_provider_rejects_hash_mismatch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    kernel = tmp_path / "tiny-test-kernel.bsp"
    kernel.write_bytes(b"not-a-real-jpl-kernel-test-fixture")
    monkeypatch.setenv("PARVA_JPL_KERNEL_PATH", str(kernel))
    monkeypatch.setenv("PARVA_JPL_KERNEL_SHA256", f"sha256:{'0' * 64}")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        JplEphemerisProvider().metadata()


def test_jpl_provider_cannot_be_selected_for_panchanga() -> None:
    with pytest.raises(ValueError, match="cannot be selected"):
        provider_from_id("jpl_de440")


@pytest.mark.skipif(
    not (os.getenv("PARVA_JPL_KERNEL_PATH") and os.getenv("PARVA_JPL_KERNEL_SHA256")),
    reason="optional JPL kernel path and SHA-256 are not configured",
)
def test_optional_jpl_kernel_metadata_lane() -> None:
    metadata = JplEphemerisProvider().metadata()

    assert metadata["available"] is True
    assert metadata["kernel_hash"].startswith("sha256:")
    assert metadata["calculation_available"] is False
    assert metadata["jpl_backed"] is False
    assert metadata["boundary_vector"]["not_authority"] is True
