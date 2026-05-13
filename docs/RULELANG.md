# Parva RuleLang

RuleLang is Project Parva's structured rule format for institutional temporal decisions.

It lets a team describe rules such as payroll dates, school exam shifts, working-day movement, and fiscal-period classification without giving the rule author arbitrary code execution.

RuleLang is designed for:

- deterministic execution
- strict input validation
- bounded loops
- allowlisted temporal functions
- source-confidence policy gates
- human-review decisions when evidence is weak
- explanation traces
- TimeGraph fact references
- evidence packet support

RuleLang is not legal, tax, payroll, banking-contract, or regulatory final authority. Official publications and institution-approved policies override computed decision support.

## Current Public Rules

The public registry lives in `data/rules/public/`.

Current public-preview rules:

| Rule | Purpose |
|---|---|
| `last_working_day_of_nepali_month` | Select the last working day in a BS month |
| `payroll_previous_working_day_if_non_working` | Move a proposed payroll date backward if it is non-working |
| `next_working_day_if_holiday` | Move a date forward when it is not working |
| `fiscal_period_for_date` | Classify a BS date into Nepali fiscal period metadata |
| `add_n_working_days` | Add a bounded number of working days |

## Public API

```bash
curl https://api.prabinghimire1.com.np/v3/api/rules/capabilities
curl https://api.prabinghimire1.com.np/v3/api/rules
curl https://api.prabinghimire1.com.np/v3/api/rules/last_working_day_of_nepali_month
```

Evaluate a public rule:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/rules/last_working_day_of_nepali_month/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input":{"bs_month":"2082-04","profile_id":"nepal_private_company_default"}}'
```

The response includes output, decision status, reason codes, trace, fact ids, confidence, warnings, release id, and claim boundary.

## Safety Model

RuleLang rules are structured JSON. They are not scripts.

Forbidden behavior:

- Python `eval`
- Python `exec`
- shell commands
- arbitrary imports
- filesystem access
- network access
- environment access
- dynamic functions outside the allowlist
- unbounded loops
- private rules in public mode

Every loop has `max_iterations` and the engine enforces absolute limits.

## Related Docs

- `docs/RULELANG_SCHEMA.md`
- `docs/RULELANG_BUILTINS.md`
- `docs/RULELANG_API.md`
- `docs/RULELANG_SECURITY.md`
- `docs/RULELANG_EXAMPLES.md`
- `docs/TIMEGRAPH.md`
- `docs/EVIDENCE_PACKETS.md`
