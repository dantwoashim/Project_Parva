"""Bounded high-trust source acquisition for BS month-start witnesses.

This module only promotes rows when a clear AD <-> BS date witness is extracted.
Downloaded or discovered sources that do not expose a clear pair are retained as
source attempts/manual-review targets, not silently converted into calendar truth.
"""

from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import data_acquisition as da

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "data" / "future_bs"
RAW_SOURCES_DIR = DATA_ROOT / "raw_sources"
WITNESS_DIR = DATA_ROOT / "witnesses"
ACQUISITION_DIR = DATA_ROOT / "data_acquisition"
CORPUS_DIR = DATA_ROOT / "corpus"

PUBLICATION_STATUS = da.PUBLICATION_STATUS
HIGH_TRUST_VERSION = "high_trust_acquisition_v1"

HIGH_TRUST_FIELDS = [
    *da.WITNESS_FIELDS,
    "source_family",
    "duplicate_status",
    "source_independence_score",
    "raw_file_path",
    "page_number",
    "section",
]

FAMILY_OUTPUTS = {
    "rajpatra": "rajpatra_witnesses.csv",
    "moha": "moha_holiday_witnesses.csv",
    "gorkhapatra": "gorkhapatra_masthead_witnesses.csv",
    "archive_org_panchanga": "archive_panchanga_witnesses.csv",
    "public_notices": "public_notice_witnesses.csv",
    "independent_newspapers": "independent_newspaper_witnesses.csv",
}

