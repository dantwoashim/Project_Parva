"""Human-review promotion plan for official-claim readiness."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
REVIEW_PATH = PROJECT_ROOT / "data" / "future_bs" / "corpus" / "human_review_queue.csv"
LAB_DIR = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab"
PUBLICATION_STATUS = "computed_prediction_not_official"

PROMOTION_FIELDS = [
    "rank",
    "bs_year",
    "bs_month",
    "current_status",
    "current_sources",
    "issue_type",
    "expected_accuracy_gain",
    "expected_claim_readiness_gain",
    "reason",
    "recommended_manual_action",
    "source_url_or_file",
    "page_or_crop_if_available",
]


def build_human_review_promotion_plan(limit: int = 100) -> list[dict[str, Any]]:
    rows = []
    if REVIEW_PATH.exists():
        with REVIEW_PATH.open(newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
    selected = []
    for rank, row in enumerate(rows[:limit], start=1):
        priority = int(row.get("priority") or 0)
        selected.append(
            {
                "rank": rank,
                "bs_year": row.get("bs_year", ""),
                "bs_month": row.get("bs_month", ""),
                "current_status": row.get("issue_type", ""),
                "current_sources": row.get("sources", ""),
                "issue_type": row.get("issue_type", ""),
                "expected_accuracy_gain": "high" if priority >= 100 else "medium",
                "expected_claim_readiness_gain": "high" if int(row.get("bs_year") or 0) in range(2076, 2084) else "medium",
                "reason": row.get("reason", ""),
                "recommended_manual_action": row.get("recommended_manual_action", ""),
                "source_url_or_file": row.get("source_file_or_url", ""),
                "page_or_crop_if_available": row.get("page_number_or_crop_if_available", ""),
            }
        )
    return selected


def write_human_review_promotion_plan(
    rows: list[dict[str, Any]],
    *,
    output_dir: Path = LAB_DIR,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "human_review_promotion_plan.csv"
    md_path = output_dir / "human_review_promotion_plan.md"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=PROMOTION_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Human Review Promotion Plan",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"Rows: {len(rows)}",
        "",
    ]
    for row in rows[:30]:
        lines.append(
            f"- #{row['rank']} {row['bs_year']}-{int(row['bs_month']):02d}: {row['issue_type']} - {row['recommended_manual_action']}"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"csv": csv_path, "markdown": md_path}
