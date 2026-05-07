#!/usr/bin/env python3
"""Generate claim-readiness report artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.claim_readiness import claim_readiness_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/future_bs/reports/claim_readiness_v7.json"))
    args = parser.parse_args()
    payload = claim_readiness_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "ready": payload["ready_for_99_percent_green_zone_claim"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
