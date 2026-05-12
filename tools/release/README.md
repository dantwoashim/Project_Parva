# Release Tools

The release tools verify public Project Parva release manifests and their listed artifacts.

## Verify A Release

```bash
python tools/release/verify_release.py data/public/releases/parva-bs-public-demo.manifest.json
```

The verifier:

- loads the manifest JSON
- checks required release fields
- checks the public claim boundary
- loads every schema listed in `schemas_used`
- computes SHA-256 for every listed artifact
- compares each hash against the manifest
- validates public-safe source registry shape when a source registry artifact is listed

The public demo release does not include private future-BS values, corrected future outputs, private model internals, or client-specific material.
