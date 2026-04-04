#!/usr/bin/env python3
"""
Build a holiday archive harvest queue covering older BS years.

This does not claim all years are already verified. It creates a structured
year-by-year acquisition plan that merges:

1. Official MoHA/DAO sources already archived in the repo
2. Older secondary archive leads discovered during research
3. Explicit gaps that still need Rajpatra/Panchang/archive work

Usage:
    PYTHONPATH=backend python backend/tools/build_archive_harvest_queue.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SOURCE_INVENTORY_DIR = DATA_DIR / "source_inventory"
SOURCE_INVENTORY_DIR.mkdir(parents=True, exist_ok=True)

OFFICIAL_INVENTORY_PATH = SOURCE_INVENTORY_DIR / "moha_official_years.json"
SECONDARY_INVENTORY_PATH = SOURCE_INVENTORY_DIR / "holiday_secondary_sources.json"
QUEUE_PATH = SOURCE_INVENTORY_DIR / "holiday_archive_targets.json"
REPORT_PATH = ROOT / "docs" / "ARCHIVE_HARVEST_QUEUE.md"


SECONDARY_FALLBACK = {
    2075: [
        {
            "source_name": "bizpati_2075_holiday_list",
            "source_type": "secondary_contemporary_news",
            "url": "https://bizpati.com/2018/04/16161/",
            "confidence": "secondary",
            "notes": "Contemporaneous report stating the 2075 holiday list was published in Rajpatra.",
        }
    ],
    2074: [
        {
            "source_name": "dnewsnepal_2074_holiday_list",
            "source_type": "secondary_contemporary_news",
            "url": "https://dnewsnepal.com/archives/28500",
            "confidence": "secondary",
            "notes": "Contemporaneous report describing the 2074 public holiday decision.",
        },
        {
            "source_name": "corporatenepal_2074_holiday_list",
            "source_type": "secondary_contemporary_news",
            "url": "https://www.corporatenepal.com/story/8033",
            "confidence": "secondary",
            "notes": "Backup secondary source for the 2074 holiday list.",
        },
    ],
    2073: [
        {
            "source_name": "onlinekhabar_2073_holiday_list",
            "source_type": "secondary_contemporary_news",
            "url": "https://www.onlinekhabar.com/2016/04/409326/%E0%A4%AF%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A4%BE-%E0%A4%9B%E0%A4%A8%E0%A5%8D-%E0%A5%A8%E0%A5%A6%E0%A5%AD%E0%A5%A9-%E0%A4%B8%E0%A4%BE%E0%A4%B2%E0%A4%95%E0%A4%BE-%E0%A4%B8%E0%A4%BE%E0%A4%B0%E0%A5%8D-2",
            "confidence": "secondary",
            "notes": "Contemporaneous report summarizing the 2073 holiday list.",
        }
    ],
    2072: [
        {
            "source_name": "onlinekhabar_2072_holiday_summary",
            "source_type": "secondary_contemporary_news",
            "url": "https://www.onlinekhabar.com/2015/02/246383/%E0%A4%95%E0%A4%BE%E0%A4%A4%E0%A5%8D%E0%A4%A4%E0%A4%BF%E0%A4%95%E0%A4%AE%E0%A4%BE-%E0%A4%AA%E0%A4%B0%E0%A5%8D%E2%80%8D%E0%A4%AF%E0%A5%8B-%E0%A5%A6%E0%A5%AD%E0%A5%A8-%E0%A4%B8%E0%A4%BE%E0%A4%B2",
            "confidence": "secondary",
            "notes": "Summary article citing the 2072 holiday count and major observance timing.",
        }
    ],
    2071: [
        {
            "source_name": "koirala_2071_holiday_list",
            "source_type": "secondary_archive_blog",
            "url": "https://koirala.com.np/content/12295.html",
            "confidence": "secondary",
            "notes": "Archived page with detailed 2071 holiday lines and office schedule notes.",
        }
    ],
}


def _load_official_inventory() -> list[dict]:
    if not OFFICIAL_INVENTORY_PATH.exists():
        return []
    payload = json.loads(OFFICIAL_INVENTORY_PATH.read_text(encoding="utf-8"))
    return payload.get("sources", [])


def _official_map() -> dict[int, dict]:
    mapping = {}
    for row in _load_official_inventory():
        year = row.get("bs_year")
        if isinstance(year, int):
            mapping[year] = row
    return mapping


def _load_secondary_inventory() -> list[dict]:
    if not SECONDARY_INVENTORY_PATH.exists():
        rows = []
        for year, sources in SECONDARY_FALLBACK.items():
            for source in sources:
                rows.append({"bs_year": year, **source})
        return rows
    payload = json.loads(SECONDARY_INVENTORY_PATH.read_text(encoding="utf-8"))
    return payload.get("sources", [])


def _secondary_map() -> dict[int, list[dict]]:
    mapping: dict[int, list[dict]] = {}
    for row in _load_secondary_inventory():
        year = row.get("bs_year")
        if isinstance(year, int):
            mapping.setdefault(year, []).append(row)
    return mapping


def _status_for_year(year: int, official_row: dict | None, secondary_rows: list[dict]) -> str:
    if official_row:
        status = str(official_row.get("status") or "").strip()
        if status:
            return status
    if secondary_rows:
        return "validated_secondary"
    return "missing"


def _next_action(status: str) -> str:
    if status == "structured_official":
        return "none"
    if status == "archived_raw_pdf":
        return "improve_extraction"
    if status == "validated_secondary":
        return "cross_validate_and_extract"
    return "discover_sources"


def _priority(status: str, year: int) -> str:
    if status == "structured_official":
        return "covered"
    if status == "archived_raw_pdf":
        return "high"
    if status == "validated_secondary":
        return "high"
    return "high" if year >= 2050 else "medium"


def build_queue(start_year: int = 2000, end_year: int = 2083) -> dict:
    official_rows = _official_map()
    secondary_rows_map = _secondary_map()
    items = []

    for year in range(start_year, end_year + 1):
        official_row = official_rows.get(year)
        secondary_rows = secondary_rows_map.get(year, [])
        status = _status_for_year(year, official_row, secondary_rows)
        sources = []
        if official_row:
            sources.append(
                {
                    "source_name": f"moha_official_{year}",
                    "source_type": official_row.get("source_type"),
                    "url": official_row.get("url"),
                    "local_path": official_row.get("local_path"),
                    "confidence": "official",
                    "status": official_row.get("status"),
                    "notes": official_row.get("notes"),
                }
            )
        sources.extend(secondary_rows)

        items.append(
            {
                "bs_year": year,
                "gregorian_span": [year - 57, year - 56],
                "status": status,
                "priority": _priority(status, year),
                "next_action": _next_action(status),
                "sources": sources,
                "target_source_types": [
                    "official_moha_pdf",
                    "official_rajpatra",
                    "rashtriya_panchang",
                    "secondary_contemporary_news",
                    "secondary_archive_blog",
                ],
            }
        )

    structured = sum(1 for row in items if row["status"] == "structured_official")
    archived = sum(1 for row in items if row["status"] == "archived_raw_pdf")
    secondary = sum(1 for row in items if row["status"] == "validated_secondary")
    missing = sum(1 for row in items if row["status"] == "missing")

    return {
        "_meta": {
            "name": "Holiday Archive Harvest Queue",
            "range_bs": [start_year, end_year],
            "structured_official_years": structured,
            "archived_raw_years": archived,
            "validated_secondary_years": secondary,
            "missing_years": missing,
        },
        "years": items,
    }


def write_report(queue: dict) -> None:
    lines = [
        "# Archive Harvest Queue",
        "",
        f"- BS range: **{queue['_meta']['range_bs'][0]}-{queue['_meta']['range_bs'][1]}**",
        f"- Structured official years: **{queue['_meta']['structured_official_years']}**",
        f"- Archived raw years: **{queue['_meta']['archived_raw_years']}**",
        f"- Validated secondary years: **{queue['_meta']['validated_secondary_years']}**",
        f"- Missing years: **{queue['_meta']['missing_years']}**",
        "",
        "## Earliest Reach",
        "",
    ]

    years = queue["years"]
    structured = [row["bs_year"] for row in years if row["status"] == "structured_official"]
    raw = [row["bs_year"] for row in years if row["status"] == "archived_raw_pdf"]
    secondary = [row["bs_year"] for row in years if row["status"] == "validated_secondary"]

    lines.append(
        f"- Earliest structured official year: **{min(structured) if structured else 'none'}**"
    )
    lines.append(f"- Earliest archived raw year: **{min(raw) if raw else 'none'}**")
    lines.append(
        f"- Earliest validated secondary year: **{min(secondary) if secondary else 'none'}**"
    )
    lines += [
        "",
        "## High-Priority Gaps",
        "",
        "| BS Year | Status | Next Action | Sources |",
        "|---|---|---|---|",
    ]

    for row in years:
        if row["priority"] != "high" or row["status"] == "structured_official":
            continue
        source_names = ", ".join(source["source_name"] for source in row["sources"]) or "-"
        lines.append(
            f"| {row['bs_year']} | {row['status']} | {row['next_action']} | {source_names} |"
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    queue = build_queue()
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(queue)
    print(f"Wrote {QUEUE_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
