"""Source docket coverage resolution for proof-carrying operations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.trust.taint import AuthorityTaint

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCKETS_ROOT = PROJECT_ROOT / "data" / "sources" / "dockets"

OFFICIAL_AUTHORITY_CLASSES = {
    "structured_official": AuthorityTaint.STRUCTURED_OFFICIAL,
    "archived_official": AuthorityTaint.ARCHIVED_OFFICIAL,
    "reviewed_institutional": AuthorityTaint.REVIEWED_INSTITUTIONAL,
}
REFERENCE_AUTHORITY_CLASSES = {
    "static_reference": AuthorityTaint.STATIC_REFERENCE,
    "third_party_reference": AuthorityTaint.THIRD_PARTY_REFERENCE,
}
SAMPLE_REVIEW_STATUSES = {"reviewed_sample", "sample", "fixture"}


@dataclass(frozen=True)
class SourceCoverageResolution:
    operation: str
    bs_date: str
    authority: AuthorityTaint
    coverage_status: str
    review_required: bool
    source_docket_ids: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    review_witnesses: tuple[str, ...] = ()
    claim_boundary: str = "decision_support_not_authority"
    reason: str = "source_coverage_unavailable"
    eligible_official: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "bs_date": self.bs_date,
            "authority": self.authority.value,
            "coverage_status": self.coverage_status,
            "review_required": self.review_required,
            "source_docket_ids": list(self.source_docket_ids),
            "source_refs": list(self.source_refs),
            "review_witnesses": list(self.review_witnesses),
            "claim_boundary": self.claim_boundary,
            "reason": self.reason,
            "eligible_official": self.eligible_official,
        }


def _read_json(path: Path) -> dict[str, Any]:
    for encoding in ("utf-8", "utf-8-sig", "utf-16"):
        try:
            return json.loads(path.read_text(encoding=encoding))
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            continue
        except (OSError, TypeError, ValueError):
            return {}
    return {}


def _iter_dockets() -> list[dict[str, Any]]:
    if not DOCKETS_ROOT.exists():
        return []
    dockets: list[dict[str, Any]] = []
    for path in sorted(DOCKETS_ROOT.glob("*.json")):
        payload = _read_json(path)
        if payload:
            payload["_docket_path"] = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            dockets.append(payload)
    return dockets


def _normalized_rows(docket: dict[str, Any]) -> list[dict[str, Any]]:
    normalized = docket.get("normalized_output")
    if not isinstance(normalized, dict):
        return []
    rel_path = normalized.get("path")
    if not isinstance(rel_path, str) or not rel_path.strip():
        return []
    payload = _read_json(PROJECT_ROOT / rel_path)
    rows = payload.get("rows")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _docket_covers_bs_date(docket: dict[str, Any], bs_date: str) -> bool:
    for row in _normalized_rows(docket):
        if str(row.get("bs_date") or "") == bs_date:
            return True

    coverage = docket.get("coverage")
    if isinstance(coverage, dict):
        years = coverage.get("bs_years")
        if isinstance(years, list) and int(bs_date[:4]) in {int(year) for year in years if str(year).isdigit()}:
            return True
        start = coverage.get("bs_start")
        end = coverage.get("bs_end")
        if isinstance(start, str) and isinstance(end, str) and start <= bs_date <= end:
            return True
    return False


def _is_sample_docket(docket: dict[str, Any]) -> bool:
    source_id = str(docket.get("source_id") or "").lower()
    review_status = str(docket.get("review_status") or "").lower()
    issuer = str(docket.get("issuer") or "").lower()
    return "sample" in source_id or "sample fixture" in issuer or review_status in SAMPLE_REVIEW_STATUSES


def resolve_bs_date_source(
    operation: str,
    *,
    year: int,
    month: int,
    day: int,
    policy_id: str = "canonical@0.1.0",
) -> SourceCoverageResolution:
    """Resolve source dockets for a BS date without upgrading sample data."""

    del policy_id
    bs_date = f"{year:04d}-{month:02d}-{day:02d}"
    covered_reference: list[tuple[dict[str, Any], AuthorityTaint]] = []

    for docket in _iter_dockets():
        if not _docket_covers_bs_date(docket, bs_date):
            continue
        authority_class = str(docket.get("authority_class") or "").lower()
        if authority_class in OFFICIAL_AUTHORITY_CLASSES and not _is_sample_docket(docket):
            authority = OFFICIAL_AUTHORITY_CLASSES[authority_class]
            return SourceCoverageResolution(
                operation=operation,
                bs_date=bs_date,
                authority=authority,
                coverage_status="covered_by_eligible_official_source",
                review_required=False,
                source_docket_ids=(str(docket.get("source_id")),),
                source_refs=(str(docket.get("source_id")),),
                review_witnesses=tuple(str(item) for item in docket.get("review_witnesses", []) if item),
                claim_boundary="official_source_interpretation_not_authority",
                reason="covered_by_eligible_official_source",
                eligible_official=True,
            )
        if authority_class in REFERENCE_AUTHORITY_CLASSES:
            covered_reference.append((docket, REFERENCE_AUTHORITY_CLASSES[authority_class]))

    if covered_reference:
        docket, authority = covered_reference[0]
        return SourceCoverageResolution(
            operation=operation,
            bs_date=bs_date,
            authority=authority,
            coverage_status="covered_by_reference_source_not_official",
            review_required=True,
            source_docket_ids=(str(docket.get("source_id")),),
            source_refs=(str(docket.get("source_id")),),
            review_witnesses=tuple(str(item) for item in docket.get("review_witnesses", []) if item),
            claim_boundary="sample_source_chain_not_authority" if _is_sample_docket(docket) else "static_reference_not_authority",
            reason="covered_source_is_reference_or_sample",
            eligible_official=False,
        )

    return SourceCoverageResolution(
        operation=operation,
        bs_date=bs_date,
        authority=AuthorityTaint.COMPUTED_UNCERTIFIED,
        coverage_status="no_eligible_source_coverage",
        review_required=True,
        claim_boundary="computed_conversion_not_source_backed_authority",
        reason="no_source_docket_covers_requested_date",
        eligible_official=False,
    )


__all__ = ["SourceCoverageResolution", "resolve_bs_date_source"]
