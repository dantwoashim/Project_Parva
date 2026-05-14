---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# RuleLang Examples

Examples use public historical or synthetic-safe values.

## Last Working Day of a BS Month

```json
{
  "input": {
    "bs_month": "2082-04",
    "profile_id": "nepal_private_company_default"
  }
}
```

Call:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/rules/last_working_day_of_nepali_month/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input":{"bs_month":"2082-04","profile_id":"nepal_private_company_default"}}'
```

The result includes a working-day date block, decision status, reason codes, trace steps, and fact ids.

## Move Payroll Backward

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/rules/payroll_previous_working_day_if_non_working/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input":{"bs_date":"2082-04-04","profile_id":"nepal_private_company_default"}}'
```

This rule demonstrates a bounded `while` loop. It moves backward until `is_working_day` returns true or the loop limit is reached.

## Explain a Rule

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/rules/explain \
  -H "Content-Type: application/json" \
  -d '{"rule_id":"last_working_day_of_nepali_month","input":{"bs_month":"2082-04","profile_id":"nepal_private_company_default"}}'
```

The explanation includes a bounded trace and claim boundary.

## Evidence Packet

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/trust/evidence/rule-execution \
  -H "Content-Type: application/json" \
  -d '{"rule_id":"last_working_day_of_nepali_month","input":{"bs_month":"2082-04","profile_id":"nepal_private_company_default"}}'
```

The packet includes rule id, version, input, output, trace summary, fact ids, release metadata, confidence, and a packet hash.
