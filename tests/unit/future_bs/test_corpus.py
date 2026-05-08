"""Corpus and source registry tests."""

from app.future_bs.corpus import corpus_summary, get_corpus_row, load_corpus
from app.future_bs.source_registry import load_source_registry, source_payload


def test_corpus_loads_source_labeled_rows():
    corpus = load_corpus()

    assert 2083 in corpus
    assert corpus[2083].source_type == "official_verified"
    if 2085 in corpus:
        assert corpus[2085].verification_status == "needs_review"


def test_corpus_summary_exposes_claim_boundary():
    summary = corpus_summary()

    assert summary["years"] >= 6
    assert "official_claim_boundary" in summary
    assert summary["source_type_counts"]["official_verified"] >= 1


def test_source_registry_resolves_known_source():
    registry = load_source_registry()
    payload = source_payload(get_corpus_row(2083).source_reference)

    assert registry["status"] in {"public_holdout_sample", "mixed_verification_corpus"}
    assert payload["source_type"] == "official_verified"
