# Plugin Architecture

## Components
- `CalendarPlugin` protocol for date conversion plugins.
- `PluginRegistry` for discovery/registration.
- `PluginValidationSuite` for corpus-driven acceptance checks.
- `ObservancePlugin` protocol for rule-based observance calculators.

## Built-in Calendar Plugins
- `bs` (Bikram Sambat): official + estimated behavior.
- `ns` (Nepal Sambat): forward approximate conversion model.
- `tibetan` (Tibetan v1): approximate conversion shell.

## Built-in Observance Plugins
- `nepali_hindu`
- `tibetan_buddhist`

## API Surface
- `GET /v2/api/engine/calendars`
- `GET /v2/api/engine/convert?date=YYYY-MM-DD&calendar=...`
- `GET /v2/api/engine/observance-plugins`
- `GET /v2/api/engine/observances?plugin=...&rule_id=...&year=...`
