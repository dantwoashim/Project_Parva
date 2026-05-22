"""Public-safe Parva TimeGraph service.

The TimeGraph is intentionally in-memory for the current public preview. It is built from public
release artifacts and existing deterministic services, so a fresh clone can
verify it without private source archives.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from functools import lru_cache
from typing import Any

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    get_bs_month_name,
    get_bs_year_end,
    gregorian_to_bs,
)
from app.calendar.fiscal import fiscal_period_for_bs_date
from app.core.source_metadata import NOT_LEGAL_AUTHORITY, build_bs_claim_meta
from app.services.compliance_service import PROFILES, evaluate_date_payload
from app.services.trust_infrastructure_service import (
    get_release_payload,
    list_sources_payload,
    load_trust_log_payload,
    resolve_release_id,
)
from app.timegraph.fact_ids import (
    ad_bs_fact_id,
    bs_ad_fact_id,
    fiscal_period_fact_id,
    format_bs_date,
    month_length_fact_id,
    profile_policy_fact_id,
    release_membership_fact_id,
    source_claim_fact_id,
    weekday_fact_id,
    working_day_fact_id,
)

TIMEGRAPH_CLAIM_BOUNDARY = "timegraph_query_not_legal_authority"
DEFAULT_LIMIT = 50
MAX_LIMIT = 200
DEFAULT_TRACE_DEPTH = 2
MAX_TRACE_DEPTH = 5


class TimeGraphError(ValueError):
    """Raised when a TimeGraph query cannot be satisfied."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class TemporalFact:
    fact_id: str
    fact_type: str
    subject: dict[str, Any]
    predicate: str
    object: dict[str, Any]
    release_id: str
    source_ids: list[str]
    confidence: str
    claim_boundary: str
    warnings: list[str] = field(default_factory=list)
    jurisdiction: str | None = "NP"
    profile_ids: list[str] = field(default_factory=list)
    validity: dict[str, str | None] = field(
        default_factory=lambda: {"valid_from": None, "valid_to": None}
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TimeGraphRelationship:
    relationship_id: str
    from_id: str
    to_id: str
    type: str
    release_id: str
    confidence: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TimeGraphConflict:
    conflict_id: str
    conflict_type: str
    status: str
    facts: list[str]
    sources: list[str]
    release_ids: list[str]
    summary: str
    resolution_policy: str
    requires_human_review: bool
    confidence: str
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TimeGraphSnapshot:
    release_id: str
    facts: dict[str, TemporalFact] = field(default_factory=dict)
    relationships: dict[str, TimeGraphRelationship] = field(default_factory=dict)
    conflicts: dict[str, TimeGraphConflict] = field(default_factory=dict)
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)
    source_records: dict[str, dict[str, Any]] = field(default_factory=dict)
    release_record: dict[str, Any] = field(default_factory=dict)

    def add_fact(self, fact: TemporalFact) -> None:
        self.facts[fact.fact_id] = fact

    def add_relationship(self, relationship: TimeGraphRelationship) -> None:
        self.relationships[relationship.relationship_id] = relationship

    def add_entity(self, entity_id: str, entity_type: str, label: str, **metadata: Any) -> None:
        self.entities[entity_id] = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "label": label,
            "release_id": self.release_id,
            "metadata": metadata,
        }

    def add_conflict(self, conflict: TimeGraphConflict) -> None:
        self.conflicts[conflict.conflict_id] = conflict


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _short_hash(payload: Any, length: int = 16) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:length]


def relationship_id(from_id: str, to_id: str, relationship_type: str, release_id: str) -> str:
    digest = _short_hash(
        {
            "from_id": from_id,
            "to_id": to_id,
            "type": relationship_type,
            "release_id": release_id,
        }
    )
    return f"rel_{relationship_type.lower()}_{digest}"


