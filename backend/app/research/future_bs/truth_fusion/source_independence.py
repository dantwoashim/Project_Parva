"""Source-independence graph for duplicate/copy-risk control."""

from __future__ import annotations

import csv
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from app.research.future_bs.paths import project_root

PROJECT_ROOT = project_root()
WITNESS_PATH = PROJECT_ROOT / "data" / "future_bs" / "witnesses" / "extracted_witnesses.csv"
PUBLICATION_STATUS = "computed_prediction_not_official"


def _read_witnesses(path: Path = WITNESS_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def build_source_independence_graph(rows: list[dict[str, str]] | None = None) -> dict[str, Any]:
    rows = rows if rows is not None else _read_witnesses()
    by_source: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    source_type: dict[str, str] = {}
    for row in rows:
        sid = row.get("source_id", "")
        if not sid:
            continue
        by_source[sid].add((row.get("bs_year", ""), row.get("bs_month", ""), row.get("ad_date", "")))
        source_type[sid] = row.get("source_type", "")
    edges = []
    for left, right in combinations(sorted(by_source), 2):
        left_set = by_source[left]
        right_set = by_source[right]
        overlap = len(left_set & right_set)
        union = len(left_set | right_set) or 1
        jaccard = overlap / union
        same_family = source_type.get(left) == source_type.get(right)
        copy_risk = jaccard >= 0.98 or (same_family and jaccard >= 0.85)
        if overlap:
            edges.append(
                {
                    "source_a": left,
                    "source_b": right,
                    "source_type_a": source_type.get(left, ""),
                    "source_type_b": source_type.get(right, ""),
                    "overlap": overlap,
                    "agreement_jaccard": round(jaccard, 6),
                    "same_source_family": same_family,
                    "copy_risk": copy_risk,
                    "independence_score": round(max(0.1, 1.0 - jaccard if copy_risk else 1.0 - 0.25 * jaccard), 6),
                }
            )
    return {
        "publication_status": PUBLICATION_STATUS,
        "source_count": len(by_source),
        "edge_count": len(edges),
        "copy_risk_edges": sum(1 for edge in edges if edge["copy_risk"]),
        "nodes": [{"source_id": key, "source_type": source_type.get(key, ""), "witness_count": len(value)} for key, value in sorted(by_source.items())],
        "edges": edges,
    }
