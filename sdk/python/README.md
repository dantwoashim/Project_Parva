# Parva Python SDK (v5 authority track)

```python
from parva_sdk import ParvaClient

client = ParvaClient("http://localhost:8000/v5/api")

today = client.today()
print(today.data["gregorian"])
print(today.meta.confidence.level, today.meta.provenance.snapshot_id)

resolved = client.resolve("2026-10-21")
print(resolved.data["bikram_sambat"]["formatted"])
trace_id = resolved.meta.trace_id
verified = client.verify_trace(trace_id)
print(verified.data["is_valid"])
```

Features:
- Typed `DataEnvelope` responses (`data` + `meta`).
- Retry/backoff on transient network and 5xx failures.
- v3 compatibility fallback for legacy raw payloads.
