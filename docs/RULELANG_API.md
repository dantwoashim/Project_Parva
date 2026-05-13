# RuleLang API

RuleLang endpoints are available under `/v3/api/rules`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v3/api/rules/capabilities` | Public RuleLang safety and capability summary |
| `GET` | `/v3/api/rules` | List public rules |
| `GET` | `/v3/api/rules/{rule_id}` | Get a public rule definition |
| `POST` | `/v3/api/rules/validate` | Validate a structured rule |
| `POST` | `/v3/api/rules/{rule_id}/evaluate` | Evaluate a public rule |
| `POST` | `/v3/api/rules/{rule_id}/test` | Run embedded tests for a public rule |
| `POST` | `/v3/api/rules/evaluate` | Evaluate a public-safe custom rule |
| `POST` | `/v3/api/rules/explain` | Return a decision and explanation trace |

## Evaluate a Rule

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/rules/last_working_day_of_nepali_month/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input":{"bs_month":"2082-04","profile_id":"nepal_private_company_default"}}'
```

Response shape:

```json
{
  "rule_id": "last_working_day_of_nepali_month",
  "rule_version": "1.0.0",
  "profile_id": "nepal_private_company_default",
  "input": {},
  "output": {},
  "decision": {
    "status": "approved",
    "requires_human_review": false,
    "reason_codes": ["RULE_VALIDATED"]
  },
  "trace": {
    "steps": []
  },
  "fact_ids": [],
  "evidence_packet_id": null,
  "release_id": "parva-bs-public-demo",
  "confidence": "source_backed",
  "claim_boundary": "enterprise_decision_support_not_legal_authority",
  "warnings": []
}
```

## Decision Statuses

Rule execution can return:

- `approved`
- `review_required`
- `blocked`
- `unsupported`
- `failed`

An approved result is still decision support, not legal authority.
