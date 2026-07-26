# CI Node 24 Readiness

Project Parva keeps project JavaScript tests on Node 20 for package/runtime
compatibility. GitHub-hosted JavaScript actions use Node 24-era v6 releases.
Each action is pinned to a verified commit SHA rather than a mutable major tag.

Workflow permissions are restricted to `contents: read`, checkout credentials
are not persisted, and `.github/dependabot.yml` maintains the pinned action
versions.

This is a CI-runtime compatibility setting. It does not claim package publication, registry acceptance, or external validation.

Verification:

```bash
python scripts/release/check_ci_node24_readiness.py
```

The check also refuses `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` and verifies
that frontend and SDK package engines remain compatible with tested Node 20 and
Node 24 runtimes.
