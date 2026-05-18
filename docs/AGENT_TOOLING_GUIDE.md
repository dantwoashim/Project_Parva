# Agent Tooling Guide

Project Parva gives software agents deterministic Nepali temporal tools. Agents should
use these tools instead of guessing Bikram Sambat dates, Panchanga signals,
holidays, fiscal years, or payroll-relevant dates.

## Recommended Agent Flow

1. Normalize the user request into a date/time operation.
2. Call a stable Parva API, SDK method, MCP tool, or local-kernel verifier.
3. Preserve the response metadata.
4. Surface `review_required`, `claim_boundary`, `not_authority`, and provenance.
5. Ask for human review for sensitive or unsupported decisions.

## Safe Operations

- BS to AD conversion
- AD to BS conversion
- date validation
- holiday check
- working-day check
- fiscal-year lookup
- BS month metadata
- Panchanga summary with proof metadata
- temporal claim checking

## Proof Mode

For sensitive answers, request proof:

```text
proof=replay
```

The response may include a membrane capsule, proof pack, boundary vector,
field-level provenance, source or method dockets, and replay metadata.

## Agent Boundaries

Agents must not say Parva is government, legal, tax, payroll, banking,
religious, ritual, official future-date, or official Panchanga authority.

Agents must not publish exact unsupported Future-BS predictions as settled
truth. They must keep review-required and non-authority language visible.
