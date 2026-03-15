# Institutional Launch Checklist

Use this checklist before putting Project Parva in front of the public as part
of an institutional website, portal, kiosk, or internal operations workflow.

## Product posture

- State clearly that the current service is a public beta.
- Keep `docs/KNOWN_LIMITS.md` visible in the implementation process and in any operator handoff.
- Avoid definitive or universal authority claims.

## Legal and source obligations

- Publish the corresponding source for the deployed build.
- Set `PARVA_SOURCE_URL` to that public repository or source archive.
- Confirm `/source` resolves correctly in production.

## Deployment

- Use the supported build path only: `backend/` plus `frontend/`
- Set `PARVA_ENV=production`
- Set `PARVA_ENABLE_EXPERIMENTAL_API=false`
- Set `PARVA_SERVE_FRONTEND=true`
- Set `PARVA_RATE_LIMIT_ENABLED=true`
- Set `CORS_ALLOW_ORIGINS` if the API is called cross-origin

## Evidence and quality gates

Run before launch:

```bash
py -3.11 scripts/release/check_repo_hygiene.py
py -3.11 scripts/release/check_render_blueprint.py
py -3.11 scripts/release/check_sdk_install.py
py -3.11 -m pytest -q
py -3.11 scripts/release/check_contract_freeze.py
py -3.11 scripts/spec/run_conformance_tests.py
py -3.11 scripts/release/generate_public_beta_artifacts.py --target 300 --computed-target 300
npm --prefix frontend run lint
npm --prefix frontend test -- --run
npm --prefix frontend run build
py -3.11 scripts/run_browser_smoke.py
```

Review the generated artifacts:

- `reports/conformance_report.json` (generated artifact)
- `reports/authority_dashboard.json` (generated artifact)
- `reports/accuracy/annual_accuracy_2082.json` (generated artifact)
- `reports/release/month9_dossier.json` (generated artifact)

## Integration choices

Choose one:

- use the public frontend directly
- use iframe/script embeds from `frontend/public/embed/`
- integrate against `/v3/api/*`

If using evidence-backed reads, provision `PARVA_API_KEYS` with `commercial.read`.

## Metadata handling

Retain these fields wherever decisions or displays depend on Parva results:

- `calculation_trace_id`
- `method`
- `method_profile`
- `quality_band`
- `assumption_set_id`
- `provenance`
- `policy`

## Privacy-sensitive flows

- Use POST JSON for personal/location-sensitive routes.
- Do not move private inputs back into GET query strings.
- Keep reverse proxies from trusting arbitrary forwarded headers; use `PARVA_TRUSTED_PROXY_IPS`.

## Manual smoke

- `/`
- `/festivals`
- `/personal`
- `/muhurta`
- `/kundali`
- `/embed/temporal-compass.html`
- `/embed/upcoming-festivals.html`
- `/source`
- `/v3/api/calendar/today`

## Handoff

- give operators the deployment settings
- give content owners the public-beta wording and known-limits language
- give developers the hosted onboarding guide and embed guide
- give operators `docs/PARTNER_ACCESS.md` if evidence-backed access will be exposed
