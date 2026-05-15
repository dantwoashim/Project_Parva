#!/usr/bin/env python3
"""Validate the external temporal rule registry and sample profiles."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = PROJECT_ROOT / "config" / "external-temporal-rules.yaml"
PROFILE_DIR = PROJECT_ROOT / "rules" / "institution_profiles"

ALLOWED_SOURCE_TIERS = {"official", "semi_official", "institutional", "published", "research", "unknown"}
SENSITIVE_APPLIES_TO = {
    "bank_holidays",
    "loan_repayment",
    "settlement",
    "payroll",
    "salary_cutoff",
    "attendance",
    "tax",
    "government_workflows",
}
FINAL_AUTHORITY_PHRASES = (
    "legal authority",
    "banking authority",
    "payroll authority",
    "tax authority",
    "final authority",
    "government approved",
    "guaranteed future",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registry(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if payload.get("claim_boundary") != "institution_rule_registry_not_authority":
        issues.append("claim_boundary must be institution_rule_registry_not_authority")
    source_tiers = set(payload.get("source_tiers", []))
    if not ALLOWED_SOURCE_TIERS.issubset(source_tiers):
        issues.append("source_tiers must include every allowed source tier")

    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        return [*issues, "rules must be a non-empty list"]

    ids = [rule.get("rule_id") for rule in rules if isinstance(rule, dict)]
    for duplicate in sorted(key for key, count in Counter(ids).items() if key and count > 1):
        issues.append(f"{duplicate}: duplicate rule_id")

    for index, rule in enumerate(rules):
        prefix = str(rule.get("rule_id") or f"rules[{index}]")
        for field in (
            "rule_id",
            "name",
            "authority_type",
            "source_tier",
            "applies_to",
            "evidence_required",
            "public_safe",
            "review_required_when",
            "conflict_resolution",
            "examples",
        ):
            if field not in rule:
                issues.append(f"{prefix}: missing {field}")
        if rule.get("source_tier") not in ALLOWED_SOURCE_TIERS:
            issues.append(f"{prefix}: unsupported source_tier {rule.get('source_tier')!r}")
        if rule.get("public_safe") is not True:
            issues.append(f"{prefix}: public_safe must be true for public registry entries")
        evidence = rule.get("evidence_required")
        review = rule.get("review_required_when")
        examples = rule.get("examples")
        if not isinstance(evidence, list) or not evidence:
            issues.append(f"{prefix}: evidence_required must be non-empty")
        if not isinstance(review, list) or not review:
            issues.append(f"{prefix}: review_required_when must be non-empty")
        if not isinstance(examples, list) or not examples:
            issues.append(f"{prefix}: examples must be non-empty")
        applies_to = set(rule.get("applies_to") or [])
        if applies_to & SENSITIVE_APPLIES_TO and not evidence:
            issues.append(f"{prefix}: sensitive rule requires evidence")
        lowered = json.dumps(rule, ensure_ascii=False).lower()
        for phrase in FINAL_AUTHORITY_PHRASES:
            if phrase in lowered and "not " + phrase not in lowered:
                issues.append(f"{prefix}: forbidden final-authority wording: {phrase}")
        if rule.get("source_tier") == "official":
            evidence_text = " ".join(str(item).lower() for item in evidence or [])
            if "official" not in evidence_text:
                issues.append(f"{prefix}: official source_tier requires official source evidence")

    return issues


def validate_profiles() -> list[str]:
    issues: list[str] = []
    for path in sorted(PROFILE_DIR.glob("*.json")):
        payload = _load_json(path)
        profile_id = payload.get("profile_id") or path.name
        if payload.get("public_safe") is not True:
            issues.append(f"{path}: public_safe must be true")
        if payload.get("official_rule") is True:
            issues.append(f"{path}: sample profile must not claim to be an official rule")
        if payload.get("review_required_for_final_use") is not True:
            issues.append(f"{path}: sample profile must require final-use review")
        if not payload.get("authority_boundary"):
            issues.append(f"{profile_id}: authority_boundary is required")
        lowered = json.dumps(payload, ensure_ascii=False).lower()
        for phrase in FINAL_AUTHORITY_PHRASES:
            if phrase in lowered and "not " + phrase not in lowered:
                issues.append(f"{path}: forbidden final-authority wording: {phrase}")
    return issues


def validate_external_temporal_rules() -> list[str]:
    return [*validate_registry(_load_json(REGISTRY_PATH)), *validate_profiles()]


def main() -> int:
    issues = validate_external_temporal_rules()
    if issues:
        for issue in issues:
            print(f"[external-rules] {issue}")
        return 1
    print("External temporal rule registry passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
