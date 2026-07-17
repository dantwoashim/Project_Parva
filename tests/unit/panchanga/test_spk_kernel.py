from __future__ import annotations

import hashlib
import struct
from pathlib import Path

import pytest
from app.panchanga.spk_kernel import SpkValidationError, validate_planetary_spk

_REQUIRED_SEGMENTS = ((3, 0), (10, 0), (301, 3), (399, 3))


def _write_spk(
    path: Path,
    *,
    segments: tuple[tuple[int, int], ...] = _REQUIRED_SEGMENTS,
    start: float = -1_000.0,
    end: float = 1_000.0,
) -> str:
    payload = bytearray(4 * 1024)
    payload[:8] = b"DAF/SPK "
    struct.pack_into("<ii", payload, 8, 2, 6)
    payload[16:76] = b"PARVA TEST SPK".ljust(60)
    struct.pack_into("<iii", payload, 76, 2, 2, 513)
    payload[88:96] = b"LTL-IEEE"
    ftp_marker = b"FTPSTR:\r:\n:\r\n:\r\x00:\x81:\x10\xce:ENDFTP"
    payload[699 : 699 + len(ftp_marker)] = ftp_marker

    summary_offset = 1024
    struct.pack_into("<ddd", payload, summary_offset, 0.0, 0.0, float(len(segments)))
    for index, (target, center) in enumerate(segments):
        offset = summary_offset + 24 + index * 40
        start_address = 385 + index * 2
        struct.pack_into("<dd6i", payload, offset, start, end, target, center, 1, 2, start_address, start_address + 1)

    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def test_validate_planetary_spk_accepts_structural_kernel_with_required_coverage(tmp_path: Path) -> None:
    kernel = tmp_path / "valid.bsp"
    digest = _write_spk(kernel)

    inventory = validate_planetary_spk(
        kernel,
        expected_sha256=digest,
        expected_size=kernel.stat().st_size,
    )

    assert inventory.byte_order == "little"
    assert inventory.internal_name == "PARVA TEST SPK"
    assert len(inventory.segments) == 4


def test_validate_planetary_spk_rejects_random_file(tmp_path: Path) -> None:
    kernel = tmp_path / "random.bsp"
    kernel.write_bytes(b"x" * (3 * 1024))
    digest = hashlib.sha256(kernel.read_bytes()).hexdigest()

    with pytest.raises(SpkValidationError, match="DAF/SPK"):
        validate_planetary_spk(kernel, expected_sha256=digest)


def test_validate_planetary_spk_rejects_wrong_hash(tmp_path: Path) -> None:
    kernel = tmp_path / "wrong-hash.bsp"
    _write_spk(kernel)

    with pytest.raises(SpkValidationError, match="SHA-256 mismatch"):
        validate_planetary_spk(kernel, expected_sha256="0" * 64)


def test_validate_planetary_spk_rejects_truncated_file(tmp_path: Path) -> None:
    kernel = tmp_path / "truncated.bsp"
    digest = _write_spk(kernel)
    kernel.write_bytes(kernel.read_bytes()[:-1])

    with pytest.raises(SpkValidationError, match="size mismatch"):
        validate_planetary_spk(kernel, expected_sha256=digest, expected_size=4 * 1024)


def test_validate_planetary_spk_rejects_missing_required_body(tmp_path: Path) -> None:
    kernel = tmp_path / "missing-body.bsp"
    digest = _write_spk(kernel, segments=_REQUIRED_SEGMENTS[:-1])

    with pytest.raises(SpkValidationError, match="lacks required Sun/Earth/Moon coverage"):
        validate_planetary_spk(kernel, expected_sha256=digest)


def test_validate_planetary_spk_rejects_out_of_coverage_epoch(tmp_path: Path) -> None:
    kernel = tmp_path / "out-of-coverage.bsp"
    digest = _write_spk(kernel, start=-10.0, end=10.0)

    with pytest.raises(SpkValidationError, match="lacks required Sun/Earth/Moon coverage"):
        validate_planetary_spk(kernel, expected_sha256=digest, epoch_tdb_seconds=11.0)
