from __future__ import annotations

from app.membranes.capsule import build_convert_bs_to_ad_capsule
from app.membranes.timepack import build_timepack
from app.membranes.verifier import verify_membrane


def test_timepacks_have_compact_audit_and_replay_levels() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)
    compact = build_timepack(membrane, "compact")
    audit = build_timepack(membrane, "audit")
    replay = build_timepack(membrane, "replay")
    assert len(str(compact)) < len(str(audit))
    assert replay["payload"]["offline_verifier"] == "parva_membrane_replay_v1"
    assert verify_membrane(replay["payload"]["membrane"])[0]
