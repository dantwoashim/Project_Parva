"""Minimal Policy VM v0 for authority-safe candidate selection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.boundary.vector import BoundaryVector
from app.policy.schema import PolicyCandidate
from app.trust.taint import AUTHORITY_RANK, AuthorityTaint

RULE_PATH = Path(__file__).with_name("rules") / "canonical.yaml"


@dataclass(frozen=True)
class PolicyDecision:
    selected: PolicyCandidate
    rejected: list[dict[str, str]]
    decision_trace: list[str]
    boundary: BoundaryVector

    def as_dict(self) -> dict[str, Any]:
        return {
            "selected_candidate": self.selected.as_dict(),
            "rejected_candidates": list(self.rejected),
            "decision_trace": list(self.decision_trace),
            "boundary": self.boundary.as_dict(),
        }


class PolicyVM:
    def __init__(self, *, policy_id: str = "canonical@0.1.0") -> None:
        self.policy_id = policy_id
        self.rules = self._load_rules()

    def _load_rules(self) -> dict[str, Any]:
        if not RULE_PATH.exists():
            return {
                "candidate_ranking": [authority.value for authority in AuthorityTaint],
                "static_reference_rule": "explicit_mode_or_compare_branch_only",
            }
        return json.loads(RULE_PATH.read_text(encoding="utf-8"))

    def select(self, candidates: list[PolicyCandidate]) -> PolicyDecision:
        if not candidates:
            raise ValueError("PolicyVM requires at least one candidate")

        eligible: list[PolicyCandidate] = []
        rejected: list[dict[str, str]] = []
        ranking = self.rules.get("candidate_ranking") or [authority.value for authority in AuthorityTaint]
        rank_index = {authority: index for index, authority in enumerate(ranking)}
        static_rule = self.rules.get("static_reference_rule", "explicit_mode_or_compare_branch_only")
        trace = [f"policy={self.policy_id}", f"rule_file={RULE_PATH.name}", "rank_candidates_by_authority"]
        for candidate in candidates:
            try:
                candidate.field_provenance.require_all_fields(candidate.result)
            except ValueError as exc:
                rejected.append({"candidate_id": candidate.candidate_id, "reason": str(exc)})
                continue
            if (
                static_rule == "explicit_mode_or_compare_branch_only"
                and candidate.authority == AuthorityTaint.STATIC_REFERENCE
                and len(candidates) > 1
            ):
                rejected.append(
                    {
                        "candidate_id": candidate.candidate_id,
                        "reason": "static_reference_requires_explicit_mode_or_compare_branch",
                    }
                )
                continue
            eligible.append(candidate)

        if not eligible:
            selected = min(candidates, key=lambda item: rank_index.get(item.authority.value, AUTHORITY_RANK[item.authority]))
            trace.append("no_eligible_candidate_selected_for_review_only")
        else:
            selected = min(eligible, key=lambda item: rank_index.get(item.authority.value, AUTHORITY_RANK[item.authority]))
            trace.append(f"selected={selected.candidate_id}")

        return PolicyDecision(
            selected=selected,
            rejected=rejected,
            decision_trace=trace,
            boundary=selected.boundary,
        )
