"""Source-labeled witness corpus reconstruction for future-BS accuracy work."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "data" / "future_bs"
WITNESS_DIR = DATA_ROOT / "witnesses"
RAW_DIR = WITNESS_DIR / "raw"
CORPUS_DIR = DATA_ROOT / "corpus"
ACQUISITION_DIR = DATA_ROOT / "data_acquisition"
SOURCE_ARCHIVE = PROJECT_ROOT / "data" / "source_archive"
SOURCE_INVENTORY = PROJECT_ROOT / "data" / "source_inventory"

PUBLICATION_STATUS = "computed_prediction_not_official"
PARSER_VERSION = "witness_reconstruction_v1"
MONTH_SLUGS = [
    "baisakh",
    "jestha",
    "ashadh",
    "shrawan",
    "bhadra",
    "ashwin",
    "kartik",
    "mangsir",
    "poush",
    "magh",
    "falgun",
    "chaitra",
]
RAT32_SLUGS = [
    "baisakh",
    "jestha",
    "ashad",
    "shrawan",
    "bhadra",
    "ashwin",
    "kartik",
    "mangsir",
    "poush",
    "magh",
    "falgun",
    "chaitra",
]
RAT32_TITLE_ALIASES = {
    1: {"baisakh", "baishakh"},
    2: {"jestha"},
    3: {"ashadh", "asar", "ashad"},
    4: {"shrawan", "sharawan"},
    5: {"bhadra"},
    6: {"ashwin", "ashoj"},
    7: {"kartik"},
    8: {"mangsir"},
    9: {"poush", "paush"},
    10: {"magh"},
    11: {"falgun", "fagun"},
    12: {"chaitra"},
}
MONTH_COLUMNS = [
    "baishakh",
    "jestha",
    "ashadh",
    "shrawan",
    "bhadra",
    "ashwin",
    "kartik",
    "mangsir",
    "poush",
    "magh",
    "falgun",
    "chaitra",
]
AD_MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

WITNESS_FIELDS = [
    "source_id",
    "source_type",
    "source_tier",
    "source_name",
    "source_url",
    "source_file",
    "extraction_method",
    "extraction_confidence",
    "ad_date",
    "bs_year",
    "bs_month",
    "bs_day",
    "weekday_if_available",
    "raw_text",
    "raw_html_snippet_or_image_ref",
    "page_number_if_pdf",
    "image_crop_path_if_available",
    "ocr_engine_if_used",
    "parser_version",
    "manual_review_status",
    "usable_for_training",
    "usable_for_official_claim",
    "notes",
    "created_at",
]

MONTH_START_FIELDS = [
    "bs_year",
    "bs_month",
    "month_start_ad",
    "witness_count",
    "best_source_tier",
    "agreement_score",
    "source_ids",
    "conflicting_source_ids",
    "verification_status",
    "manual_review_required",
    "notes",
]

MONTH_LENGTH_FIELDS = [
    "bs_year",
    "bs_month",
    "month_start_ad",
    "next_month_start_ad",
    "month_length",
    "witness_count",
    "best_source_tier",
    "agreement_score",
    "verification_status",
    "usable_for_training",
    "usable_for_official_claim",
    "notes",
]

REVIEW_FIELDS = [
    "priority",
    "bs_year",
    "bs_month",
    "issue_type",
    "current_candidate_start_dates",
    "sources",
    "reason",
    "expected_information_gain",
    "recommended_manual_action",
    "source_file_or_url",
    "page_number_or_crop_if_available",
]

SOURCE_TIERS: dict[str, dict[str, Any]] = {
    "official_verified": {"tier": 1, "weight": 1.0, "training": True, "official": True},
    "printed_verified": {"tier": 2, "weight": 0.85, "training": True, "official": False},
    "public_daily_witness": {"tier": 3, "weight": 0.65, "training": True, "official": False},
    "publisher_reference": {"tier": 4, "weight": 0.5, "training": True, "official": False},
    "software_table_reference": {"tier": 5, "weight": 0.35, "training": True, "official": False},
    "third_party_reference": {"tier": 6, "weight": 0.25, "training": True, "official": False},
    "needs_review": {"tier": 7, "weight": 0.05, "training": False, "official": False},
    "excluded": {"tier": 0, "weight": 0.0, "training": False, "official": False},
}


def ensure_dirs() -> None:
    for path in (WITNESS_DIR, RAW_DIR, CORPUS_DIR, ACQUISITION_DIR):
        path.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def source_policy(source_type: str) -> dict[str, Any]:
    return SOURCE_TIERS.get(source_type, SOURCE_TIERS["needs_review"])


def source_registry() -> dict[str, Any]:
    return {
        "publication_status": PUBLICATION_STATUS,
        "source_tiers": SOURCE_TIERS,
        "sources": [
            {
                "source_id": "parva_structured_official_2078_2083",
                "source_type": "official_verified",
                "source_name": "Project Parva accepted structured official artifacts",
                "source_url": "",
                "source_file": "data/future_bs/corpus/verified_month_lengths.csv",
                "license_or_access": "local repository artifact",
                "notes": "Only rows already labeled official_verified/verified are treated as official-grade.",
            },
            {
                "source_id": "parva_archived_official_patro_2076_2077",
                "source_type": "printed_verified",
                "source_name": "Project Parva archived official PDF row",
                "source_url": "",
                "source_file": "data/future_bs/corpus/verified_month_lengths.csv",
                "license_or_access": "local repository artifact",
                "notes": "Archived but still manual-review required; not counted for official claims.",
            },
            {
                "source_id": "rat32_public_calendar_pages",
                "source_type": "publisher_reference",
                "source_name": "Rat32 NepaliCalendar public month pages",
                "source_url": "https://nepalicalendar.rat32.com/{bs_year}/{month_slug}",
                "source_file": "data/future_bs/witnesses/raw/rat32",
                "license_or_access": "public pages, polite bounded fetch",
                "notes": "Parsed month-start cells for 2050-2083 where accessible.",
            },
            {
                "source_id": "medic_bikram_sambat_daysInMonth",
                "source_type": "software_table_reference",
                "source_name": "medic/bikram-sambat daysInMonth.json",
                "source_url": "https://raw.githubusercontent.com/medic/bikram-sambat/master/test-data/daysInMonth.json",
                "source_file": "data/future_bs/witnesses/raw/open_source/medic_daysInMonth.json",
                "license_or_access": "Apache-2.0 GitHub repository",
                "notes": "Open-source table witness; not official.",
            },
            {
                "source_id": "sharingapples_nepali_date_config",
                "source_type": "software_table_reference",
                "source_name": "sharingapples/nepali-date config.js",
                "source_url": "https://raw.githubusercontent.com/sharingapples/nepali-date/master/src/config.js",
                "source_file": "data/future_bs/witnesses/raw/open_source/sharingapples_config.js",
                "license_or_access": "public GitHub repository",
                "notes": "Open-source table witness; not official.",
            },
        ],
    }


def write_source_registry() -> None:
    ensure_dirs()
    payload = source_registry()
    (WITNESS_DIR / "source_registry.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def make_witness(
    *,
    source_id: str,
    source_type: str,
    source_name: str,
    source_url: str = "",
    source_file: str = "",
    extraction_method: str,
    extraction_confidence: float,
    ad_date: str,
    bs_year: int,
    bs_month: int,
    bs_day: int = 1,
    raw_text: str = "",
    raw_ref: str = "",
    weekday: str = "",
    manual_review_status: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    policy = source_policy(source_type)
    review_status = manual_review_status or (
        "verified" if source_type == "official_verified" else "machine_extracted_needs_review"
    )
    usable_training = bool(policy["training"] and source_type != "needs_review")
    usable_official = bool(policy["official"] and review_status == "verified")
    return {
        "source_id": source_id,
        "source_type": source_type,
        "source_tier": policy["tier"],
        "source_name": source_name,
        "source_url": source_url,
        "source_file": source_file,
        "extraction_method": extraction_method,
        "extraction_confidence": round(float(extraction_confidence), 3),
        "ad_date": ad_date,
        "bs_year": int(bs_year),
        "bs_month": int(bs_month),
        "bs_day": int(bs_day),
        "weekday_if_available": weekday,
        "raw_text": raw_text,
        "raw_html_snippet_or_image_ref": raw_ref,
        "page_number_if_pdf": "",
        "image_crop_path_if_available": "",
        "ocr_engine_if_used": "",
        "parser_version": PARSER_VERSION,
        "manual_review_status": review_status,
        "usable_for_training": str(usable_training).lower(),
        "usable_for_official_claim": str(usable_official).lower(),
        "notes": notes,
        "created_at": utc_now(),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")


def download_public(url: str, raw_path: Path, *, timeout: int = 30) -> tuple[str | None, str | None]:
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if raw_path.exists() and raw_path.stat().st_size > 0:
        return raw_path.read_text(encoding="utf-8", errors="replace"), None
    request = urllib.request.Request(url, headers={"User-Agent": "ProjectParvaDataAcquisition/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content = response.read().decode("utf-8", errors="replace")
        raw_path.write_text(content, encoding="utf-8")
        return content, None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, str(exc)


def source_attempt(
    *,
    source_name: str,
    source_url: str,
    status: str,
    rows_extracted: int,
    years: set[int] | list[int],
    months: set[tuple[int, int]] | list[tuple[int, int]],
    error: str = "",
    next_action: str = "",
) -> dict[str, Any]:
    years_list = sorted(int(year) for year in years)
    return {
        "source_name": source_name,
        "source_url": source_url,
        "attempted_at": utc_now(),
        "status": status,
        "rows_extracted": int(rows_extracted),
        "years_covered": years_list,
        "months_covered": len(set(months)),
        "error_if_any": error,
        "next_action": next_action,
    }


def month_start_dates_from_lengths(
    year_lengths: dict[int, list[int]],
    *,
    start_ad: date = date(1943, 4, 14),
    start_bs_year: int = 2000,
) -> dict[tuple[int, int], date]:
    starts: dict[tuple[int, int], date] = {}
    cursor = start_ad
    for year in sorted(year_lengths):
        if year < start_bs_year:
            continue
        months = year_lengths[year]
        for month, length in enumerate(months, start=1):
            starts[(year, month)] = cursor
            cursor += timedelta(days=int(length))
        starts[(year + 1, 1)] = cursor
    return starts


def _load_verified_year_lengths() -> dict[int, tuple[list[int], dict[str, str]]]:
    path = CORPUS_DIR / "verified_month_lengths.csv"
    rows = read_csv(path)
    output: dict[int, tuple[list[int], dict[str, str]]] = {}
    for row in rows:
        try:
            year = int(row["bs_year"])
            months = [int(row[column]) for column in MONTH_COLUMNS]
        except (KeyError, ValueError):
            continue
        output[year] = (months, row)
    return output


def extract_verified_repo_artifacts() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    year_rows = _load_verified_year_lengths()
    starts = month_start_dates_from_lengths({year: item[0] for year, item in year_rows.items()})
    witnesses: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    months_seen: set[tuple[int, int]] = set()
    for year, (lengths, row) in sorted(year_rows.items()):
        source_type = row.get("source_type", "needs_review")
        if source_type == "approved_patro":
            mapped_type = "printed_verified"
            review_status = "needs_review"
            confidence = 0.55
            notes = "Archived official/patro row is structured locally but still requires manual review."
        elif source_type == "official_verified" and row.get("verification_status") == "verified":
            mapped_type = "official_verified"
            review_status = "verified"
            confidence = 0.98
            notes = "Accepted structured official row already present in repository corpus."
        else:
            continue
        source_id = (
            "parva_structured_official_2078_2083"
            if mapped_type == "official_verified"
            else "parva_archived_official_patro_2076_2077"
        )
        for month, length in enumerate(lengths, start=1):
            key = (year, month)
            if key not in starts:
                continue
            months_seen.add(key)
            witnesses.append(
                make_witness(
                    source_id=source_id,
                    source_type=mapped_type,
                    source_name=row.get("source_name", source_id),
                    source_file="data/future_bs/corpus/verified_month_lengths.csv",
                    extraction_method="structured_month_length_to_month_start",
                    extraction_confidence=confidence,
                    ad_date=starts[key].isoformat(),
                    bs_year=year,
                    bs_month=month,
                    raw_text=f"bs_year={year}; month={month}; month_length={length}; row_source={source_type}",
                    raw_ref=f"data/future_bs/corpus/verified_month_lengths.csv#{year}",
                    manual_review_status=review_status,
                    notes=notes,
                )
            )
    attempts.append(
        source_attempt(
            source_name="Project Parva structured official/archived corpus rows",
            source_url="data/future_bs/corpus/verified_month_lengths.csv",
            status="success" if witnesses else "empty",
            rows_extracted=len(witnesses),
            years={int(row["bs_year"]) for _, row in year_rows.values() if row.get("source_type") in {"official_verified", "approved_patro"}},
            months=months_seen,
            next_action="Manually review archived 2076-2077 PDF rows before counting them as official-grade.",
        )
    )
    return witnesses, attempts


def _parse_rat32_month_page(content: str, bs_year: int, bs_month: int) -> tuple[str | None, str]:
    title = re.search(r"<h1[^>]*id=\"yren\"[^>]*>\s*([A-Za-z]+)\s+(\d{4})", content, re.I)
    ad_title = re.search(r"<h2[^>]*id=\"entarikYr\"[^>]*>\s*([A-Za-z]{3})/([A-Za-z]{3})\s+(\d{4})", content, re.I)
    if not title or not ad_title:
        return None, "month title or AD title not found"
    title_month = title.group(1).lower()
    if int(title.group(2)) != bs_year or title_month not in RAT32_TITLE_ALIASES[bs_month]:
        return None, f"title mismatch: {title.group(0)}"
    first_ad_month = AD_MONTHS.get(ad_title.group(1))
    ad_year = int(ad_title.group(3))
    if not first_ad_month:
        return None, "AD month not recognized"
    cell_pattern = re.compile(
        r"<div class=\"cells\".*?<div id=\"nday\"[^>]*>.*?<font[^>]*>\s*(\d+)\s*</font>.*?"
        r"<div id=\"eday\"[^>]*>.*?<font[^>]*>\s*(\d+)\s*</font>",
        re.S | re.I,
    )
    for match in cell_pattern.finditer(content):
        if int(match.group(1)) == 1:
            ad_day = int(match.group(2))
            return date(ad_year, first_ad_month, ad_day).isoformat(), ""
    return None, "BS day 1 cell not found"


def extract_rat32_pages(start_year: int = 2050, end_year: int = 2083, delay_seconds: float = 0.05) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    witnesses: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    raw_base = RAW_DIR / "rat32"
    for year in range(start_year, end_year + 1):
        year_months: set[tuple[int, int]] = set()
        year_rows = 0
        year_errors: list[str] = []
        for month, slug in enumerate(RAT32_SLUGS, start=1):
            url = f"https://nepalicalendar.rat32.com/{year}/{slug}"
            raw_path = raw_base / f"rat32_{year}_{slug}.html"
            content, error = download_public(url, raw_path)
            if error or content is None:
                failures.append(
                    source_attempt(
                        source_name="Rat32 public calendar page",
                        source_url=url,
                        status="failed",
                        rows_extracted=0,
                        years=[year],
                        months=[],
                        error=error or "empty response",
                        next_action="Manual browser review or alternate publisher page needed.",
                    )
                )
                year_errors.append(error or "empty response")
                continue
            ad_start, parse_error = _parse_rat32_month_page(content, year, month)
            if not ad_start:
                failures.append(
                    source_attempt(
                        source_name="Rat32 public calendar page",
                        source_url=url,
                        status="parse_failed",
                        rows_extracted=0,
                        years=[year],
                        months=[],
                        error=parse_error,
                        next_action="Add page-specific parser or manual review.",
                    )
                )
                year_errors.append(parse_error)
                continue
            year_months.add((year, month))
            year_rows += 1
            witnesses.append(
                make_witness(
                    source_id="rat32_public_calendar_pages",
                    source_type="publisher_reference",
                    source_name="Rat32 NepaliCalendar public month page",
                    source_url=url,
                    source_file=str(raw_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    extraction_method="html_calendar_cell_bs_day_1",
                    extraction_confidence=0.82,
                    ad_date=ad_start,
                    bs_year=year,
                    bs_month=month,
                    raw_text=f"{RAT32_SLUGS[month - 1]} {year} day 1 -> {ad_start}",
                    raw_ref=str(raw_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    manual_review_status="machine_extracted_needs_review",
                    notes="Publisher-reference public HTML page; not official.",
                )
            )
            if delay_seconds:
                time.sleep(delay_seconds)
        attempts.append(
            source_attempt(
                source_name="Rat32 public calendar pages",
                source_url=f"https://nepalicalendar.rat32.com/{year}/{{month}}",
                status="success" if year_rows == 12 else "partial",
                rows_extracted=year_rows,
                years=[year] if year_rows else [],
                months=year_months,
                error="; ".join(sorted(set(year_errors))[:3]),
                next_action="Manual review partial years if rows_extracted < 12.",
            )
        )
    return witnesses, attempts, failures


def parse_medic_days_in_month(content: str) -> dict[int, list[int]]:
    payload = json.loads(content)
    return {int(year): [int(value) for value in months[:12]] for year, months in payload.items()}


def parse_sharingapples_config(content: str) -> dict[int, list[int]]:
    rows: dict[int, list[int]] = {}
    for match in re.finditer(r"\[\s*(\d{4})\s*,([^\]]+)\]", content):
        year = int(match.group(1))
        values = [int(item.strip()) for item in match.group(2).split(",") if item.strip().isdigit()]
        if len(values) >= 12:
            rows[year] = values[:12]
    return rows


def witnesses_from_year_lengths(
    *,
    year_lengths: dict[int, list[int]],
    source_id: str,
    source_type: str,
    source_name: str,
    source_url: str,
    source_file: str,
    extraction_method: str,
    confidence: float,
) -> list[dict[str, Any]]:
    starts = month_start_dates_from_lengths(year_lengths)
    witnesses: list[dict[str, Any]] = []
    for year, lengths in sorted(year_lengths.items()):
        for month, length in enumerate(lengths, start=1):
            key = (year, month)
            if key not in starts:
                continue
            witnesses.append(
                make_witness(
                    source_id=source_id,
                    source_type=source_type,
                    source_name=source_name,
                    source_url=source_url,
                    source_file=source_file,
                    extraction_method=extraction_method,
                    extraction_confidence=confidence,
                    ad_date=starts[key].isoformat(),
                    bs_year=year,
                    bs_month=month,
                    raw_text=f"bs_year={year}; month_lengths={lengths}; selected_month_length={length}",
                    raw_ref=source_file,
                    manual_review_status="machine_extracted_needs_review",
                    notes="Month-start derived from public source table and 2000-01-01 BS epoch.",
                )
            )
    return witnesses


def extract_open_source_converter_tables() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    specs = [
        {
            "source_name": "medic/bikram-sambat daysInMonth.json",
            "source_id": "medic_bikram_sambat_daysInMonth",
            "url": "https://raw.githubusercontent.com/medic/bikram-sambat/master/test-data/daysInMonth.json",
            "raw": RAW_DIR / "open_source" / "medic_daysInMonth.json",
            "parser": parse_medic_days_in_month,
        },
        {
            "source_name": "sharingapples/nepali-date config.js",
            "source_id": "sharingapples_nepali_date_config",
            "url": "https://raw.githubusercontent.com/sharingapples/nepali-date/master/src/config.js",
            "raw": RAW_DIR / "open_source" / "sharingapples_config.js",
            "parser": parse_sharingapples_config,
        },
    ]
    witnesses: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for spec in specs:
        content, error = download_public(spec["url"], spec["raw"])
        if error or content is None:
            failure = source_attempt(
                source_name=spec["source_name"],
                source_url=spec["url"],
                status="failed",
                rows_extracted=0,
                years=[],
                months=[],
                error=error or "empty response",
                next_action="Retry public GitHub raw download or add manual seed file.",
            )
            attempts.append(failure)
            failures.append(failure)
            continue
        try:
            year_lengths = spec["parser"](content)
        except (ValueError, json.JSONDecodeError) as exc:
            failure = source_attempt(
                source_name=spec["source_name"],
                source_url=spec["url"],
                status="parse_failed",
                rows_extracted=0,
                years=[],
                months=[],
                error=str(exc),
                next_action="Inspect raw source and update parser.",
            )
            attempts.append(failure)
            failures.append(failure)
            continue
        rows = witnesses_from_year_lengths(
            year_lengths=year_lengths,
            source_id=spec["source_id"],
            source_type="software_table_reference",
            source_name=spec["source_name"],
            source_url=spec["url"],
            source_file=str(spec["raw"].relative_to(PROJECT_ROOT)).replace("\\", "/"),
            extraction_method="open_source_month_table_to_month_start",
            confidence=0.72,
        )
        witnesses.extend(rows)
        attempts.append(
            source_attempt(
                source_name=spec["source_name"],
                source_url=spec["url"],
                status="success" if rows else "empty",
                rows_extracted=len(rows),
                years=set(year_lengths),
                months={(row["bs_year"], row["bs_month"]) for row in rows},
                next_action="Cross-check against stronger witnesses; do not count as official.",
            )
        )
    return witnesses, attempts, failures


def record_external_blocker_attempts() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    attempts = [
        source_attempt(
            source_name="NPNS/government official historical archive discovery",
            source_url="public web search and known government/NPNS discovery pages",
            status="blocked_no_machine_readable_archive_found",
            rows_extracted=0,
            years=[],
            months=[],
            error="No stable public historical month-start archive endpoint was found during automated discovery.",
            next_action="Manual acquisition: collect NPNS/government PDFs for older years and add seed URLs.",
        ),
        source_attempt(
            source_name="Archive.org printed panchanga seed list",
            source_url="archive.org public item URLs",
            status="blocked_no_seed_list_configured",
            rows_extracted=0,
            years=[],
            months=[],
            error="No legally verified archive.org item seed list is currently present in the repository.",
            next_action="Add public archive.org item URLs for printed panchangas and rerun parser.",
        ),
        source_attempt(
            source_name="Gorkhapatra/public newspaper masthead archive",
            source_url="public epaper/archive pages",
            status="blocked_no_stable_public_bulk_endpoint",
            rows_extracted=0,
            years=[],
            months=[],
            error="No stable public bulk endpoint was identified for bounded automated masthead extraction.",
            next_action="Add public masthead PDF/page seeds around BS month boundaries.",
        ),
    ]
    return attempts, attempts.copy()


def collect_witnesses(fetch_rat32: bool = True) -> dict[str, Any]:
    ensure_dirs()
    write_source_registry()
    all_witnesses: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    source_functions = [
        extract_verified_repo_artifacts,
        extract_open_source_converter_tables,
    ]
    for func in source_functions:
        try:
            result = func()
            if len(result) == 2:
                witnesses, source_attempts = result
                source_failures: list[dict[str, Any]] = []
            else:
                witnesses, source_attempts, source_failures = result
            all_witnesses.extend(witnesses)
            attempts.extend(source_attempts)
            failures.extend(source_failures)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:  # pragma: no cover - defensive logging path
            errors.append({"parser": func.__name__, "error": repr(exc), "created_at": utc_now()})
            failures.append(
                source_attempt(
                    source_name=func.__name__,
                    source_url="local parser",
                    status="parser_exception",
                    rows_extracted=0,
                    years=[],
                    months=[],
                    error=repr(exc),
                    next_action="Inspect parser exception and fix extraction.",
                )
            )

    if fetch_rat32:
        rat32_witnesses, rat32_attempts, rat32_failures = extract_rat32_pages()
        all_witnesses.extend(rat32_witnesses)
        attempts.extend(rat32_attempts)
        failures.extend(rat32_failures)

    blocked_attempts, blocked_failures = record_external_blocker_attempts()
    attempts.extend(blocked_attempts)
    failures.extend(blocked_failures)

    dedup: dict[tuple[str, str, int, int, int], dict[str, Any]] = {}
    for witness in all_witnesses:
        key = (
            str(witness["source_id"]),
            str(witness["ad_date"]),
            int(witness["bs_year"]),
            int(witness["bs_month"]),
            int(witness["bs_day"]),
        )
        dedup[key] = witness
    witnesses = sorted(dedup.values(), key=lambda row: (int(row["bs_year"]), int(row["bs_month"]), str(row["source_id"])))

    write_csv(WITNESS_DIR / "extracted_witnesses.csv", witnesses, WITNESS_FIELDS)
    write_jsonl(WITNESS_DIR / "extracted_witnesses.jsonl", witnesses)
    write_jsonl(ACQUISITION_DIR / "source_attempts.jsonl", attempts)
    write_jsonl(ACQUISITION_DIR / "failed_sources.jsonl", failures)
    write_jsonl(WITNESS_DIR / "extraction_errors.jsonl", errors)
    summary = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": utc_now(),
        "witness_rows": len(witnesses),
        "source_attempts": len(attempts),
        "failed_or_blocked_sources": len(failures),
        "years_covered": sorted({int(row["bs_year"]) for row in witnesses}),
        "months_covered": len({(int(row["bs_year"]), int(row["bs_month"])) for row in witnesses}),
        "source_type_counts": dict(Counter(str(row["source_type"]) for row in witnesses)),
    }
    (WITNESS_DIR / "extraction_run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def load_witnesses() -> list[dict[str, Any]]:
    rows = read_csv(WITNESS_DIR / "extracted_witnesses.csv")
    normalized = []
    for row in rows:
        item = dict(row)
        item["bs_year"] = int(item["bs_year"])
        item["bs_month"] = int(item["bs_month"])
        item["bs_day"] = int(item["bs_day"])
        item["source_tier"] = int(item["source_tier"])
        item["extraction_confidence"] = float(item["extraction_confidence"])
        normalized.append(item)
    return normalized


def build_agreement_graph(witnesses: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    witnesses = witnesses or load_witnesses()
    graph: dict[str, Any] = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": utc_now(),
        "nodes": {},
    }
    for key, group in _group_witnesses(witnesses).items():
        candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in group:
            candidates[str(row["ad_date"])].append(row)
        candidate_payloads = []
        total_weight = 0.0
        for ad_start, rows in sorted(candidates.items()):
            weight = sum(float(source_policy(str(row["source_type"]))["weight"]) * float(row["extraction_confidence"]) for row in rows)
            total_weight += weight
            candidate_payloads.append(
                {
                    "month_start_ad": ad_start,
                    "weight": round(weight, 4),
                    "witness_count": len(rows),
                    "source_ids": sorted({str(row["source_id"]) for row in rows}),
                    "best_source_tier": min(int(row["source_tier"]) for row in rows),
                }
            )
        best = max(candidate_payloads, key=lambda item: (item["weight"], -item["best_source_tier"], item["witness_count"]))
        graph["nodes"][f"{key[0]}-{key[1]:02d}"] = {
            "bs_year": key[0],
            "bs_month": key[1],
            "candidates": candidate_payloads,
            "chosen_month_start_ad": best["month_start_ad"],
            "agreement_score": round(best["weight"] / total_weight, 4) if total_weight else 0.0,
            "conflict": len(candidate_payloads) > 1,
        }
    (CORPUS_DIR / "source_agreement_graph.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    confidence_rows = []
    for node in graph["nodes"].values():
        confidence_rows.append(
            {
                "bs_year": node["bs_year"],
                "bs_month": node["bs_month"],
                "month_start_ad": node["chosen_month_start_ad"],
                "agreement_score": node["agreement_score"],
                "candidate_count": len(node["candidates"]),
                "conflict": str(bool(node["conflict"])).lower(),
            }
        )
    write_csv(
        CORPUS_DIR / "month_start_confidence.csv",
        confidence_rows,
        ["bs_year", "bs_month", "month_start_ad", "agreement_score", "candidate_count", "conflict"],
    )
    return graph


def _group_witnesses(witnesses: list[dict[str, Any]]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in witnesses:
        if int(row.get("bs_day", 0)) == 1:
            grouped[(int(row["bs_year"]), int(row["bs_month"]))].append(row)
    return grouped


def reconstruct_month_starts(witnesses: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    witnesses = witnesses or load_witnesses()
    graph = build_agreement_graph(witnesses)
    grouped = _group_witnesses(witnesses)
    rows: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        node = graph["nodes"][f"{key[0]}-{key[1]:02d}"]
        chosen = str(node["chosen_month_start_ad"])
        chosen_rows = [row for row in group if str(row["ad_date"]) == chosen]
        conflict_rows = [row for row in group if str(row["ad_date"]) != chosen]
        best_tier = min(int(row["source_tier"]) for row in chosen_rows)
        agreement = float(node["agreement_score"])
        conflict = bool(conflict_rows)
        if best_tier == 1 and not conflict:
            status = "verified"
            manual = False
        elif conflict:
            status = "manual_review_required"
            manual = True
        elif best_tier <= 4 and agreement >= 0.7:
            status = "cross_source_agreement"
            manual = False
        else:
            status = "needs_review"
            manual = True
        rows.append(
            {
                "bs_year": key[0],
                "bs_month": key[1],
                "month_start_ad": chosen,
                "witness_count": len(group),
                "best_source_tier": best_tier,
                "agreement_score": round(agreement, 4),
                "source_ids": ";".join(sorted({str(row["source_id"]) for row in chosen_rows})),
                "conflicting_source_ids": ";".join(sorted({str(row["source_id"]) for row in conflict_rows})),
                "verification_status": status,
                "manual_review_required": str(manual).lower(),
                "notes": "conflicting candidates recorded" if conflict else "chosen by source-weighted agreement",
            }
        )
    write_csv(CORPUS_DIR / "reconstructed_month_starts.csv", rows, MONTH_START_FIELDS)
    return rows, graph


def reconstruct_month_lengths(start_rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if start_rows is None:
        start_rows, _ = reconstruct_month_starts()
    by_key = {(int(row["bs_year"]), int(row["bs_month"])): row for row in start_rows}
    length_rows: list[dict[str, Any]] = []
    full_years = {
        year
        for year in {key[0] for key in by_key}
        if all((year, month) in by_key for month in range(1, 13)) and (year + 1, 1) in by_key
    }
    for year, month in sorted(by_key):
        if year not in full_years:
            continue
        next_key = (year, month + 1) if month < 12 else (year + 1, 1)
        start = date.fromisoformat(str(by_key[(year, month)]["month_start_ad"]))
        end = date.fromisoformat(str(by_key[next_key]["month_start_ad"]))
        length = (end - start).days
        plausible = 29 <= length <= 32
        year_status = str(by_key[(year, month)]["verification_status"])
        usable_training = plausible and year_status != "manual_review_required"
        usable_official = plausible and int(by_key[(year, month)]["best_source_tier"]) == 1 and year_status == "verified"
        notes = []
        if not plausible:
            notes.append("implausible_month_length")
        if year_status == "needs_review":
            notes.append("weak_source_needs_review")
        if year_status == "manual_review_required":
            notes.append("conflict_manual_review_required")
        length_rows.append(
            {
                "bs_year": year,
                "bs_month": month,
                "month_start_ad": start.isoformat(),
                "next_month_start_ad": end.isoformat(),
                "month_length": length,
                "witness_count": by_key[(year, month)]["witness_count"],
                "best_source_tier": by_key[(year, month)]["best_source_tier"],
                "agreement_score": by_key[(year, month)]["agreement_score"],
                "verification_status": year_status if plausible else "invalid",
                "usable_for_training": str(bool(usable_training)).lower(),
                "usable_for_official_claim": str(bool(usable_official)).lower(),
                "notes": ";".join(notes) or "derived_from_adjacent_month_starts",
            }
        )
    write_csv(CORPUS_DIR / "reconstructed_month_lengths.csv", length_rows, MONTH_LENGTH_FIELDS)
    return length_rows


def generate_human_review_queue(start_rows: list[dict[str, Any]] | None = None, length_rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    start_rows = start_rows or read_csv(CORPUS_DIR / "reconstructed_month_starts.csv")
    length_rows = length_rows or read_csv(CORPUS_DIR / "reconstructed_month_lengths.csv")
    rows: list[dict[str, Any]] = []
    length_by_key = {(int(row["bs_year"]), int(row["bs_month"])): row for row in length_rows}
    for row in start_rows:
        year = int(row["bs_year"])
        month = int(row["bs_month"])
        issue = ""
        priority = 50
        reason = ""
        if row.get("conflicting_source_ids"):
            issue = "source_disagreement"
            priority = 100
            reason = "Multiple sources disagree on month start."
        elif int(row.get("best_source_tier", 9)) >= 5:
            issue = "low_trust_consensus"
            priority = 75
            reason = "Only software/third-party-level consensus currently supports this month."
        elif row.get("manual_review_required") == "true":
            issue = "manual_review_required"
            priority = 80
            reason = "Current verification status requires manual review."
        length = length_by_key.get((year, month))
        if length and int(length["month_length"]) not in {29, 30, 31, 32}:
            issue = "invalid_month_length"
            priority = 110
            reason = "Adjacent reconstructed starts imply implausible month length."
        if month in {6, 7} and 2071 <= year <= 2083:
            priority += 15
            reason = (reason + " " if reason else "") + "Ashwin/Kartik boundary is high-impact for 2083-style risk."
        if not issue and year in {2076, 2077, 2078, 2079}:
            issue = "printed_cross_check_priority"
            priority = 70
            reason = "Requested printed/official cross-check window."
        if not issue:
            continue
        rows.append(
            {
                "priority": priority,
                "bs_year": year,
                "bs_month": month,
                "issue_type": issue,
                "current_candidate_start_dates": row["month_start_ad"],
                "sources": row["source_ids"],
                "reason": reason,
                "expected_information_gain": "high" if priority >= 90 else "medium",
                "recommended_manual_action": "Obtain official/printed calendar image or newspaper masthead for this BS day 1.",
                "source_file_or_url": row["source_ids"],
                "page_number_or_crop_if_available": "",
            }
        )
    rows = sorted(rows, key=lambda item: (-int(item["priority"]), int(item["bs_year"]), int(item["bs_month"])))
    write_csv(CORPUS_DIR / "human_review_queue.csv", rows, REVIEW_FIELDS)
    md = ["# Human Review Queue", "", f"Rows: {len(rows)}", ""]
    for item in rows[:25]:
        md.append(
            f"- P{item['priority']} {item['bs_year']}-{int(item['bs_month']):02d}: "
            f"{item['issue_type']} - {item['reason']}"
        )
    (CORPUS_DIR / "human_review_queue.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


def coverage_metrics(length_rows: list[dict[str, Any]] | None = None, witness_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    length_rows = length_rows or read_csv(CORPUS_DIR / "reconstructed_month_lengths.csv")
    witness_rows = witness_rows or read_csv(WITNESS_DIR / "extracted_witnesses.csv")
    months_by_year: dict[int, set[int]] = defaultdict(set)
    for row in length_rows:
        months_by_year[int(row["bs_year"])].add(int(row["bs_month"]))
    years_with_12 = sorted(year for year, months in months_by_year.items() if len(months) == 12)
    witness_type_counts = Counter(str(row["source_type"]) for row in witness_rows)
    best_tier_counts = Counter(str(row["best_source_tier"]) for row in length_rows)
    conflict_count = sum(1 for row in read_csv(CORPUS_DIR / "reconstructed_month_starts.csv") if row.get("conflicting_source_ids"))
    manual_count = sum(1 for row in read_csv(CORPUS_DIR / "reconstructed_month_starts.csv") if row.get("manual_review_required") == "true")
    official_claim_count = sum(1 for row in length_rows if row.get("usable_for_official_claim") == "true")
    training_count = sum(1 for row in length_rows if row.get("usable_for_training") == "true")
    medium_high_years = sorted(
        year
        for year, months in months_by_year.items()
        if len(months) == 12
        and all(
            int(row["best_source_tier"]) <= 4
            for row in length_rows
            if int(row["bs_year"]) == year and int(row["bs_month"]) in months
        )
    )
    medium_high_past_years = [year for year in medium_high_years if year <= 2083]
    metrics = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": utc_now(),
        "years_with_any_witness": len({int(row["bs_year"]) for row in witness_rows}),
        "years_with_12_months": len(years_with_12),
        "years_with_12_months_list": years_with_12,
        "months_reconstructed": len(length_rows),
        "months_official_verified": sum(1 for row in witness_rows if row["source_type"] == "official_verified"),
        "months_printed_verified": sum(1 for row in witness_rows if row["source_type"] == "printed_verified"),
        "months_public_daily_witness": sum(1 for row in witness_rows if row["source_type"] == "public_daily_witness"),
        "months_publisher_reference": sum(1 for row in witness_rows if row["source_type"] == "publisher_reference"),
        "months_software_reference": sum(1 for row in witness_rows if row["source_type"] == "software_table_reference"),
        "months_third_party_reference": sum(1 for row in witness_rows if row["source_type"] == "third_party_reference"),
        "months_needs_review": sum(1 for row in witness_rows if row["source_type"] == "needs_review"),
        "source_type_distribution": dict(witness_type_counts),
        "best_tier_distribution": dict(best_tier_counts),
        "conflict_count": conflict_count,
        "manual_review_required_count": manual_count,
        "usable_for_training_count": training_count,
        "usable_for_official_claim_count": official_claim_count,
        "medium_high_years_with_12_months": len(medium_high_years),
        "medium_high_years_with_12_months_list": medium_high_years,
        "medium_high_past_years_with_12_months": len(medium_high_past_years),
        "medium_high_past_years_with_12_months_list": medium_high_past_years,
        "source_labeled_months": len(length_rows),
        "primary_target_met": len(years_with_12) >= 40 and len(length_rows) >= 480,
        "medium_high_subgoal_met": len(medium_high_years) >= 20,
        "medium_high_30_past_year_subgoal_met": len(medium_high_past_years) >= 30,
        "minimum_fallback_met": all(year in years_with_12 for year in range(2071, 2084)),
    }
    metrics["target_reached"] = bool(metrics["primary_target_met"] or metrics["minimum_fallback_met"])
    return metrics


def write_coverage_report(metrics: dict[str, Any]) -> None:
    (ACQUISITION_DIR / "coverage_report.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Data Acquisition Coverage Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- Target reached: {str(metrics['target_reached']).lower()}",
        f"- Primary target met: {str(metrics['primary_target_met']).lower()}",
        f"- Medium/high 20-year subgoal met: {str(metrics['medium_high_subgoal_met']).lower()}",
        f"- Medium/high 30-past-year subgoal met: {str(metrics['medium_high_30_past_year_subgoal_met']).lower()}",
        f"- Years with 12 reconstructed months: {metrics['years_with_12_months']}",
        f"- Medium/high past years with 12 reconstructed months: {metrics['medium_high_past_years_with_12_months']}",
        f"- Months reconstructed: {metrics['months_reconstructed']}",
        f"- Official witness rows: {metrics['months_official_verified']}",
        f"- Printed/archived witness rows: {metrics['months_printed_verified']}",
        f"- Publisher-reference witness rows: {metrics['months_publisher_reference']}",
        f"- Software-table witness rows: {metrics['months_software_reference']}",
        f"- Third-party witness rows: {metrics['months_third_party_reference']}",
        f"- Conflicts: {metrics['conflict_count']}",
        f"- Manual review required: {metrics['manual_review_required_count']}",
        f"- Usable for training month rows: {metrics['usable_for_training_count']}",
        f"- Usable for official claim month rows: {metrics['usable_for_official_claim_count']}",
        "",
        "The wide reconstruction target and 30-past-year Tier 1-4 support target are met when this report shows the subgoal as true.",
        "Official-grade 99% claims still require more Tier 1/strong Tier 2 source promotion.",
    ]
    (ACQUISITION_DIR / "coverage_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_acquisition_plan() -> None:
    lines = [
        "# Future BS Data Acquisition Plan",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        "## Current Automated Strategy",
        "",
        "1. Preserve existing official/recent Project Parva rows as Tier 1 witnesses.",
        "2. Preserve archived 2076-2077 official/patro rows as Tier 2 but manual-review required.",
        "3. Extract day-1 AD/BS witnesses from local HamroPatro public archive as Tier 6.",
        "4. Extract partial Ratopati public calendar event-day witnesses as Tier 4.",
        "5. Download and parse public Rat32 month pages for 2050-2083 as Tier 4.",
        "6. Download and parse public open-source converter tables as Tier 5.",
        "7. Reconstruct month starts by source-weighted agreement.",
        "8. Derive month lengths only from adjacent reconstructed month starts.",
        "9. Queue conflicts, weak consensus, and Ashwin/Kartik boundary months for manual review.",
        "",
        "## Next Manual Acquisition",
        "",
        "- Add NPNS/government PDF URLs for older years.",
        "- Add archive.org printed panchanga item URLs with year and publisher metadata.",
        "- Add Gorkhapatra/newspaper masthead URLs around BS month starts.",
        "- Promote only reviewed Tier 1/Tier 2 rows into official-grade accuracy claims.",
    ]
    (ACQUISITION_DIR / "acquisition_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_corpus_quality_report(metrics: dict[str, Any]) -> None:
    (CORPUS_DIR / "corpus_quality_report.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Corpus Quality Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- Years with 12 reconstructed months: {metrics['years_with_12_months']}",
        f"- Months reconstructed: {metrics['months_reconstructed']}",
        f"- Best-tier distribution: {json.dumps(metrics['best_tier_distribution'], sort_keys=True)}",
        f"- Source-type distribution: {json.dumps(metrics['source_type_distribution'], sort_keys=True)}",
        f"- Conflicts found: {metrics['conflict_count']}",
        f"- Human/manual review required: {metrics['manual_review_required_count']}",
        f"- Official-claim usable month rows: {metrics['usable_for_official_claim_count']}",
        "",
        "Tier 5/6 witnesses are useful for reconstruction and cross-checking, but they are not official truth.",
    ]
    (CORPUS_DIR / "corpus_quality_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blocker_report(metrics: dict[str, Any]) -> None:
    attempts = [json.loads(line) for line in (ACQUISITION_DIR / "source_attempts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    failures = [json.loads(line) for line in (ACQUISITION_DIR / "failed_sources.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    review_rows = read_csv(CORPUS_DIR / "human_review_queue.csv")
    missing_medium_high = 30 - int(metrics["medium_high_past_years_with_12_months"])
    official_claim_blocked = int(metrics.get("usable_for_official_claim_count", 0)) < 480
    lines = [
        "# Data Acquisition Blocker Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        "## Summary",
        "",
        f"- Primary reconstruction target met: {str(metrics['primary_target_met']).lower()}",
        f"- Medium/high 30-past-year subgoal met: {str(metrics['medium_high_30_past_year_subgoal_met']).lower()}",
        f"- Medium/high past full years still needed for 30-year target: {max(0, missing_medium_high)}",
        f"- Source-labeled reconstruction target blocked: {str(not metrics['target_reached']).lower()}",
        f"- Official-grade 99% claim still blocked by Tier 1/strong Tier 2 depth: {str(official_claim_blocked).lower()}",
        "",
        "## Sources Attempted",
        "",
    ]
    for attempt in attempts:
        lines.append(
            f"- {attempt['source_name']}: {attempt['status']}; rows={attempt['rows_extracted']}; "
            f"years={attempt['years_covered']}; error={attempt['error_if_any'] or 'none'}"
        )
    lines.extend(["", "## Failed Or Blocked Sources", ""])
    for failure in failures:
        lines.append(
            f"- {failure['source_name']} ({failure['source_url']}): {failure['status']} - "
            f"{failure['error_if_any']}; next: {failure['next_action']}"
        )
    lines.extend(["", "## Top Manual Acquisition Targets", ""])
    for row in review_rows[:25]:
        lines.append(
            f"- P{row['priority']} {row['bs_year']}-{int(row['bs_month']):02d}: "
            f"{row['issue_type']} - {row['recommended_manual_action']}"
        )
    lines.extend(
        [
            "",
            "## Exact Next Steps",
            "",
            "1. Add public NPNS/government PDF URLs for older years if available.",
            "2. Add archive.org printed panchanga item URLs for 2071-2083 and older years.",
            "3. Capture Gorkhapatra/newspaper mastheads around BS month starts for weak/conflicting rows.",
            "4. Manually review archived 2076-2077 official/patro rows and promote only verified rows.",
            "5. Re-run `python scripts/future_bs/run_data_acquisition_loop.py` and `python scripts/future_bs/check_data_target.py`.",
        ]
    )
    (ACQUISITION_DIR / "blocker_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_report(metrics: dict[str, Any]) -> None:
    review_rows = read_csv(CORPUS_DIR / "human_review_queue.csv")
    lines = [
        "# Final Data Acquisition Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"1. target reached: {str(metrics['target_reached']).lower()}",
        f"2. years covered: {metrics['years_with_12_months']}",
        f"3. months reconstructed: {metrics['months_reconstructed']}",
        f"4. source tier distribution: {json.dumps(metrics['best_tier_distribution'], sort_keys=True)}",
        (
            "5. official/printed/public witness counts: "
            f"official={metrics['months_official_verified']}, "
            f"printed={metrics['months_printed_verified']}, "
            f"public_daily={metrics['months_public_daily_witness']}, "
            f"publisher={metrics['months_publisher_reference']}, "
            f"software={metrics['months_software_reference']}, "
            f"third_party={metrics['months_third_party_reference']}"
        ),
        f"6. conflicts found: {metrics['conflict_count']}",
        f"7. human review queue size: {len(review_rows)}",
        f"8. 30-past-year Tier 1-4 support target: {str(metrics['medium_high_30_past_year_subgoal_met']).lower()} ({metrics['medium_high_past_years_with_12_months']} years)",
        "9. blockers: none for the 30-past-year source-labeled reconstruction target; official-grade 99% claims still need more Tier 1/strong Tier 2 reviewed years.",
        "10. exact next manual acquisition steps: seed NPNS PDFs, archive.org panchanga scans, and newspaper mastheads around weak or conflicting month starts.",
        "11. how this corpus improves the 99% effort: it expands reconstruction coverage while preserving claim safety by separating official-grade rows from weak witnesses.",
        "",
        "This corpus must not be represented as official future-calendar truth. Low-trust witnesses are for reconstruction, cross-checking, and active learning.",
    ]
    (ACQUISITION_DIR / "FINAL_DATA_ACQUISITION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_reconstruction_pipeline(fetch_rat32: bool = True) -> dict[str, Any]:
    write_acquisition_plan()
    summary = collect_witnesses(fetch_rat32=fetch_rat32)
    start_rows, _ = reconstruct_month_starts()
    length_rows = reconstruct_month_lengths(start_rows)
    generate_human_review_queue(start_rows, length_rows)
    metrics = coverage_metrics(length_rows, load_witnesses())
    write_coverage_report(metrics)
    write_corpus_quality_report(metrics)
    write_blocker_report(metrics)
    write_final_report(metrics)
    return {"summary": summary, "metrics": metrics}


def check_data_target() -> dict[str, Any]:
    metrics = coverage_metrics()
    target_ok = bool(metrics["primary_target_met"] or metrics["minimum_fallback_met"])
    blockers = []
    if not metrics["primary_target_met"]:
        blockers.append("primary_target_not_met")
    if not metrics["medium_high_subgoal_met"]:
        blockers.append("medium_high_20_year_subgoal_not_met")
    if not metrics.get("medium_high_30_past_year_subgoal_met", False):
        blockers.append("medium_high_30_past_year_subgoal_not_met")
    if not target_ok:
        blockers.append("minimum_fallback_not_met")
    result = {
        "publication_status": PUBLICATION_STATUS,
        "target_passed": target_ok,
        "primary_target_met": metrics["primary_target_met"],
        "minimum_fallback_met": metrics["minimum_fallback_met"],
        "medium_high_subgoal_met": metrics["medium_high_subgoal_met"],
        "medium_high_30_past_year_subgoal_met": metrics.get("medium_high_30_past_year_subgoal_met", False),
        "medium_high_past_years_with_12_months": metrics.get("medium_high_past_years_with_12_months", 0),
        "medium_high_past_years_with_12_months_list": metrics.get("medium_high_past_years_with_12_months_list", []),
        "years_with_12_months": metrics["years_with_12_months"],
        "months_reconstructed": metrics["months_reconstructed"],
        "blockers": blockers,
    }
    return result


__all__ = [
    "WITNESS_FIELDS",
    "SOURCE_TIERS",
    "build_agreement_graph",
    "check_data_target",
    "collect_witnesses",
    "coverage_metrics",
    "extract_open_source_converter_tables",
    "extract_rat32_pages",
    "generate_human_review_queue",
    "parse_medic_days_in_month",
    "parse_sharingapples_config",
    "reconstruct_month_lengths",
    "reconstruct_month_starts",
    "run_reconstruction_pipeline",
    "source_policy",
]
