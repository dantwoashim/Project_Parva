#!/usr/bin/env python3
"""Build a lightweight uncertainty calibration artifact from evaluation history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HISTORY_PATH = PROJECT_ROOT / "reports" / "evaluation_history.jsonl"
OUT_PATH = PROJECT_ROOT / "reports" / "uncertainty_calibration.json"


def _load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    rows = []
    for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def main() -> None:
    rows = _load_history()
    total_cases = sum(int(r.get("total", 0)) for r in rows)
    total_passed = sum(int(r.get("passed", 0)) for r in rows)

    empirical = (total_passed / total_cases) if total_cases else 0.95

    # Keep priors conservative even if tiny sample appears perfect.
    exact_prob = min(0.999, max(0.95, empirical))
    confident_prob = min(0.995, max(0.9, empirical - 0.01))
    estimated_prob = min(0.95, max(0.8, empirical - 0.07))
    uncertain_prob = min(0.85, max(0.65, empirical - 0.2))
    degraded_prob = min(0.75, max(0.5, empirical - 0.3))

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(HISTORY_PATH),
        "data_points": total_cases,
        "empirical_pass_rate": round(empirical, 4),
        "levels": {
            "exact": {"probability": round(exact_prob, 4), "interval_hours": 0.5},
            "confident": {"probability": round(confident_prob, 4), "interval_hours": 6.0},
            "estimated": {"probability": round(estimated_prob, 4), "interval_hours": 24.0},
            "uncertain": {"probability": round(uncertain_prob, 4), "interval_hours": 48.0},
            "degraded": {"probability": round(degraded_prob, 4), "interval_hours": 72.0},
        },
        "methodology": "Empirical pass-rate shrinkage with conservative priors by certainty class",
    }

    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"data_points": total_cases, "empirical_pass_rate": round(empirical, 4)}, indent=2))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
