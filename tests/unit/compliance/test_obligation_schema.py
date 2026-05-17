from __future__ import annotations

from pathlib import Path

from app.compliance.notice_ingestion import ingest_notice


def test_obligation_object_contains_boundary_and_deadline_membrane() -> None:
    flow = ingest_notice(Path("examples/notices/sample_notice.md").read_text(encoding="utf-8"))
    obligation = flow["obligation"]
    assert obligation["claim_type"] == "deadline_claim"
    assert obligation["deadline_bs"] == "2082-04-31"
    assert obligation["boundary"]["review_required"] is True
    assert flow["deadline_membrane"]["witness_hash"]


def test_notice_ingestion_extracts_structured_fields_from_template() -> None:
    flow = ingest_notice(
        """
        issuer: Fictional cooperative board
        published: 2082-03-15
        effective: 2082-04-01
        deadline: 2082-04-31
        action: Submit date-risk audit export.
        affected_party: cooperative_vendor
        jurisdiction: np:sample
        """
    )

    receipt = flow["extraction_receipt"]
    obligation = flow["obligation"]
    assert receipt["extraction"]["issuer"] == "Fictional cooperative board"
    assert receipt["extraction"]["required_action"] == "Submit date-risk audit export."
    assert obligation["effective_bs"] == "2082-04-01"
    assert obligation["required_action"] == "Submit date-risk audit export."


def test_notice_ingestion_requires_deadline() -> None:
    try:
        ingest_notice("issuer: sample\naction: Review only")
    except ValueError as exc:
        assert "deadline" in str(exc)
    else:
        raise AssertionError("notice without deadline should fail")
