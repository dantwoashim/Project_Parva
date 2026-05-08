import json
import subprocess
from pathlib import Path

ROOT = Path("data/future_bs/accuracy_lab")


def _ensure_regime_artifacts() -> None:
    if not (ROOT / "official_strict_green_certification.json").exists():
        subprocess.run(["python", "scripts/future_bs/optimize_regime_aware_accuracy_loop.py"], check=True)


def test_regime_green_certification_is_conservative_and_clean():
    _ensure_regime_artifacts()
    payload = json.loads((ROOT / "official_strict_green_certification.json").read_text(encoding="utf-8"))

    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["accuracy"] >= 0.99
    if payload["green_count"]:
        assert payload["green_accuracy"] >= 0.99
    else:
        assert payload["green_coverage"] == 0.0
    assert payload["wrong_green_count"] == 0
    assert payload["false_green_rate"] == 0.0
