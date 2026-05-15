---
status: public-beta
audience: enterprise
---

# Institution Rule Profiles

Institution profiles describe how an organization wants to apply source-backed
Nepali time rules. They are decision-support profiles, not legal, tax, payroll,
banking, or government authority.

Profile families:

| Family | Evidence needed before final use |
| --- | --- |
| Government office | Official holiday release and office-specific notices. |
| Bank or cooperative | Institution-approved bank holiday and repayment policy. |
| Payroll/HR | Employer payroll cutoff, attendance, leave, and holiday policy. |
| School/college | Academic calendar and local closure notices. |
| Municipality | Local holiday or office notice. |
| Festival/Panchanga | Published Panchanga or authority decision for the target edition. |

Default public profiles may help developers test workflow shape. Production
use must attach the institution's own evidence and preserve review gates for
source conflicts, future dates, unsupported ranges, and authority-sensitive
decisions.
