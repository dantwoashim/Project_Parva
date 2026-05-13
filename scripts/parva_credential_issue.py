#!/usr/bin/env python3
"""Issue a hash-only preview Parva Calendar Credential."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.protocol_service import issue_calendar_credential_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", default="date_conversion", dest="claim_type")
    parser.add_argument("--bs-date", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    payload = issue_calendar_credential_payload({"claim_type": args.claim_type, "bs_date": args.bs_date})
    text = json.dumps(payload["credential"], indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
