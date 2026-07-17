"""Fail-closed validation for NAIF DAF/SPK planetary kernels."""

from __future__ import annotations

import hashlib
import math
import re
import struct
from dataclasses import dataclass
from pathlib import Path

DAF_RECORD_BYTES = 1024
DAF_WORD_BYTES = 8
REQUIRED_PLANETARY_SEGMENTS = frozenset({(3, 0), (10, 0), (301, 3), (399, 3)})
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class SpkValidationError(ValueError):
    """Raised when a configured file is not an acceptable planetary SPK."""


@dataclass(frozen=True)
class SpkSegment:
    start_tdb_seconds: float
    end_tdb_seconds: float
    target: int
    center: int
    frame: int
    data_type: int
    start_address: int
    end_address: int

    def covers(self, epoch_tdb_seconds: float) -> bool:
        return self.start_tdb_seconds <= epoch_tdb_seconds <= self.end_tdb_seconds


@dataclass(frozen=True)
class SpkInventory:
    byte_order: str
    internal_name: str
    segments: tuple[SpkSegment, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _integer_double(value: float, *, field: str) -> int:
    if not math.isfinite(value) or value < 0 or not value.is_integer():
        raise SpkValidationError(f"invalid DAF {field}: {value!r}")
    return int(value)


def inspect_spk(path: Path) -> SpkInventory:
    """Parse the DAF file record and complete SPK segment inventory."""

    if not path.is_file():
        raise SpkValidationError("SPK kernel path is not a regular file")
    size = path.stat().st_size
    if size < DAF_RECORD_BYTES * 3 or size % DAF_RECORD_BYTES:
        raise SpkValidationError("SPK kernel size is not a complete DAF record sequence")

    record_count = size // DAF_RECORD_BYTES
    with path.open("rb") as stream:
        header = stream.read(DAF_RECORD_BYTES)
        if header[:8] != b"DAF/SPK ":
            raise SpkValidationError("kernel does not have a DAF/SPK file record")

        binary_format = header[88:96]
        if binary_format == b"LTL-IEEE":
            endian = "<"
            byte_order = "little"
        elif binary_format == b"BIG-IEEE":
            endian = ">"
            byte_order = "big"
        else:
            raise SpkValidationError("kernel uses an unsupported DAF binary format")

        nd, ni = struct.unpack(f"{endian}ii", header[8:16])
        if (nd, ni) != (2, 6):
            raise SpkValidationError(f"invalid SPK summary dimensions: ND={nd}, NI={ni}")
        if b"FTPSTR" not in header or b"ENDFTP" not in header:
            raise SpkValidationError("DAF file record is missing the FTP corruption marker")

        first_summary, last_summary, first_free = struct.unpack(f"{endian}iii", header[76:88])
        if not (2 <= first_summary <= record_count and 2 <= last_summary <= record_count):
            raise SpkValidationError("DAF summary record pointer is outside the file")
        if not (1 < first_free <= size // DAF_WORD_BYTES + 1):
            raise SpkValidationError("DAF free-address pointer is outside the file")

        summary_words = nd + (ni + 1) // 2
        max_summaries = (DAF_RECORD_BYTES // DAF_WORD_BYTES - 3) // summary_words
        segments: list[SpkSegment] = []
        visited: set[int] = set()
        previous_summary = 0
        summary_record = first_summary

        while summary_record:
            if summary_record in visited:
                raise SpkValidationError("DAF summary record chain contains a cycle")
            if not 2 <= summary_record <= record_count:
                raise SpkValidationError("DAF summary record chain leaves the file")
            visited.add(summary_record)

            stream.seek((summary_record - 1) * DAF_RECORD_BYTES)
            record = stream.read(DAF_RECORD_BYTES)
            if len(record) != DAF_RECORD_BYTES:
                raise SpkValidationError("DAF summary record is truncated")
            next_value, previous_value, count_value = struct.unpack(f"{endian}ddd", record[:24])
            next_summary = _integer_double(next_value, field="next summary record")
            declared_previous = _integer_double(previous_value, field="previous summary record")
            summary_count = _integer_double(count_value, field="summary count")
            if declared_previous != previous_summary:
                raise SpkValidationError("DAF summary record chain has an invalid back pointer")
            if not 0 <= summary_count <= max_summaries:
                raise SpkValidationError("DAF summary count exceeds record capacity")

            for index in range(summary_count):
                offset = 24 + index * summary_words * DAF_WORD_BYTES
                start, end = struct.unpack(f"{endian}dd", record[offset : offset + 16])
                target, center, frame, data_type, start_address, end_address = struct.unpack(
                    f"{endian}6i", record[offset + 16 : offset + 40]
                )
                if not math.isfinite(start) or not math.isfinite(end) or start >= end:
                    raise SpkValidationError("SPK segment has an invalid coverage interval")
                if frame <= 0 or data_type <= 0:
                    raise SpkValidationError("SPK segment has an invalid frame or data type")
                if not (1 <= start_address <= end_address < first_free):
                    raise SpkValidationError("SPK segment address is outside the declared DAF data area")
                segments.append(
                    SpkSegment(
                        start_tdb_seconds=start,
                        end_tdb_seconds=end,
                        target=target,
                        center=center,
                        frame=frame,
                        data_type=data_type,
                        start_address=start_address,
                        end_address=end_address,
                    )
                )

            previous_summary = summary_record
            summary_record = next_summary

        if previous_summary != last_summary:
            raise SpkValidationError("DAF last-summary pointer does not match the summary chain")
        if not segments:
            raise SpkValidationError("SPK kernel contains no segment summaries")

    internal_name = header[16:76].decode("ascii", errors="strict").rstrip()
    return SpkInventory(byte_order=byte_order, internal_name=internal_name, segments=tuple(segments))


def validate_planetary_spk(
    path: Path,
    *,
    expected_sha256: str,
    expected_size: int | None = None,
    epoch_tdb_seconds: float = 0.0,
) -> SpkInventory:
    """Validate identity, structure, required bodies, and epoch coverage."""

    normalized_hash = expected_sha256.lower().removeprefix("sha256:")
    if not _SHA256_RE.fullmatch(normalized_hash):
        raise SpkValidationError("a full 64-character SHA-256 digest is required")
    if expected_size is not None and path.stat().st_size != expected_size:
        raise SpkValidationError(
            f"SPK size mismatch: expected {expected_size}, got {path.stat().st_size}"
        )
    actual_hash = sha256_file(path)
    if actual_hash != normalized_hash:
        raise SpkValidationError(
            f"SPK SHA-256 mismatch: expected {normalized_hash}, got {actual_hash}"
        )

    inventory = inspect_spk(path)
    coverage = {
        (segment.target, segment.center)
        for segment in inventory.segments
        if segment.covers(epoch_tdb_seconds)
    }
    missing = sorted(REQUIRED_PLANETARY_SEGMENTS - coverage)
    if missing:
        raise SpkValidationError(
            f"SPK lacks required Sun/Earth/Moon coverage at epoch {epoch_tdb_seconds}: {missing}"
        )
    return inventory


__all__ = [
    "REQUIRED_PLANETARY_SEGMENTS",
    "SpkInventory",
    "SpkSegment",
    "SpkValidationError",
    "inspect_spk",
    "sha256_file",
    "validate_planetary_spk",
]
