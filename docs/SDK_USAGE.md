---
status: public-beta
tier: 1
lane: dx
last_verified: 2026-05-14
owner: dx-team
---

# SDK Usage

Project Parva SDKs are alpha developer surfaces for stable public calendar APIs and the public future-BS capabilities summary.

They are intended for teams that want a cleaner integration path than raw HTTP calls while preserving source policy and claim boundaries.

## JavaScript and TypeScript

Install from a package release when available:

```bash
npm install @project-parva/parva-js
```

Local repository development:

```bash
npm --prefix packages/parva-js install
npm --prefix packages/parva-js test
npm --prefix packages/parva-js run build
```

Example:

```ts
import { ParvaClient } from "@project-parva/parva-js";

const parva = new ParvaClient();

const today = await parva.getToday();
const adToBs = await parva.adToBs("2026-04-14");
const bsToAd = await parva.bsToAd({ year: 2083, month: 1, day: 1 });
const validation = await parva.validateBsDate({ year: 2083, month: 1, day: 32 });
const rule = await parva.evaluateRule("last_working_day_of_nepali_month", {
  input: { bs_month: "2082-04", profile_id: "nepal_private_company_default" },
});
const impact = await parva.simulateChangeSet({ changes: [] });
const claim = await parva.verifyTemporalClaim({
  claim: "2083-01-01 BS maps to 2026-04-14 AD.",
});
const protocol = await parva.getProtocolVersion();
const futureBsCapabilities = await parva.getFutureBsCapabilities();
```

## Python

Install from the repository:

```bash
python -m pip install -e packages/parva-python
```

Example:

```python
from parva import ParvaClient

parva = ParvaClient()

today = parva.get_today()
ad_to_bs = parva.ad_to_bs("2026-04-14")
bs_to_ad = parva.bs_to_ad(2083, 1, 1)
validation = parva.validate_bs_date(2083, 1, 32)
rule = parva.evaluate_rule(
    "last_working_day_of_nepali_month",
    input_payload={
        "bs_month": "2082-04",
        "profile_id": "nepal_private_company_default",
    },
)
impact = parva.simulate_change_set({"changes": []})
claim = parva.verify_temporal_claim("2083-01-01 BS maps to 2026-04-14 AD.")
protocol = parva.get_protocol_version()
future_bs_capabilities = parva.get_future_bs_capabilities()
future_bs_methodology = parva.get_future_bs_methodology()
future_bs_forecast = parva.get_future_bs_forecast(2084)
```

## CLI

Run from the repository root:

```bash
python -m pip install -e packages/parva-python
parva --help
parva today
parva convert ad 2026-04-14
parva convert bs 2083-01-01
parva validate-bs 2083-01-32
parva capabilities future-bs
```

The CLI reads `PARVA_API_BASE` when `--base-url` is not provided. It calls the same public SDK client and does not expose private future-BS prediction routes.

RuleLang SDK helpers include:

- `getRuleCapabilities` / `get_rule_capabilities`
- `listRules` / `list_rules`
- `getRule` / `get_rule`
- `validateRule` / `validate_rule`
- `evaluateRule` / `evaluate_rule`
- `testRule` / `test_rule`
- `evaluateCustomRule` / `evaluate_custom_rule`
- `explainRule` / `explain_rule`

Preview SDK helpers include:

- impact simulation: `simulateChangeSet` / `simulate_change_set`
- impact release diff: `simulateReleaseDiff` / `simulate_release_diff`
- agent claim checks: `verifyTemporalClaim` / `verify_temporal_claim`
- agent schedule plans: `planSchedule` / `plan_schedule`
- Parva Protocol version and capabilities: `getProtocolVersion` / `get_protocol_version`
- Parva Protocol conformance: `runConformance` / `run_conformance`
- hash-only preview credentials: `issueCalendarCredential` / `issue_calendar_credential`
- offline bundle manifest: `getOfflineBundleManifest` / `get_offline_bundle_manifest`

## API Base Configuration

Default public API base:

```text
https://api.prabinghimire1.com.np/v3/api
```

Future-BS public endpoint root:

```text
https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Private deployments may override these values, but public SDK examples must stay on stable public surfaces.

## Public and Private Boundary

## Maturity Exposure Policy

The SDK surface is split by maturity lane:

| Lane | SDK posture |
| --- | --- |
| Stable | Top-level calendar, conversion, validation, and policy helpers. |
| Public preview | Top-level compatibility helpers are allowed, but docs must label them as preview. |
| Developer preview | RuleLang, TimeGraph, impact, and agent helpers are preview helpers and may move under explicit preview namespaces in a future major SDK version. |
| Protocol draft | Protocol helpers expose draft metadata only and are not standards certification helpers. |
| Public research preview | Curated capabilities, methodology, and single-year forecast helpers preserve review and publication boundaries. |
| Research private | Bulk predictions, exports, backtests, residuals, model runs, and schedule-impact routes are omitted from public SDKs. |
| Deprecated compatibility | `/api/*` aliases are compatibility-only and should not be used in new SDK examples. |

Public SDK methods in this alpha:

- `getToday` or `get_today`
- `adToBs` or `ad_to_bs`
- `bsToAd` or `bs_to_ad`
- `validateBsDate` or `validate_bs_date`
- `simulateChangeSet` or `simulate_change_set`
- `verifyTemporalClaim` or `verify_temporal_claim`
- `planSchedule` or `plan_schedule`
- `getProtocolVersion` or `get_protocol_version`
- `getFutureBsCapabilities` or `get_future_bs_capabilities`
- `getFutureBsMethodology` or `get_future_bs_methodology`
- `getFutureBsForecast` or `get_future_bs_forecast`

The SDKs do not call private future-BS month-length prediction, full-range export, model-run, backtest, residual, external comparison, corrected-value, or schedule-impact endpoints.

## Future-BS Claim Boundary

The Future-BS SDK methods return a curated research snapshot and its selected methodology. They preserve human-review and authority boundaries.

Any future-BS output exposed through public SDKs must preserve:

```text
computed_prediction_not_official
```

Official publication overrides computed output.

## Conformance Path

The SDKs should use the repository conformance suite as the baseline compatibility target:

```bash
python tools/conformance_runner/run.py
```

Future SDK work should add language-specific conformance adapters that load the JSON cases under `conformance/` and compare SDK outputs against the same public-safe cases.

## Copy-paste examples

Runnable examples are kept under:

- `examples/python/convert.py`
- `examples/python/holidays.py`
- `examples/python/verify_bundle.py`
- `examples/javascript/convert.mjs`
- `examples/javascript/holidays.mjs`
- `examples/javascript/protocol-version.mjs`
- `examples/curl/quickstart.sh`

They use public or local API bases only and avoid private future-BS exact prediction surfaces.

## Release And Trace Metadata

API responses may include optional metadata such as `release_id`, `calculation_trace_id`, `source_policy`, or `publication_status`.

SDK consumers should preserve this metadata when storing or forwarding calendar results. A release identifier explains which public artifact set was used. A trace identifier explains which calculation steps produced the result.

Future-BS metadata still remains:

```text
computed_prediction_not_official
```
