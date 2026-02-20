#!/usr/bin/env python3
"""Migrate provisional rule seeds into executable template mappings."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rules.catalog_v4 import list_rules_v4, rule_has_algorithm, rule_quality_band  # noqa: E402
from app.rules.dsl import rule_to_dsl_document  # noqa: E402

OUTPUT_PATH = PROJECT_ROOT / "data" / "festivals" / "rule_execution_templates.json"


def main() -> int:
    rules = list_rules_v4()

    templates: dict[str, dict] = {}
    counts = {
        "total_rules": len(rules),
        "mapped": 0,
        "computed": 0,
        "provisional": 0,
        "inventory": 0,
    }

    for rule in rules:
        band = rule_quality_band(rule)
        counts[band] += 1

        dsl = rule_to_dsl_document(rule)
        if not dsl.executable:
            continue
        if not rule_has_algorithm(rule):
            continue

        templates[rule.festival_id] = {
            "execution_template": dsl.execution_template,
            "rule_type": rule.rule_type,
            "rule_family": rule.rule_family,
            "quality_band": band,
            "payload": dsl.payload,
        }
        counts["mapped"] += 1

    payload = {
        "version": 1,
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "templates": templates,
        "summary": {
            **counts,
            "template_coverage_pct": round((counts["mapped"] / max(counts["total_rules"], 1)) * 100, 2),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
