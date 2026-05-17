from __future__ import annotations

import pytest
from parva import (
    DEFAULT_API_BASE,
    DEFAULT_FUTURE_BS_CAPABILITIES_URL,
    ParvaAPIError,
    ParvaClient,
)


def test_bs_to_ad_uses_public_v3_base() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {"gregorian": "2026-04-14"}

    client = ParvaClient(transport=transport)
    payload = client.bs_to_ad(2083, 1, 1)

    assert payload["gregorian"] == "2026-04-14"
    assert calls[0][0] == "POST"
    assert calls[0][1] == f"{DEFAULT_API_BASE}/calendar/bs-to-gregorian"
    assert calls[0][3] == {"year": 2083, "month": 1, "day": 1}
    assert calls[0][4] == 10.0


def test_base_url_override_and_timeout_are_passed_to_transport() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {"english": "2026-04-14"}

    client = ParvaClient(
        base_url="https://calendar.example/v3/api/",
        timeout=2.5,
        transport=transport,
    )
    payload = client.ad_to_bs("2026-04-14")

    assert payload["english"] == "2026-04-14"
    assert calls == [
        (
            "GET",
            "https://calendar.example/v3/api/calendar/convert?date=2026-04-14",
            None,
            None,
            2.5,
        )
    ]


def test_future_capabilities_uses_public_v4_endpoint() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {
            "surface": "future_bs_risk_research",
            "publication_status": "computed_prediction_not_official",
        }

    client = ParvaClient(transport=transport)
    payload = client.get_future_bs_capabilities()

    assert payload["publication_status"] == "computed_prediction_not_official"
    assert calls[0][1] == DEFAULT_FUTURE_BS_CAPABILITIES_URL


def test_validate_bs_date_returns_false_for_public_400() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        raise ParvaAPIError("Invalid BS date", status=400, body={"detail": "Invalid BS date"})

    client = ParvaClient(transport=transport)
    payload = client.validate_bs_date(2083, 1, 32)

    assert payload["valid"] is False
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert len(calls) == 1


def test_client_does_not_expose_private_or_research_exact_routes() -> None:
    method_names = {name for name in dir(ParvaClient) if not name.startswith("_")}
    forbidden_fragments = {
        "admin",
        "audit_private",
        "backtest",
        "billing",
        "loan_impact",
        "month_length_prediction",
        "private_source",
        "research_backtest",
    }

    exposed = sorted(
        name
        for name in method_names
        for fragment in forbidden_fragments
        if fragment in name
    )

    assert exposed == []


def test_retries_retry_after_for_429() -> None:
    calls = []
    sleeps = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        if len(calls) == 1:
            raise ParvaAPIError(
                "rate limited",
                status=429,
                body={"detail": "slow down"},
                headers={"Retry-After": "0.5"},
            )
        return {"gregorian": "2026-04-14"}

    client = ParvaClient(transport=transport, retry_sleep=sleeps.append)
    payload = client.bs_to_ad(2083, 1, 1)

    assert payload["gregorian"] == "2026-04-14"
    assert len(calls) == 2
    assert sleeps == [0.5]


def test_retries_can_be_disabled() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append(url)
        raise ParvaAPIError("rate limited", status=429, body={"detail": "slow down"})

    client = ParvaClient(transport=transport, max_retries=0)
    with pytest.raises(ParvaAPIError):
        client.bs_to_ad(2083, 1, 1)

    assert len(calls) == 1


def test_public_month_fiscal_business_and_policy_methods() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {"ok": True}

    client = ParvaClient(transport=transport)

    client.get_month_calendar(2026, 4)
    client.get_fiscal_year(2082)
    client.get_bs_months(2082)
    client.get_business_days("2082-01-01", "2082-01-07")
    client.get_enterprise_capabilities()
    client.get_policy()

    assert calls[0][1] == f"{DEFAULT_API_BASE}/calendar/dual-month?year=2026&month=4"
    assert calls[1][1] == f"{DEFAULT_API_BASE}/enterprise/fiscal-year/2082"
    assert calls[2][1] == f"{DEFAULT_API_BASE}/enterprise/bs-months/2082"
    assert calls[3][1] == f"{DEFAULT_API_BASE}/enterprise/business-days"
    assert calls[3][3] == {
        "start_bs": "2082-01-01",
        "end_bs": "2082-01-07",
        "weekend": "saturday",
        "include_start": True,
        "include_end": True,
        "holiday_policy": "none",
    }
    assert calls[4][1] == f"{DEFAULT_API_BASE}/enterprise/capabilities"
    assert calls[5][1] == f"{DEFAULT_API_BASE}/policy"


