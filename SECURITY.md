# Security Policy

## Supported Version
- Current maintained line: `v2` API contracts.

## Reporting a Vulnerability
- Open a private disclosure with reproduction steps, impacted endpoint, and expected risk.
- Include affected commit hash/tag if known.

## Baseline Controls Implemented
- Request-size/query-length guard middleware
- Security response headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`)
- Dependency audit script:
  - `python3 scripts/security/run_audit.py`
- Route validation through Pydantic/FastAPI schemas

## Hardening Routine
- Run `pytest` and smoke tests before release.
- Run dependency audits and archive report in `reports/security_audit.json`.
- Review deprecation/sunset headers for unversioned API usage.
