from __future__ import annotations

import json
import random
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

from .future_bs import DEFAULT_FUTURE_BS_CAPABILITIES_URL, build_future_bs_url

DEFAULT_API_BASE = "https://api.prabinghimire1.com.np/v3/api"

JsonObject = dict[str, Any]
Transport = Callable[[str, str, dict[str, str] | None, JsonObject | None, float], JsonObject]
Sleep = Callable[[float], None]

_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


class ParvaAPIError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.status = status
        self.body = body
        self.headers = headers or {}


class ParvaNetworkError(RuntimeError):
    pass


@dataclass(frozen=True)
class BsDateInput:
    year: int
    month: int
    day: int


class ParvaClient:
    def __init__(
        self,
        base_url: str = DEFAULT_API_BASE,
        *,
        future_bs_capabilities_url: str = DEFAULT_FUTURE_BS_CAPABILITIES_URL,
        timeout: float = 10.0,
        transport: Transport | None = None,
        max_retries: int = 2,
        retry_base_delay: float = 0.25,
        retry_sleep: Sleep | None = None,
    ) -> None:
        self.base_url = _validated_http_url(base_url, "base_url").rstrip("/")
        self.future_bs_capabilities_url = _validated_http_url(
            future_bs_capabilities_url, "future_bs_capabilities_url"
        )
        self.timeout = timeout
        self._transport = transport
        self.max_retries = max(0, max_retries)
        self.retry_base_delay = max(0.0, retry_base_delay)
        self._retry_sleep = retry_sleep or time.sleep

    def get_today(self, risk_mode: str | None = None) -> JsonObject:
        params = {"risk_mode": risk_mode} if risk_mode else None
        return self._request("GET", "/calendar/today", params=params)

    def ad_to_bs(self, date: str, *, proof: str | None = None) -> JsonObject:
        return self._request("GET", "/calendar/convert", params=_clean_params({"date": date, "proof": proof}))

    def bs_to_ad(self, year: int, month: int, day: int, *, proof: str | None = None) -> JsonObject:
        return self._request(
            "POST",
            "/calendar/bs-to-gregorian",
            params=_clean_params({"proof": proof}),
            json_body={"year": year, "month": month, "day": day},
        )

    def validate_bs_date(self, year: int, month: int, day: int, *, proof: str | None = None) -> JsonObject:
        if proof:
            return self._request(
                "GET",
                "/calendar/validate-bs-date",
                params=_clean_params({"year": year, "month": month, "day": day, "proof": proof}),
            )
        try:
            payload = self.bs_to_ad(year, month, day)
        except ParvaAPIError as exc:
            if exc.status == 400:
                return {
                    "valid": False,
                    "publication_status": "computed_prediction_not_official",
                    "error": str(exc),
                }
            raise
        return {
            "valid": True,
            "publication_status": "computed_prediction_not_official",
            "result": payload,
        }

    def get_month_calendar(self, year: int, month: int) -> JsonObject:
        return self._request(
            "GET",
            "/calendar/dual-month",
            params={"year": str(year), "month": str(month)},
        )

    def get_fiscal_year(self, bs_year: int, *, proof: str | None = None) -> JsonObject:
        return self._request("GET", f"/enterprise/fiscal-year/{bs_year}", params=_clean_params({"proof": proof}))

    def get_bs_months(self, bs_year: int, *, mode: str = "canonical", proof: str | None = None) -> JsonObject:
        return self._request(
            "GET",
            f"/enterprise/bs-months/{bs_year}",
            params=_clean_params({"mode": mode if mode != "canonical" else None, "proof": proof}),
        )

    def get_business_days(
        self,
        start_bs: str,
        end_bs: str,
        *,
        weekend: str = "saturday",
        include_start: bool = True,
        include_end: bool = True,
        holiday_policy: str = "none",
    ) -> JsonObject:
        return self._request(
            "POST",
            "/enterprise/business-days",
            json_body={
                "start_bs": start_bs,
                "end_bs": end_bs,
                "weekend": weekend,
                "include_start": include_start,
                "include_end": include_end,
                "holiday_policy": holiday_policy,
            },
        )

    def get_enterprise_capabilities(self) -> JsonObject:
        return self._request("GET", "/enterprise/capabilities")

    def list_profiles(self) -> JsonObject:
        return self._request("GET", "/compliance/profiles")

    def get_profile(self, profile_id: str) -> JsonObject:
        return self._request("GET", f"/compliance/profiles/{urllib.parse.quote(profile_id, safe='')}")

    def evaluate_date(
        self,
        *,
        profile_id: str = "nepal_private_company_default",
        bs_date: str | None = None,
        ad_date: str | None = None,
        decision_intent: str = "general",
        proof: str | None = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/compliance/evaluate-date",
            params=_clean_params({"proof": proof}),
            json_body={
                "profile_id": profile_id,
                "bs_date": bs_date,
                "ad_date": ad_date,
                "decision_intent": decision_intent,
            },
        )

    def check_holiday(
        self,
        *,
        bs_date: str | None = None,
        ad_date: str | None = None,
        profile_id: str = "nepal_public_general",
        proof: str | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            "/compliance/holiday",
            params=_clean_params(
                {"bs_date": bs_date, "ad_date": ad_date, "profile_id": profile_id, "proof": proof},
            ),
        )

    def get_panchanga(
        self,
        date: str,
        *,
        proof: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        timezone: str = "Asia/Kathmandu",
        ephemeris_provider: str = "builtin_swiss_moshier",
        ephemeris_fixture_id: str | None = None,
        ayanamsa: str = "lahiri",
    ) -> JsonObject:
        return self._request(
            "GET",
            "/calendar/panchanga",
            params=_clean_params(
                {
                    "date": date,
                    "proof": proof,
                    "lat": latitude,
                    "lon": longitude,
                    "tz": timezone,
                    "ephemeris_provider": ephemeris_provider,
                    "ephemeris_fixture_id": ephemeris_fixture_id,
                    "ayanamsa": ayanamsa,
                },
            ),
        )

    def verify_membrane(self, membrane: JsonObject) -> JsonObject:
        """Run SDK-side structural checks for a membrane receipt.

        Full replay verification is available in the local kernel/backend
        verifier. This SDK helper is intentionally conservative and never
        upgrades authority.
        """

        required = {"kind", "canonical_query", "identity_hash", "result", "boundary", "field_provenance", "witness_hash"}
        missing = sorted(required - set(membrane))
        if missing:
            return {"verified": False, "reason": "required_fields_missing", "missing": missing}
        if not str(membrane.get("identity_hash", "")).startswith("parva:id:v1:sha256:"):
            return {"verified": False, "reason": "identity_hash_invalid"}
        if not str(membrane.get("witness_hash", "")).startswith("parva:wit:v1:sha256:"):
            return {"verified": False, "reason": "witness_hash_invalid"}
        if not isinstance(membrane.get("boundary"), dict) or not membrane["boundary"].get("claim_boundary"):
            return {"verified": False, "reason": "boundary_vector_missing"}
        if not isinstance(membrane.get("field_provenance"), dict):
            return {"verified": False, "reason": "field_provenance_missing"}
        return {"verified": True, "reason": "structural_checks_passed_replay_required_for_full_verification"}

    def verify_proofpack(self, proofpack: JsonObject) -> JsonObject:
        if isinstance(proofpack.get("membrane"), dict):
            return self.verify_membrane(proofpack["membrane"])
        required = {"identity_hash", "witness_hash", "boundary"}
        missing = sorted(required - set(proofpack))
        return {
            "verified": not missing,
            "reason": "verified_compact_proofpack" if not missing else "required_fields_missing",
            "missing": missing,
        }

    def verify_timepack(self, timepack: JsonObject) -> JsonObject:
        if timepack.get("kind") != "parva_timepack" or not isinstance(timepack.get("proof_packs"), list):
            return {"verified": False, "reason": "timepack_schema_invalid"}
        for proofpack in timepack["proof_packs"]:
            result = self.verify_proofpack(proofpack)
            if not result["verified"]:
                return {"verified": False, "reason": f"child_{result['reason']}"}
        boundary = timepack.get("boundary_summary") or {}
        if not boundary.get("not_authority"):
            return {"verified": False, "reason": "timepack_boundary_summary_missing"}
        return {"verified": True, "reason": "structural_checks_passed_replay_required_for_full_verification"}

    def replay_panchanga_membrane(self, membrane: JsonObject) -> JsonObject:
        structural = self.verify_membrane(membrane)
        if not structural["verified"]:
            return structural
        if (membrane.get("canonical_query") or {}).get("operation") != "panchanga_summary":
            return {"verified": False, "reason": "not_panchanga_membrane"}
        metadata = membrane.get("ephemeris_metadata") or {}
        if not metadata.get("provider_id") or not metadata.get("provider_kind"):
            return {"verified": False, "reason": "ephemeris_metadata_missing"}
        return {
            "verified": True,
            "reason": "structural_panchanga_checks_passed_local_kernel_or_backend_replay_required",
        }

    def next_working_day(
        self,
        *,
        profile_id: str = "nepal_private_company_default",
        bs_date: str | None = None,
        ad_date: str | None = None,
        include_input: bool = False,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/compliance/next-working-day",
            json_body={
                "profile_id": profile_id,
                "bs_date": bs_date,
                "ad_date": ad_date,
                "include_input": include_input,
            },
        )

    def previous_working_day(
        self,
        *,
        profile_id: str = "nepal_private_company_default",
        bs_date: str | None = None,
        ad_date: str | None = None,
        include_input: bool = False,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/compliance/previous-working-day",
            json_body={
                "profile_id": profile_id,
                "bs_date": bs_date,
                "ad_date": ad_date,
                "include_input": include_input,
            },
        )

    def add_working_days(
        self,
        *,
        working_days: int,
        profile_id: str = "nepal_private_company_default",
        bs_date: str | None = None,
        ad_date: str | None = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/compliance/add-working-days",
            json_body={
                "profile_id": profile_id,
                "bs_date": bs_date,
                "ad_date": ad_date,
                "working_days": working_days,
            },
        )

    def month_closing_day(
        self,
        *,
        bs_year: int,
        bs_month: int,
        profile_id: str = "nepal_private_company_default",
    ) -> JsonObject:
        return self._request(
            "POST",
            "/compliance/month-closing-day",
            json_body={
                "profile_id": profile_id,
                "bs_year": bs_year,
                "bs_month": bs_month,
            },
        )

    def fiscal_period(
        self,
        *,
        profile_id: str = "nepal_private_company_default",
        bs_date: str | None = None,
        ad_date: str | None = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/compliance/fiscal-period",
            json_body={
                "profile_id": profile_id,
                "bs_date": bs_date,
                "ad_date": ad_date,
            },
        )

    def get_policy(self) -> JsonObject:
        return self._request("GET", "/policy")

    def get_trust_capabilities(self) -> JsonObject:
        return self._request("GET", "/trust/capabilities")

    def list_sources(self, release_id: str | None = None) -> JsonObject:
        params = {"release_id": release_id} if release_id else None
        return self._request("GET", "/trust/sources", params=params)

    def get_source(self, source_id: str, release_id: str | None = None) -> JsonObject:
        params = {"release_id": release_id} if release_id else None
        return self._request(
            "GET",
            f"/trust/sources/{urllib.parse.quote(source_id, safe='')}",
            params=params,
        )

    def list_releases(self) -> JsonObject:
        return self._request("GET", "/trust/releases")

    def get_release(self, release_id: str) -> JsonObject:
        return self._request("GET", f"/trust/releases/{urllib.parse.quote(release_id, safe='')}")

    def diff_releases(self, from_release: str, to_release: str) -> JsonObject:
        return self._request(
            "GET",
            "/trust/releases/"
            f"{urllib.parse.quote(from_release, safe='')}/diff/"
            f"{urllib.parse.quote(to_release, safe='')}",
        )

    def get_trust_log(self, release_id: str | None = None) -> JsonObject:
        params = {"release_id": release_id} if release_id else None
        return self._request("GET", "/trust/log", params=params)

    def create_date_conversion_evidence(
        self,
        *,
        ad_date: str | None = None,
        bs_date: str | None = None,
        release_id: str | None = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/trust/evidence/date-conversion",
            json_body={
                "ad_date": ad_date,
                "bs_date": bs_date,
                "release_id": release_id,
            },
        )

    def create_compliance_decision_evidence(
        self,
        *,
        profile_id: str = "nepal_private_company_default",
        bs_date: str | None = None,
        ad_date: str | None = None,
        decision_intent: str = "general",
        release_id: str | None = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/trust/evidence/compliance-decision",
            json_body={
                "profile_id": profile_id,
                "bs_date": bs_date,
                "ad_date": ad_date,
                "decision_intent": decision_intent,
                "release_id": release_id,
            },
        )

    def get_timegraph_capabilities(self) -> JsonObject:
        return self._request("GET", "/timegraph/capabilities")

    def get_rule_capabilities(self) -> JsonObject:
        return self._request("GET", "/rules/capabilities")

    def list_rules(self) -> JsonObject:
        return self._request("GET", "/rules")

    def get_rule(self, rule_id: str) -> JsonObject:
        return self._request("GET", f"/rules/{urllib.parse.quote(rule_id, safe='')}")

    def validate_rule(self, rule: JsonObject) -> JsonObject:
        return self._request("POST", "/rules/validate", json_body={"rule": rule})

    def evaluate_rule(
        self,
        rule_id: str,
        *,
        input_payload: JsonObject | None = None,
        release_id: str | None = None,
        include_evidence: bool = False,
    ) -> JsonObject:
        return self._request(
            "POST",
            f"/rules/{urllib.parse.quote(rule_id, safe='')}/evaluate",
            json_body={
                "input": input_payload or {},
                "release_id": release_id,
                "include_evidence": include_evidence,
            },
        )

    def test_rule(self, rule_id: str) -> JsonObject:
        return self._request("POST", f"/rules/{urllib.parse.quote(rule_id, safe='')}/test")

    def evaluate_custom_rule(
        self,
        *,
        rule: JsonObject,
        input_payload: JsonObject | None = None,
        release_id: str | None = None,
        include_evidence: bool = False,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/rules/evaluate",
            json_body={
                "rule": rule,
                "input": input_payload or {},
                "release_id": release_id,
                "include_evidence": include_evidence,
            },
        )

    def explain_rule(
        self,
        *,
        rule_id: str | None = None,
        rule: JsonObject | None = None,
        input_payload: JsonObject | None = None,
        release_id: str | None = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/rules/explain",
            json_body={
                "rule_id": rule_id,
                "rule": rule,
                "input": input_payload or {},
                "release_id": release_id,
            },
        )

    def list_facts(
        self,
        *,
        release_id: str | None = None,
        fact_type: str | None = None,
        date: str | None = None,
        calendar: str | None = None,
        source_id: str | None = None,
        profile_id: str | None = None,
        confidence: str | None = None,
        claim_boundary: str | None = None,
        jurisdiction: str | None = None,
        has_conflicts: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            "/timegraph/facts",
            params=_clean_params(
                {
                    "release_id": release_id,
                    "fact_type": fact_type,
                    "date": date,
                    "calendar": calendar,
                    "source_id": source_id,
                    "profile_id": profile_id,
                    "confidence": confidence,
                    "claim_boundary": claim_boundary,
                    "jurisdiction": jurisdiction,
                    "has_conflicts": has_conflicts,
                    "limit": limit,
                    "offset": offset,
                },
            ),
        )

    def get_fact(self, fact_id: str, release_id: str | None = None) -> JsonObject:
        return self._request(
            "GET",
            f"/timegraph/facts/{urllib.parse.quote(fact_id, safe='')}",
            params=_clean_params({"release_id": release_id}),
        )

    def query_facts(self, **filters: Any) -> JsonObject:
        return self._request("POST", "/timegraph/query", json_body=filters)

    def get_facts_for_date(
        self,
        calendar: str,
        date: str,
        *,
        release_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            "/timegraph/date/"
            f"{urllib.parse.quote(calendar, safe='')}/"
            f"{urllib.parse.quote(date, safe='')}",
            params=_clean_params({"release_id": release_id, "limit": limit, "offset": offset}),
        )

    def get_facts_for_source(
        self,
        source_id: str,
        *,
        release_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            f"/timegraph/sources/{urllib.parse.quote(source_id, safe='')}/facts",
            params=_clean_params({"release_id": release_id, "limit": limit, "offset": offset}),
        )

    def get_facts_for_release(
        self,
        release_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            f"/timegraph/releases/{urllib.parse.quote(release_id, safe='')}/facts",
            params=_clean_params({"limit": limit, "offset": offset}),
        )

    def get_facts_for_profile(
        self,
        profile_id: str,
        *,
        release_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            f"/timegraph/profiles/{urllib.parse.quote(profile_id, safe='')}/facts",
            params=_clean_params({"release_id": release_id, "limit": limit, "offset": offset}),
        )

    def get_relationships(
        self,
        entity_id: str,
        *,
        release_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            f"/timegraph/entities/{urllib.parse.quote(entity_id, safe='')}/relationships",
            params=_clean_params({"release_id": release_id, "limit": limit, "offset": offset}),
        )

    def trace_fact(
        self,
        fact_id: str,
        *,
        release_id: str | None = None,
        depth: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            f"/timegraph/facts/{urllib.parse.quote(fact_id, safe='')}/trace",
            params=_clean_params({"release_id": release_id, "depth": depth}),
        )

    def list_conflicts(
        self,
        *,
        release_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> JsonObject:
        return self._request(
            "GET",
            "/timegraph/conflicts",
            params=_clean_params({"release_id": release_id, "limit": limit, "offset": offset}),
        )

    def get_impact_capabilities(self) -> JsonObject:
        return self._request("GET", "/impact/capabilities")

    def diff_releases_for_impact(
        self,
        *,
        from_release: str = "parva-bs-public-demo",
        to_release: str = "parva-bs-public-demo",
    ) -> JsonObject:
        return self._request(
            "POST",
            "/impact/diff-releases",
            json_body={"from_release_id": from_release, "to_release_id": to_release},
        )

    def simulate_change_set(self, change_set: JsonObject) -> JsonObject:
        return self._request("POST", "/impact/simulate-change-set", json_body={"change_set": change_set})

    def simulate_release_diff(
        self,
        *,
        from_release: str = "parva-bs-public-demo",
        to_release: str = "parva-bs-public-demo",
    ) -> JsonObject:
        return self._request(
            "POST",
            "/impact/simulate-release-diff",
            json_body={"from_release_id": from_release, "to_release_id": to_release},
        )

    def get_impact_run(self, impact_run_id: str) -> JsonObject:
        return self._request("GET", f"/impact/runs/{urllib.parse.quote(impact_run_id, safe='')}")

    def list_impact_reason_codes(self) -> JsonObject:
        return self._request("GET", "/impact/reason-codes")

    def list_impact_recommended_actions(self) -> JsonObject:
        return self._request("GET", "/impact/recommended-actions")

    def get_impact_event_schema(self) -> JsonObject:
        return self._request("GET", "/impact/event-schema")

    def get_agent_capabilities(self) -> JsonObject:
        return self._request("GET", "/agent/capabilities")

    def list_agent_tools(self) -> JsonObject:
        return self._request("GET", "/agent/tools")

    def get_agent_manifest(self) -> JsonObject:
        return self._request("GET", "/agent/manifest")

    def resolve_temporal_intent(self, text: str, *, context: JsonObject | None = None) -> JsonObject:
        return self._request(
            "POST",
            "/agent/resolve-intent",
            json_body={"text": text, "context": context or {}},
        )

    def verify_temporal_claim(
        self,
        claim: str,
        *,
        context: JsonObject | None = None,
        include_evidence: bool = False,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/agent/verify-claim",
            json_body={
                "claim": claim,
                "context": context or {},
                "include_evidence": include_evidence,
            },
        )

    def plan_schedule(
        self,
        *,
        schedule_type: str,
        bs_year: int,
        profile_id: str = "nepal_private_company_default",
        months: list[int] | None = None,
    ) -> JsonObject:
        return self._request(
            "POST",
            "/agent/plan-schedule",
            json_body={
                "schedule_type": schedule_type,
                "bs_year": bs_year,
                "profile_id": profile_id,
                "months": months,
            },
        )

    def explain_temporal_decision(
        self,
        *,
        explanation_type: str,
        payload: JsonObject,
    ) -> JsonObject:
        request_payload = {**payload, "type": explanation_type}
        return self._request(
            "POST",
            "/agent/explain",
            json_body={"payload": request_payload},
        )

    def check_human_review(self, decision: JsonObject) -> JsonObject:
        return self._request("POST", "/agent/check-human-review", json_body={"payload": decision})

    def draft_rule(self, instruction: str, *, context: JsonObject | None = None) -> JsonObject:
        return self._request(
            "POST",
            "/agent/draft-rule",
            json_body={"text": instruction, "profile_id": str((context or {}).get("profile_id") or "nepal_private_company_default")},
        )

    def run_agent_tool(self, tool_name: str, input_payload: JsonObject | None = None) -> JsonObject:
        return self._request(
            "POST",
            "/agent/run-tool",
            json_body={"tool_name": tool_name, "input": input_payload or {}},
        )

    def get_protocol_version(self) -> JsonObject:
        return self._request("GET", "/protocol/version")

    def get_protocol_capabilities(self) -> JsonObject:
        return self._request("GET", "/protocol/capabilities")

    def list_protocol_specs(self) -> JsonObject:
        return self._request("GET", "/protocol/specs")

    def list_protocol_schemas(self) -> JsonObject:
        return self._request("GET", "/protocol/schemas")

    def list_protocol_compatibility_levels(self) -> JsonObject:
        return self._request("GET", "/protocol/compatibility-levels")

    def run_conformance(self, *, target: str = "local", level: str = "parva_core") -> JsonObject:
        return self._request(
            "POST",
            "/protocol/conformance/run",
            json_body={"target": target, "level": level},
        )

    def issue_calendar_credential(
        self,
        *,
        subject: JsonObject,
        claims: JsonObject,
        release_id: str = "parva-bs-public-demo",
    ) -> JsonObject:
        return self._request(
            "POST",
            "/protocol/credentials/issue",
            json_body={"subject": subject, "claims": claims, "release_id": release_id},
        )

    def verify_calendar_credential(self, credential: JsonObject) -> JsonObject:
        return self._request(
            "POST",
            "/protocol/credentials/verify",
            json_body={"credential": credential},
        )

    def get_calendar_credential_schema(self) -> JsonObject:
        return self._request("GET", "/protocol/credentials/schema")

    def get_offline_bundle_manifest(self) -> JsonObject:
        return self._request("GET", "/protocol/offline-bundle/manifest")

    def get_future_bs_capabilities(self) -> JsonObject:
        return self._request_absolute("GET", self.future_bs_capabilities_url)

    def get_future_bs_methodology(self) -> JsonObject:
        return self._request_absolute(
            "GET", build_future_bs_url(self.future_bs_capabilities_url, "methodology")
        )

    def get_future_bs_forecast(self, bs_year: int) -> JsonObject:
        if isinstance(bs_year, bool) or not isinstance(bs_year, int) or bs_year <= 0:
            raise ValueError("bs_year must be a positive integer")
        return self._request_absolute(
            "GET", build_future_bs_url(self.future_bs_capabilities_url, f"forecast/{bs_year}")
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: JsonObject | None = None,
    ) -> JsonObject:
        url = _build_url(self.base_url, path, params)
        return self._request_absolute(method, url, json_body=json_body)

    def _request_absolute(
        self,
        method: str,
        url: str,
        *,
        json_body: JsonObject | None = None,
    ) -> JsonObject:
        for attempt in range(self.max_retries + 1):
            try:
                return self._request_once(method, url, json_body=json_body)
            except ParvaAPIError as exc:
                if not _is_retryable_error(exc) or attempt >= self.max_retries:
                    raise
                self._retry_sleep(_retry_delay_seconds(exc, attempt, self.retry_base_delay))
            except ParvaNetworkError:
                if attempt >= self.max_retries:
                    raise
                self._retry_sleep(_retry_delay_seconds(None, attempt, self.retry_base_delay))
        raise ParvaNetworkError("Parva API request failed after retry attempts")

    def _request_once(
        self,
        method: str,
        url: str,
        *,
        json_body: JsonObject | None = None,
    ) -> JsonObject:
        if self._transport is not None:
            return self._transport(method, url, None, json_body, self.timeout)

        data = None
        headers = {"Accept": "application/json"}
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec B310
                return _decode_response(response.read(), response.status)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            parsed = _parse_json(body)
            detail = _extract_detail(parsed) or exc.reason
            raise ParvaAPIError(
                f"Parva API request failed with status {exc.code}: {detail}",
                status=exc.code,
                body=parsed,
                headers={key: value for key, value in exc.headers.items()},
            ) from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            raise ParvaNetworkError(f"Parva API request failed: {exc}") from exc


def _is_retryable_error(exc: ParvaAPIError) -> bool:
    return exc.status in _RETRYABLE_STATUSES


def _validated_http_url(url: str, field_name: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{field_name} must be an absolute http(s) URL")
    return url


def _retry_delay_seconds(exc: ParvaAPIError | None, attempt: int, base_delay: float) -> float:
    if exc is not None and exc.status == 429:
        retry_after = _parse_retry_after_seconds(exc.headers.get("Retry-After"))
        if retry_after is not None:
            return retry_after
    exponential = base_delay * (2**attempt)
    jitter = random.uniform(0.0, base_delay) if base_delay > 0 else 0.0  # nosec B311
    return exponential + jitter


def _parse_retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    return max(0.0, seconds)


def get_today(*, client: ParvaClient | None = None, risk_mode: str | None = None) -> JsonObject:
    return (client or ParvaClient()).get_today(risk_mode=risk_mode)


def ad_to_bs(date: str, *, client: ParvaClient | None = None, proof: str | None = None) -> JsonObject:
    return (client or ParvaClient()).ad_to_bs(date, proof=proof)


def bs_to_ad(
    year: int,
    month: int,
    day: int,
    *,
    client: ParvaClient | None = None,
    proof: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).bs_to_ad(year, month, day, proof=proof)


def validate_bs_date(
    year: int,
    month: int,
    day: int,
    *,
    client: ParvaClient | None = None,
    proof: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).validate_bs_date(year, month, day, proof=proof)


def get_month_calendar(
    year: int,
    month: int,
    *,
    client: ParvaClient | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_month_calendar(year, month)


def get_fiscal_year(bs_year: int, *, client: ParvaClient | None = None, proof: str | None = None) -> JsonObject:
    return (client or ParvaClient()).get_fiscal_year(bs_year, proof=proof)


def get_bs_months(
    bs_year: int,
    *,
    client: ParvaClient | None = None,
    mode: str = "canonical",
    proof: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_bs_months(bs_year, mode=mode, proof=proof)


def get_business_days(
    start_bs: str,
    end_bs: str,
    *,
    client: ParvaClient | None = None,
    weekend: str = "saturday",
    include_start: bool = True,
    include_end: bool = True,
    holiday_policy: str = "none",
) -> JsonObject:
    return (client or ParvaClient()).get_business_days(
        start_bs,
        end_bs,
        weekend=weekend,
        include_start=include_start,
        include_end=include_end,
        holiday_policy=holiday_policy,
    )


def get_enterprise_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_enterprise_capabilities()


def list_profiles(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_profiles()


def get_profile(profile_id: str, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_profile(profile_id)


def evaluate_date(
    *,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
    bs_date: str | None = None,
    ad_date: str | None = None,
    decision_intent: str = "general",
    proof: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).evaluate_date(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        decision_intent=decision_intent,
        proof=proof,
    )


def check_holiday(
    *,
    client: ParvaClient | None = None,
    bs_date: str | None = None,
    ad_date: str | None = None,
    profile_id: str = "nepal_public_general",
    proof: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).check_holiday(
        bs_date=bs_date,
        ad_date=ad_date,
        profile_id=profile_id,
        proof=proof,
    )


def get_panchanga(
    date: str,
    *,
    client: ParvaClient | None = None,
    proof: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    timezone: str = "Asia/Kathmandu",
    ephemeris_provider: str = "builtin_swiss_moshier",
    ephemeris_fixture_id: str | None = None,
    ayanamsa: str = "lahiri",
) -> JsonObject:
    return (client or ParvaClient()).get_panchanga(
        date,
        proof=proof,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        ephemeris_provider=ephemeris_provider,
        ephemeris_fixture_id=ephemeris_fixture_id,
        ayanamsa=ayanamsa,
    )


def next_working_day(
    *,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
    bs_date: str | None = None,
    ad_date: str | None = None,
    include_input: bool = False,
) -> JsonObject:
    return (client or ParvaClient()).next_working_day(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        include_input=include_input,
    )


def previous_working_day(
    *,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
    bs_date: str | None = None,
    ad_date: str | None = None,
    include_input: bool = False,
) -> JsonObject:
    return (client or ParvaClient()).previous_working_day(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        include_input=include_input,
    )


def add_working_days(
    *,
    working_days: int,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
    bs_date: str | None = None,
    ad_date: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).add_working_days(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        working_days=working_days,
    )


def month_closing_day(
    *,
    bs_year: int,
    bs_month: int,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
) -> JsonObject:
    return (client or ParvaClient()).month_closing_day(
        profile_id=profile_id,
        bs_year=bs_year,
        bs_month=bs_month,
    )


def fiscal_period(
    *,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
    bs_date: str | None = None,
    ad_date: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).fiscal_period(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
    )


def get_policy(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_policy()


def get_trust_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_trust_capabilities()


def list_sources(
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).list_sources(release_id=release_id)


def get_source(
    source_id: str,
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_source(source_id, release_id=release_id)


def list_releases(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_releases()


def get_release(release_id: str, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_release(release_id)


def diff_releases(
    from_release: str,
    to_release: str,
    *,
    client: ParvaClient | None = None,
) -> JsonObject:
    return (client or ParvaClient()).diff_releases(from_release, to_release)


def get_trust_log(
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_trust_log(release_id=release_id)


def create_date_conversion_evidence(
    *,
    client: ParvaClient | None = None,
    ad_date: str | None = None,
    bs_date: str | None = None,
    release_id: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).create_date_conversion_evidence(
        ad_date=ad_date,
        bs_date=bs_date,
        release_id=release_id,
    )


def create_compliance_decision_evidence(
    *,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
    bs_date: str | None = None,
    ad_date: str | None = None,
    decision_intent: str = "general",
    release_id: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).create_compliance_decision_evidence(
        profile_id=profile_id,
        bs_date=bs_date,
        ad_date=ad_date,
        decision_intent=decision_intent,
        release_id=release_id,
    )


def get_timegraph_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_timegraph_capabilities()


def get_rule_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_rule_capabilities()


def list_rules(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_rules()


def get_rule(rule_id: str, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_rule(rule_id)


def validate_rule(rule: JsonObject, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).validate_rule(rule)


def evaluate_rule(
    rule_id: str,
    *,
    client: ParvaClient | None = None,
    input_payload: JsonObject | None = None,
    release_id: str | None = None,
    include_evidence: bool = False,
) -> JsonObject:
    return (client or ParvaClient()).evaluate_rule(
        rule_id,
        input_payload=input_payload,
        release_id=release_id,
        include_evidence=include_evidence,
    )


def test_rule(rule_id: str, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).test_rule(rule_id)


def evaluate_custom_rule(
    *,
    rule: JsonObject,
    client: ParvaClient | None = None,
    input_payload: JsonObject | None = None,
    release_id: str | None = None,
    include_evidence: bool = False,
) -> JsonObject:
    return (client or ParvaClient()).evaluate_custom_rule(
        rule=rule,
        input_payload=input_payload,
        release_id=release_id,
        include_evidence=include_evidence,
    )


def explain_rule(
    *,
    client: ParvaClient | None = None,
    rule_id: str | None = None,
    rule: JsonObject | None = None,
    input_payload: JsonObject | None = None,
    release_id: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).explain_rule(
        rule_id=rule_id,
        rule=rule,
        input_payload=input_payload,
        release_id=release_id,
    )


def list_facts(*, client: ParvaClient | None = None, **filters: Any) -> JsonObject:
    return (client or ParvaClient()).list_facts(**filters)


def get_fact(
    fact_id: str,
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_fact(fact_id, release_id=release_id)


def query_facts(*, client: ParvaClient | None = None, **filters: Any) -> JsonObject:
    return (client or ParvaClient()).query_facts(**filters)


def get_facts_for_date(
    calendar: str,
    date: str,
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_facts_for_date(
        calendar,
        date,
        release_id=release_id,
        limit=limit,
        offset=offset,
    )


def get_facts_for_source(
    source_id: str,
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_facts_for_source(
        source_id,
        release_id=release_id,
        limit=limit,
        offset=offset,
    )


def get_facts_for_release(
    release_id: str,
    *,
    client: ParvaClient | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_facts_for_release(
        release_id,
        limit=limit,
        offset=offset,
    )


def get_facts_for_profile(
    profile_id: str,
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_facts_for_profile(
        profile_id,
        release_id=release_id,
        limit=limit,
        offset=offset,
    )


def get_relationships(
    entity_id: str,
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> JsonObject:
    return (client or ParvaClient()).get_relationships(
        entity_id,
        release_id=release_id,
        limit=limit,
        offset=offset,
    )


def trace_fact(
    fact_id: str,
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
    depth: int | None = None,
) -> JsonObject:
    return (client or ParvaClient()).trace_fact(fact_id, release_id=release_id, depth=depth)


def list_conflicts(
    *,
    client: ParvaClient | None = None,
    release_id: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> JsonObject:
    return (client or ParvaClient()).list_conflicts(
        release_id=release_id,
        limit=limit,
        offset=offset,
    )


def get_impact_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_impact_capabilities()


def diff_releases_for_impact(
    *,
    client: ParvaClient | None = None,
    from_release: str = "parva-bs-public-demo",
    to_release: str = "parva-bs-public-demo",
) -> JsonObject:
    return (client or ParvaClient()).diff_releases_for_impact(
        from_release=from_release,
        to_release=to_release,
    )


def simulate_change_set(change_set: JsonObject, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).simulate_change_set(change_set)


def simulate_release_diff(
    *,
    client: ParvaClient | None = None,
    from_release: str = "parva-bs-public-demo",
    to_release: str = "parva-bs-public-demo",
) -> JsonObject:
    return (client or ParvaClient()).simulate_release_diff(
        from_release=from_release,
        to_release=to_release,
    )


def get_impact_run(impact_run_id: str, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_impact_run(impact_run_id)


def list_impact_reason_codes(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_impact_reason_codes()


def list_impact_recommended_actions(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_impact_recommended_actions()


def get_impact_event_schema(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_impact_event_schema()


def get_agent_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_agent_capabilities()


def list_agent_tools(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_agent_tools()


def get_agent_manifest(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_agent_manifest()


def resolve_temporal_intent(
    text: str,
    *,
    client: ParvaClient | None = None,
    context: JsonObject | None = None,
) -> JsonObject:
    return (client or ParvaClient()).resolve_temporal_intent(text, context=context)


def verify_temporal_claim(
    claim: str,
    *,
    client: ParvaClient | None = None,
    context: JsonObject | None = None,
    include_evidence: bool = False,
) -> JsonObject:
    return (client or ParvaClient()).verify_temporal_claim(
        claim,
        context=context,
        include_evidence=include_evidence,
    )


def plan_schedule(
    *,
    schedule_type: str,
    bs_year: int,
    client: ParvaClient | None = None,
    profile_id: str = "nepal_private_company_default",
    months: list[int] | None = None,
) -> JsonObject:
    return (client or ParvaClient()).plan_schedule(
        schedule_type=schedule_type,
        bs_year=bs_year,
        profile_id=profile_id,
        months=months,
    )


def explain_temporal_decision(
    *,
    explanation_type: str,
    payload: JsonObject,
    client: ParvaClient | None = None,
) -> JsonObject:
    return (client or ParvaClient()).explain_temporal_decision(
        explanation_type=explanation_type,
        payload=payload,
    )


def check_human_review(decision: JsonObject, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).check_human_review(decision)


def draft_rule(
    instruction: str,
    *,
    client: ParvaClient | None = None,
    context: JsonObject | None = None,
) -> JsonObject:
    return (client or ParvaClient()).draft_rule(instruction, context=context)


def run_agent_tool(
    tool_name: str,
    input_payload: JsonObject | None = None,
    *,
    client: ParvaClient | None = None,
) -> JsonObject:
    return (client or ParvaClient()).run_agent_tool(tool_name, input_payload)


def get_protocol_version(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_protocol_version()


def get_protocol_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_protocol_capabilities()


def list_protocol_specs(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_protocol_specs()


def list_protocol_schemas(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_protocol_schemas()


def list_protocol_compatibility_levels(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).list_protocol_compatibility_levels()


def run_conformance(
    *,
    client: ParvaClient | None = None,
    target: str = "local",
    level: str = "parva_core",
) -> JsonObject:
    return (client or ParvaClient()).run_conformance(target=target, level=level)


def issue_calendar_credential(
    *,
    subject: JsonObject,
    claims: JsonObject,
    client: ParvaClient | None = None,
    release_id: str = "parva-bs-public-demo",
) -> JsonObject:
    return (client or ParvaClient()).issue_calendar_credential(
        subject=subject,
        claims=claims,
        release_id=release_id,
    )


def verify_calendar_credential(
    credential: JsonObject,
    *,
    client: ParvaClient | None = None,
) -> JsonObject:
    return (client or ParvaClient()).verify_calendar_credential(credential)


def get_calendar_credential_schema(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_calendar_credential_schema()


def get_offline_bundle_manifest(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_offline_bundle_manifest()


def _build_url(base_url: str, path: str, params: dict[str, str] | None = None) -> str:
    normalized = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if not params:
        return normalized
    return f"{normalized}?{urllib.parse.urlencode(params)}"


def _clean_params(params: dict[str, Any]) -> dict[str, str] | None:
    cleaned: dict[str, str] = {}
    for key, value in params.items():
        if value is None or value == "":
            continue
        cleaned[key] = str(value).lower() if isinstance(value, bool) else str(value)
    return cleaned or None


def _decode_response(body: bytes, status: int) -> JsonObject:
    parsed = _parse_json(body)
    if not isinstance(parsed, dict):
        raise ParvaAPIError(
            "Parva API returned a non-object JSON payload",
            status=status,
            body=parsed,
        )
    return parsed


def _parse_json(body: bytes) -> Any:
    if not body:
        return {}
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _extract_detail(payload: Any) -> str | None:
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict) and isinstance(error.get("message"), str):
            return error["message"]
        if isinstance(payload.get("detail"), str):
            return payload["detail"]
    return None
