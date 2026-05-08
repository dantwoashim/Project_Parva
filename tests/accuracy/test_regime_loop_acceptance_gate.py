import json
import subprocess
from pathlib import Path

ROOT = Path("data/future_bs/accuracy_lab")


def _ensure_regime_artifacts() -> None:
    if not (ROOT / "regime_aware_loop_history.json").exists():
        subprocess.run(["python", "scripts/future_bs/optimize_regime_aware_accuracy_loop.py"], check=True)


def test_regime_loop_records_rejections_and_stop_condition():
    _ensure_regime_artifacts()
    history = json.loads((ROOT / "regime_aware_loop_history.json").read_text(encoding="utf-8"))
    rows = history["loop_history"]

    assert rows
    assert any(item["accepted"] for item in rows)
    assert any(not item["accepted"] for item in rows)
    assert all("gate" in item and "reason" in item for item in rows)

    rejected = [item for item in rows if not item["accepted"]]
    assert any(item["gate"]["failed_checks"] for item in rejected)
