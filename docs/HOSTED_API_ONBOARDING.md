# Hosted API Onboarding

This guide is for teams that want to adopt Project Parva as an API-first service
instead of only embedding the frontend widgets.

The stable public-beta contract is `v3` under `/v3/api/*`.

## Choose an adoption path

### 1. Public read only

Best for:

- festival search and timeline integrations
- calendar conversion
- panchanga readouts
- embeds and iCal feeds

No API key is required for the public `v3` read-only product routes.

### 2. Evidence-backed integration

Best for:

- institutions that need conformance visibility
- provenance verification
- artifact discovery
- operational review before internal rollout

These routes require `commercial.read` via `X-API-Key` or the admin bearer token:

- `/v3/api/reliability/status`
- `/v3/api/reliability/slos`
- `/v3/api/reliability/playbooks`
- `/v3/api/spec/conformance`
- `/v3/api/public/artifacts/manifest`
- `/v3/api/public/artifacts/dashboard`
- `/v3/api/provenance/root`
- `/v3/api/provenance/proof`
- `/v3/api/provenance/verify/trace/{trace_id}`

## Local development

```bash
py -3.11 -m pip install -e .[test,dev]
py -3.11 -m pip install -e sdk/python
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Local development credentials are deterministic when `PARVA_ENV` is `development`,
`local`, `test`, or `dev`:

- read key: `parva-dev-read-key`
- admin bearer token: `parva-dev-admin-token`

## Provision a read key

In production, define `PARVA_API_KEYS` with one or more records:

```text
partner-prod:replace-me:commercial.read|public.read
```

Multiple keys are separated by semicolons:

```text
partner-a:key-a:commercial.read|public.read;partner-b:key-b:commercial.read|public.read
```

You can generate a strong key entry with:

```bash
py -3.11 scripts/release/generate_partner_api_key.py --key-id partner-prod
```

Call non-public read surfaces with:

```bash
curl "https://your-host.example/v3/api/spec/conformance" ^
  -H "X-API-Key: replace-me"
```

## Minimal first integration

1. Read `GET /v3/api/calendar/today`
2. Read `GET /v3/api/festivals/upcoming?days=30`
3. Switch privacy-sensitive requests to POST:
   - `/v3/api/personal/panchanga`
   - `/v3/api/muhurta/heatmap`
   - `/v3/api/kundali`
4. Preserve metadata in storage or logs:
   - `calculation_trace_id`
   - `method`
   - `method_profile`
   - `quality_band`
   - `assumption_set_id`
   - `provenance`

## Deployment baseline

For the zero-budget path, deploy the full stack on a single free Render service.

Required production settings:

- `PARVA_ENV=production`
- `PARVA_ENABLE_EXPERIMENTAL_API=false`
- `PARVA_RATE_LIMIT_ENABLED=true`
- `PARVA_SERVE_FRONTEND=true`
- `PARVA_SOURCE_URL=<public repo or source archive>`

Recommended when you expose evidence-backed reads:

- `PARVA_API_KEYS=<your commercial.read keys>`
- `CORS_ALLOW_ORIGINS=<allowed origins>`

## Verification before sharing the endpoint

```bash
py -3.11 scripts/release/check_repo_hygiene.py
py -3.11 scripts/release/check_sdk_install.py
py -3.11 -m pytest -q
py -3.11 scripts/release/generate_public_beta_artifacts.py --target 300 --computed-target 300
npm --prefix frontend run build
py -3.11 scripts/run_browser_smoke.py
```

## Public-beta guardrails

- Treat the service as public beta in user-facing copy.
- Keep `KNOWN_LIMITS.md` visible anywhere results are presented as authoritative.
- Do not market the current build as definitive or universally final.

## Related materials

- `docs/API_QUICKSTART.md`
- `docs/EMBED_GUIDE.md`
- `docs/PARTNER_ACCESS.md`
- `docs/RENDER_ZERO_BUDGET_RUNBOOK.md`
- `docs/USAGE_TIERS.md`
- `docs/INSTITUTIONAL_LAUNCH_CHECKLIST.md`
