import json
import subprocess
from pathlib import Path

ROOT = Path("data/future_bs/accuracy_lab")


def _ensure_regime_artifacts() -> None:
    if not (ROOT / "regime_ensemble_metrics.json").exists():
        subprocess.run(["python", "scripts/future_bs/optimize_regime_aware_accuracy_loop.py"], check=True)


def test_regime_ensemble_preserves_official_2078_2083():
    _ensure_regime_artifacts()
    payload = json.loads((ROOT / "regime_ensemble_metrics.json").read_text(encoding="utf-8"))
    metric = payload["best_metrics"]["official_strict"]

    assert metric["total_months_tested"] == 72
    assert metric["exact_matches"] == 72
    assert metric["wrong_green_count"] == 0
    assert metric["false_green_rate"] == 0.0
