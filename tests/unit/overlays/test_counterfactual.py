from __future__ import annotations

import json
from pathlib import Path

from app.overlays.counterfactual import counterfactual_membrane


def test_overlay_changes_schedule_without_mutating_baseline() -> None:
    baseline = {"selected_days": [2, 3, 4]}
    overlay = json.loads(Path("examples/overlays/company_payroll_overlay.json").read_text(encoding="utf-8"))
    membrane = counterfactual_membrane(baseline, overlay)
    assert membrane["baseline"]["selected_days"] == [2, 3, 4]
    assert membrane["changed"]["selected_days"] == [3, 4]
    assert membrane["membrane_kind"] == "counterfactual"