def test_compliance_profile_and_decision_support_methods() -> None:
    calls = []
    meta = {
        "source": {
            "id": "parva_enterprise_compliance_profiles",
            "label": "Parva enterprise compliance profile definitions",
            "tier": "publisher_reference",
            "authority": "derived_reference_not_legal_authority",
        },
        "confidence": "source_backed",
        "data_version": "parva-public-calendar-v1",
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
        "warnings": ["not_legal_tax_or_banking_contract_authority"],
        "trace_id": "trace",
    }

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {"ok": True, "meta": meta}

    client = ParvaClient(transport=transport)

    client.list_profiles()
    client.get_profile("nepal_private_company_default")
    payload = client.evaluate_date(
        profile_id="nepal_private_company_default",
        bs_date="2082-04-02",
    )
    client.next_working_day(profile_id="nepal_private_company_default", bs_date="2082-04-04")
    client.previous_working_day(profile_id="nepal_private_company_default", bs_date="2082-04-04")
    client.add_working_days(
        profile_id="nepal_private_company_default",
        bs_date="2082-04-02",
        working_days=2,
    )
    client.month_closing_day(profile_id="nepal_private_company_default", bs_year=2082, bs_month=4)
    client.fiscal_period(profile_id="nepal_private_company_default", bs_date="2082-04-02")

    assert calls[0][1] == f"{DEFAULT_API_BASE}/compliance/profiles"
    assert calls[1][1] == f"{DEFAULT_API_BASE}/compliance/profiles/nepal_private_company_default"
    assert calls[2][1] == f"{DEFAULT_API_BASE}/compliance/evaluate-date"
    assert calls[2][0] == "POST"
    assert calls[2][3] == {
        "profile_id": "nepal_private_company_default",
        "bs_date": "2082-04-02",
        "ad_date": None,
        "decision_intent": "general",
    }
    assert calls[3][1] == f"{DEFAULT_API_BASE}/compliance/next-working-day"
    assert calls[4][1] == f"{DEFAULT_API_BASE}/compliance/previous-working-day"
    assert calls[5][1] == f"{DEFAULT_API_BASE}/compliance/add-working-days"
    assert calls[6][1] == f"{DEFAULT_API_BASE}/compliance/month-closing-day"
    assert calls[7][1] == f"{DEFAULT_API_BASE}/compliance/fiscal-period"
    assert payload["meta"] == meta


def test_temporal_trust_helper_methods() -> None:
    calls = []
    packet = {
        "packet_type": "date_conversion",
        "release": {"release_id": "parva-bs-public-demo"},
        "integrity": {
            "packet_hash": "sha256:abc",
            "signature_status": "unsigned_public_preview",
        },
    }

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        if "/evidence/" in url:
            return packet
        return {"ok": True}

    client = ParvaClient(transport=transport)

    client.get_trust_capabilities()
    client.list_sources(release_id="parva-bs-public-demo")
    client.get_source("parva_public_bs_ad_corpus")
    client.list_releases()
    client.get_release("parva-bs-public-demo")
    client.diff_releases("parva-bs-public-demo", "parva-bs-public-demo")
    client.get_trust_log()
    evidence = client.create_date_conversion_evidence(ad_date="2026-04-14")
    client.create_compliance_decision_evidence(
        profile_id="nepal_private_company_default",
        bs_date="2082-04-02",
    )

    assert calls[0][1] == f"{DEFAULT_API_BASE}/trust/capabilities"
    assert calls[1][1] == f"{DEFAULT_API_BASE}/trust/sources?release_id=parva-bs-public-demo"
    assert calls[2][1] == f"{DEFAULT_API_BASE}/trust/sources/parva_public_bs_ad_corpus"
    assert calls[3][1] == f"{DEFAULT_API_BASE}/trust/releases"
    assert calls[4][1] == f"{DEFAULT_API_BASE}/trust/releases/parva-bs-public-demo"
    assert calls[5][1] == (
        f"{DEFAULT_API_BASE}/trust/releases/parva-bs-public-demo/diff/parva-bs-public-demo"
    )
    assert calls[6][1] == f"{DEFAULT_API_BASE}/trust/log"
    assert calls[7][1] == f"{DEFAULT_API_BASE}/trust/evidence/date-conversion"
    assert calls[7][0] == "POST"
    assert calls[7][3] == {"ad_date": "2026-04-14", "bs_date": None, "release_id": None}
    assert calls[8][1] == f"{DEFAULT_API_BASE}/trust/evidence/compliance-decision"
    assert evidence["integrity"]["packet_hash"] == "sha256:abc"


