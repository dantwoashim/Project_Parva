"""Static bundle bitplane helpers."""

from __future__ import annotations

from app.bitplanes.causal import CausalBitplane


def build_working_day_plane(days: int, weekend_offsets: set[int]) -> CausalBitplane:
    return CausalBitplane(
        name="working_day",
        bits=tuple(index not in weekend_offsets for index in range(1, days + 1)),
        witness_refs=("static_bundle_manifest",),
    )
