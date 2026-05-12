# AGENTS.md - Project Parva Repository Guidance

These instructions apply to this repository unless a nested `AGENTS.md` overrides them.

## Public Safety Rules

- Do not expose private future-BS predictions publicly.
- Do not add full future month-length vectors, full future month-start dates, private calibration artifacts, private model runs, or residual reports to public docs, examples, fixtures, OpenAPI output, or public API payloads.
- Do not add client, prospect, or partner names to public docs, examples, tests, fixtures, or source comments.
- Do not claim official government calendar authority.
- Do not claim assured future accuracy or broad future-calendar certainty.
- Do not use em dashes in public README or docs.
- Public examples must use historical published dates or clearly synthetic data.
- Future-BS outputs must be labeled `computed_prediction_not_official`.
- Keep experimental and private routes gated behind explicit environment variables.

## Route Review Rules

Treat these as serious review issues:

- private endpoint exposure in public OpenAPI
- missing route gating for prediction, export, backtest, model-run, residual, client-compare, corrected-value, or schedule-impact surfaces
- public capabilities payloads that advertise private routes as public live endpoints
- broad accuracy claims without source-policy metadata
- secrets, tokens, billing credentials, or private environment values
- generated private artifacts committed by accident

## Source Policy

Keep official, printed, public-witness, publisher-reference, software-table, third-party, and needs-review evidence separate.

Weak third-party and software-table data may support shadow comparison or review targeting. They must not support official-grade claims.

## Testing Expectations

When changing routing, docs, future-BS behavior, examples, schemas, or public contracts, run focused checks for:

- public and private route boundaries
- OpenAPI schema safety
- public capabilities payload shape
- prohibited public phrases
- absence of client-specific naming
- absence of full future vectors in public examples
- schema validity when public contracts change

If full tests are too slow or fail because of unrelated existing issues, run targeted tests and document exactly what passed and what did not run.
