---
status: public-beta
tier: 1
lane: dx
last_verified: 2026-05-14
owner: dx-team
---

# API Quickstart

Status: public integration quickstart.

Project Parva's stable public-beta API lives under `/v3/api/*`.

The lightweight public demo may expose a narrower subset for evaluation. Private or full deployments can enable the broader stable API surface with controlled configuration.

Base URL (deployment example):

```text
https://api.prabinghimire1.com.np/v3/api
```

## What is stable now

- Calendar today, AD to BS conversion, BS to AD conversion, and BS date validation through conversion
- Month calendar and BS month metadata helpers
- Fiscal-year and weekend-only business-day helpers
- Compliance-profile decision support helpers in full/private deployments
- TimeGraph fact, relationship, trace, and conflict helpers where enabled
- RuleLang structured temporal rule helpers where enabled
- Impact simulator helpers where enabled
- Agent-safe deterministic temporal tools where enabled
- Parva Protocol preview helpers where enabled
- Read-only calendar and festival endpoints
- POST-first personal compute flows for location-sensitive requests
- Integration metadata such as `calculation_trace_id`, `method`, `quality_band`, `provenance`, `policy`, and request tracing on errors

## Start the stack

```bash
python3.11 -m pip install -e .[test,dev]
uvicorn app.main:app --app-dir backend --reload --port 8000
```

## 1. Calendar today

```bash
curl https://api.prabinghimire1.com.np/v3/api/calendar/today
```

## 2. Gregorian to Bikram Sambat conversion

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2026-10-21"
```

## 3. Bikram Sambat to Gregorian conversion

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/calendar/bs-to-gregorian \
  -H "Content-Type: application/json" \
  -d '{"year":2083,"month":1,"day":1}'
```

If the BS date is invalid, the endpoint returns a 400 response with a structured error envelope. SDK validation helpers use this route.

## 4. Month calendar

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/dual-month?year=2026&month=4"
```

## 5. Fiscal-year boundaries

```bash
curl https://api.prabinghimire1.com.np/v3/api/enterprise/fiscal-year/2082
```

## 6. BS month metadata

```bash
curl https://api.prabinghimire1.com.np/v3/api/enterprise/bs-months/2082
```

By default this uses the solar-civil sankranti computation path and returns
`calculation_mode: "solar_civil"`. Static table lookup is retained only as an
explicit compatibility/reference mode:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/enterprise/bs-months/2082?mode=static_lookup"
```

## 7. Business days

This helper counts business days with a weekend rule. Holiday exclusion is disabled unless a private deployment configures a holiday policy.

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/enterprise/business-days \
  -H "Content-Type: application/json" \
  -d '{"start_bs":"2082-01-01","end_bs":"2082-01-07","weekend":"saturday"}'
```

## 8. Compliance profile evaluation

Full and private deployments expose enterprise compliance-preview endpoints. The lightweight public demo may exclude them.

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/compliance/evaluate-date \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"nepal_private_company_default","bs_date":"2082-04-02"}'
```

Compliance responses include `decision.reason_codes`, `decision.requires_human_review`, and source-aware `meta`. They are decision support, not legal or payroll authority.

## 9. Trust and evidence packets

```bash
curl https://api.prabinghimire1.com.np/v3/api/trust/capabilities
```

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/trust/evidence/date-conversion \
  -H "Content-Type: application/json" \
  -d '{"ad_date":"2026-04-14"}'
```

Evidence packets include release id, source records, confidence, warnings, trace id, and packet hash. They are audit explanations, not legal certificates.

## 10. TimeGraph fact trace

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/capabilities
```

```bash
curl "https://api.prabinghimire1.com.np/v3/api/timegraph/facts/fact_bs_ad_2083_01_01/trace?depth=2"
```

TimeGraph links temporal facts to sources, releases, profiles, evidence packets, relationships, and conflicts. It is audit support, not legal or government authority.

## 11. RuleLang structured rules

```bash
curl https://api.prabinghimire1.com.np/v3/api/rules/capabilities
```

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/rules/last_working_day_of_nepali_month/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input":{"bs_month":"2082-04","profile_id":"nepal_private_company_default"}}'
```

RuleLang responses include decision status, reason codes, trace steps, fact ids, confidence, warnings, and claim boundary. They are decision support, not legal or payroll final authority.

## 12. Impact simulation

```bash
curl https://api.prabinghimire1.com.np/v3/api/impact/capabilities
```

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/impact/simulate-change-set \
  -H "Content-Type: application/json" \
  -d '{"change_set":{"changes":[]}}'
```

Impact reports are bounded decision-support artifacts. They explain affected dependency classes, severity, reason codes, and recommended review actions without exposing private future-BS vectors.

## 13. Agent-safe temporal tools

```bash
curl https://api.prabinghimire1.com.np/v3/api/agent/tools
```

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/agent/verify-claim \
  -H "Content-Type: application/json" \
  -d '{"claim":"2083-01-01 BS maps to 2026-04-14 AD."}'
```

Agent tools are deterministic public tools with reason codes, confidence, evidence identifiers, and human-review gates. They are not generic chatbot authority.

## 14. Parva Protocol preview

```bash
curl https://api.prabinghimire1.com.np/v3/api/protocol/version
```

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/protocol/conformance/run \
  -H "Content-Type: application/json" \
  -d '{"target":"local","level":"parva_core"}'
```

Protocol preview endpoints expose public schemas, compatibility levels, conformance metadata, hash-only credentials, and offline bundle manifests.

## 15. Policy metadata

```bash
curl https://api.prabinghimire1.com.np/v3/api/policy
```

## 16. Personal Panchanga with POST JSON

