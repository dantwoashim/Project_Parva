# Protocol Offline Bundles

Offline bundles allow public Parva artifacts to be verified without a live API.

The bundle contains specs, schemas, release artifacts, trust log data, and checksums.

Generate:

```bash
python scripts/parva_offline_bundle.py --output dist/parva-offline-bundle
```

Verify:

```bash
python scripts/parva_offline_verify.py dist/parva-offline-bundle
```
