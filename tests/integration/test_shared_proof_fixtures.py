from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from app.membranes.verifier import verify_membrane
from app.sources.hashing import canonical_json_hash
from app.witnesses.hashing import witness_hash

FIXTURE_ROOT = Path("tests/fixtures/proof")


def _fixtures(group: str) -> list[dict[str, Any]]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((FIXTURE_ROOT / group).glob("*.json"))
    ]


def _make_wrong_but_self_consistent(membrane: dict[str, Any]) -> dict[str, Any]:
    tampered = deepcopy(membrane)
    first_field = next(iter(tampered["result"]))
    value = tampered["result"][first_field]
    tampered["result"][first_field] = not value if isinstance(value, bool) else "tampered"
    tampered["proof_pack"]["steps"][-1]["output_hash"] = f"sha256:{canonical_json_hash(tampered['result'])}"
    tampered["witness"]["output_hash"] = f"sha256:{canonical_json_hash(tampered['result'])}"
    witness_without_id = {key: val for key, val in tampered["witness"].items() if key != "witness_id"}
    new_id = witness_hash(witness_without_id)
    tampered["witness"]["witness_id"] = new_id
    tampered["witness_hash"] = new_id
    return tampered


@pytest.mark.parametrize("fixture", _fixtures("civil") + _fixtures("panchanga"), ids=lambda item: item["name"])
def test_shared_proof_fixture_verifies_in_backend(fixture: dict[str, Any]) -> None:
    assert verify_membrane(fixture["membrane"]) == (True, "verified")
    assert fixture["expected_replay_result"] == fixture["membrane"]["result"]


@pytest.mark.parametrize("fixture", _fixtures("civil") + _fixtures("panchanga"), ids=lambda item: item["name"])
def test_shared_proof_fixture_rejects_wrong_but_self_consistent_result(fixture: dict[str, Any]) -> None:
    tampered = _make_wrong_but_self_consistent(fixture["membrane"])
    assert verify_membrane(tampered) == (False, "replayed_result_mismatch")


def test_panchanga_fixture_rejects_tampered_ephemeris_hash() -> None:
    fixture = _fixtures("panchanga")[0]
    membrane = deepcopy(fixture["membrane"])
    membrane["ephemeris_metadata"]["kernel_hash"] = "sha256:wrong"

    assert verify_membrane(membrane) == (False, "ephemeris_fixture_hash_mismatch")


def test_panchanga_identity_changes_with_location_and_ayanamsa() -> None:
    fixture = _fixtures("panchanga")[0]["membrane"]
    changed_location = deepcopy(fixture)
    changed_location["canonical_query"]["context"]["latitude"] = 28.0
    changed_ayanamsa = deepcopy(fixture)
    changed_ayanamsa["canonical_query"]["context"]["ayanamsa"] = "raman"

    assert verify_membrane(changed_location) == (False, "identity_hash_mismatch")
    assert verify_membrane(changed_ayanamsa) == (False, "identity_hash_mismatch")
