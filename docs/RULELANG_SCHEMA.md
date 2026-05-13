# RuleLang Schema

RuleLang uses structured JSON rule files.

Each rule must include:

- `rule_id`
- `version`
- `label`
- `description`
- `status`
- `inputs`
- `outputs`
- `steps`
- `risk_policy`
- `claim_boundary`

Optional fields include:

- `profile_id`
- `tests`
- `tags`
- `owner`

## Rule Status

Supported statuses:

- `public_preview`
- `enterprise_preview`
- `active`
- `deprecated`
- `private`
- `fixture_only`

Private rules are not loaded in public mode.

## Input Types

Supported input types:

- `bs_date`
- `ad_date`
- `date`
- `bs_month`
- `ad_month`
- `profile_id`
- `integer`
- `string`
- `boolean`
- `enum`

Inputs are validated before execution. Invalid inputs return structured errors.

## Step Types

Supported step types:

- `set`
- `if`
- `while`
- `return`
- `call`

Each `while` step must define `max_iterations`.

## Operators

Supported operators:

- `and`
- `or`
- `not`
- `equals`
- `not_equals`
- `greater_than`
- `less_than`
- `greater_or_equal`
- `less_or_equal`
- `in`
- `not_in`

## Variables

Supported variable references:

- `$input.<name>`
- `$var.<name>`
- `$rule.<field>`

No other dynamic lookup is allowed.

## Risk Policy

Example:

```json
{
  "require_confidence_at_least": "source_backed",
  "block_research_preview": true,
  "block_disputed_facts": true,
  "unsupported_result_action": "human_review_required",
  "future_date_action": "human_review_required"
}
```

The JSON schema is available at `schemas/rulelang-rule.schema.json`.
