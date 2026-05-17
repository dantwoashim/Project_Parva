from __future__ import annotations

from app.membranes.branch import branch_set_membrane


def test_branch_membrane_preserves_multiple_boundaries() -> None:
    membrane = branch_set_membrane(
        [
            {"branch_id": "canonical", "result": {"date": "2082-01-01"}, "boundary": {"authority": "computed_uncertified"}},
            {"branch_id": "community", "result": {"date": "2082-01-02"}, "boundary": {"authority": "community_specific"}},
        ]
    )
    assert membrane["membrane_kind"] == "branch_set"
    assert len(membrane["branches"]) == 2
