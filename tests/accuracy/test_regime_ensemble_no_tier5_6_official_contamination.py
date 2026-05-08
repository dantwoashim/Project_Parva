import json
import subprocess
from pathlib import Path

ROOT = Path("data/future_bs/accuracy_lab")


def _ensure_regime_artifacts() -> None:
    if not (ROOT / "regime_aware_loop_history.json").exists():
        subprocess.run(["python", "scripts/future_bs/optimize_regime_aware_accuracy_loop.py"], check=True)


def test_regime_ensemble_rejects_tier5_6_official_contamination():
    _ensure_regime_artifacts()
    history = json.loads((ROOT / "regime_aware_loop_history.json").read_text(encoding="utf-8"))
    candidates = {
        item["candidate"]["candidate_id"]: item
        for item in history["loop_history"]
    }
    contaminated = candidates["all_witness_training_rejected_for_official"]

    assert contaminated["accepted"] is False
    assert "no_tier_5_6_official_contamination" in contaminated["gate"]["failed_checks"]