Privacy-sensitive inputs should use POST bodies instead of query strings.

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/personal/panchanga ^
  -H "Content-Type: application/json" ^
  -d "{\"date\":\"2026-10-21\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\"}"
```

## 17. Muhurta heatmap

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/muhurta/heatmap ^
  -H "Content-Type: application/json" ^
  -d "{\"date\":\"2026-10-21\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\",\"type\":\"travel\",\"assumption_set\":\"np-mainstream-v2\"}"
```

## 18. Kundali

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/kundali ^
  -H "Content-Type: application/json" ^
  -d "{\"datetime\":\"2026-02-15T06:30:00+05:45\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\"}"
```

## 19. Upcoming festivals

```bash
curl "https://api.prabinghimire1.com.np/v3/api/festivals/upcoming?days=30&quality_band=computed"
```

## JavaScript SDK example

```js
import { ParvaClient } from "@project-parva/parva-js";

const client = new ParvaClient();

const today = await client.getToday();
const adToBs = await client.adToBs("2026-04-14");
const bsToAd = await client.bsToAd({ year: 2083, month: 1, day: 1 });
const month = await client.getMonthCalendar(2026, 4);
const fiscalYear = await client.getFiscalYear(2082);
const compliance = await client.evaluateDate({
  profile_id: "nepal_private_company_default",
  bs_date: "2082-04-02",
});
const trust = await client.getTrustCapabilities();
const evidence = await client.createDateConversionEvidence({ ad_date: "2026-04-14" });
const timegraph = await client.traceFact("fact_bs_ad_2083_01_01");
const rule = await client.evaluateRule("last_working_day_of_nepali_month", {
  input: { bs_month: "2082-04", profile_id: "nepal_private_company_default" },
});
const impact = await client.simulateChangeSet({ changes: [] });
const claim = await client.verifyTemporalClaim({
  claim: "2083-01-01 BS maps to 2026-04-14 AD.",
});
const protocol = await client.getProtocolVersion();
const policy = await client.getPolicy();

console.log(today.gregorian);
console.log(adToBs.bikram_sambat);
console.log(bsToAd.gregorian);
console.log(month.days.length);
console.log(fiscalYear.fiscal_year);
console.log(compliance.decision.reason_codes);
console.log(trust.active_release_id);
console.log(evidence.integrity.packet_hash);
console.log(timegraph.trace.fact.fact_id);
console.log(rule.decision.reason_codes);
console.log(impact.status);
console.log(claim.status);
console.log(protocol.protocol_version);
console.log(policy.policy.publication_status);
```

## Future-BS capabilities summary

The public future-BS route returns capability metadata only. It does not return direct future month lengths or private audit outputs.

```bash
curl https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Future-BS research outputs are labeled:

```text
computed_prediction_not_official
```

## Python SDK example

```python
from parva import ParvaClient

client = ParvaClient("https://api.prabinghimire1.com.np/v3/api")

today = client.get_today()
ad_to_bs = client.ad_to_bs("2026-04-14")
bs_to_ad = client.bs_to_ad(2083, 1, 1)
validation = client.validate_bs_date(2083, 1, 32)
month = client.get_month_calendar(2026, 4)
fiscal_year = client.get_fiscal_year(2082)
business_days = client.get_business_days("2082-01-01", "2082-01-07")
compliance = client.evaluate_date(
    profile_id="nepal_private_company_default",
    bs_date="2082-04-02",
)
trust = client.get_trust_capabilities()
evidence = client.create_date_conversion_evidence(ad_date="2026-04-14")
timegraph = client.trace_fact("fact_bs_ad_2083_01_01")
rule = client.evaluate_rule(
    "last_working_day_of_nepali_month",
    input_payload={
        "bs_month": "2082-04",
        "profile_id": "nepal_private_company_default",
    },
)
impact = client.simulate_change_set({"changes": []})
claim = client.verify_temporal_claim("2083-01-01 BS maps to 2026-04-14 AD.")
protocol = client.get_protocol_version()
policy = client.get_policy()
future_bs_capabilities = client.get_future_bs_capabilities()

print(today["gregorian"])
print(month["days"][0]["gregorian"]["iso"])
print(fiscal_year["fiscal_year"])
print(business_days["business_days"])
print(compliance["decision"]["reason_codes"])
print(trust["active_release_id"])
print(evidence["integrity"]["packet_hash"])
print(timegraph["trace"]["fact"]["fact_id"])
print(rule["decision"]["reason_codes"])
print(impact["status"])
print(claim["status"])
print(protocol["protocol_version"])
print(policy["policy"]["publication_status"])
print(future_bs_capabilities["publication_status"])
```

## Error format

User input errors return the legacy `detail` field and a structured `error` object:

```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD",
  "request_id": "trace-id",
  "version": "3.0.0",
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid date format. Use YYYY-MM-DD",
    "details": {},
    "trace_id": "trace-id"
  }
}
```

Preserve `request_id` or `error.trace_id` in logs so support can correlate failures.

## Metadata to preserve

For integrations that store or forward Parva output, keep these fields:

- `meta.source`
- `meta.confidence`
- `meta.data_version`
- `meta.claim_boundary`
- `meta.warnings`
- `meta.trace_id`
- `calculation_trace_id`
- `method`
- `method_profile`
- `quality_band`
- `assumption_set_id`
- `provenance`
- `policy`

The `meta` object is the source-aware contract. It distinguishes official-source-backed, public-corpus, calculated, fixture, research-preview, disputed, unsupported, and unknown claim postures. Do not strip it when storing API responses.

## Operational notes

- Personal compute responses are served with `Cache-Control: no-store`.
- If you need a drop-in website integration, see `docs/EMBED_GUIDE.md`.
- For local development, point the same `/v3/api` path at your local backend instead of the deployment example above.
