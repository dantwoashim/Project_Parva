# Lunar Month Specification (Parva V2)

## Scope
Defines how Parva computes lunar month boundaries and month identity for festival rules.

## Boundary Model
- Month window is **Amavasya -> next Amavasya**.
- `start_amavasya` = exact instant when Krishna 15 ends (elongation reaches 360°/0°).
- `end_amavasya` = next such instant.
- Month contains:
  - Shukla paksha from `start_amavasya` up to Purnima
  - Krishna paksha from Purnima up to `end_amavasya`

## Purnima Instant
- Purnima is the **end of Shukla 15**, not its start.
- Implemented by finding Shukla 15 start then locating tithi end boundary.

## Month Naming
- Parva uses a solar-aligned naming model for compatibility with existing festival rules:
  - Determine Sun rashi at the month's Purnima.
  - Map rashi -> BS month name (`Baishakh...Chaitra`).
- This convention is explicitly documented because traditional naming systems can vary by school.

## Adhik Maas Rule
- A lunar month is **Adhik** if no sankranti occurs inside `[start_amavasya, end_amavasya)`.
- Operational check: Sun rashi at start and end remains identical.

## API/Engine Functions
- `find_amavasya(after)`
- `find_purnima(after)`
- `lunar_month_boundaries(gregorian_year)`
- `name_lunar_month(start_amavasya, end_amavasya)`
- `detect_adhik_maas(month_start, month_end)`

## Validation
- Reference fixture: `tests/fixtures/adhik_maas_reference.json`
- Tests:
  - `tests/unit/engine/test_adhik_maas_reference.py`
  - `tests/unit/engine/test_lunar_boundaries.py`

## Known Limits
- Naming conventions can differ by regional/traditional school.
- Festival rule profiles should carry explicit policy when traditions diverge.
