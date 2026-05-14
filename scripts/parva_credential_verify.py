#!/usr/bin/env python3
"""Verify a Parva Calendar Credential."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.protocol_service import verify_calendar_credential_payload  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print("usage: python scripts/parva_credential_verify.py path/to/credential.json")
        return 0 if len(sys.argv) == 2 and sys.argv[1] in {"-h", "--help"} else 2
    credential = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result = verify_calendar_credential_payload(credential)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
