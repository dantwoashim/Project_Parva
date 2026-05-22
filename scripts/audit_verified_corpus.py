#!/usr/bin/env python3
"""Audit and optionally repair the future-BS source-labeled month corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

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
EXTENDED_FIELDS = [
    "bs_year",
    *MONTH_COLUMNS,
    "source_type",
    "source_name",
    "source_url_or_scan",
    "verification_status",
    "entered_by",
    "reviewed_by",
    "checksum",
    "notes",
]
VALID_SOURCE_TYPES = {
    "official_verified",
    "printed_verified",
    "physical_patro_verified",
    "approved_patro",
    "internal_reference",
    "third_party_reference",
    "scraped_reference",
    "needs_review",
}
VALID_STATUSES = {
    "verified",
    "reviewed",
    "archived_unstructured_needs_review",
    "needs_review",
    "excluded",
}


class MissingPrivateCorpusError(FileNotFoundError):
    """Raised when the private Future-BS corpus is intentionally absent."""


def _missing_private_corpus_message(path: Path) -> str:
    return (
        f"Future-BS verified month corpus is missing: {path}. "
        "This is a private/wide-corpus input intentionally absent from public clones. "
        "Provide the corpus with --corpus or restore data/future_bs/corpus/verified_month_lengths.csv "
        "from the private source archive before running this audit. "
        "The script will not create an empty replacement because that would weaken accuracy evidence."
    )


def row_checksum(row: dict[str, str]) -> str:
    parts = [
        row.get("bs_year", ""),
        *(row.get(column, "") for column in MONTH_COLUMNS),
        row.get("source_type", ""),
        row.get("source_name") or row.get("source_reference", ""),
        row.get("source_url_or_scan", ""),
        row.get("verification_status", ""),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    source_name = row.get("source_name") or row.get("source_reference", "")
    normalized = {field: row.get(field, "") for field in EXTENDED_FIELDS}
    normalized["source_name"] = source_name
    normalized["entered_by"] = normalized["entered_by"] or "system"
    normalized["reviewed_by"] = normalized["reviewed_by"] or ""
    normalized["source_url_or_scan"] = normalized["source_url_or_scan"] or source_name
    normalized["notes"] = normalized["notes"] or ""
    normalized["checksum"] = normalized["checksum"] or row_checksum(normalized)
    return normalized


def audit(path: Path, *, fix_checksums: bool = False) -> tuple[dict, list[dict[str, str]]]:
    if not path.exists():
        raise MissingPrivateCorpusError(_missing_private_corpus_message(path))
    if fix_checksums and not path.is_file():
        raise MissingPrivateCorpusError(_missing_private_corpus_message(path))

    rows: list[dict[str, str]] = []
    issues: list[dict[str, str]] = []
    source_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    years: list[int] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            row = normalize_row(raw)
            rows.append(row)
            year_label = row.get("bs_year", "?")
            try:
                year = int(row["bs_year"])
                years.append(year)
            except ValueError:
                issues.append({"year": year_label, "severity": "critical", "issue": "invalid bs_year"})
                continue
            try:
                months = [int(row[column]) for column in MONTH_COLUMNS]
            except ValueError:
                issues.append({"year": year_label, "severity": "critical", "issue": "non-numeric month length"})
                continue
            if any(days < 29 or days > 32 for days in months):
                issues.append({"year": year_label, "severity": "critical", "issue": "month length outside 29-32"})
            if sum(months) not in {365, 366}:
                issues.append({"year": year_label, "severity": "major", "issue": "year total outside 365/366"})
            if row["source_type"] not in VALID_SOURCE_TYPES:
                issues.append({"year": year_label, "severity": "major", "issue": "unknown source_type"})
            if row["verification_status"] not in VALID_STATUSES:
                issues.append({"year": year_label, "severity": "major", "issue": "unknown verification_status"})
            expected = row_checksum(row)
            if row["checksum"] != expected:
                if fix_checksums:
                    row["checksum"] = expected
                else:
                    issues.append({"year": year_label, "severity": "major", "issue": "checksum mismatch"})
            source_counts[row["source_type"]] = source_counts.get(row["source_type"], 0) + 1
            status_counts[row["verification_status"]] = status_counts.get(row["verification_status"], 0) + 1

    duplicate_years = sorted(year for year in set(years) if years.count(year) > 1)
    for year in duplicate_years:
        issues.append({"year": str(year), "severity": "critical", "issue": "duplicate bs_year"})
    missing_years = []
    if years:
        missing_years = [year for year in range(min(years), max(years) + 1) if year not in years]
        for year in missing_years:
            issues.append({"year": str(year), "severity": "major", "issue": "missing year in corpus range"})

    if fix_checksums:
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=EXTENDED_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    official_rows = [
        row
        for row in rows
        if row["source_type"] == "official_verified" and row["verification_status"] == "verified"
    ]
    summary = {
        "path": str(path),
        "rows": len(rows),
        "range": f"{min(years)}-{max(years)} BS" if years else None,
        "source_type_counts": source_counts,
        "verification_status_counts": status_counts,
        "official_verified_years": len(official_rows),
        "official_verified_month_cases": len(official_rows) * 12,
        "minimum_month_cases_for_99_claim": 528,
        "ready_for_99_claim": len(official_rows) * 12 >= 528,
        "issues": issues,
        "ok": not any(issue["severity"] == "critical" for issue in issues),
    }
    return summary, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("data/future_bs/corpus/verified_month_lengths.csv"),
    )
    parser.add_argument("--fix-checksums", action="store_true")
    parser.add_argument(
        "--audit-log",
        type=Path,
        default=Path("data/future_bs/corpus/audit_log.jsonl"),
    )
    args = parser.parse_args()
    try:
        summary, _ = audit(args.corpus, fix_checksums=args.fix_checksums)
    except MissingPrivateCorpusError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    args.audit_log.parent.mkdir(parents=True, exist_ok=True)
    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "future_bs_corpus_audit",
        "summary": summary,
    }
    with args.audit_log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
