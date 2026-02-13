# Integrations (M20)

## iCal Feeds
All feed endpoints return `text/calendar` content.

- `GET /v2/api/feeds/ical?festivals=dashain,tihar&years=2&lang=en`
- `GET /v2/api/feeds/all.ics`
- `GET /v2/api/feeds/national.ics`
- `GET /v2/api/feeds/newari.ics`
- `GET /v2/api/feeds/custom.ics?festivals=dashain,tihar&lang=ne`
- `GET /v2/api/feeds/next?days=30` (JSON preview helper)

### Notes
- Events are all-day `VEVENT`s.
- `DTEND` is non-inclusive (`end_date + 1 day`), as required by iCal all-day semantics.
- Nepali summary is used when `lang=ne` and localized name exists.

## Webhooks
Subscription endpoints:
- `POST /v2/api/webhooks/subscribe`
- `GET /v2/api/webhooks`
- `GET /v2/api/webhooks/{id}`
- `DELETE /v2/api/webhooks/{id}`

Dispatch endpoint:
- `POST /v2/api/webhooks/dispatch?date=YYYY-MM-DD&dry_run=true`

### Subscription Schema
```json
{
  "subscriber_url": "https://example.com/parva-hook",
  "festivals": ["dashain", "tihar"],
  "remind_days_before": [3, 1, 0],
  "format": "json",
  "active": true
}
```

### Delivery Behavior
- Duplicate suppression key: `subscription_id + festival_id + start_date + remind_days_before`
- Retries: up to 3 attempts with exponential backoff
- `mock://` URLs are supported for integration tests:
  - `mock://success` => successful delivery
  - `mock://fail` => forced failure

Storage path:
- `/Users/rohanbasnet14/Documents/Project Parva/backend/data/webhooks/subscriptions.json`

## Polling + Bot Integrations
- `GET /v2/api/observances/next` for “next event” pull clients
- `GET /v2/api/observances/stream` for rolling sync windows

Telegram bot PoC:
- `/Users/rohanbasnet14/Documents/Project Parva/scripts/telegram/bot_poc.py`
- Commands: `/panchanga [YYYY-MM-DD]`, `/upcoming [days]`
