from __future__ import annotations

import json
from pathlib import Path

from app.conformance.report import render_conformance_report
from app.conformance.runner import run_conformance_capsule


def test_conformance_capsule_runs_from_local_repo_data() -> None:
    capsule = json.loads(Path("examples/conformance/payroll_core_2082.json").read_text(encoding="utf-8"))
    result = run_conformance_capsule(capsule)
    report = render_conformance_report(result)
    assert result["claim_boundary"] == "conformance_report_not_certification"
    assert "invalid_bs_date" in report
    assert "review_required_future_sensitive" in report
    assert "not certification" in report
