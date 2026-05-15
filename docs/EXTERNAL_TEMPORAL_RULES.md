---
status: public-beta
audience: integrators
---

# External Temporal Rules

Project Parva separates astronomical computation from institutional rule truth.
A solar ingress, tithi, or panchanga calculation can be precise and still not be
the final civil, holiday, payroll, school, banking, or government decision.

The registry in `config/external-temporal-rules.yaml` records rule categories,
source tier, evidence requirements, public-safety posture, review triggers, and
conflict resolution.

Rules are not official just because they are listed. A rule is official only
when the required source evidence exists and the relevant authority actually
published it. Inferred or research rules remain review-required.

## Interaction With Astronomy

Astronomy can answer "what did the Sun or Moon do?" External rules answer "what
did an institution decide to do with that fact?" Parva can encode, verify, and
test the connection, but it cannot become the institution.

Sensitive workflows should keep `review_required` true until an operator has
attached the appropriate release, institution policy, or source evidence.
