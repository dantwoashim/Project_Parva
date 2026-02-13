#!/usr/bin/env python3
"""Audit transparency log integrity and print summary."""

from __future__ import annotations

import json
from pathlib import Path

from app.provenance.transparency import verify_log_integrity

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = PROJECT_ROOT / "reports" / "transparency_audit.json"


def main() -> None:
    report = verify_log_integrity()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"valid": report["valid"], "total_entries": report["total_entries"]}, indent=2))
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
