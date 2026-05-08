import json
import subprocess
from pathlib import Path


def test_official_claim_readiness_requires_sufficient_corpus():
    path = Path("data/future_bs/accuracy_lab/accuracy_readiness_final.json")
    if not path.exists():
        subprocess.run(["python", "scripts/future_bs/run_accuracy_loop.py", "--final"], check=True)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["official_cases"] < payload["required_official_cases"]:
        assert payload["claim_ready_with_sufficient_corpus"] is False
        assert payload["claim_ready_99_green_zone"] is False