def timegraph_capabilities_payload() -> dict[str, Any]:
    return {
        "surface": "parva_timegraph",
        "status": "public_preview",
        "active_release_id": resolve_release_id(None),
        "fact_types": [
            "source_claim",
            "release_membership",
            "bs_ad_mapping",
            "ad_bs_mapping",
            "weekday",
            "month_length",
            "fiscal_period_membership",
            "profile_policy",
            "working_day_decision",
            "conflict",
        ],
        "relationship_types": [
            "SUPPORTED_BY",
            "CONTAINS_FACT",
            "DERIVED_FROM",
            "APPLIES_TO",
            "REFERENCES_FACT",
            "CONTRADICTED_BY",
            "REQUIRES_REVIEW",
            "PINNED_TO_RELEASE",
        ],
        "default_limit": DEFAULT_LIMIT,
        "max_limit": MAX_LIMIT,
        "trace_depth": {"default": DEFAULT_TRACE_DEPTH, "max": MAX_TRACE_DEPTH},
        "claim_boundary": TIMEGRAPH_CLAIM_BOUNDARY,
        "warnings": [
            "TimeGraph is an audit and explanation graph, not legal authority.",
            "Public graph uses public release artifacts and does not require private archives.",
        ],
    }


def build_public_timegraph(release_id: str | None = None) -> TimeGraphSnapshot:
    selected = resolve_release_id(release_id)
    return _build_public_timegraph_cached(selected)


@lru_cache(maxsize=4)
def _build_public_timegraph_cached(release_id: str) -> TimeGraphSnapshot:
    release_payload = get_release_payload(release_id)["release"]
    sources_payload = list_sources_payload(release_id=release_id)
    graph = TimeGraphSnapshot(release_id=release_id)
    graph.release_record = release_payload

    graph.add_entity(
        f"release_{release_id}",
        "CalendarRelease",
        release_id,
        status=release_payload.get("status"),
        release_type=release_payload.get("release_type"),
    )

    for source in sources_payload["sources"]:
        source_id = str(source["id"])
        graph.source_records[source_id] = source
        graph.add_entity(
            f"source_{source_id}",
            "SourceRecord",
            str(source.get("label") or source_id),
            tier=source.get("tier"),
            authority=source.get("authority"),
        )
        source_fact = TemporalFact(
            fact_id=source_claim_fact_id(source_id),
            fact_type="source_claim",
            subject={"entity_type": "source", "id": source_id},
            predicate="declares_public_source",
            object={
                "label": source.get("label"),
                "tier": source.get("tier"),
                "authority": source.get("authority"),
            },
            release_id=release_id,
            source_ids=[source_id],
            confidence=str(source.get("tier") or "unknown"),
            claim_boundary=str(source.get("authority") or NOT_LEGAL_AUTHORITY),
            warnings=["source_record_is_metadata_not_legal_authority"],
            metadata={"source": source},
        )
        _add_fact_with_standard_links(graph, source_fact)

    _build_release_membership_facts(graph, release_payload)
    _build_public_bs_ad_facts(graph, release_payload)
    _build_profile_facts(graph)
    _build_trust_log_facts(graph)
    _build_fixture_conflict(graph)
    return graph


def _build_release_membership_facts(graph: TimeGraphSnapshot, release_payload: dict[str, Any]) -> None:
    release_id = graph.release_id
    for source_id in sorted(graph.source_records):
        fact = TemporalFact(
            fact_id=release_membership_fact_id(release_id, source_id),
            fact_type="release_membership",
            subject={"entity_type": "release", "id": release_id},
            predicate="contains_source",
            object={"entity_type": "source", "id": source_id},
            release_id=release_id,
            source_ids=[source_id],
            confidence="source_backed",
            claim_boundary=TIMEGRAPH_CLAIM_BOUNDARY,
            warnings=["release_membership_is_metadata_level"],
        )
        _add_fact_with_standard_links(graph, fact)
    for artifact in release_payload.get("artifact_hashes", []):
        artifact_id = str(artifact.get("artifact_id"))
        fact = TemporalFact(
            fact_id=release_membership_fact_id(release_id, f"artifact_{artifact_id}"),
            fact_type="release_membership",
            subject={"entity_type": "release", "id": release_id},
            predicate="contains_artifact",
            object={
                "entity_type": "artifact",
                "id": artifact_id,
                "sha256": artifact.get("sha256"),
                "media_type": artifact.get("media_type"),
            },
            release_id=release_id,
            source_ids=["parva-public-api-contract"],
            confidence="source_backed",
            claim_boundary=TIMEGRAPH_CLAIM_BOUNDARY,
            warnings=["artifact_membership_is_metadata_level"],
        )
        _add_fact_with_standard_links(graph, fact)


