# Protocol Offline Bundles

Preview offline bundles allow public Parva artifacts to be verified without a live API.

The bundle contains specs, protocol draft schemas, release artifacts, trust log data, and checksums. It is a reproducibility package, not a signed production credential and not an official calendar publication.

## Included Artifacts

The preview bundle should include:

- `specs/parva-protocol/VERSION`
- `specs/parva-protocol/README.md`
- all `schemas/parva-protocol/*.schema.json`
- public release manifest metadata
- public source registry metadata
- public trust log entries
- checksums for each required file

It must not include private future-BS vectors, private calibration artifacts, customer data, private source archives, or corrected future values.

Generate:

```bash
python scripts/parva_offline_bundle.py --output dist/parva-offline-bundle
```

Verify:

```bash
python scripts/parva_offline_verify.py dist/parva-offline-bundle
```

## Integrity Model

The preview verifier checks local file presence and SHA-256 checksums. It does not claim a production signature. A production deployment should add signing, key rotation, release attestation, and an external transparency log before treating a bundle as a governed release artifact.
