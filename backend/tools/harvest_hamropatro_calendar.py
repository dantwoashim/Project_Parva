"""Harvest public Hamro Patro BS month-length data.

This scraper uses publicly accessible Hamro Patro pages only. It does not call
disallowed widget/date-converter endpoints from robots.txt.

Outputs:
- data/source_archive/hamropatro/hamropatro_month_lengths_2000_2099.json
- data/source_archive/hamropatro/hamropatro_bs_ad_2000_2099.csv
- data/source_inventory/hamropatro_calendar_sources.json
- reports/hamropatro_bs_ad_audit_2000_2100.{json,md}
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "data" / "source_archive" / "hamropatro"
INVENTORY_DIR = ROOT / "data" / "source_inventory"
REPORT_DIR = ROOT / "reports"
DEFAULT_DATE_URL = "https://english.hamropatro.com/date/2082-1-1"
USER_AGENT = "Project-Parva-Research/1.0 (+https://api.prabinghimire1.com.np)"


@dataclass(frozen=True)
class HarvestResult:
    requested_start_year: int
    requested_end_year: int
    harvested_start_year: int
    harvested_end_year: int
    unavailable_years: list[int]
    total_years: int
    total_months: int
    total_days: int
    anchor_bs: str
    anchor_ad: str
    base_bs: str
    base_ad: str
    source_url: str


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=45) as response:
            return response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc


def ensure_allowed_by_robots(url: str, robots_text: str) -> None:
    parsed = urlparse(url)
    path = parsed.path or "/"
    disallowed = []
    for line in robots_text.splitlines():
        line = line.strip()
        if not line.lower().startswith("disallow:"):
            continue
        rule = line.split(":", 1)[1].strip()
        if rule and path.startswith(rule):
            disallowed.append(rule)
    if disallowed:
        raise RuntimeError(f"Refusing to fetch {url}; robots.txt disallows {disallowed}")


def extract_month_lengths(html: str) -> dict[int, list[int]]:
    match = re.search(
        r"let\s+daysInMonth\s*=\s*(\[[\s\S]*?\n\s*\])\s*\n\s*function\s+getDaysInMonth",
        html,
    )
    if not match:
        raise RuntimeError("Could not find Hamro Patro daysInMonth JavaScript table.")

    rows: dict[int, list[int]] = {}
    for raw in re.findall(r"\[(\d{4}(?:\s*,\s*\d+){12})\]", match.group(1)):
        values = [int(part.strip()) for part in raw.split(",")]
        year, months = values[0], values[1:]
        if len(months) != 12:
            raise RuntimeError(f"Bad month count for BS {year}: {months}")
        if not all(29 <= days <= 32 for days in months):
            raise RuntimeError(f"Bad month length for BS {year}: {months}")
        rows[year] = months

    if not rows:
        raise RuntimeError("Hamro Patro daysInMonth table was empty.")
    expected = list(range(min(rows), max(rows) + 1))
    missing = [year for year in expected if year not in rows]
    if missing:
        raise RuntimeError(f"Hamro Patro daysInMonth table has missing years: {missing}")
    return rows


def parse_date_token(value: str) -> date:
    year, month, day = (int(part) for part in value.split("-"))
    return date(year, month, day)


def extract_anchor(html: str) -> tuple[tuple[int, int, int], date]:
    # Date pages include this note hook, for example:
    # AddNotesPopUP('2082-1-1','2025-4-14')
    match = re.search(
        r"AddNotesPopUP\('(\d{4})-(\d{1,2})-(\d{1,2})','(\d{4}-\d{1,2}-\d{1,2})'\)",
        html,
    )
    if not match:
        raise RuntimeError("Could not recover BS/AD anchor from Hamro Patro page.")
    bs = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    ad = parse_date_token(match.group(4))
    return bs, ad


def days_before_bs_date(
    month_lengths: dict[int, list[int]],
    *,
    base_year: int,
    target: tuple[int, int, int],
) -> int:
    year, month, day = target
    days = 0
    for cursor_year in range(base_year, year):
        days += sum(month_lengths[cursor_year])
    for cursor_month in range(1, month):
        days += month_lengths[year][cursor_month - 1]
    return days + day - 1


def build_day_rows(
    month_lengths: dict[int, list[int]],
    *,
    base_ad: date,
    base_year: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    offset = 0
    for year in range(min(month_lengths), max(month_lengths) + 1):
        for month, days_in_month in enumerate(month_lengths[year], start=1):
            for day in range(1, days_in_month + 1):
                ad = base_ad + timedelta(days=offset)
                rows.append(
                    {
                        "bs_year": year,
                        "bs_month": month,
                        "bs_day": day,
                        "bs": f"{year:04d}-{month:02d}-{day:02d}",
                        "ad": ad.isoformat(),
                        "source": "hamropatro_public_daysInMonth_js",
                    }
                )
                offset += 1
    return rows


def load_parva_month_lengths() -> dict[int, list[int]]:
    constants_path = ROOT / "backend" / "app" / "calendar" / "constants.py"
    if not constants_path.exists():
        return {}
    text = constants_path.read_text(encoding="utf-8")
    match = re.search(
        r"BS_MONTH_LENGTHS\s*:\s*dict\[int,\s*list\[int\]\]\s*=\s*(\{[\s\S]*?\n\})",
        text,
    )
    if not match:
        return {}
    try:
        parsed = ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError):
        return {}
    return {int(year): list(months) for year, months in parsed.items()}


def build_parva_comparison(
    hamro_lengths: dict[int, list[int]], parva_lengths: dict[int, list[int]]
) -> list[dict[str, object]]:
    comparison = []
    for year in sorted(set(hamro_lengths).intersection(parva_lengths)):
        hamro = hamro_lengths[year]
        parva = parva_lengths[year]
        diffs = [
            {
                "month": idx + 1,
                "hamropatro_days": hamro[idx],
                "parva_days": parva[idx],
            }
            for idx in range(12)
            if hamro[idx] != parva[idx]
        ]
        if diffs:
            comparison.append(
                {
                    "bs_year": year,
                    "hamropatro_total_days": sum(hamro),
                    "parva_total_days": sum(parva),
                    "differences": diffs,
                }
            )
    return comparison


def write_outputs(
    *,
    html: str,
    source_url: str,
    requested_start_year: int,
    requested_end_year: int,
    month_lengths: dict[int, list[int]],
    anchor_bs: tuple[int, int, int],
    anchor_ad: date,
) -> HarvestResult:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    INVENTORY_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    harvested_start = min(month_lengths)
    harvested_end = max(month_lengths)
    start_year = max(requested_start_year, harvested_start)
    end_year = min(requested_end_year, harvested_end)
    scoped_lengths = {
        year: month_lengths[year] for year in range(start_year, end_year + 1)
    }
    unavailable = [
        year
        for year in range(requested_start_year, requested_end_year + 1)
        if year not in month_lengths
    ]

    source_html_path = SOURCE_DIR / "hamropatro_date_2082-1-1.html"
    source_html_path.write_text(html, encoding="utf-8")

    anchor_offset = days_before_bs_date(
        month_lengths,
        base_year=harvested_start,
        target=anchor_bs,
    )
    base_ad = anchor_ad - timedelta(days=anchor_offset)
    day_rows = build_day_rows(scoped_lengths, base_ad=base_ad, base_year=start_year)

    month_json = {
        "_meta": {
            "source_name": "hamropatro",
            "source_url": source_url,
            "source_type": "secondary_public_web_js_table",
            "requested_range": [requested_start_year, requested_end_year],
            "available_range": [harvested_start, harvested_end],
            "harvested_range": [start_year, end_year],
            "unavailable_years": unavailable,
            "anchor_bs": f"{anchor_bs[0]:04d}-{anchor_bs[1]:02d}-{anchor_bs[2]:02d}",
            "anchor_ad": anchor_ad.isoformat(),
            "base_bs": f"{harvested_start:04d}-01-01",
            "base_ad": base_ad.isoformat(),
            "note": (
                "Hamro Patro is a secondary public calendar source, not an "
                "official Government of Nepal source."
            ),
        },
        "years": [
            {
                "bs_year": year,
                "months": [
                    {"month": idx + 1, "days": days}
                    for idx, days in enumerate(months)
                ],
                "total_days": sum(months),
            }
            for year, months in scoped_lengths.items()
        ],
    }
    month_json_path = (
        SOURCE_DIR / f"hamropatro_month_lengths_{start_year}_{end_year}.json"
    )
    month_json_path.write_text(
        json.dumps(month_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    csv_path = SOURCE_DIR / f"hamropatro_bs_ad_{start_year}_{end_year}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["bs_year", "bs_month", "bs_day", "bs", "ad", "source"],
        )
        writer.writeheader()
        writer.writerows(day_rows)

    parva_comparison = build_parva_comparison(scoped_lengths, load_parva_month_lengths())
    inventory = {
        "_meta": {
            "name": "Hamro Patro Calendar Source Inventory",
            "source_type": "secondary_public_web",
            "generated_by": "backend/tools/harvest_hamropatro_calendar.py",
            "robots_policy": (
                "Uses public /date pages. Does not use robots-disallowed "
                "/widgets/dateconverter.php or calendar widget endpoints."
            ),
        },
        "sources": [
            {
                "name": "Hamro Patro date page embedded daysInMonth table",
                "url": source_url,
                "local_path": str(source_html_path.relative_to(ROOT)),
                "status": "harvested",
                "available_range": [harvested_start, harvested_end],
                "requested_range": [requested_start_year, requested_end_year],
                "unavailable_years": unavailable,
                "derived_artifacts": [
                    str(month_json_path.relative_to(ROOT)),
                    str(csv_path.relative_to(ROOT)),
                ],
            }
        ],
    }
    inventory_path = INVENTORY_DIR / "hamropatro_calendar_sources.json"
    inventory_path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = HarvestResult(
        requested_start_year=requested_start_year,
        requested_end_year=requested_end_year,
        harvested_start_year=start_year,
        harvested_end_year=end_year,
        unavailable_years=unavailable,
        total_years=len(scoped_lengths),
        total_months=len(scoped_lengths) * 12,
        total_days=len(day_rows),
        anchor_bs=f"{anchor_bs[0]:04d}-{anchor_bs[1]:02d}-{anchor_bs[2]:02d}",
        anchor_ad=anchor_ad.isoformat(),
        base_bs=f"{harvested_start:04d}-01-01",
        base_ad=base_ad.isoformat(),
        source_url=source_url,
    )

    report_json = {
        "summary": asdict(result),
        "artifacts": {
            "source_html": str(source_html_path.relative_to(ROOT)),
            "month_lengths_json": str(month_json_path.relative_to(ROOT)),
            "bs_ad_csv": str(csv_path.relative_to(ROOT)),
            "inventory": str(inventory_path.relative_to(ROOT)),
        },
        "parva_comparison": {
            "overlap_years_with_differences": len(parva_comparison),
            "differences": parva_comparison,
        },
    }
    report_json_path = REPORT_DIR / "hamropatro_bs_ad_audit_2000_2100.json"
    report_json_path.write_text(
        json.dumps(report_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    mismatch_lines = []
    for item in parva_comparison[:30]:
        diff_text = ", ".join(
            f"m{d['month']}: HP {d['hamropatro_days']} vs Parva {d['parva_days']}"
            for d in item["differences"]
        )
        mismatch_lines.append(f"- BS {item['bs_year']}: {diff_text}")
    if len(parva_comparison) > 30:
        mismatch_lines.append(
            f"- ... {len(parva_comparison) - 30} more years in JSON report"
        )

    report_md = "\n".join(
        [
            "# Hamro Patro BS/AD Harvest Audit",
            "",
            "## Summary",
            f"- Requested range: {requested_start_year}-{requested_end_year} BS",
            f"- Harvested range: {start_year}-{end_year} BS",
            f"- Unavailable from Hamro Patro table: {unavailable}",
            f"- Total days exported: {len(day_rows)}",
            f"- Anchor: {result.anchor_bs} BS = {result.anchor_ad} AD",
            f"- Derived base: {result.base_bs} BS = {result.base_ad} AD",
            "",
            "## Artifacts",
            f"- `{source_html_path.relative_to(ROOT)}`",
            f"- `{month_json_path.relative_to(ROOT)}`",
            f"- `{csv_path.relative_to(ROOT)}`",
            f"- `{inventory_path.relative_to(ROOT)}`",
            "",
            "## Parva Differences In Overlap",
            f"- Years with month-length differences: {len(parva_comparison)}",
            *(mismatch_lines or ["- No differences found in overlap."]),
            "",
            "## Caveat",
            (
                "Hamro Patro is a secondary public calendar source. This harvest "
                "must not be labeled official government provenance."
            ),
            "",
        ]
    )
    (REPORT_DIR / "hamropatro_bs_ad_audit_2000_2100.md").write_text(
        report_md,
        encoding="utf-8",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-url", default=DEFAULT_DATE_URL)
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2100)
    args = parser.parse_args(argv)

    robots = fetch_text("https://english.hamropatro.com/robots.txt")
    ensure_allowed_by_robots(args.source_url, robots)

    html = fetch_text(args.source_url)
    month_lengths = extract_month_lengths(html)
    anchor_bs, anchor_ad = extract_anchor(html)
    result = write_outputs(
        html=html,
        source_url=args.source_url,
        requested_start_year=args.start_year,
        requested_end_year=args.end_year,
        month_lengths=month_lengths,
        anchor_bs=anchor_bs,
        anchor_ad=anchor_ad,
    )
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