def _build_public_bs_ad_facts(graph: TimeGraphSnapshot, release_payload: dict[str, Any]) -> None:
    coverage = release_payload.get("coverage", {})
    start = date.fromisoformat(str(coverage.get("ad_date_start", "2021-04-14")))
    end = date.fromisoformat(str(coverage.get("ad_date_end", "2026-04-14")))
    if end < start:
        return

    cursor = start
    while cursor <= end:
        bs_year, bs_month, bs_day = gregorian_to_bs(cursor)
        bs_date = format_bs_date(bs_year, bs_month, bs_day)
        meta = build_bs_claim_meta(bs_year)
        source_id = str(meta["source"]["id"])
        confidence = str(meta["confidence"])
        boundary = str(meta["claim_boundary"])
        warnings = list(meta.get("warnings") or [])
        graph.add_entity(f"date_ad_{cursor.isoformat()}", "DateNode", cursor.isoformat(), calendar="AD")
        graph.add_entity(f"date_bs_{bs_date}", "DateNode", bs_date, calendar="BS")

        bs_ad = TemporalFact(
            fact_id=bs_ad_fact_id(bs_year, bs_month, bs_day),
            fact_type="bs_ad_mapping",
            subject={"calendar": "BS", "date": bs_date},
            predicate="maps_to",
            object={"calendar": "AD", "date": cursor.isoformat()},
            release_id=graph.release_id,
            source_ids=[source_id],
            confidence=confidence,
            claim_boundary=boundary,
            warnings=warnings,
            metadata={"source_range": meta["source"].get("version")},
        )
        _add_fact_with_standard_links(graph, bs_ad)

        ad_bs = TemporalFact(
            fact_id=ad_bs_fact_id(cursor),
            fact_type="ad_bs_mapping",
            subject={"calendar": "AD", "date": cursor.isoformat()},
            predicate="maps_to",
            object={"calendar": "BS", "date": bs_date},
            release_id=graph.release_id,
            source_ids=[source_id],
            confidence=confidence,
            claim_boundary=boundary,
            warnings=warnings,
        )
        _add_fact_with_standard_links(graph, ad_bs)
        _add_derivation(graph, ad_bs.fact_id, bs_ad.fact_id, confidence=confidence)

        weekday = TemporalFact(
            fact_id=weekday_fact_id(cursor),
            fact_type="weekday",
            subject={"calendar": "AD", "date": cursor.isoformat()},
            predicate="has_weekday",
            object={"weekday": cursor.strftime("%A").upper()},
            release_id=graph.release_id,
            source_ids=["parva_estimated_calendar_model"],
            confidence="calculated",
            claim_boundary=NOT_LEGAL_AUTHORITY,
            warnings=["weekday_is_computed_from_gregorian_calendar"],
        )
        _add_fact_with_standard_links(graph, weekday)
        _add_derivation(graph, weekday.fact_id, ad_bs.fact_id, confidence="calculated")

        fiscal = fiscal_period_for_bs_date(bs_year, bs_month, bs_day)
        fiscal_fact = TemporalFact(
            fact_id=fiscal_period_fact_id(bs_year, bs_month, bs_day),
            fact_type="fiscal_period_membership",
            subject={"calendar": "BS", "date": bs_date},
            predicate="belongs_to_fiscal_period",
            object={
                "fiscal_year_label": fiscal.fiscal_year_label,
                "fiscal_month": fiscal.fiscal_month,
                "fiscal_quarter": fiscal.fiscal_quarter,
            },
            release_id=graph.release_id,
            source_ids=["parva_enterprise_compliance_profiles"],
            confidence="source_backed",
            claim_boundary="enterprise_decision_support_not_legal_authority",
            warnings=["fiscal_period_is_decision_support_not_legal_authority"],
        )
        _add_fact_with_standard_links(graph, fiscal_fact)
        _add_derivation(graph, fiscal_fact.fact_id, bs_ad.fact_id, confidence="source_backed")

        cursor += timedelta(days=1)

    _build_month_length_facts(graph, end)


