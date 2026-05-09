# Calendar Conversion Example

These examples use public-safe endpoints.

```bash
curl https://api.prabinghimire1.com.np/v3/api/calendar/today
```

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2026-04-14"
```

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/calendar/bs-to-gregorian \
  -H "Content-Type: application/json" \
  -d '{"year":2083,"month":1,"day":1}'
```
