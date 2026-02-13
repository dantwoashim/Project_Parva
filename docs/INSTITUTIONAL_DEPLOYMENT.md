# Institutional Deployment (Offline Kit)

## 1) Build bundle
```bash
bash scripts/offline/build_offline_bundle.sh v3_week40
```

Outputs:
- `output/offline/parva_offline_<version>_<timestamp>/`
- `output/offline/parva_offline_<version>_<timestamp>.tar.gz`
- `output/offline/parva_offline_<version>_<timestamp>.tar.gz.sha256`

## 2) Verify integrity
```bash
shasum -a 256 -c output/offline/parva_offline_<...>.tar.gz.sha256
```

## 3) Run via Docker (optional reproducible runtime)
```bash
docker build -t parva-offline:latest .
docker run --rm -p 8000:8000 parva-offline:latest
```

## 4) Parity verification
```bash
PYTHONPATH=backend python3 scripts/offline/verify_offline_parity.py --base-url http://localhost:8000
# If remote runtime is unavailable, run structural parity locally:
PYTHONPATH=backend python3 scripts/offline/verify_offline_parity.py --local-only
```

## 5) What institutions should archive
- Bundle archive + checksum
- `MANIFEST.sha256` from bundle directory
- Benchmark packs used for validation
- Provenance snapshot metadata from `/v2/api/provenance/root`
