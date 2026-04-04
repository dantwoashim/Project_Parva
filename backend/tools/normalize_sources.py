#!/usr/bin/env python3
"""Normalize source records and build source disagreement report."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

from app.calendar.bikram_sambat import bs_to_gregorian

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "data" / "ingest_reports"
OVERRIDES_PATH = PROJECT_ROOT / "backend" / "app" / "calendar" / "ground_truth_overrides.json"
OUT_JSON = PROJECT_ROOT / "data" / "normalized_sources.json"
OUT_MD = PROJECT_ROOT / "docs" / "SOURCE_COMPARISON.md"

MONTH_VARIANTS = {
    "वैशाख": 1,
    "बैशाख": 1,
    "वेशाख": 1,
    "जेठ": 2,
    "असार": 3,
    "आषाढ": 3,
    "साउन": 4,
    "श्रावण": 4,
    "सावन": 4,
    "भदौ": 5,
    "भाद्र": 5,
    "असोज": 6,
    "आश्विन": 6,
    "अशोज": 6,
    "कात्तिक": 7,
    "कार्तिक": 7,
    "कातिक": 7,
    "मङ्सिर": 8,
    "मंसिर": 8,
    "पुस": 9,
    "पौष": 9,
    "माघ": 10,
    "फागुन": 11,
    "फाल्गुन": 11,
    "चैत": 12,
    "चैत्र": 12,
}


def nep_to_int(text: str) -> int:
    return int(text.translate(str.maketrans("०१२३४५६७८९", "0123456789")))


def parse_moha_rows() -> list[dict]:
    rows: list[dict] = []
    for csv_path in sorted(REPORTS_DIR.glob("holidays_*_matched.csv")):
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                festival_id = (row.get("match_id") or "").strip()
                if not festival_id:
                    continue
                bs_year = int((row.get("bs_year") or "0").strip())
                month_raw = (row.get("month_raw") or "").strip()
                day_raw = (row.get("day_raw") or "").strip()
                if bs_year <= 0 or month_raw not in MONTH_VARIANTS or not day_raw:
                    continue
                try:
                    month_num = MONTH_VARIANTS[month_raw]
                    day_num = nep_to_int(day_raw)
                    g_date = bs_to_gregorian(bs_year, month_num, day_num)
                except Exception:
                    continue

                rows.append(
                    {
                        "festival_id": festival_id,
                        "gregorian": g_date.isoformat(),
                        "source": f"moha_pdf_{bs_year}",
                        "confidence": row.get("parse_confidence") or "medium",
                        "notes": row.get("name_raw") or "",
                    }
                )
    return rows


def parse_overrides_rows() -> list[dict]:
    if not OVERRIDES_PATH.exists():
        return []
    data = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    rows = []
    for year, festivals in data.items():
        if year.startswith("_"):
            continue
        for festival_id, detail in festivals.items():
            rows.append(
                {
                    "festival_id": festival_id,
                    "gregorian": detail.get("start"),
                    "source": detail.get("source") or "override",
                    "confidence": detail.get("confidence") or "official",
                    "notes": detail.get("notes") or "",
                }
            )
    return rows


def main() -> None:
    rows = parse_moha_rows() + parse_overrides_rows()

    grouped = defaultdict(list)
    for row in rows:
        key = (row["festival_id"], row["gregorian"])
        grouped[key].append(row)

    by_festival = defaultdict(set)
    for row in rows:
        by_festival[row["festival_id"]].add(row["gregorian"])

    disagreements = []
    for festival_id, dates in by_festival.items():
        if len(dates) > 1:
            disagreements.append(
                {
                    "festival_id": festival_id,
                    "dates": sorted(dates),
                    "sources": sorted(
                        {
                            row["source"]
                            for row in rows
                            if row["festival_id"] == festival_id and row["gregorian"] in dates
                        }
                    ),
                }
            )

    normalized = {
        "rows": rows,
        "summary": {
            "total_rows": len(rows),
            "unique_festivals": len(by_festival),
            "disagreement_count": len(disagreements),
        },
        "disagreements": disagreements,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Source Comparison Report",
        "",
        f"- Total normalized rows: **{normalized['summary']['total_rows']}**",
        f"- Unique festivals: **{normalized['summary']['unique_festivals']}**",
        f"- Festivals with source disagreement: **{normalized['summary']['disagreement_count']}**",
        "",
        "## Disagreements",
        "",
        "| Festival ID | Dates | Sources |",
        "|---|---|---|",
    ]

    for item in disagreements[:100]:
        lines.append(
            f"| {item['festival_id']} | {', '.join(item['dates'])} | {', '.join(item['sources'])} |"
        )

    if not disagreements:
        lines.append("| (none) | - | - |")

    lines += [
        "",
        "## Artifacts",
        "",
        f"- Normalized data: `{OUT_JSON}`",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