def test_timegraph_helper_methods() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {
            "items": [],
            "fact": {"fact_id": "fact_bs_ad_2083_01_01"},
            "trace": {"fact": {"fact_id": "fact_bs_ad_2083_01_01"}},
            "meta": {"claim_boundary": "timegraph_query_not_legal_authority"},
        }

    client = ParvaClient(transport=transport)

    client.get_timegraph_capabilities()
    client.list_facts(fact_type="bs_ad_mapping", limit=5, has_conflicts=False)
    client.get_fact("fact_bs_ad_2083_01_01")
    client.query_facts(calendar="BS", date="2083-01-01")
    client.get_facts_for_date("BS", "2083-01-01", limit=3)
    client.get_facts_for_source("parva_public_bs_ad_corpus")
    client.get_facts_for_release("parva-bs-public-demo", limit=2)
    client.get_facts_for_profile("nepal_private_company_default")
    client.get_relationships("fact_bs_ad_2083_01_01")
    client.trace_fact("fact_bs_ad_2083_01_01", depth=2)
    client.list_conflicts()

    assert calls[0][1] == f"{DEFAULT_API_BASE}/timegraph/capabilities"
    assert calls[1][1] == (
        f"{DEFAULT_API_BASE}/timegraph/facts?"
        "fact_type=bs_ad_mapping&has_conflicts=false&limit=5"
    )
    assert calls[2][1] == f"{DEFAULT_API_BASE}/timegraph/facts/fact_bs_ad_2083_01_01"
    assert calls[3][1] == f"{DEFAULT_API_BASE}/timegraph/query"
    assert calls[3][0] == "POST"
    assert calls[3][3] == {"calendar": "BS", "date": "2083-01-01"}
    assert calls[4][1] == f"{DEFAULT_API_BASE}/timegraph/date/BS/2083-01-01?limit=3"
    assert calls[5][1] == f"{DEFAULT_API_BASE}/timegraph/sources/parva_public_bs_ad_corpus/facts"
    assert calls[6][1] == f"{DEFAULT_API_BASE}/timegraph/releases/parva-bs-public-demo/facts?limit=2"
    assert calls[7][1] == (
        f"{DEFAULT_API_BASE}/timegraph/profiles/nepal_private_company_default/facts"
    )
    assert calls[8][1] == (
        f"{DEFAULT_API_BASE}/timegraph/entities/fact_bs_ad_2083_01_01/relationships"
    )
    assert calls[9][1] == (
        f"{DEFAULT_API_BASE}/timegraph/facts/fact_bs_ad_2083_01_01/trace?depth=2"
    )
    assert calls[10][1] == f"{DEFAULT_API_BASE}/timegraph/conflicts"


def test_rulelang_helper_methods() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {
            "rule_id": "last_working_day_of_nepali_month",
            "decision": {"status": "approved", "reason_codes": ["RULE_VALIDATED"]},
            "trace": {"steps": []},
        }

    client = ParvaClient(transport=transport)

    client.get_rule_capabilities()
    client.list_rules()
    client.get_rule("last_working_day_of_nepali_month")
    client.validate_rule({"rule_id": "demo_rule"})
    client.evaluate_rule(
        "last_working_day_of_nepali_month",
        input_payload={"bs_month": "2082-04"},
    )
    client.test_rule("last_working_day_of_nepali_month")
    client.evaluate_custom_rule(rule={"rule_id": "demo_rule"}, input_payload={"bs_date": "2082-04-02"})
    client.explain_rule(
        rule_id="last_working_day_of_nepali_month",
        input_payload={"bs_month": "2082-04"},
    )

    assert calls[0][1] == f"{DEFAULT_API_BASE}/rules/capabilities"
    assert calls[1][1] == f"{DEFAULT_API_BASE}/rules"
    assert calls[2][1] == f"{DEFAULT_API_BASE}/rules/last_working_day_of_nepali_month"
    assert calls[3][1] == f"{DEFAULT_API_BASE}/rules/validate"
    assert calls[3][0] == "POST"
    assert calls[3][3] == {"rule": {"rule_id": "demo_rule"}}
    assert calls[4][1] == f"{DEFAULT_API_BASE}/rules/last_working_day_of_nepali_month/evaluate"
    assert calls[4][3] == {
        "input": {"bs_month": "2082-04"},
        "release_id": None,
        "include_evidence": False,
    }
    assert calls[5][1] == f"{DEFAULT_API_BASE}/rules/last_working_day_of_nepali_month/test"
    assert calls[6][1] == f"{DEFAULT_API_BASE}/rules/evaluate"
    assert calls[7][1] == f"{DEFAULT_API_BASE}/rules/explain"


