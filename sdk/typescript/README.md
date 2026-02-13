# Parva TypeScript SDK (v5 authority track)

```ts
import { ParvaClient } from "@parva/sdk";

const client = new ParvaClient({ baseUrl: "http://localhost:8000/v5/api" });
const today = await client.today();
console.log(today.data.gregorian, today.meta.confidence.level);

const resolved = await client.resolve("2026-10-21");
const trace = await client.verifyTrace(resolved.meta.trace_id!);
console.log(trace.data.is_valid);
```

Features:
- Typed `DataEnvelope<T>` responses with authority metadata.
- Retry/backoff support.
- Compatibility fallback when consuming legacy v3 endpoints.
