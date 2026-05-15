# Parva MCP Server

This package is a thin, optional, read-only MCP adapter manifest for Project
Parva public temporal capabilities.

It is not the core runtime. It does not call private Future-BS prediction,
private source audit, admin, billing, trust mutation, shell execution, or
filesystem write surfaces.

Resources:

- `parva://capabilities`
- `parva://route-maturity`
- `parva://source-policy`
- `parva://supported-ranges`
- `parva://known-limitations`
- `parva://benchmark-summary`

Tools:

- `convert_bs_to_ad`
- `convert_ad_to_bs`
- `get_nepali_today`
- `check_holiday`
- `check_working_day`
- `get_fiscal_year`
- `get_festival_date`
- `get_panchanga_summary`
- `check_temporal_claim`

Prompts:

- `explain_nepali_date_safely`
- `check_claim_with_sources`
- `plan_schedule_with_review_gates`

Parva MCP is decision support only. It is not official government, legal, tax,
banking, payroll, future-date, or religious authority.
