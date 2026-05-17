from __future__ import annotations

import pytest
from app.bitplanes.attestation import attest_bitplane
from app.bitplanes.causal import CausalBitplane
from app.forge.bitplanes import build_working_day_plane


def test_working_day_bitplane_has_per_bit_cause_stamps() -> None:
    plane = build_working_day_plane(5, {4})
    payload = plane.as_dict()

    assert len(payload["bits"]) == 5
    assert len(payload["cause_stamps"]) == 5
    assert payload["cause_stamps"][3]["reason"] == "weekend_offset"
    assert payload["cause_stamps"][3]["value"] is False
    assert payload["cause_stamps"][0]["reason"] == "default_working_day"
    assert payload["hash"].startswith("sha256:")


def test_causal_bitplane_rejects_unstamped_bits() -> None:
    with pytest.raises(ValueError, match="cause_stamps length"):
        CausalBitplane(
            name="working_day",
            bits=(True, False),
            witness_refs=("sample",),
            cause_stamps=({"day": 1},),
        )


def test_bitplane_attestation_binds_manifest_entry_hash() -> None:
    plane = build_working_day_plane(5, {4})
    attestation = attest_bitplane(
        plane,
        "sha256:manifest",
        manifest_entry_hash="sha256:plane-file",
    )
    payload = attestation.as_dict()

    assert payload["plane_hash"] == plane.hash
    assert payload["manifest_entry_hash"] == "sha256:plane-file"
    assert payload["attestation_hash"].startswith("sha256:")
