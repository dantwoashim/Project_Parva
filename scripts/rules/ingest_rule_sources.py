#!/usr/bin/env python3
"""Rule-ingestion pipeline for scaling canonical festival rule coverage.

Pipeline stages:
1) ingested -> canonical normalized catalog (v4)
2) normalized -> typed rule DSL snapshot
3) optional triad generation (rule/evidence/validation)
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rules.catalog_v4 import (  # noqa: E402
    CATALOG_V4_PATH,
    build_canonical_catalog,
    get_rules_scoreboard,
)
from app.rules.dsl import rule_to_dsl_document  # noqa: E402
from app.rules.triad_pipeline import generate_rule_triads, triad_integrity_report  # noqa: E402


def _summarize(catalog_payload: dict) -> dict:
    festivals = catalog_payload.get("festivals", [])
    by_status = Counter(rule.get("status", "unknown") for rule in festivals)
    by_source = Counter(rule.get("source", "unknown") for rule in festivals)
    by_type = Counter(rule.get("rule_type", "unknown") for rule in festivals)
    generated = sum(1 for rule in festivals if "generated" in (rule.get("tags") or []))

    return {
        "total_rules": len(festivals),
        "generated_rules": generated,
        "by_status": dict(by_status),
        "by_source_top10": dict(by_source.most_common(10)),
        "by_type": dict(by_type),
    }


def _canonicalize_source_path(raw: str) -> str:
    value = str(raw).replace("\\", "/")
    parts = Path(value).parts
    for marker in ("backend", "data", "docs", "tests", "scripts"):
        if marker in parts:
            return Path(*parts[parts.index(marker):]).as_posix()
    return value


def _normalize_for_check(payload: dict) -> dict:
    normalized = dict(payload)
    normalized.pop("generated_at", None)
    source_files = normalized.get("source_files")
    if isinstance(source_files, list):
        normalized["source_files"] = sorted({_canonicalize_source_path(item) for item in source_files})
    return normalized


def _write_rule_dsl_snapshot(catalog, output_path: Path) -> dict:
    docs = [rule_to_dsl_document(rule).model_dump(mode="json") for rule in catalog.festivals]
    payload = {
        "generated_at": catalog.generated_at,
        "total_rules": len(docs),
        "rules": docs,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    executable_count = sum(1 for row in docs if row.get("executable"))
    return {
        "dsl_snapshot_path": str(output_path),
        "dsl_total": len(docs),
        "dsl_executable": executable_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build/validate ingested v4 rule catalog.")
    parser.add_argument("--target", type=int, default=300, help="Coverage target threshold.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check-only mode: fail if on-disk catalog differs from generated output.",
    )
    parser.add_argument(
        "--summary-out",
        type=str,
        default=str(PROJECT_ROOT / "reports" / "rule_ingestion_summary.json"),
        help="Summary JSON output path.",
    )
    parser.add_argument(
        "--dsl-out",
        type=str,
        default=str(PROJECT_ROOT / "reports" / "rule_dsl_snapshot.json"),
        help="Rule DSL snapshot output path.",
    )
    parser.add_argument(
        "--computed-target",
        type=int,
        default=200,
        help="Minimum computed-rule baseline expected for Month-4 quality gate.",
    )
    parser.add_argument(
        "--emit-triads",
        action="store_true",
        help="Generate rule/evidence/validation triad artifacts after catalog write.",
    )
    args = parser.parse_args()

    catalog = build_canonical_catalog()
    payload = catalog.model_dump(mode="json")
    canonical = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.check:
        if not CATALOG_V4_PATH.exists():
            print(f"[FAIL] Missing catalog: {CATALOG_V4_PATH}")
            return 1
        current_payload = json.loads(CATALOG_V4_PATH.read_text(encoding="utf-8"))
        if _normalize_for_check(current_payload) != _normalize_for_check(payload):
            print(f"[FAIL] Catalog drift detected for {CATALOG_V4_PATH}.")
            print("Run: python3 scripts/rules/ingest_rule_sources.py")
            return 1
    else:
        CATALOG_V4_PATH.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_V4_PATH.write_text(canonical, encoding="utf-8")
        print(f"Wrote {CATALOG_V4_PATH}")

    summary = _summarize(payload)
    summary["target"] = args.target
    summary["computed_target"] = args.computed_target
    summary["coverage_pct"] = round((summary["total_rules"] / args.target) * 100, 2) if args.target > 0 else 0.0
    summary["scoreboard"] = get_rules_scoreboard(target=args.target)

    dsl_summary = _write_rule_dsl_snapshot(catalog, Path(args.dsl_out))
    summary.update(dsl_summary)

    if args.emit_triads and not args.check:
        triad_summary = generate_rule_triads(overwrite=True)
        summary["triad"] = {
            "total_rules": triad_summary.total_rules,
            "rule_files_written": triad_summary.rule_files_written,
            "evidence_files_written": triad_summary.evidence_files_written,
            "validation_files_written": triad_summary.validation_files_written,
            "computed_with_cases": triad_summary.computed_with_cases,
            "integrity": triad_integrity_report(),
        }

    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if summary["total_rules"] < args.target:
        print(
            f"[WARN] Catalog is below target: {summary['total_rules']} < {args.target}. "
            "Pipeline completed but coverage target not met."
        )
        return 2

    computed_count = summary["scoreboard"]["computed"]["count"]
    if computed_count < args.computed_target:
        print(
            f"[WARN] Computed baseline below target: {computed_count} < {args.computed_target}. "
            "Pipeline completed but promotion baseline is not met."
        )
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
