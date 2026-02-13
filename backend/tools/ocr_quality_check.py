#!/usr/bin/env python3
"""Compute OCR extraction quality metrics from MoHA ingest reports."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "data" / "ingest_reports"
OUT_JSON = PROJECT_ROOT / "data" / "ingest_reports" / "ocr_quality_summary.json"
OUT_MD = PROJECT_ROOT / "docs" / "OCR_QUALITY_REPORT.md"


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    parsed_files = sorted(REPORTS_DIR.glob("holidays_*_parsed.csv"))
    matched_files = sorted(REPORTS_DIR.glob("holidays_*_matched.csv"))

    parsed_rows = []
    matched_rows = []
    for fp in parsed_files:
        parsed_rows.extend(load_rows(fp))
    for fp in matched_files:
        matched_rows.extend(load_rows(fp))

    total_parsed = len(parsed_rows)
    total_matched = sum(1 for r in matched_rows if (r.get("match_id") or "").strip())

    def normalized_confidence(row: dict[str, str]) -> str:
        c = (row.get("parse_confidence") or "").strip()
        if c in {"high", "medium", "low"}:
            return c
        return "medium" if (row.get("match_id") or "").strip() else "low"

    confidence_counts = Counter(normalized_confidence(r) for r in matched_rows)

    # Precision proxy: among mapped entries, how many have medium/high confidence.
    mapped_rows = [r for r in matched_rows if (r.get("match_id") or "").strip()]
    high_medium = [r for r in mapped_rows if normalized_confidence(r) in {"high", "medium"}]

    precision_proxy = (len(high_medium) / len(mapped_rows) * 100.0) if mapped_rows else 0.0
    recall_proxy = (len(mapped_rows) / total_parsed * 100.0) if total_parsed else 0.0

    summary = {
        "total_parsed_rows": total_parsed,
        "total_mapped_rows": len(mapped_rows),
        "mapped_ratio_percent": round(recall_proxy, 2),
        "precision_proxy_percent": round(precision_proxy, 2),
        "confidence_distribution": dict(confidence_counts),
        "files": {
            "parsed": [p.name for p in parsed_files],
            "matched": [p.name for p in matched_files],
        },
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# OCR Quality Report",
        "",
        f"- Parsed rows: **{summary['total_parsed_rows']}**",
        f"- Mapped rows: **{summary['total_mapped_rows']}**",
        f"- Mapping coverage (recall proxy): **{summary['mapped_ratio_percent']}%**",
        f"- Mapping quality (precision proxy): **{summary['precision_proxy_percent']}%**",
        "",
        "## Confidence Distribution",
        "",
        "| Confidence | Count |",
        "|---|---:|",
    ]

    for level in ["high", "medium", "low", "unknown"]:
        lines.append(f"| {level} | {summary['confidence_distribution'].get(level, 0)} |")

    lines += [
        "",
        "## Notes",
        "",
        "- `precision_proxy` counts mapped rows with `high|medium` parse confidence.",
        "- `recall_proxy` is mapped rows divided by total parsed rows.",
        "- For strict precision/recall, attach a manually verified gold set in future iterations.",
        "",
    ]

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