def _build_month_length_facts(graph: TimeGraphSnapshot, ad_end: date) -> None:
    for bs_year in range(2078, 2084):
        try:
            year_end = get_bs_year_end(bs_year)
        except ValueError:
            continue
        if year_end > ad_end:
            continue
        meta = build_bs_claim_meta(bs_year)
        source_id = str(meta["source"]["id"])
        for month in range(1, 13):
            start = bs_to_gregorian(bs_year, month, 1)
            length = days_in_bs_month(bs_year, month)
            fact = TemporalFact(
                fact_id=month_length_fact_id(bs_year, month),
                fact_type="month_length",
                subject={"calendar": "BS", "year": bs_year, "month": month},
                predicate="has_month_length_days",
                object={
                    "days": length,
                    "month_name": get_bs_month_name(month),
                    "month_start_ad": start.isoformat(),
                },
                release_id=graph.release_id,
                source_ids=[source_id],
                confidence=str(meta["confidence"]),
                claim_boundary=str(meta["claim_boundary"]),
                warnings=list(meta.get("warnings") or []),
                metadata={"past_complete_month": True},
            )
            _add_fact_with_standard_links(graph, fact)


def _build_profile_facts(graph: TimeGraphSnapshot) -> None:
    sample_bs_date = "2082-04-02"
    sample_year, sample_month, sample_day = (2082, 4, 2)
    for profile in PROFILES.values():
        graph.add_entity(
            f"profile_{profile.profile_id}",
            "InstitutionProfile",
            profile.label,
            jurisdiction=profile.jurisdiction,
            status=profile.status,
        )
        fact = TemporalFact(
            fact_id=profile_policy_fact_id(profile.profile_id),
            fact_type="profile_policy",
            subject={"entity_type": "profile", "id": profile.profile_id},
            predicate="defines_temporal_policy",
            object=profile.to_public_dict(),
            release_id=graph.release_id,
            source_ids=["parva_enterprise_compliance_profiles"],
            confidence="source_backed" if profile.status != "synthetic_demo" else "fixture",
            claim_boundary="enterprise_decision_support_not_legal_authority",
            warnings=list(profile.warnings),
            profile_ids=[profile.profile_id],
        )
        _add_fact_with_standard_links(graph, fact)

        decision = evaluate_date_payload(
            profile_id=profile.profile_id,
            bs_date=sample_bs_date,
            decision_intent="general",
        )
        decision_fact = TemporalFact(
            fact_id=working_day_fact_id(profile.profile_id, sample_year, sample_month, sample_day),
            fact_type="working_day_decision",
            subject={
                "calendar": "BS",
                "date": sample_bs_date,
                "profile_id": profile.profile_id,
            },
            predicate="evaluates_working_day",
            object=decision["decision"],
            release_id=graph.release_id,
            source_ids=["parva_enterprise_compliance_profiles"],
            confidence=str(decision.get("meta", {}).get("confidence", "source_backed")),
            claim_boundary=str(
                decision.get("meta", {}).get(
                    "claim_boundary", "enterprise_decision_support_not_legal_authority"
                )
            ),
            warnings=list(decision.get("meta", {}).get("warnings", [])),
            profile_ids=[profile.profile_id],
            metadata={"date": decision.get("date"), "trace_url": _trace_url_for_fact("")},
        )
        _add_fact_with_standard_links(graph, decision_fact)
        graph.facts[decision_fact.fact_id].metadata["trace_url"] = _trace_url_for_fact(
            decision_fact.fact_id
        )
        _add_derivation(
            graph,
            decision_fact.fact_id,
            profile_policy_fact_id(profile.profile_id),
            confidence=decision_fact.confidence,
        )
        _add_derivation(
            graph,
            decision_fact.fact_id,
            fiscal_period_fact_id(sample_year, sample_month, sample_day),
            confidence=decision_fact.confidence,
        )


def _build_trust_log_facts(graph: TimeGraphSnapshot) -> None:
    log = load_trust_log_payload(release_id=graph.release_id)
    for entry in log.get("entries", []):
        entry_id = str(entry.get("entry_id"))
        graph.add_entity(
            f"trust_log_{entry_id}",
            "TrustLogEntry",
            entry_id,
            event_type=entry.get("event_type"),
            entry_hash=entry.get("entry_hash"),
        )
        fact = TemporalFact(
            fact_id=release_membership_fact_id(graph.release_id, f"trust_log_{entry_id}"),
            fact_type="release_membership",
            subject={"entity_type": "release", "id": graph.release_id},
            predicate="has_trust_log_entry",
            object={"entity_type": "trust_log_entry", "id": entry_id, "entry_hash": entry.get("entry_hash")},
            release_id=graph.release_id,
            source_ids=["parva-public-api-contract"],
            confidence="source_backed",
            claim_boundary=TIMEGRAPH_CLAIM_BOUNDARY,
            warnings=["trust_log_entry_is_alpha_public_preview"],
        )
        _add_fact_with_standard_links(graph, fact)