def test_impact_agent_and_protocol_helper_methods() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {"ok": True}

    client = ParvaClient(transport=transport)

    client.get_impact_capabilities()
    client.diff_releases_for_impact()
    client.simulate_change_set({"changes": []})
    client.simulate_release_diff()
    client.get_impact_run("impact_run_demo")
    client.list_impact_reason_codes()
    client.list_impact_recommended_actions()
    client.get_impact_event_schema()
    client.get_agent_capabilities()
    client.list_agent_tools()
    client.get_agent_manifest()
    client.resolve_temporal_intent("2083-01-01 BS maps to 2026-04-14 AD.")
    client.verify_temporal_claim("2083-01-01 BS maps to 2026-04-14 AD.")
    client.plan_schedule(schedule_type="payroll", bs_year=2082, months=[4])
    client.explain_temporal_decision(explanation_type="claim", payload={"claim": "demo"})
    client.check_human_review({"requires_human_review": True})
    client.draft_rule("move payroll to next working day")
    client.run_agent_tool("parva.get_capabilities")
    client.get_protocol_version()
    client.get_protocol_capabilities()
    client.list_protocol_specs()
    client.list_protocol_schemas()
    client.list_protocol_compatibility_levels()
    client.run_conformance()
    client.issue_calendar_credential(
        subject={"type": "date_conversion"},
        claims={"bs_date": "2083-01-01", "ad_date": "2026-04-14"},
    )
    client.verify_calendar_credential({"credential_id": "demo"})
    client.get_calendar_credential_schema()
    client.get_offline_bundle_manifest()

    assert calls[0][1] == f"{DEFAULT_API_BASE}/impact/capabilities"
    assert calls[1][1] == f"{DEFAULT_API_BASE}/impact/diff-releases"
    assert calls[1][3] == {
        "from_release_id": "parva-bs-public-demo",
        "to_release_id": "parva-bs-public-demo",
    }
    assert calls[2][1] == f"{DEFAULT_API_BASE}/impact/simulate-change-set"
    assert calls[2][3] == {"change_set": {"changes": []}}
    assert calls[3][1] == f"{DEFAULT_API_BASE}/impact/simulate-release-diff"
    assert calls[4][1] == f"{DEFAULT_API_BASE}/impact/runs/impact_run_demo"
    assert calls[8][1] == f"{DEFAULT_API_BASE}/agent/capabilities"
    assert calls[11][1] == f"{DEFAULT_API_BASE}/agent/resolve-intent"
    assert calls[13][3]["schedule_type"] == "payroll"
    assert calls[17][3] == {"tool_name": "parva.get_capabilities", "input": {}}
    assert calls[18][1] == f"{DEFAULT_API_BASE}/protocol/version"
    assert calls[23][1] == f"{DEFAULT_API_BASE}/protocol/conformance/run"
    assert calls[24][1] == f"{DEFAULT_API_BASE}/protocol/credentials/issue"
    assert calls[25][1] == f"{DEFAULT_API_BASE}/protocol/credentials/verify"
    assert calls[27][1] == f"{DEFAULT_API_BASE}/protocol/offline-bundle/manifest"


def test_error_extraction_prefers_public_error_envelope() -> None:
    from parva.client import _extract_detail

    payload = {
        "detail": "legacy",
        "error": {
            "code": "BAD_REQUEST",
            "message": "Use YYYY-MM-DD",
            "details": {},
            "trace_id": "test",
        },
    }

    assert _extract_detail(payload) == "Use YYYY-MM-DD"


def test_client_preserves_source_aware_metadata() -> None:
    meta = {
        "source": {
            "id": "parva_public_bs_ad_corpus",
            "label": "Parva public BS/AD corpus",
            "tier": "software_table_reference",
            "authority": "derived_reference_not_legal_authority",
            "version": "parva-public-calendar-v1",
        },
        "confidence": "source_backed",
        "data_version": "parva-public-calendar-v1",
        "claim_boundary": "public_corpus_reference_only",
        "warnings": ["not_legal_tax_or_banking_contract_authority"],
        "trace_id": "trace",
        "result_class": "ad_to_bs_conversion",
    }

    def transport(method, url, params, json_body, timeout):
        return {"gregorian": "2026-04-14", "meta": meta}

    client = ParvaClient(transport=transport)
    payload = client.ad_to_bs("2026-04-14")

    assert payload["meta"] == meta


