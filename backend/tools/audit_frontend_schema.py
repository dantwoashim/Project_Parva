#!/usr/bin/env python3
"""Audit frontend-consumed fields against live API responses (in-process)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_MD = PROJECT_ROOT / "docs" / "SCHEMA_DIFF_WEEK37.md"


def has_path(payload: dict, path: str) -> bool:
    current = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    return True


def main() -> None:
    client = TestClient(app)

    checks = [
        {
            "endpoint": "/v2/api/calendar/today",
            "params": None,
            "fields": [
                "bikram_sambat.year",
                "bikram_sambat.month",
                "bikram_sambat.day",
                "bikram_sambat.confidence",
                "bikram_sambat.source_range",
                "bikram_sambat.estimated_error_days",
                "tithi.method",
                "tithi.confidence",
            ],
        },
        {
            "endpoint": "/v2/api/festivals/dashain",
            "params": {"year": 2026},
            "fields": [
                "festival.id",
                "festival.name",
                "festival.description",
                "festival.calendar_type",
                "festival.regional_focus",
                "dates.start_date",
                "dates.end_date",
            ],
        },
        {
            "endpoint": "/v2/api/festivals/dashain/explain",
            "params": {"year": 2026},
            "fields": [
                "festival_id",
                "year",
                "explanation",
                "steps",
                "calculation_trace_id",
            ],
        },
    ]

    lines = [
        "# Frontend Schema Audit (Week 37)",
        "",
        f"- Generated: {date.today().isoformat()}",
        "",
        "| Endpoint | Field | Present |",
        "|---|---|---|",
    ]

    missing = 0

    for item in checks:
        resp = client.get(item["endpoint"], params=item["params"])
        payload = resp.json() if resp.status_code == 200 else {}
        for field in item["fields"]:
            present = has_path(payload, field)
            if not present:
                missing += 1
            lines.append(f"| {item['endpoint']} | {field} | {'✅' if present else '❌'} |")

    lines += [
        "",
        f"- Missing fields: **{missing}**",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