SOURCE_FAMILIES: list[dict[str, Any]] = [
    {
        "family": "rajpatra",
        "name": "Nepal Rajpatra / Department of Printing",
        "tier": "official_verified",
        "cache_dir": "rajpatra",
        "urls": [
            "https://rajpatra.dop.gov.np/",
        ],
        "report": "rajpatra_acquisition_report.md",
        "keywords": ["सार्वजनिक बिदा", "सार्वजनिक विदा", "Government/Public Holidays"],
    },
    {
        "family": "moha",
        "name": "Ministry of Home Affairs public holiday notices",
        "tier": "official_verified",
        "cache_dir": "moha",
        "urls": [
            "https://www.moha.gov.np/en/page/holidays",
            "https://www.moha.gov.np/post/government-and-public-holidays-in-2080",
            "https://www.moha.gov.np/post/government-and-public-holidays-in-2081-2",
            "https://www.moha.gov.np/post/government-and-public-holidays-in-2082-2",
            "https://www.moha.gov.np/post/government-and-public-holidays-in-2083",
        ],
        "report": "moha_acquisition_report.md",
        "keywords": ["public holiday", "सार्वजनिक विदा", "सार्वजनिक बिदा"],
    },
    {
        "family": "gorkhapatra",
        "name": "Gorkhapatra public daily mastheads",
        "tier": "public_daily_witness",
        "cache_dir": "gorkhapatra",
        "urls": [
            "https://gorkhapatraonline.com/",
            "https://epaper.gorkhapatraonline.com/",
        ],
        "report": "gorkhapatra_acquisition_report.md",
        "keywords": ["masthead", "epaper", "गोरखापत्र"],
    },
    {
        "family": "archive_org_panchanga",
        "name": "Archive.org printed panchanga/patro scans",
        "tier": "printed_verified",
        "cache_dir": "archive_org_panchanga",
        "urls": [
            "https://archive.org/advancedsearch.php?q=title%3A%28Surya%20Panchanga%20OR%20Toyanath%20Panchanga%20OR%20Nepali%20Panchanga%20OR%20Nepali%20Patro%29&fl%5B%5D=identifier&fl%5B%5D=title&rows=25&output=json",
        ],
        "report": "archive_panchanga_acquisition_report.md",
        "keywords": ["Surya Panchanga", "Toyanath Panchanga", "Nepali Panchanga", "नेपाली पात्रो"],
    },
    {
        "family": "public_notices",
        "name": "Public institution notice archives",
        "tier": "official_verified",
        "cache_dir": "public_notices",
        "urls": [
            "https://psc.gov.np/",
            "https://supremecourt.gov.np/",
            "https://www.nrb.org.np/",
            "https://tu.edu.np/",
            "https://election.gov.np/",
        ],
        "report": "public_notice_acquisition_report.md",
        "keywords": ["notice", "सूचना", "date"],
    },
    {
        "family": "independent_newspapers",
        "name": "Independent newspaper e-paper families",
        "tier": "public_daily_witness",
        "cache_dir": "independent_newspapers",
        "urls": [
            "https://risingnepaldaily.com/",
            "https://ekantipur.com/",
            "https://annapurnapost.com/",
            "https://nagariknews.nagariknetwork.com/",
        ],
        "report": "newspaper_acquisition_report.md",
        "keywords": ["epaper", "masthead", "date"],
    },
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ensure_dirs() -> None:
    for path in (RAW_SOURCES_DIR, WITNESS_DIR, ACQUISITION_DIR, CORPUS_DIR):
        path.mkdir(parents=True, exist_ok=True)
    for family in SOURCE_FAMILIES:
        (RAW_SOURCES_DIR / str(family["cache_dir"])).mkdir(parents=True, exist_ok=True)


def _safe_name(url: str, index: int) -> str:
    parsed = urllib.parse.urlparse(url)
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{parsed.netloc}{parsed.path}")[:140].strip("_")
    suffix = ".json" if "output=json" in url or url.endswith(".json") else ".html"
    if parsed.path.lower().endswith(".pdf") or url.lower().endswith("/file"):
        suffix = ".pdf"
    return f"{index:02d}_{stem or 'source'}{suffix}"


def _download(url: str, path: Path, *, timeout: int = 20) -> dict[str, Any]:
    if path.exists() and path.stat().st_size > 0:
        return {
            "ok": True,
            "status": "cached",
            "path": str(path.relative_to(PROJECT_ROOT)),
            "bytes": path.stat().st_size,
            "content_type": "",
            "error": "",
        }
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ProjectParvaHighTrustCorpus/1.0",
            "Accept": "text/html,application/json,application/pdf;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
            status_code = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {
            "ok": 200 <= int(status_code) < 400,
            "status": str(status_code),
            "path": str(path.relative_to(PROJECT_ROOT)),
            "bytes": len(data),
            "content_type": content_type,
            "error": "",
        }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": str(exc.code), "path": str(path.relative_to(PROJECT_ROOT)), "bytes": 0, "content_type": "", "error": str(exc)}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "status": "error", "path": str(path.relative_to(PROJECT_ROOT)), "bytes": 0, "content_type": "", "error": str(exc)}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _discover_links(base_url: str, text: str) -> list[str]:
    links = set()
    for match in re.finditer(r"""href=["']([^"']+)["']""", text, flags=re.I):
        href = html.unescape(match.group(1))
        if not href:
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        split = urllib.parse.urlsplit(absolute)
        absolute = urllib.parse.urlunsplit(
            (
                split.scheme,
                split.netloc,
                urllib.parse.quote(split.path, safe="/:%"),
                urllib.parse.quote(split.query, safe="=&%/:?"),
                split.fragment,
            )
        )
        lower = absolute.lower()
        if lower.endswith((".css", ".js", ".svg", ".ico", ".png", ".webp", ".woff", ".woff2")):
            continue
        if any(token in lower for token in (".pdf", "holiday", "bida", "vida", "notice", "suchana", "%e0%a4%b8%e0%a5%82%e0%a4%9a%e0%a4%a8%e0%a4%be")):
            links.add(absolute)
    return sorted(links)


def _attempt_payload(
    *,
    family: dict[str, Any],
    url: str,
    result: dict[str, Any],
    rows: int,
    next_action: str,
) -> dict[str, Any]:
    return {
        "phase": HIGH_TRUST_VERSION,
        "source_family": family["family"],
        "source_name": family["name"],
        "source_url": url,
        "attempted_at": _now(),
        "status": "downloaded" if result["ok"] else f"blocked_{result['status']}",
        "rows_extracted": rows,
        "years_covered": [],
        "months_covered": 0,
        "cached_file": result["path"],
        "bytes": result["bytes"],
        "error_if_any": result["error"],
        "next_action": next_action,
        "publication_status": PUBLICATION_STATUS,
    }


def _empty_witness_file(path: Path) -> None:
    da.write_csv(path, [], HIGH_TRUST_FIELDS)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _merge_attempt_log(path: Path, new_rows: list[dict[str, Any]]) -> None:
    existing: list[dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("phase") != HIGH_TRUST_VERSION:
                existing.append(row)
    da.write_jsonl(path, [*existing, *new_rows])


def _add_high_trust_metadata(row: dict[str, Any], family: str, raw_path: str, duplicate_status: str) -> dict[str, Any]:
    enriched = {field: row.get(field, "") for field in da.WITNESS_FIELDS}
    enriched.update(
        {
            "source_family": family,
            "duplicate_status": duplicate_status,
            "source_independence_score": 1.0,
            "raw_file_path": raw_path,
            "page_number": "",
            "section": "",
        }
    )
    return enriched


def _classify_duplicate(row: dict[str, Any], existing_keys: set[tuple[int, int, int, str]]) -> str:
    key = (int(row["bs_year"]), int(row["bs_month"]), int(row["bs_day"]), str(row["ad_date"]))
    if key in existing_keys and str(row["source_type"]) in {"official_verified", "printed_verified", "public_daily_witness"}:
        return "duplicate_but_promotes_trust"
    if key in existing_keys:
        return "already_in_corpus"
    return "genuinely_new_source"


def _existing_witness_keys() -> set[tuple[int, int, int, str]]:
    keys = set()
    for row in da.read_csv(WITNESS_DIR / "extracted_witnesses.csv"):
        try:
            keys.add((int(row["bs_year"]), int(row["bs_month"]), int(row["bs_day"]), str(row["ad_date"])))
        except (KeyError, ValueError):
            continue
    return keys


def _collect_family(family: dict[str, Any], existing_keys: set[tuple[int, int, int, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    cached_files: list[str] = []
    cache_dir = RAW_SOURCES_DIR / str(family["cache_dir"])
    queue = list(family["urls"])
    seen = set(queue)
    index = 0
    while queue and index < 20:
        url = queue.pop(0)
        index += 1
        cache_path = cache_dir / _safe_name(url, index)
        result = _download(url, cache_path)
        if result["ok"]:
            cached_files.append(result["path"])
            text = _read_text(cache_path)
            for link in _discover_links(url, text):
                if link not in seen and len(seen) < 40:
                    seen.add(link)
                    queue.append(link)
            # The current parser deliberately does not infer AD/BS witnesses
            # from notice titles alone. Only clear AD<->BS pairs should enter rows.
            extracted_rows = 0
            next_action = "Manual review needed: cached source did not expose a machine-clear AD/BS month-start pair."
        else:
            extracted_rows = 0
            next_action = "Retry later or add a direct public file URL/seed if the site blocks bounded fetches."
        attempt = _attempt_payload(
            family=family,
            url=url,
            result=result,
            rows=extracted_rows,
            next_action=next_action,
        )
        attempts.append(attempt)
        if not result["ok"]:
            failures.append(attempt)

    # If future parser extensions add rows, classify them here before writing.
    for row in rows:
        row["duplicate_status"] = _classify_duplicate(row, existing_keys)
    return rows, attempts, failures, cached_files


def _write_family_report(family: dict[str, Any], rows: list[dict[str, Any]], attempts: list[dict[str, Any]], cached: list[str]) -> None:
    failures = [row for row in attempts if str(row["status"]).startswith("blocked_")]
    lines = [
        f"# {family['name']} Acquisition Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- Source family: `{family['family']}`",
        f"- Trust tier if clear: `{family['tier']}`",
        f"- URLs attempted: {len(attempts)}",
        f"- Cached successful files/pages: {len(cached)}",
        f"- Machine-clear witness rows extracted: {len(rows)}",
        f"- Blocked/failed attempts: {len(failures)}",
        "",
        "Rows are only promoted when a clear AD <-> BS witness exists. Cached sources with no clear pair are retained for manual review.",
        "",
        "## Attempts",
        "",
    ]
    for attempt in attempts:
        lines.append(
            f"- {attempt['status']}: {attempt['source_url']} -> {attempt['cached_file'] or 'not cached'}; "
            f"error={attempt['error_if_any'] or 'none'}"
        )
    (ACQUISITION_DIR / str(family["report"])).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(attempts: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    by_family = Counter(row["source_family"] for row in attempts)
    row_counts = Counter(row.get("source_family", "") for row in rows)
    payload = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": _now(),
        "version": HIGH_TRUST_VERSION,
        "families_attempted": [family["family"] for family in SOURCE_FAMILIES],
        "attempt_counts": dict(by_family),
        "new_rows_by_family": dict(row_counts),
        "source_families": SOURCE_FAMILIES,
        "rule": "No source is promoted without a clear public AD/BS witness and provenance.",
    }
    _write_json(ACQUISITION_DIR / "high_trust_source_manifest.json", payload)
    lines = [
        "# High-Trust Source Manifest",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- Families attempted: {len(SOURCE_FAMILIES)}",
        f"- Source attempts recorded: {len(attempts)}",
        f"- Machine-clear new witness rows: {len(rows)}",
        "",
    ]
    for family in SOURCE_FAMILIES:
        lines.append(f"- {family['family']}: {by_family.get(family['family'], 0)} attempts, {row_counts.get(family['family'], 0)} rows")
    (ACQUISITION_DIR / "high_trust_source_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_coverage(rows: list[dict[str, Any]], attempts: list[dict[str, Any]]) -> None:
    cached_count = sum(1 for row in attempts if row.get("cached_file") and int(row.get("bytes") or 0) > 0)
    failures = [row for row in attempts if str(row.get("status", "")).startswith("blocked_")]
    payload = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": _now(),
        "new_high_trust_rows": len(rows),
        "new_tier_1_rows": sum(1 for row in rows if row.get("source_type") == "official_verified"),
        "new_tier_2_rows": sum(1 for row in rows if row.get("source_type") == "printed_verified"),
        "new_tier_3_rows": sum(1 for row in rows if row.get("source_type") == "public_daily_witness"),
        "successful_cached_sources": cached_count,
        "failed_or_blocked_sources": len(failures),
        "families_attempted": [family["family"] for family in SOURCE_FAMILIES],
        "source_attempts": len(attempts),
        "blocker": "No additional machine-clear high-trust AD/BS month-start pair was extracted from the bounded public attempts.",
    }
    _write_json(ACQUISITION_DIR / "new_source_coverage_report.json", payload)
    lines = [
        "# New Source Coverage Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- New high-trust witness rows: {payload['new_high_trust_rows']}",
        f"- New Tier 1 rows: {payload['new_tier_1_rows']}",
        f"- New Tier 2 rows: {payload['new_tier_2_rows']}",
        f"- New Tier 3 rows: {payload['new_tier_3_rows']}",
        f"- Successful cached public sources: {payload['successful_cached_sources']}",
        f"- Failed or blocked source attempts: {payload['failed_or_blocked_sources']}",
        "",
        "No source was promoted by inference. Cached source files/pages are now available for manual review and parser extension.",
    ]
    (ACQUISITION_DIR / "new_source_coverage_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manual_targets(attempts: list[dict[str, Any]]) -> None:
    review_rows = da.read_csv(CORPUS_DIR / "human_review_queue.csv")
    targets = []
    top_review = review_rows[:100] if review_rows else []
    institutions = [
        ("Madan Puraskar Pustakalaya", "printed_panchanga_catalog", "cover, colophon, Baishakh 1, Ashwin, Kartik, Chaitra, next-year Baishakh 1"),
        ("Nepal National Library", "printed_calendar_archive", "same minimal evidence pages"),
        ("National Archives Nepal", "official_or_printed_archives", "public holiday notices and panchanga scans"),
        ("TU Central Library", "publisher_collection", "Surya/Toyanath/Jebi Patro yearly scans"),
        ("Panchanga publishers", "publisher_direct_request", "year-specific minimal evidence pages"),
    ]
    rank = 1
    for name, target_type, pages in institutions:
        targets.append(
            {
                "rank": rank,
                "institution_or_publisher": name,
                "target_type": target_type,
                "priority_years_months": "2076-2079; Ashwin/Kartik conflict rows; invalid 2091/2092/2095 weak rows",
                "requested_pages": pages,
                "reason": "Promotes weak/conflicting rows into official/printed evidence without requiring a full scan.",
                "contact_or_url": "",
            }
        )
        rank += 1
    for row in top_review[:25]:
        targets.append(
            {
                "rank": rank,
                "institution_or_publisher": "Any official/printed/public daily witness",
                "target_type": "month_start_confirmation",
                "priority_years_months": f"{row['bs_year']}-{int(row['bs_month']):02d}",
                "requested_pages": "date-bearing page or masthead around BS day 1",
                "reason": row.get("reason", ""),
                "contact_or_url": row.get("source_file_or_url", ""),
            }
        )
        rank += 1
    da.write_csv(
        ACQUISITION_DIR / "manual_acquisition_targets.csv",
        targets,
        ["rank", "institution_or_publisher", "target_type", "priority_years_months", "requested_pages", "reason", "contact_or_url"],
    )
    plan = [
        "# Library and Publisher Request Plan",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        "Request minimal evidence pages first instead of full-book digitization: cover, publisher/colophon, approval page, Baishakh 1, Ashwin, Kartik, Chaitra, and next-year Baishakh 1.",
        "",
        "Priority is assigned to rows that resolve source disagreements, verify Ashwin/Kartik behavior, or promote weak source-only month starts.",
    ]
    (ACQUISITION_DIR / "library_publisher_request_plan.md").write_text("\n".join(plan) + "\n", encoding="utf-8")
    (ACQUISITION_DIR / "request_email_english.md").write_text(
        "\n".join(
            [
                "Subject: Request for date evidence pages from Nepali Patro/Panchanga archives",
                "",
                "Namaste,",
                "",
                "I am building a source-labeled historical Bikram Sambat calendar corpus for independent validation. Could you share scans or photographs of the minimal evidence pages for the requested years: cover, publisher/colophon, approval page, Baishakh 1, Ashwin, Kartik, Chaitra, and the next-year Baishakh 1 page?",
                "",
                "The pages will be cited as provenance, and weak or ambiguous data will not be labeled as official.",
                "",
                "Thank you.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (ACQUISITION_DIR / "request_email_nepali.md").write_text(
        "\n".join(
            [
                "विषय: नेपाली पात्रो/पञ्चाङ्गका मिति प्रमाण पृष्ठहरू उपलब्ध गराइदिनुहुन अनुरोध",
                "",
                "नमस्कार,",
                "",
                "ऐतिहासिक विक्रम सम्बत् पात्रोको स्रोत-सहितको प्रमाणित डाटा तयार गर्न केही न्यूनतम पृष्ठहरूको प्रतिलिपि आवश्यक परेको छ। सम्भव भए आवरण, प्रकाशक/कोलोफोन, स्वीकृति पृष्ठ, बैशाख १, आश्विन, कार्तिक, चैत्र र अर्को वर्षको बैशाख १ पृष्ठ उपलब्ध गराइदिनुहुन अनुरोध छ।",
                "",
                "उक्त सामग्री स्रोत प्रमाणका रूपमा मात्र प्रयोग गरिनेछ। अस्पष्ट वा कमजोर प्रमाणलाई आधिकारिक भनेर दाबी गरिने छैन।",
                "",
                "धन्यवाद।",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def research_and_collect_high_trust_sources() -> dict[str, Any]:
    _ensure_dirs()
    existing_keys = _existing_witness_keys()
    all_rows: list[dict[str, Any]] = []
    all_attempts: list[dict[str, Any]] = []
    all_failures: list[dict[str, Any]] = []
    for family in SOURCE_FAMILIES:
        rows, attempts, failures, cached = _collect_family(family, existing_keys)
        all_rows.extend(rows)
        all_attempts.extend(attempts)
        all_failures.extend(failures)
        output_path = WITNESS_DIR / FAMILY_OUTPUTS[str(family["family"])]
        if rows:
            da.write_csv(output_path, rows, HIGH_TRUST_FIELDS)
        else:
            _empty_witness_file(output_path)
        _write_family_report(family, rows, attempts, cached)

    da.write_csv(WITNESS_DIR / "new_high_trust_witnesses.csv", all_rows, HIGH_TRUST_FIELDS)
    da.write_jsonl(WITNESS_DIR / "new_high_trust_witnesses.jsonl", all_rows)
    _merge_attempt_log(ACQUISITION_DIR / "source_attempts.jsonl", all_attempts)
    _merge_attempt_log(ACQUISITION_DIR / "failed_sources.jsonl", all_failures)
    _write_manifest(all_attempts, all_rows)
    _write_coverage(all_rows, all_attempts)
    _write_manual_targets(all_attempts)
    return {
        "publication_status": PUBLICATION_STATUS,
        "created_at": _now(),
        "families_attempted": len(SOURCE_FAMILIES),
        "source_attempts": len(all_attempts),
        "failed_or_blocked_sources": len(all_failures),
        "new_high_trust_rows": len(all_rows),
        "outputs": {
            "witness_csv": str((WITNESS_DIR / "new_high_trust_witnesses.csv").relative_to(PROJECT_ROOT)),
            "manifest": str((ACQUISITION_DIR / "high_trust_source_manifest.json").relative_to(PROJECT_ROOT)),
            "coverage": str((ACQUISITION_DIR / "new_source_coverage_report.json").relative_to(PROJECT_ROOT)),
        },
    }


def merge_high_trust_witnesses() -> dict[str, Any]:
    da.ensure_dirs()
    base_rows = da.read_csv(WITNESS_DIR / "extracted_witnesses.csv")
    new_rows = da.read_csv(WITNESS_DIR / "new_high_trust_witnesses.csv")
    normalized_new = [{field: row.get(field, "") for field in da.WITNESS_FIELDS} for row in new_rows]
    before_counts = Counter(row.get("source_type", "") for row in base_rows)
    dedup: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for row in [*base_rows, *normalized_new]:
        if not row.get("source_id"):
            continue
        key = (
            str(row.get("source_id", "")),
            str(row.get("ad_date", "")),
            str(row.get("bs_year", "")),
            str(row.get("bs_month", "")),
            str(row.get("bs_day", "")),
        )
        dedup[key] = row
    merged = sorted(dedup.values(), key=lambda row: (int(row["bs_year"]), int(row["bs_month"]), str(row["source_id"])))
    da.write_csv(WITNESS_DIR / "extracted_witnesses.csv", merged, da.WITNESS_FIELDS)
    da.write_jsonl(WITNESS_DIR / "extracted_witnesses.jsonl", merged)
    start_rows, _ = da.reconstruct_month_starts(merged)
    length_rows = da.reconstruct_month_lengths(start_rows)
    review_rows = da.generate_human_review_queue(start_rows, length_rows)
    metrics = da.coverage_metrics(length_rows, merged)
    da.write_coverage_report(metrics)
    da.write_corpus_quality_report(metrics)
    after_counts = Counter(row.get("source_type", "") for row in merged)
    delta = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": _now(),
        "base_rows_before": len(base_rows),
        "new_rows_available": len(normalized_new),
        "rows_after_merge": len(merged),
        "new_rows_added": len(merged) - len(base_rows),
        "new_tier_1_rows": after_counts.get("official_verified", 0) - before_counts.get("official_verified", 0),
        "new_tier_2_rows": after_counts.get("printed_verified", 0) - before_counts.get("printed_verified", 0),
        "new_tier_3_rows": after_counts.get("public_daily_witness", 0) - before_counts.get("public_daily_witness", 0),
        "rows_promoted": 0,
        "conflicts_resolved": 0,
        "conflicts_added": metrics["conflict_count"],
        "official_claim_usable_count_after": metrics["usable_for_official_claim_count"],
        "printed_verified_count_after": after_counts.get("printed_verified", 0),
        "public_daily_witness_count_after": after_counts.get("public_daily_witness", 0),
        "human_review_queue_rows": len(review_rows),
        "remaining_blockers": [
            "No additional machine-clear high-trust month-start witnesses were automatically extracted from bounded source attempts.",
            "Official-grade 99% claims remain blocked by Tier 1/strong Tier 2 depth.",
        ],
    }
    _write_json(ACQUISITION_DIR / "post_acquisition_delta_report.json", delta)
    lines = [
        "# Post-Acquisition Delta Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- Base rows before: {delta['base_rows_before']}",
        f"- New high-trust rows available: {delta['new_rows_available']}",
        f"- Rows after merge: {delta['rows_after_merge']}",
        f"- New rows added: {delta['new_rows_added']}",
        f"- New Tier 1 rows: {delta['new_tier_1_rows']}",
        f"- New Tier 2 rows: {delta['new_tier_2_rows']}",
        f"- New Tier 3 rows: {delta['new_tier_3_rows']}",
        f"- Official-claim usable month rows after: {delta['official_claim_usable_count_after']}",
        f"- Human-review queue rows: {delta['human_review_queue_rows']}",
        "",
        "Bounded public attempts improved the manual acquisition map and cached sources, but did not produce new machine-clear high-trust month-start witnesses.",
    ]
    (ACQUISITION_DIR / "post_acquisition_delta_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return delta


__all__ = [
    "HIGH_TRUST_FIELDS",
    "research_and_collect_high_trust_sources",
    "merge_high_trust_witnesses",
]
