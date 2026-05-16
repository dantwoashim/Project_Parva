---
status: public-beta
audience: enterprise
---

# Enterprise Deployment

Enterprise deployment is for organizations that need controlled Nepali calendar
validation, source-aware temporal decisions, and internal audit evidence.

Recommended deployment shape:

- pin Python 3.11.x and Node 20.x,
- run `python scripts/verify_environment.py`,
- run `python scripts/release/verify_public.py` before release promotion,
- configure durable rate limiting and provenance storage,
- reject localhost CORS, default peppers, wildcard trusted proxies, and
  nondurable billing/provenance stores in production,
- keep private source archives and research artifacts out of public routes,
- publish the source URL required by AGPL or use a commercial license.

Enterprise use remains decision support. Parva is not a government authority,
legal authority, tax advisor, banking-contract authority, payroll final
authority, or religious authority.

For vendor audit and conformance deployments, run the public gate first, then
attach organization-specific source policies for holidays, payroll cutoffs,
banking calendars, fiscal assumptions, and local holidays. Do not use public
demo profiles as final institution policy.

The free public tier is useful for evaluation and development, but enterprise
deployments should not depend on free-tier limits, public demo availability, or
public-demo operational posture. Use paid API-key access or private deployment
when contractual support, controlled quotas, or dedicated operations are needed.
