# Partner Access

This guide is for operators who want to expose the non-public evidence-backed
read surfaces to a partner, customer, or institutional evaluator.

Those routes require `commercial.read` through `X-API-Key` or the admin bearer
token. For partner access, prefer `X-API-Key`.

## What is worth gating

Recommended `commercial.read` surfaces:

- `/v3/api/reliability/status`
- `/v3/api/reliability/slos`
- `/v3/api/reliability/playbooks`
- `/v3/api/spec/conformance`
- `/v3/api/public/artifacts/manifest`
- `/v3/api/public/artifacts/dashboard`
- `/v3/api/provenance/root`
- `/v3/api/provenance/proof`
- `/v3/api/provenance/verify/trace/{trace_id}`

## Generate a partner key

```bash
py -3.11 scripts/release/generate_partner_api_key.py --key-id municipality-kathmandu-prod
```

JSON output:

```bash
py -3.11 scripts/release/generate_partner_api_key.py --key-id municipality-kathmandu-prod --json
```

## Add it to production

`PARVA_API_KEYS` accepts semicolon-separated records:

```text
partner-a:key-a:commercial.read|public.read;partner-b:key-b:commercial.read|public.read
```

Single record example:

```text
municipality-kathmandu-prod:replace-me:commercial.read|public.read
```

## Verify the key

```bash
curl "https://your-host.example/v3/api/spec/conformance" ^
  -H "X-API-Key: replace-me"
```

You should receive a conformance payload instead of `401`.

## Operational advice

- Use one key per partner or institution.
- Keep the `key_id` stable and human-readable.
- Rotate keys by replacing only the secret, not the identifier.
- Do not use the admin bearer token for routine partner access.
- Do not place local dev credentials in production config.

## Related materials

- `docs/HOSTED_API_ONBOARDING.md`
- `docs/ROUTE_ACCESS.md`
- `docs/USAGE_TIERS.md`
