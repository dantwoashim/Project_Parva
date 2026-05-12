# Parva Conformance Runner

Run the public conformance suite from the repository root:

```bash
python tools/conformance_runner/run.py
```

The default runner uses local backend functions and validates every JSON case file under `conformance/`.

Optional API mode:

```bash
PARVA_CONFORMANCE_BASE_URL=http://localhost:8000 python tools/conformance_runner/run.py --api
```

API mode is intentionally limited. It checks public conversion endpoints where practical and still validates all local case structure.

The runner exits with status `1` if any case file is malformed, unsafe, or fails its local checks.
