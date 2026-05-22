# Evidence-Backed Outreach

## Target Audiences

- Maintainers of Nepali date libraries.
- Nepal-facing ERP, accounting, payroll, and compliance software teams.
- Developers choosing Nepali date APIs.
- Reviewers checking whether Project Parva's claims are bounded by evidence.

## What To Send

- A short note with one public case or fixture link.
- The specific failure class being represented.
- Whether the case is verified, reported, partial, or review-needed.
- A clear statement that no dependency or integration is required.

## What Not To Send

- Broad claims that an upstream project is broken.
- Replacement pitches.
- Claims of production impact unless the public issue says so directly.
- Legal, tax, payroll, banking, ritual, or official calendar claims.
- Mass comments across many issue trackers.

## Sample Short Message

Hi, I was collecting public Nepali date regression cases for Project Parva's
conformance suite.

I added this issue as a public conformance case because it captures a clear
failure class: `[failure class]`.

No dependency or integration is required. Sharing in case the fixture is useful
for future tests:

`[public fixture link]`

The case is marked as `[verified/reported/review-needed]` and includes an
explicit authority boundary.

## Safe Claims

- Project Parva tracks public Nepali date regression cases as fixtures.
- Project Parva contributed a standalone source consistency guard to
  `yarsa/nepal-compliance`.
- Project Parva keeps future BS cases behind review-needed boundaries when
  source certainty is incomplete.

## Forbidden Claims

- Do not claim upstream adoption without explicit evidence.
- Do not claim official calendar, legal, tax, payroll, or banking authority.
- Do not claim listed projects are globally broken.
- Do not claim public issue evidence proves production impact by itself.

## When To Send

Send outreach only when:

- The fixture or doc is already public.
- The comment is short and directly useful.
- The target issue is active enough or the note is clearly harmless.
- The message does not ask maintainers to adopt Project Parva.
