from __future__ import annotations

from pathlib import Path

from app.compliance.notice_ingestion import ingest_notice
from app.compliance.report import render_obligation_report


def test_notice_to_obligation_flow_generates_report() -> None:
    flow = ingest_notice(Path("examples/notices/sample_notice.md").read_text(encoding="utf-8"))
    report = render_obligation_report(flow)
    assert "Required action" in report
    assert "Boundary" in report
    assert "not legal or tax authority" in report
