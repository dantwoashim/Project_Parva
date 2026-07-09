"""Source-labeled witness corpus reconstruction for future-BS accuracy work."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from app.research.future_bs.paths import project_root

PROJECT_ROOT = project_root()
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


def collect_source_witnesses(fetch_rat32: bool = True) -> dict[str, Any]:
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