def test_core_methods_expose_proof_modes() -> None:
    calls = []

    def transport(method, url, params, json_body, timeout):
        calls.append((method, url, params, json_body, timeout))
        return {"proof": {"mode": "membrane", "capsule": {"kind": "parva_membrane"}}}

    client = ParvaClient(transport=transport)

    client.ad_to_bs("2025-04-14", proof="membrane")
    client.bs_to_ad(2082, 1, 1, proof="membrane")
    client.validate_bs_date(2082, 1, 1, proof="membrane")
    client.check_holiday(bs_date="2082-01-01", proof="membrane")
    client.evaluate_date(bs_date="2082-01-01", proof="membrane")
    client.get_fiscal_year(2082, proof="membrane")
    client.get_bs_months(2082, mode="compare", proof="membrane")
    client.get_panchanga(
        "2025-04-14",
        proof="replay",
        latitude=27.7172,
        longitude=85.324,
        ephemeris_provider="pinned_panchanga_fixture",
        ephemeris_fixture_id="kathmandu_2025_04_14_lahiri",
    )

    assert calls[0][1] == f"{DEFAULT_API_BASE}/calendar/convert?date=2025-04-14&proof=membrane"
    assert calls[1][1] == f"{DEFAULT_API_BASE}/calendar/bs-to-gregorian?proof=membrane"
    assert calls[2][1] == (
        f"{DEFAULT_API_BASE}/calendar/validate-bs-date?year=2082&month=1&day=1&proof=membrane"
    )
    assert calls[3][1] == (
        f"{DEFAULT_API_BASE}/compliance/holiday?bs_date=2082-01-01&profile_id=nepal_public_general&proof=membrane"
    )
    assert calls[4][1] == f"{DEFAULT_API_BASE}/compliance/evaluate-date?proof=membrane"
    assert calls[5][1] == f"{DEFAULT_API_BASE}/enterprise/fiscal-year/2082?proof=membrane"
    assert calls[6][1] == f"{DEFAULT_API_BASE}/enterprise/bs-months/2082?mode=compare&proof=membrane"
    assert calls[7][1].startswith(f"{DEFAULT_API_BASE}/calendar/panchanga?date=2025-04-14&proof=replay")
    assert "ephemeris_provider=pinned_panchanga_fixture" in calls[7][1]


def test_sdk_membrane_structural_verifier_does_not_upgrade_authority() -> None:
    client = ParvaClient(transport=lambda *_args: {})

    assert client.verify_membrane({"kind": "parva_membrane"})["verified"] is False
    result = client.verify_membrane(
        {
            "kind": "parva_membrane",
            "canonical_query": {"operation": "ad_to_bs"},
            "identity_hash": "parva:id:v1:sha256:abc",
            "result": {"bs_date": "2082-01-01"},
            "boundary": {"claim_boundary": "decision_support_not_authority"},
            "field_provenance": {"bs_date": {"authority": "static_reference"}},
            "witness_hash": "parva:wit:v1:sha256:def",
        }
    )

    assert result == {
        "verified": True,
        "reason": "structural_checks_passed_replay_required_for_full_verification",
    }


def test_sdk_proofpack_timepack_and_panchanga_helpers_are_boundary_preserving() -> None:
    client = ParvaClient(transport=lambda *_args: {})
    membrane = {
        "kind": "parva_membrane",
        "canonical_query": {"operation": "panchanga_summary"},
        "identity_hash": "parva:id:v1:sha256:abc",
        "result": {"tithi": {"name": "Pratipada"}},
        "boundary": {"claim_boundary": "computed_ephemeris_not_panchanga_authority"},
        "field_provenance": {"tithi": {"authority": "computed_uncertified"}},
        "witness_hash": "parva:wit:v1:sha256:def",
        "ephemeris_metadata": {"provider_id": "pinned_panchanga_fixture", "provider_kind": "pinned_fixture"},
    }

    assert client.verify_proofpack({"level": "audit", "membrane": membrane})["verified"] is True
    assert client.verify_timepack(
        {
            "kind": "parva_timepack",
            "proof_packs": [{"level": "audit", "membrane": membrane}],
            "boundary_summary": {"not_authority": True},
        }
    )["verified"] is True
    assert client.replay_panchanga_membrane(membrane)["verified"] is True


def test_non_validation_errors_are_not_hidden() -> None:
    def transport(method, url, params, json_body, timeout):
        raise ParvaAPIError("server unavailable", status=503)

    client = ParvaClient(transport=transport)
    with pytest.raises(ParvaAPIError):
        client.validate_bs_date(2083, 1, 1)
