"""Static bundle bitplane helpers."""

from __future__ import annotations

from app.bitplanes.causal import CausalBitplane


def build_working_day_plane(days: int, weekend_offsets: set[int]) -> CausalBitplane:
    cause_stamps = tuple(
        {
            "day": index,
            "value": index not in weekend_offsets,
            "reason": "default_working_day" if index not in weekend_offsets else "weekend_offset",
            "source": "static_bundle_manifest",
            "policy": "working_day_bitplane@v1",
        }
        for index in range(1, days + 1)
    )
    return CausalBitplane(
        name="working_day",
        bits=tuple(index not in weekend_offsets for index in range(1, days + 1)),
        witness_refs=("static_bundle_manifest",),
        cause_stamps=cause_stamps,
    )
