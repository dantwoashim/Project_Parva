# CI Node 24 Readiness

Project Parva keeps project JavaScript tests on Node 20 for package/runtime compatibility, while GitHub-hosted JavaScript actions are opted into the Node 24 action runtime with:

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
```

This is a CI-runtime compatibility setting. It does not claim package publication, registry acceptance, or external validation.

Verification:

```bash
python scripts/release/check_ci_node24_readiness.py
```

The check also refuses `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION`.
