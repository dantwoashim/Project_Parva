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
