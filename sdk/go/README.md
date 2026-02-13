# Parva Go SDK (v5 authority track)

```go
client := parva.NewClient("http://localhost:8000/v5/api")
today, err := client.Today()
if err != nil { panic(err) }

var todayData map[string]any
if err := parva.DecodeData(today, &todayData); err != nil { panic(err) }
fmt.Println(todayData["gregorian"], today.Meta.Confidence.Level)

resolved, err := client.Resolve("2026-10-21", "np-mainstream", 27.7172, 85.3240, true)
if err != nil { panic(err) }
fmt.Println(*resolved.Meta.TraceID)
```

Features:
- Typed envelope metadata (`confidence`, `provenance`, `policy`).
- Retry/backoff for transient errors.
- Decoder helper for strongly-typed `data`.
