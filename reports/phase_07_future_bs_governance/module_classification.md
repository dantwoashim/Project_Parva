# Phase 07 Future-BS Governance Module Classification

Status: public generated artifact required for release hygiene.

This generated artifact classifies Future-BS modules by exposure boundary. It is
not an accuracy report and it does not publish exact unsupported future BS
predictions.

| Module family | Public posture | Private/research posture | Notes |
| --- | --- | --- | --- |
| `backend/app/future_bs/model_registry.py` | Metadata only | Method registry | Public payloads may name model families and `computed_prediction_not_official`. |
| `backend/app/future_bs/ephemeris/*` | Availability metadata only | Optional JPL and Swiss research adapters | Kernel paths and private files must not be returned by public routes. |
| `backend/app/future_bs/solar_ingress_*` | No exact future vector output | Research computation input | Solar ingress can inform candidates, not official civil decisions. |
| `backend/app/future_bs/month_start/*` | No public exact month starts | Research inversion and diagnostics | Exact future month starts are private research artifacts. |
| `backend/app/api/future_bs_routes.py` | Capability summaries only | Exact routes require private gates | Public profile must not mount private exact output routes. |
| `backend/app/api/calendar_model_risk_routes.py` | Capability summaries only | Risk audit and stress routes require private gates | Public profile must not expose exact prediction or sheet-audit data. |

Public-safe rule: a public user may learn which capabilities exist, what source
policy applies, and why review is required. A public user must not receive exact
unsupported future BS month-length vectors, backtest internals, private source
evidence, or loan/schedule impact simulations based on future vectors.
