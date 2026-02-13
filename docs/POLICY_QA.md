# Policy QA Scenarios (Year 3 Week 31-32)

## Scenario Matrix
| Scenario | Expected Behavior | Status |
|---|---|---|
| User consumes festival date for app UI | Response includes `policy.usage="informational"` | Covered |
| User requests forecast year far ahead | Response still includes policy + confidence decay metadata | Covered |
| Institution uses API for notices | Institutional guidance available in docs | Covered |
| Religious authority asks for binding date | Policy advises consultation with local authority | Covered |

## Automated Coverage
- `tests/contract/test_reliability_policy_contract.py`
  - verifies policy metadata on calendar + forecast responses

## Manual QA checklist
1. Verify `/v2/api/policy` returns advisory text.
2. Verify `/v2/api/calendar/today` includes `policy`.
3. Verify `/v2/api/forecast/festivals` includes `policy`.
4. Verify README links to policy and institutional docs.
