"""Rule triad pipeline: rule/evidence/validation artifacts.

Triad contract per rule:
- rule.json: typed DSL document and execution template.
- evidence.json: source lineage and confidence metadata.
- validation_cases.json: deterministic validation corpus metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .catalog_v4 import list_rules_v4
from .dsl import rule_to_dsl_document
from .execution import validation_cases_for_rule
from .schema_v4 import FestivalRuleV4

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRIAD_ROOT = PROJECT_ROOT / "data" / "festivals" / "rule_triads"


@dataclass
class TriadWriteSummary:
    total_rules: int
    rule_files_written: int
    evidence_files_written: int
    validation_files_written: int
    computed_with_cases: int


def triad_paths(festival_id: str) -> dict[str, Path]:
    root = TRIAD_ROOT / festival_id
    return {
        "root": root,
        "rule": root / "rule.json",
        "evidence": root / "evidence.json",
        "validation": root / "validation_cases.json",
    }


def _json_write(path: Path, payload: dict[str, Any], *, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def _validation_payload(rule: FestivalRuleV4) -> dict[str, Any]:
    cases = validation_cases_for_rule(rule)
    return {
        "festival_id": rule.festival_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validation_framework": "parva_rule_validation_v1",
        "cases": cases,
    }


def _evidence_payload(rule: FestivalRuleV4) -> dict[str, Any]:
    source_evidence_ids = [rule.source]
    source_line = (rule.rule or {}).get("source_line")
    if source_line:
        digest = hashlib.sha1(str(source_line).encode("utf-8")).hexdigest()[:12]
        source_evidence_ids.append(f"source-line:{digest}")

    return {
        "festival_id": rule.festival_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_evidence_ids": source_evidence_ids,
        "confidence": rule.confidence,
        "status": rule.status,
        "rule_family": rule.rule_family,
        "tags": list(rule.tags or []),
        "notes": rule.notes,
    }


def write_rule_triad(rule: FestivalRuleV4, *, overwrite: bool = True) -> dict[str, bool]:
    dsl_document = rule_to_dsl_document(rule)
    paths = triad_paths(rule.festival_id)

    wrote_rule = _json_write(paths["rule"], dsl_document.model_dump(mode="json"), overwrite=overwrite)
    wrote_evidence = _json_write(paths["evidence"], _evidence_payload(rule), overwrite=overwrite)
    wrote_validation = _json_write(paths["validation"], _validation_payload(rule), overwrite=overwrite)

    return {
        "rule": wrote_rule,
        "evidence": wrote_evidence,
        "validation": wrote_validation,
    }


def generate_rule_triads(*, overwrite: bool = True, computed_only: bool = False) -> TriadWriteSummary:
    rules = list_rules_v4()
    if computed_only:
        rules = [rule for rule in rules if rule.status == "computed"]

    counts = {
        "rule": 0,
        "evidence": 0,
        "validation": 0,
        "computed_with_cases": 0,
    }

    for rule in rules:
        result = write_rule_triad(rule, overwrite=overwrite)
        counts["rule"] += int(result["rule"])
        counts["evidence"] += int(result["evidence"])
        counts["validation"] += int(result["validation"])

        validation_path = triad_paths(rule.festival_id)["validation"]
        payload = json.loads(validation_path.read_text(encoding="utf-8"))
        if any(case.get("status") == "passed" for case in payload.get("cases", [])):
            counts["computed_with_cases"] += 1

    return TriadWriteSummary(
        total_rules=len(rules),
        rule_files_written=counts["rule"],
        evidence_files_written=counts["evidence"],
        validation_files_written=counts["validation"],
        computed_with_cases=counts["computed_with_cases"],
    )


def triad_integrity_report() -> dict[str, Any]:
    rules = list_rules_v4()
    missing = []
    with_cases = 0

    for rule in rules:
        paths = triad_paths(rule.festival_id)
        required = [paths["rule"], paths["evidence"], paths["validation"]]
        if not all(path.exists() for path in required):
            missing.append(rule.festival_id)
            continue

        validation_payload = json.loads(paths["validation"].read_text(encoding="utf-8"))
        if any(case.get("status") == "passed" for case in validation_payload.get("cases", [])):
            with_cases += 1

    return {
        "total_rules": len(rules),
        "triad_complete": len(rules) - len(missing),
        "triad_missing": len(missing),
        "rules_with_passed_cases": with_cases,
        "missing_ids_sample": missing[:20],
    }
