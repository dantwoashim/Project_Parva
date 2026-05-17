from __future__ import annotations

import json
from pathlib import Path

from app.canonicalization.equivalence import equivalent
from app.canonicalization.normalize import canonicalize_query, identity_hash


def test_canonicalization_equivalence_corpus() -> None:
    corpus = json.loads(Path("tests/fixtures/canonicalization_equivalence.json").read_text(encoding="utf-8"))
    assert len(corpus["equivalent"]) >= 50
    assert len(corpus["different"]) >= 50
    for left, right in corpus["equivalent"]:
        assert equivalent(left, right)
    for left, right in corpus["different"]:
        assert not equivalent(left, right)


def test_hidden_defaults_are_expanded() -> None:
    canonical = canonicalize_query({"operation": "check_working_day", "input": {"date": "2082-01-01"}})
    assert canonical["context"]["place_id"] == "np:national:default"
    assert canonical["context"]["timezone"] == "asia/kathmandu"
    assert identity_hash(canonical).startswith("parva:id:v1:sha256:")
