---
status: public-beta
audience: vendors-ai-systems
---

# AI Should Not Guess Nepali Time

Nepali time is not only BS/AD conversion. Real software workflows also depend
on source-backed holidays, working-day rules, fiscal boundaries, festival
authority, panchanga conventions, unsupported future-date behavior, and review
gates for payroll, repayment, banking, legal, and government workflows.

Large language models and static date tables are unsafe for this domain because
they can produce a plausible date without source tier, supported range,
uncertainty, or authority boundary. That is enough to break schedules, invoices,
loan reminders, payroll cutoffs, government filing flows, and public notices.

Project Parva's benchmark v0 tests whether a system can:

- convert BS/AD dates inside supported public ranges,
- reject invalid BS dates,
- preserve holiday and working-day source boundaries,
- handle fiscal-year boundaries,
- report festival and panchanga metadata,
- mark payroll and repayment-style cases for review,
- refuse public exact unsupported Future-BS predictions,
- return machine-readable source, confidence, and evidence metadata.

The benchmark does not prove official authority. It does not replace MoHA,
NPNS, Panchanga publishers, banks, payroll departments, courts, tax offices, or
any government body. It is a public-safe technical benchmark for deterministic
tool behavior and boundary preservation.

The benchmark files live under the public benchmark directory. Runner output is
scored on correctness, source awareness, uncertainty handling, review-gate
behavior, and machine-readable structure.
