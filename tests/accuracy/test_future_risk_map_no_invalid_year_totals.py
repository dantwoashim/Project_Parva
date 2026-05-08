import json
import subprocess
from pathlib import Path

ROOT = Path("data/future_bs/accuracy_lab")


def _ensure_regime_artifacts() -> None:
    if not (ROOT / "future_2084_2099_risk_map.json").exists():
        subprocess.run(["python", "scripts/future_bs/optimize_regime_aware_accuracy_loop.py"], check=True)


def test_future_risk_map_has_no_invalid_parva_year_totals():
    _ensure_regime_artifacts()
    payload = json.loads((ROOT / "future_2084_2099_risk_map.json").read_text(encoding="utf-8"))

    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["invalid_year_total_count"] == 0
    assert payload["invalid_years"] == []
    assert payload["rows"]
