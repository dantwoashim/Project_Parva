# Phase 01 Canonical Runtime Discovery



This is a draft discovery map for Phase 03. It is not a migration.



| Subsystem | Current maturity | Public exposure | Route profiles | Canonical candidate | Primary risks |
| --- | --- | --- | --- | --- | --- |
| Core Calendar | stable | true | public_demo, public_reference, developer_preview | backend/app/calendar/routes.py; backend/app/calendar/bikram_sambat.py | future estimated fallback policy requires ongoing public boundary checks |
| Panchanga | public_preview | partial | public_reference, developer_preview | backend/app/calendar/panchanga.py | CPU-heavy calculations must be bounded or precomputed in later phases |
| Tithi | public_preview | partial | public_reference, developer_preview | backend/app/calendar/tithi/ | parallel module/package naming causes canonical-runtime ambiguity |
| Nakshatra/Yoga/Karana | public_preview | partial | public_reference, developer_preview | backend/app/calendar/panchanga.py | authority-sensitive interpretation needs clear claim boundary |
| Festivals/Observances | public_preview | true | public_demo, public_reference, developer_preview | backend/app/rules/service.py; backend/app/rules/catalog_v4.py | legacy naming and multiple calculators obscure source of truth |
| Holidays | public_preview | true | public_reference, developer_preview | backend/app/api/festival_routes.py; backend/app/calendar/routes.py | official release ingestion workflow is not fully matured |
| Fiscal/Working Day | stable | true | public_demo, public_reference, developer_preview | backend/app/api/enterprise_routes.py | institution-specific policies need explicit profile separation |
| RuleLang | developer_preview | partial | public_demo, developer_preview, enterprise_preview | backend/app/services/rulelang_service.py | trace privacy and human-review policy need deeper hardening |
| Trust/Provenance | public_preview | true | public_demo, public_reference, developer_preview | backend/app/services/trust_infrastructure_service.py | deterministic regeneration from fresh clone remains a release gate |
| Source Registry | public_preview | true | public_reference, developer_preview | data/public/source_registry | private source inventory must stay out of public artifacts |
| Release Manifests | public_preview | true | public_reference, developer_preview | data/public/releases | hash drift must fail CI |
| Evidence Packets | public_preview | partial | public_reference, developer_preview | backend/app/services/trust_infrastructure_service.py | must not leak private source paths |
| Transparency Logs | hash-only preview | partial | developer_preview, enterprise_preview | data/transparency; trust service | unsigned preview must not look like third-party certification |
| Offline Bundles | public_preview | true | public_reference, developer_preview | scripts/parva_offline_bundle.py | bundle integrity must not depend on local private data |
| TimeGraph | developer_preview | partial | public_demo, developer_preview, enterprise_preview | backend/app/services/timegraph_service.py | currently public-artifact/in-memory oriented |
| Impact Simulator | developer_preview | partial | developer_preview, enterprise_preview | backend/app/services/impact_service.py | sample dependency extraction is not production-grade |
| Agent Tools | developer_preview | partial | developer_preview, enterprise_preview | backend/app/api/agent_routes.py | unsupported operational claims must require human review |
| Parva Protocol | protocol_draft | true | public_reference, developer_preview | schemas/parva-protocol; specs/parva-protocol | must not be described as a standard before external implementation |
| Conformance | protocol_draft | true | public_reference, developer_preview | scripts/parva_conformance.py | suite must reject invalid fixtures meaningfully |
| Credentials | protocol_draft | partial | public_reference, developer_preview | schemas/parva-protocol/calendar-credential.schema.json | must not imply third-party or government certification |
| Future-BS Research | research_private | metadata_only | public_reference capabilities, private experimental routes | backend/app/future_bs; backend/app/api/future_bs_routes.py | exact future predictions must remain gated and labeled computed_prediction_not_official |
| Kundali | public_preview | partial | developer_preview, enterprise_preview | backend/app/api/kundali_routes.py | authority-sensitive and CPU-heavy outputs need gating |
| Muhurta | public_preview | partial | public_reference, developer_preview | backend/app/api/muhurta_routes.py | must preserve review gates for sensitive decisions |
| Frontend | public_preview | true | public_demo | frontend/src/redesign/ParvaRedesign.jsx | large component surface and route capability complexity |
| Embeds | public_preview | partial | public_demo | frontend and docs embeds | must not hardcode private routes or exact future values |
| Python SDK | public_preview | true | public_reference | packages/parva-python | legacy SDK path may confuse canonical client story |
| JS/TS SDK | public_preview | true | public_reference | packages/parva-js | OpenAPI drift and retry behavior need continuous tests |
| CLI/scripts | public_preview | partial | local | scripts/ | scripts must clearly separate public, private, and research lanes |
| Billing/API keys | enterprise_preview | partial | enterprise_preview | backend/app/billing | manual activation/idempotency and store production posture need audit |
| CI/SRE | public_preview | true | ci | .github/workflows; scripts/release/verify_public.py | verification breadth and performance budgets still need maturity lanes |
| Docs | public_preview | true | docs | docs/README.md | historical docs can conflict with current maturity labels |
