# Parva Python SDK Alpha

Public-safe Python SDK for Project Parva calendar APIs.

This alpha package uses the stable public calendar surface and the public future-BS capabilities summary. It does not call private future-BS prediction, export, model-run, backtest, comparison, corrected-value, or schedule-impact endpoints.

## Install

From this repository:

```bash
python -m pip install -e packages/parva-python
```

## Quick Start

```python
from parva import ParvaClient

client = ParvaClient()

today = client.get_today()
ad_to_bs = client.ad_to_bs("2026-04-14")
bs_to_ad = client.bs_to_ad(2083, 1, 1)
validation = client.validate_bs_date(2083, 1, 32)
month = client.get_month_calendar(2026, 4)
fiscal_year = client.get_fiscal_year(2082)
bs_months = client.get_bs_months(2082)
business_days = client.get_business_days("2082-01-01", "2082-01-07")
enterprise = client.get_enterprise_capabilities()
compliance = client.evaluate_date(
    profile_id="nepal_private_company_default",
    bs_date="2082-04-02",
)
trust = client.get_trust_capabilities()
evidence = client.create_date_conversion_evidence(ad_date="2026-04-14")
timegraph = client.get_timegraph_capabilities()
facts = client.get_facts_for_date("BS", "2083-01-01")
trace = client.trace_fact("fact_bs_ad_2083_01_01")
rule = client.evaluate_rule(
    "last_working_day_of_nepali_month",
    input_payload={
        "bs_month": "2082-04",
        "profile_id": "nepal_private_company_default",
    },
)
policy = client.get_policy()
capabilities = client.get_future_bs_capabilities()
```

## Covered Public Surfaces

- current calendar context
- AD to BS conversion
- BS to AD conversion
- BS date validation through conversion
- month calendar
- fiscal-year boundaries
- BS month metadata
- weekend-rule business-day helper
- enterprise capability metadata
- compliance profile listing and decision support helpers
- trust source, release, diff, log, and evidence packet helpers
- TimeGraph fact, relationship, trace, and conflict helpers
- RuleLang registry, validation, execution, test, and explanation helpers
- public policy metadata
- future-BS capabilities summary

## Maturity Policy

| Lane | Python SDK posture |
| --- | --- |
| Stable | Calendar today, AD/BS conversion, BS validation, month calendar, fiscal-year, business-day, and public policy helpers. |
| Public preview | Trust, evidence, TimeGraph, RuleLang, and public capability helpers remain labeled preview. |
| Developer preview | Impact, agent, and advanced decision-support helpers are preview compatibility helpers. |
| Protocol draft | Protocol helpers carry draft status and are not standards certification helpers. |
| Research private | Exact future-BS prediction, export, backtest, residual, model-run, comparison, and schedule-impact routes are not exposed. |
| Deprecated compatibility | The SDK defaults to `/v3/api`, not legacy `/api/*` aliases. |

## TimeGraph

TimeGraph helpers expose public-safe temporal facts and traces. They preserve fact ids,
relationships, source ids, release ids, confidence, warnings, trace ids, and conflict
metadata.

```python
date_facts = client.get_facts_for_date("BS", "2083-01-01", limit=10)
fact = client.get_fact("fact_bs_ad_2083_01_01")
trace = client.trace_fact("fact_bs_ad_2083_01_01", depth=2)
conflicts = client.list_conflicts()
```

TimeGraph responses are audit support and not legal, tax, payroll, banking-contract,
or government authority.

## RuleLang

RuleLang helpers evaluate structured temporal rules with bounded execution, reason
codes, traces, metadata, and fact ids.

```python
rules = client.list_rules()
result = client.evaluate_rule(
    "last_working_day_of_nepali_month",
    input_payload={
        "bs_month": "2082-04",
        "profile_id": "nepal_private_company_default",
    },
)
explanation = client.explain_rule(
    rule_id="last_working_day_of_nepali_month",
    input_payload={
        "bs_month": "2082-04",
        "profile_id": "nepal_private_company_default",
    },
)
```

RuleLang is decision support and not legal, tax, payroll, banking-contract, or
government authority.

## API Base

Default public API base:

```text
https://api.prabinghimire1.com.np/v3/api
```

Future-BS capabilities endpoint:

```text
https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Private deployments can override both values:

```python
client = ParvaClient(
    base_url="https://calendar.example.com/v3/api",
    future_bs_capabilities_url="https://calendar.example.com/v4/api/future-bs/capabilities",
)
```

The default base is the public demo service, not a required production host.
Private deployments should pass their own `base_url`.

## Retry Behavior

The SDK retries `429`, `500`, `502`, `503`, and `504` responses with conservative
backoff. `Retry-After` is honored for `429` responses.

```python
client = ParvaClient(max_retries=2, retry_base_delay=0.25)
```

Set `max_retries=0` to disable retries.

## Claim Boundary

Future-BS capabilities describe a research surface. They are not official calendar publication and must preserve:

```text
computed_prediction_not_official
```
