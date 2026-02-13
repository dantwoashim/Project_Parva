# Udaya Implementation Audit (Week 13)

## Audit Target
- `backend/app/calendar/tithi/tithi_udaya.py`
- `backend/app/calendar/ephemeris/swiss_eph.py`

## Findings
1. Sunrise source is correct:
- Uses Swiss Ephemeris `rise_trans` and returns timezone-aware UTC datetime.

2. Udaya tithi path is correct:
- `get_udaya_tithi()` computes tithi at sunrise, not midnight.

3. Gaps found (fixed in Week 14/15):
- Vriddhi/ksheepana helpers were heuristic; now explicit sunrise-to-sunrise checks exist.
- API responses lacked consistent `reference_time` + `sunrise_used`; now added.

## Current Status
- Udaya method is now first-class and explicitly represented in API contracts.
