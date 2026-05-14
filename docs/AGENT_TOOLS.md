---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Agent Tools

Public preview tools include:

- `parva.get_today`
- `parva.convert_date`
- `parva.validate_date`
- `parva.get_fiscal_period`
- `parva.evaluate_compliance_date`
- `parva.evaluate_rule`
- `parva.explain_rule_execution`
- `parva.generate_evidence_packet`
- `parva.trace_fact`
- `parva.verify_temporal_claim`
- `parva.plan_schedule`
- `parva.simulate_impact`
- `parva.check_human_review_required`
- `parva.get_capabilities`

All tools are allowlisted. The public run-tool endpoint cannot execute arbitrary code or arbitrary routes.

Agent tool responses preserve a top-level `evidence` block with available evidence packet, fact, and source identifiers. Empty evidence arrays mean the public tool did not need or generate a supporting packet for that request.
