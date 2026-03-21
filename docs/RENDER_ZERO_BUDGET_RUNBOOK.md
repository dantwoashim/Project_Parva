# Render Zero-Budget Runbook

This is the recommended production deployment path for the current Parva build.

It assumes:

- one free Render web service
- frontend and backend served together
- public `v3` API
- public beta posture

## Validate the blueprint

```bash
py -3.11 scripts/release/check_render_blueprint.py
```

This guard checks that `render.yaml` stays aligned with the current production
expectations and does not quietly drift toward experimental or insecure defaults.

## Required settings

The Render blueprint should provide or prompt for:

- `PARVA_ENV=production`
- `PARVA_ENABLE_EXPERIMENTAL_API=false`
- `PARVA_ALLOW_EXPERIMENTAL_IN_PROD=false`
- `PARVA_RATE_LIMIT_ENABLED=true`
- `PARVA_RATE_LIMIT_BACKEND=redis`
- `PARVA_REDIS_URL=<managed Redis or external Redis connection URL>`
- `PARVA_SERVE_FRONTEND=true`
- `PARVA_SOURCE_URL=<your public repo or source archive>`

Practical note for existing Render Blueprints:

- Render only prompts for `sync: false` variables during the first Blueprint creation flow.
- If the service already exists, add or update `PARVA_REDIS_URL` manually in the Render dashboard before redeploying.

Recommended additions after initial bring-up:

- `PARVA_API_KEYS=<partner keys>` if you expose `commercial.read` routes
- `CORS_ALLOW_ORIGINS=<allowed origins>` for cross-origin API use

## Launch sequence

1. Push the current repository state.
2. Create the Render Blueprint from `render.yaml`.
3. Supply `PARVA_SOURCE_URL` during setup.
4. Supply `PARVA_REDIS_URL` during setup, or add it manually if this Blueprint already exists.
5. Deploy.
6. Verify:
   - `/health/ready`
   - `/source`
   - `/developers/index.html`
   - `/institutions/index.html`
   - `/embed/index.html`
   - `/v3/api/calendar/today`

## Before going public

Run locally:

```bash
py -3.11 scripts/release/check_repo_hygiene.py
py -3.11 scripts/release/check_render_blueprint.py
py -3.11 scripts/release/check_sdk_install.py
py -3.11 -m pytest -q
py -3.11 scripts/release/generate_public_beta_artifacts.py --target 300 --computed-target 300
npm --prefix frontend run build
py -3.11 scripts/run_browser_smoke.py
```

## Truth-first reminders

- This build is public beta.
- Keep `KNOWN_LIMITS.md` visible in launch and operator materials.
- Do not market unsupported uptime, billing, or definitive-authority claims.
