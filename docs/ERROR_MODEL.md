---
status: public-beta
audience: developer
---

# Error Model

Public APIs should converge on this structured error envelope without breaking
current compatibility responses:

```json
{
  "error": {
    "code": "BS_DATE_OUT_OF_RANGE",
    "message": "The requested BS date is outside the supported public range.",
    "request_id": "req_example",
    "claim_boundary": "unsupported",
    "review_required": true,
    "docs_url": "https://api.prabinghimire1.com.np/docs"
  }
}
```

Responses should include these headers when rate limiting and request tracing
are active:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `X-Request-ID`

If an existing route cannot yet emit this shape, preserve compatibility and add
tests before changing the wire contract.

## Client Handling

- Retry only `429`, `500`, `502`, `503`, and `504`.
- Honor `Retry-After` on `429`.
- Do not retry invalid-date, unsupported-range, auth, private-route, or
  review-required responses as if they were transient failures.
- Preserve `claim_boundary` and `review_required` in logs and downstream
  decisions.
- Treat `computed_prediction_not_official` as a safety label, not a warning that
  can be hidden.