def _build_fixture_conflict(graph: TimeGraphSnapshot) -> None:
    source_id = "parva-public-conformance-v0-1"
    fact_a = TemporalFact(
        fact_id="fact_fixture_conflict_candidate_a",
        fact_type="conflict",
        subject={"fixture": "timegraph_conflict_fixture", "candidate": "A"},
        predicate="claims_synthetic_temporal_value",
        object={"synthetic_value": "candidate_a"},
        release_id=graph.release_id,
        source_ids=[source_id],
        confidence="fixture",
        claim_boundary="fixture_only_not_temporal_authority",
        warnings=["fixture_conflict_not_real_calendar_claim"],
        metadata={"fixture_only": True},
    )
    fact_b = TemporalFact(
        fact_id="fact_fixture_conflict_candidate_b",
        fact_type="conflict",
        subject={"fixture": "timegraph_conflict_fixture", "candidate": "B"},
        predicate="claims_synthetic_temporal_value",
        object={"synthetic_value": "candidate_b"},
        release_id=graph.release_id,
        source_ids=[source_id],
        confidence="fixture",
        claim_boundary="fixture_only_not_temporal_authority",
        warnings=["fixture_conflict_not_real_calendar_claim"],
        metadata={"fixture_only": True},
    )
    _add_fact_with_standard_links(graph, fact_a)
    _add_fact_with_standard_links(graph, fact_b)
    conflict = TimeGraphConflict(
        conflict_id="conflict_fixture_public_timegraph",
        conflict_type="fixture_source_disagreement",
        status="fixture_only",
        facts=[fact_a.fact_id, fact_b.fact_id],
        sources=[source_id],
        release_ids=[graph.release_id],
        summary="Synthetic TimeGraph conflict used to prove conflict representation without claiming a real calendar dispute.",
        resolution_policy="fixture_only_no_operational_resolution",
        requires_human_review=True,
        confidence="fixture",
        warnings=["fixture_conflict_not_real_calendar_claim"],
        metadata={"fixture_only": True},
    )
    graph.add_conflict(conflict)
    _add_relationship(
        graph,
        from_id=fact_a.fact_id,
        to_id=fact_b.fact_id,
        relationship_type="CONTRADICTED_BY",
        confidence="fixture",
        metadata={"conflict_id": conflict.conflict_id},
    )
    _add_relationship(
        graph,
        from_id=fact_b.fact_id,
        to_id=fact_a.fact_id,
        relationship_type="CONTRADICTED_BY",
        confidence="fixture",
        metadata={"conflict_id": conflict.conflict_id},
    )


def _add_fact_with_standard_links(graph: TimeGraphSnapshot, fact: TemporalFact) -> None:
    graph.add_fact(fact)
    _add_relationship(
        graph,
        from_id=f"release_{fact.release_id}",
        to_id=fact.fact_id,
        relationship_type="CONTAINS_FACT",
        confidence=fact.confidence,
    )
    _add_relationship(
        graph,
        from_id=fact.fact_id,
        to_id=f"release_{fact.release_id}",
        relationship_type="PINNED_TO_RELEASE",
        confidence=fact.confidence,
    )
    for source_id in fact.source_ids:
        _add_relationship(
            graph,
            from_id=fact.fact_id,
            to_id=f"source_{source_id}",
            relationship_type="SUPPORTED_BY",
            confidence=fact.confidence,
        )
    for profile_id in fact.profile_ids:
        _add_relationship(
            graph,
            from_id=fact.fact_id,
            to_id=f"profile_{profile_id}",
            relationship_type="APPLIES_TO",
            confidence=fact.confidence,
        )


def _add_derivation(
    graph: TimeGraphSnapshot,
    fact_id: str,
    derived_from_fact_id: str,
    *,
    confidence: str,
) -> None:
    if derived_from_fact_id in graph.facts:
        _add_relationship(
            graph,
            from_id=fact_id,
            to_id=derived_from_fact_id,
            relationship_type="DERIVED_FROM",
            confidence=confidence,
        )


