# Public API Boundary

The public Project Parva deployment exposes stable calendar, fiscal-year, festival, and public methodology surfaces for technical evaluation.

Public surfaces include:

| Surface | Purpose |
| --- | --- |
| `/v3/api/calendar/*` | BS/AD conversion, today, validation, calendar utilities, and enabled panchanga helpers |
| `/v3/api/enterprise/*` | Nepali fiscal-year and business date validation logic |
| `/v3/api/festivals/*` | Festival and observance APIs |
| `/v4/api/future-bs/capabilities` | Public summary of the future-BS research layer |

Private future-BS workflows such as direct future month-length prediction, full-range exports, model runs, residual analysis, backtests, client sheet comparison, and loan-impact simulation are not public surfaces by default.

Future outputs are treated as `computed_prediction_not_official`.

The public service is not the authority for legal, tax, regulatory, or banking-contract decisions. Production use should be validated against the organization's own requirements and source policy.
