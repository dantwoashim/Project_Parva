import csv
import json
import subprocess
from pathlib import Path

from app.future_bs.source_policy import POLICIES

ROOT = Path("data/future_bs/accuracy_lab")


def test_hamropatro_shadow_policy_is_not_official_claim_policy():
    policy = POLICIES["hamropatro_shadow_experimental"]
    assert policy["tier_5_6_allowed"] is True
    assert policy["shadow_only"] is True
    assert "official claim-readiness" in policy["claim_scope"]


def test_hamropatro_shadow_artifacts_are_generated_and_guarded():
    subprocess.run(["python", "scripts/future_bs/run_hamropatro_shadow_evaluation.py"], check=True)

    metrics_path = ROOT / "hamropatro_shadow_2000_2070_metrics.json"
    md_path = ROOT / "hamropatro_shadow_2000_2070_metrics.md"
    disagreements_path = ROOT / "hamropatro_shadow_2000_2070_disagreements.csv"
    queue_path = ROOT / "hamropatro_shadow_2000_2070_verification_queue.csv"

    for path in [metrics_path, md_path, disagreements_path, queue_path]:
        assert path.exists()
        assert path.stat().st_size > 0

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics["evaluation_mode"] == "hamropatro_shadow_experimental"
    assert metrics["source_type"] == "third_party_reference"
    assert metrics["source_tier"] == 6
    assert metrics["total_months_tested"] == 852
    assert metrics["calibration_policy"]["hamropatro_used_for_calibration"] is False
    assert metrics["calibration_policy"]["hamropatro_used_for_official_strict_metrics"] is False
    assert metrics["calibration_policy"]["hamropatro_used_for_official_claim_readiness"] is False
    assert metrics["calibration_policy"]["hamropatro_supported_rows_marked_official"] is False
    assert "official accuracy" in metrics["claim_scope"]

    md_text = md_path.read_text(encoding="utf-8")
    assert "shadow agreement" in md_text.lower()
    assert "not official accuracy" in md_text.lower()

    with disagreements_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows
    assert {row["official_claim_usable"] for row in rows} == {"False"}

    with queue_path.open(newline="", encoding="utf-8") as fh:
        queue = list(csv.DictReader(fh))
    assert 1 <= len(queue) <= 100