def _add_relationship(
    graph: TimeGraphSnapshot,
    *,
    from_id: str,
    to_id: str,
    relationship_type: str,
    confidence: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    graph.add_relationship(
        TimeGraphRelationship(
            relationship_id=relationship_id(from_id, to_id, relationship_type, graph.release_id),
            from_id=from_id,
            to_id=to_id,
            type=relationship_type,
            release_id=graph.release_id,
            confidence=confidence,
            metadata=metadata or {},
        )
    )


def timegraph_meta(
    *,
    release_id: str,
    trace_id: str | None = None,
    confidence: str = "source_backed",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "release_id": release_id,
        "confidence": confidence,
        "claim_boundary": TIMEGRAPH_CLAIM_BOUNDARY,
        "warnings": list(warnings or ["timegraph_output_is_not_legal_authority"]),
        "trace_id": trace_id,
    }


def list_facts_payload(
    *,
    release_id: str | None = None,
    fact_type: str | None = None,
    date_value: str | None = None,
    calendar: str | None = None,
    source_id: str | None = None,
    profile_id: str | None = None,
    confidence: str | None = None,
    claim_boundary: str | None = None,
    jurisdiction: str | None = None,
    has_conflicts: bool | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    trace_id: str | None = None,
) -> dict[str, Any]:
    graph = build_public_timegraph(release_id)
    facts = _filter_facts(
        list(graph.facts.values()),
        fact_type=fact_type,
        date_value=date_value,
        calendar=calendar,
        source_id=source_id,
        release_id=graph.release_id,
        profile_id=profile_id,
        confidence=confidence,
        claim_boundary=claim_boundary,
        jurisdiction=jurisdiction,
        has_conflicts=has_conflicts,
        graph=graph,
    )
    bounded_limit = _bounded_limit(limit)
    safe_offset = max(0, offset)
    page = facts[safe_offset : safe_offset + bounded_limit]
    return {
        "items": [fact.to_dict() for fact in page],
        "pagination": {
            "limit": bounded_limit,
            "offset": safe_offset,
            "total": len(facts),
            "has_more": safe_offset + bounded_limit < len(facts),
        },
        "meta": timegraph_meta(release_id=graph.release_id, trace_id=trace_id),
    }


def query_facts_payload(query: dict[str, Any], *, trace_id: str | None = None) -> dict[str, Any]:
    return list_facts_payload(
        release_id=_string_or_none(query.get("release_id")),
        fact_type=_string_or_none(query.get("fact_type")),
        date_value=_string_or_none(query.get("date")),
        calendar=_string_or_none(query.get("calendar")),
        source_id=_string_or_none(query.get("source_id")),
        profile_id=_string_or_none(query.get("profile_id")),
        confidence=_string_or_none(query.get("confidence")),
        claim_boundary=_string_or_none(query.get("claim_boundary")),
        jurisdiction=_string_or_none(query.get("jurisdiction")),
        has_conflicts=query.get("has_conflicts") if isinstance(query.get("has_conflicts"), bool) else None,
        limit=int(query.get("limit") or DEFAULT_LIMIT),
        offset=int(query.get("offset") or 0),
        trace_id=trace_id,
    )


def get_fact_payload(
    fact_id: str,
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    graph = build_public_timegraph(release_id)
    fact = graph.facts.get(fact_id)
    if fact is None:
        raise TimeGraphError(f"unknown fact id: {fact_id}", status_code=404)
    return {
        "fact": fact.to_dict(),
        "relationships": [
            relationship.to_dict()
            for relationship in graph.relationships.values()
            if relationship.from_id == fact_id or relationship.to_id == fact_id
        ],
        "meta": timegraph_meta(release_id=graph.release_id, trace_id=trace_id, confidence=fact.confidence),
    }


def get_facts_for_date_payload(
    calendar: str,
    date_value: str,
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    return list_facts_payload(
        release_id=release_id,
        calendar=calendar.upper(),
        date_value=date_value,
        limit=limit,
        trace_id=trace_id,
    )


def get_facts_for_source_payload(
    source_id: str,
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    graph = build_public_timegraph(release_id)
    if source_id not in graph.source_records:
        raise TimeGraphError(f"unknown source id: {source_id}", status_code=404)
    return list_facts_payload(
        release_id=graph.release_id,
        source_id=source_id,
        limit=limit,
        trace_id=trace_id,
    )


def get_facts_for_release_payload(
    release_id: str,
    *,
    trace_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    return list_facts_payload(release_id=release_id, limit=limit, trace_id=trace_id)


def get_facts_for_profile_payload(
    profile_id: str,
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    if profile_id not in PROFILES:
        raise TimeGraphError(f"unknown profile id: {profile_id}", status_code=404)
    return list_facts_payload(
        release_id=release_id,
        profile_id=profile_id,
        limit=limit,
        trace_id=trace_id,
    )


def get_relationships_payload(
    entity_id: str,
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    graph = build_public_timegraph(release_id)
    relationships = [
        relationship
        for relationship in graph.relationships.values()
        if relationship.from_id == entity_id or relationship.to_id == entity_id
    ]
    bounded_limit = _bounded_limit(limit)
    return {
        "entity_id": entity_id,
        "relationships": [relationship.to_dict() for relationship in relationships[:bounded_limit]],
        "pagination": {
            "limit": bounded_limit,
            "offset": 0,
            "total": len(relationships),
            "has_more": len(relationships) > bounded_limit,
        },
        "meta": timegraph_meta(release_id=graph.release_id, trace_id=trace_id),
    }


def trace_fact_payload(
    fact_id: str,
    *,
    release_id: str | None = None,
    depth: int = DEFAULT_TRACE_DEPTH,
    trace_id: str | None = None,
) -> dict[str, Any]:
    graph = build_public_timegraph(release_id)
    fact = graph.facts.get(fact_id)
    if fact is None:
        raise TimeGraphError(f"unknown fact id: {fact_id}", status_code=404)
    safe_depth = max(1, min(int(depth), MAX_TRACE_DEPTH))
    relationships = [
        relationship
        for relationship in graph.relationships.values()
        if relationship.from_id == fact_id or relationship.to_id == fact_id
    ]
    derived_from_ids = [
        relationship.to_id
        for relationship in relationships
        if relationship.from_id == fact_id
        and relationship.type == "DERIVED_FROM"
        and relationship.to_id in graph.facts
    ]
    conflicts = [
        conflict.to_dict()
        for conflict in graph.conflicts.values()
        if fact_id in conflict.facts
    ]
    evidence_packets = _evidence_references_for_fact(fact)
    trace = {
        "fact_id": fact_id,
        "fact": fact.to_dict(),
        "sources": [graph.source_records[source_id] for source_id in fact.source_ids if source_id in graph.source_records],
        "release": graph.release_record,
        "derived_from": [
            graph.facts[derived_id].to_dict()
            for derived_id in derived_from_ids[:safe_depth]
        ],
        "relationships": [relationship.to_dict() for relationship in relationships],
        "evidence_packets": evidence_packets,
        "conflicts": conflicts,
        "confidence": fact.confidence,
        "warnings": fact.warnings,
        "claim_boundary": fact.claim_boundary,
        "trace_depth": safe_depth,
    }
    return {
        "trace": trace,
        "meta": timegraph_meta(release_id=graph.release_id, trace_id=trace_id, confidence=fact.confidence),
    }


def list_conflicts_payload(
    *,
    release_id: str | None = None,
    trace_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, Any]:
    graph = build_public_timegraph(release_id)
    conflicts = list(graph.conflicts.values())
    bounded_limit = _bounded_limit(limit)
    return {
        "conflicts": [conflict.to_dict() for conflict in conflicts[:bounded_limit]],
        "pagination": {
            "limit": bounded_limit,
            "offset": 0,
            "total": len(conflicts),
            "has_more": len(conflicts) > bounded_limit,
        },
        "meta": timegraph_meta(
            release_id=graph.release_id,
            trace_id=trace_id,
            warnings=[
                "fixture conflicts are labeled fixture-only",
                "conflict output is not legal authority",
            ],
        ),
    }


def trace_url_for_fact(fact_id: str) -> str:
    return _trace_url_for_fact(fact_id)


def validate_public_timegraph() -> dict[str, Any]:
    graph = build_public_timegraph()
    issues: list[str] = []
    if len(graph.facts) != len(set(graph.facts)):
        issues.append("duplicate fact ids")
    if len(graph.relationships) != len(set(graph.relationships)):
        issues.append("duplicate relationship ids")
    known_entities = set(graph.entities) | set(graph.facts)
    for relationship in graph.relationships.values():
        if relationship.from_id not in known_entities:
            issues.append(f"{relationship.relationship_id}: unknown from_id {relationship.from_id}")
        if relationship.to_id not in known_entities:
            issues.append(f"{relationship.relationship_id}: unknown to_id {relationship.to_id}")
    for fact in graph.facts.values():
        if fact.release_id != graph.release_id:
            issues.append(f"{fact.fact_id}: release mismatch")
        for source_id in fact.source_ids:
            if source_id not in graph.source_records:
                issues.append(f"{fact.fact_id}: unknown source {source_id}")
        serialized = _canonical_json(fact.to_dict())
        local_drive_markers = [f"{drive}:" + "\\\\" for drive in ("C", "D")]
        if any(marker in serialized for marker in local_drive_markers):
            issues.append(f"{fact.fact_id}: local absolute path leak")
    for conflict in graph.conflicts.values():
        for fact_id in conflict.facts:
            if fact_id not in graph.facts:
                issues.append(f"{conflict.conflict_id}: unknown conflict fact {fact_id}")
    sample = graph.facts.get(bs_ad_fact_id(2083, 1, 1))
    if sample is None:
        issues.append("missing sample BS/AD fact for 2083-01-01")
    else:
        trace = trace_fact_payload(sample.fact_id)
        if not trace["trace"]["sources"]:
            issues.append("sample trace has no sources")
    return {
        "ok": not issues,
        "release_id": graph.release_id,
        "fact_count": len(graph.facts),
        "relationship_count": len(graph.relationships),
        "conflict_count": len(graph.conflicts),
        "issues": issues,
    }


def _filter_facts(
    facts: list[TemporalFact],
    *,
    fact_type: str | None,
    date_value: str | None,
    calendar: str | None,
    source_id: str | None,
    release_id: str,
    profile_id: str | None,
    confidence: str | None,
    claim_boundary: str | None,
    jurisdiction: str | None,
    has_conflicts: bool | None,
    graph: TimeGraphSnapshot,
) -> list[TemporalFact]:
    conflict_fact_ids = {fact_id for conflict in graph.conflicts.values() for fact_id in conflict.facts}

    def matches(fact: TemporalFact) -> bool:
        if fact.release_id != release_id:
            return False
        if fact_type and fact.fact_type != fact_type:
            return False
        if source_id and source_id not in fact.source_ids:
            return False
        if profile_id and profile_id not in fact.profile_ids:
            return False
        if confidence and fact.confidence != confidence:
            return False
        if claim_boundary and fact.claim_boundary != claim_boundary:
            return False
        if jurisdiction and fact.jurisdiction != jurisdiction:
            return False
        if has_conflicts is not None and ((fact.fact_id in conflict_fact_ids) is not has_conflicts):
            return False
        if date_value and not _fact_has_date(fact, date_value=date_value, calendar=calendar):
            return False
        if calendar and not date_value and not _fact_has_calendar(fact, calendar=calendar):
            return False
        return True

    return sorted((fact for fact in facts if matches(fact)), key=lambda item: item.fact_id)


def _fact_has_date(fact: TemporalFact, *, date_value: str, calendar: str | None) -> bool:
    for field_name in ("subject", "object"):
        value = getattr(fact, field_name)
        if calendar and str(value.get("calendar", "")).upper() != calendar.upper():
            continue
        if value.get("date") == date_value:
            return True
    date_block = fact.metadata.get("date")
    if isinstance(date_block, dict) and date_value in {date_block.get("bs"), date_block.get("ad")}:
        return True
    return False


def _fact_has_calendar(fact: TemporalFact, *, calendar: str) -> bool:
    return any(
        str(getattr(fact, field_name).get("calendar", "")).upper() == calendar.upper()
        for field_name in ("subject", "object")
    )


def _bounded_limit(limit: int) -> int:
    return max(1, min(int(limit), MAX_LIMIT))


def _string_or_none(value: Any) -> str | None:
    return str(value) if value is not None and str(value) else None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _evidence_references_for_fact(fact: TemporalFact) -> list[dict[str, Any]]:
    if fact.fact_type in {"bs_ad_mapping", "ad_bs_mapping"}:
        return [
            {
                "packet_type": "date_conversion",
                "endpoint": "/v3/api/trust/evidence/date-conversion",
                "fact_id": fact.fact_id,
            }
        ]
    if fact.fact_type == "working_day_decision":
        return [
            {
                "packet_type": "compliance_decision",
                "endpoint": "/v3/api/trust/evidence/compliance-decision",
                "fact_id": fact.fact_id,
            }
        ]
    return []


def _trace_url_for_fact(fact_id: str) -> str:
    return f"/v3/api/timegraph/facts/{fact_id}/trace"
