# Udaya Tithi Specification

## Definition
Udaya tithi is the tithi prevailing at local sunrise for a given date/location.
This is the official day-level tithi used for festival observance.

## Computation Steps
1. Compute sunrise moment (`UTC`) for the target date/location via Swiss Ephemeris `rise_trans`.
2. Evaluate Sun-Moon elongation at sunrise.
3. Convert elongation to tithi:
   - `absolute_tithi = floor(elongation / 12) + 1` (1..30)
   - `display_tithi = absolute_tithi` for 1..15, else `absolute_tithi - 15`
   - paksha: `shukla` for 1..15, `krishna` for 16..30
4. Use this result as the day’s official tithi.

## Edge Cases
- **Vriddhi**: same absolute tithi at two consecutive sunrises.
- **Ksheepana**: sunrise-to-sunrise jump of 2 tithis (one tithi skipped between sunrises).

## API Metadata Requirements
- `method`: `ephemeris_udaya`
- `reference_time`: `sunrise`
- `sunrise_used`: ISO timestamp in local time
- `confidence`: `exact` (within ephemeris-valid range)
