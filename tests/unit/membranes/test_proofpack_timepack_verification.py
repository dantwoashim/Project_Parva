from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from app.membranes.capsule import build_convert_bs_to_ad_capsule
from app.membranes.proofpack import proof_pack, verify_proof_pack
from app.membranes.timepack import build_timepack, verify_timepack


def test_replay_proofpack_verifies_and_tamper_fails() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)
    pack = proof_pack(membrane, "replay")

    assert verify_proof_pack(pack) == (True, "verified")

    tampered = deepcopy(pack)
    tampered["membrane"]["result"]["ad_date"] = "2025-04-15"

    assert verify_proof_pack(tampered) == (False, "witness_output_hash_mismatch")


def test_timepack_verifies_and_aggregate_tamper_fails() -> None:
    membrane = build_convert_bs_to_ad_capsule(2082, 1, 1)
    timepack = build_timepack(membrane, "replay")

    assert verify_timepack(timepack) == (True, "verified")

    tampered = deepcopy(timepack)
    tampered["aggregate_witness_hash"] = "sha256:wrong"

    assert verify_timepack(tampered) == (False, "timepack_aggregate_hash_mismatch")


def test_cli_commands_are_exposed() -> None:
    source = Path("packages/parva-python/parva/cli.py").read_text(encoding="utf-8")

    assert "verify-proofpack" in source
    assert "verify-timepack" in source
