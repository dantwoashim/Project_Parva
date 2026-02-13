# Hebrew Calendar Notes (Year-2 Week 17–20)

## Implementation
- Formulaic Hebrew conversion plugin (Metonic leap cycle).
- Supports Gregorian ↔ Hebrew conversion through Julian-day arithmetic.

## Implemented Observances
- Rosh Hashanah (1 Tishrei)
- Yom Kippur (10 Tishrei)
- Passover (15 Nisan)
- Hanukkah (25 Kislev)

## API
- `GET /v2/api/engine/convert?date=YYYY-MM-DD&calendar=hebrew`
- `GET /v2/api/engine/observances?plugin=hebrew&rule_id=rosh-hashanah&year=2026`

## Limitation
- Rule corpus currently includes major observances only; broader holiday set is planned for later Year-2 milestones.
