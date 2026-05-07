#!/usr/bin/env python3
"""Generate the 2083 Ashwin red-team replay artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.red_team_2083 import replay_2083_ashwin  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/future_bs/reports/case_2083_ashwin_replay.json"))
    args = parser.parse_args()
    payload = replay_2083_ashwin()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "predicted_days": payload["parva_prediction_before_publication"]["predicted_days"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
