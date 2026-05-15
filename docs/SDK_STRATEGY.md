---
status: public-beta
audience: developer
---

# SDK Strategy

`packages/parva-python` is the canonical Python SDK. `packages/parva-js` is the
canonical JavaScript and TypeScript SDK. `sdk/python` is compatibility
scaffolding for older smoke checks and should not be the primary integration
path for new applications.

SDK defaults use stable public routes under `/v3/api`. Future-BS support is
limited to the public `/v4/api/future-bs/capabilities` metadata endpoint. SDKs
must not expose exact unpublished Future-BS prediction, export, backtest,
model-run, comparison, corrected-value, or schedule-impact routes by default.

Required SDK posture:

| Surface | Python | JS/TS | Status |
| --- | --- | --- | --- |
| BS/AD conversion | `ParvaClient.ad_to_bs`, `ParvaClient.bs_to_ad` | `adToBs`, `bsToAd` | Stable |
| Fiscal and business-day logic | `get_fiscal_year`, `get_business_days`, compliance helpers | `getFiscalYear`, `getBusinessDays`, compliance helpers | Stable/public preview |
| Trust metadata | trust/source helpers | trust/source helpers | Public preview |
| TimeGraph and RuleLang | helper methods | helper methods | Developer preview |
| Future-BS | capabilities only | capabilities only | Research boundary metadata |

Publishing readiness requires passing package tests, build/pack checks, public
leakage checks, docs review, and versioned release notes. See
[SDK Publishing Checklist](SDK_PUBLISHING_CHECKLIST.md).
