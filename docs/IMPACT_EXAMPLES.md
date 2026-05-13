# Impact Examples

Self-diff:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/impact/diff-releases \
  -H "Content-Type: application/json" \
  -d '{"from_release_id":"parva-bs-public-demo","to_release_id":"parva-bs-public-demo"}'
```

Fixture simulation:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/impact/simulate-release-diff \
  -H "Content-Type: application/json" \
  -d '{"from_release_id":"parva-bs-public-demo","to_release_id":"parva-bs-public-demo","include_fixture":true}'
```

Fixture output is for conformance and demo use only.
