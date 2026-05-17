from __future__ import annotations

from app.bitplanes.attestation import attest_bitplane
from app.forge.bitplanes import build_working_day_plane


def test_bitplane_attestation_links_plane_and_manifest() -> None:
    plane = build_working_day_plane(5, {2})
    assert plane.bits == (True, False, True, True, True)
    attestation = attest_bitplane(plane, "sha256:manifest")
    assert attestation.plane_hash == plane.hash
    assert attestation.attestation_hash.startswith("sha256:")
