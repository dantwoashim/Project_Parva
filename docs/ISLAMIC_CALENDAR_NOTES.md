# Islamic Calendar Notes (Year-2 Week 13–16)

## Modes
- `tabular`: algorithmic Hijri conversion (implemented)
- `announced`: uses override file when available (`data/islamic/announced_dates.json`)
- `astronomical`: placeholder mode label currently mapped to proxy output with `approximate` confidence

## Implemented Observances
- Islamic New Year (1 Muharram)
- Eid al-Fitr (1 Shawwal)
- Eid al-Adha (10 Dhu al-Hijjah)
- Shab-e-Barat (15 Sha'ban)

## API
- `GET /v2/api/engine/convert?date=YYYY-MM-DD&calendar=islamic`
- `GET /v2/api/engine/observances?plugin=islamic&rule_id=eid-al-fitr&year=2026&mode=announced`

## Limitation
- True moon-sighting visibility model is not yet implemented; `astronomical` mode is declared as approximate.
