---
status: public-beta
audience: maintainers
---

# Package Publishing

Project Parva packages are prepared for public-beta registry release, but this
repository does not claim PyPI or npm publication until the registry entries
exist.

## Packages

- `project-parva-python-sdk` at `packages/parva-python`
- `@project-parva/parva-js` at `packages/parva-js`
- `parva-agent-tools` at `packages/parva-agent-tools`
- `parva-mcp-server` at `packages/parva-mcp-server`

## Preferred Release Path

- Use PyPI trusted publishing for Python packages.
- Use npm trusted publishing or npm 2FA for JavaScript packages.
- Never commit registry tokens or local credential files.
- Run dry-run/package checks before publishing.
- Publish alpha versions first, then verify install in a clean environment.

## Dry-Run Commands

```bash
python scripts/release/check_package_readiness.py
python -m build packages/parva-python
python -m build packages/parva-agent-tools
python -m build packages/parva-mcp-server
npm --prefix packages/parva-js pack --dry-run
```

## Rollback Notes

If a bad package is published, deprecate the registry version with a clear
message and publish a corrected patch or alpha version. Do not delete provenance
or rewrite public registry history unless the registry requires it for security
reasons.

## Claim Boundary

Package publication does not create government, legal, tax, banking, payroll,
religious, official future-date, external certification, or registry endorsement
authority.
