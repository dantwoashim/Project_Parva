from __future__ import annotations

from app.provenance.light_cone import blast_radius


def test_light_cone_finds_affected_identities() -> None:
    assert blast_radius("source-a", {"report-1": ["source-a"], "report-2": ["source-b"]}) == ["report-1"]
