# Project Parva — Weekly Implementation Plan: Year 2

> **Year 2: Multi-Calendar Expansion + Ecosystem** (March 2027 – February 2028)
>
> **Exit Criteria**: 5+ calendar families through unified API, per-output confidence, regional observance variants, published SDKs/iCal/webhooks, community governance with signed rule changes, public beta launched.

> Note: Year-2 execution logs in `docs/weekly_execution/` use `year2_week1..` numbering for convenience:
> - `year2_week1` maps to plan Week 49
> - ...
> - `year2_week10` maps to plan Week 58
> - `year2_week20` maps to plan Week 68
> - `year2_week30` maps to plan Week 78
> - `year2_week40` maps to plan Week 88
> - `year2_week48` maps to plan Week 96 (end of original Year-2 plan)
> - `year2_week49..52` are execution-level closure/handoff extensions used in this repo

---

## M13: Plugin Architecture for Calendars (Mar 1–28, 2027)

### Week 49 (Mar 1–7) — Plugin Interface Design

| Day | Deliverables |
|---|---|
| Mon | Survey all calendar-specific code in `engine/`: identify common patterns (epoch conversion, month naming, leap handling, date arithmetic). |
| Tue | Design `CalendarPlugin` protocol: `convert_to_jd(year, month, day) → float`, `convert_from_jd(jd) → CalendarDate`, `month_lengths(year) → list[int]`, `validate(year, month, day) → bool`, `metadata() → CalendarMetadata`. |
| Wed | Design `ObservancePlugin` protocol: `list_rules() → list[ObservanceRule]`, `calculate(rule, year, engine) → ObservanceDate`, `validate_result(result, ground_truth) → ValidationResult`. |
| Thu | Design plugin registration system: `PluginRegistry` that discovers and loads plugins. Each plugin declares its calendar family, version, and confidence characteristics. |
| Fri | Write `docs/PLUGIN_DEVELOPMENT.md`: how to create a new calendar plugin with examples. |
| Sat | Design per-plugin validation protocol: each plugin must ship with a test corpus and pass a standard acceptance suite before activation. |
| Sun | Buffer |

---

### Week 50 (Mar 8–14) — Refactor BS as First Plugin

| Day | Deliverables |
|---|---|
| Mon | Extract Bikram Sambat code into `engine/plugins/bikram_sambat/`: `plugin.py` implementing `CalendarPlugin`, `constants.py`, `estimated_mode.py`. |
| Tue | Extract Nepal Sambat into `engine/plugins/nepal_sambat/`: same structure. |
| Wed | Extract solar/tithi-based observance rules into `rules/plugins/nepali_hindu/`: implements `ObservancePlugin`. |
| Thu | Wire plugin registry into API: `/v2/calendars` lists available calendar plugins. `/v2/convert` accepts `calendar` parameter. |
| Fri | Regression: verify all existing endpoints return identical results after plugin extraction. |
| Sat | Write plugin-level unit tests that run independently. |
| Sun | Buffer |

---

### Week 51 (Mar 15–21) — Plugin Validation Framework

| Day | Deliverables |
|---|---|
| Mon | Implement `PluginValidationSuite`: given a plugin + test corpus, runs all conversions and checks accuracy. |
| Tue | Implement validation report generator: per-plugin accuracy, edge case results, confidence characteristics. |
| Wed | Add CI gate: no plugin can be activated unless it passes validation suite with documented accuracy. |
| Thu | Create plugin template: `engine/plugins/_template/` with boilerplate, example tests, README skeleton. |
| Fri | Write 2 example observance rules using new DSL to prove the system works end-to-end. |
| Sat | Document plugin architecture: `docs/PLUGIN_ARCHITECTURE.md`. |
| Sun | Buffer |

---

### Week 52 (Mar 22–28) — M13 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full regression across all endpoints. |
| Tue | Verify plugin discovery and registration works with multiple plugins loaded. |
| Wed | Performance: plugin dispatch adds < 1ms overhead. |
| Thu | Documentation finalization. |
| Fri | M13 postmortem. Git tag `v2.2.0-m13`. |
| Sat–Sun | Buffer / rest |

**M13 Definition of Done**: Plugin architecture operational. BS and NS refactored as plugins. New calendars can be added without touching core API code.

---

## M14: Buddhist/Tibetan Module v1 (Mar 29 – Apr 25, 2027)

### Week 53 (Mar 29 – Apr 4) — Research & Corpus Building

| Day | Deliverables |
|---|---|
| Mon | Research Tibetan calendar system: document structure (months, leap months, zodiac system, Losar variants). Write `docs/TIBETAN_CALENDAR_NOTES.md`. |
| Tue | Research key Buddhist observances in Nepal: Saga Dawa, Losar (Sonam, Gyalpo, Tamu), Buddha Jayanti overlap, Gunla. |
| Wed | Collect reference dates for Tibetan observances: 2020–2027 from official Tibetan calendar sources. Store in `tests/fixtures/tibetan_reference.json`. |
| Thu | Determine precision modes: which observances can be computed astronomically? Which require table lookup? Which are tradition-announced? Document each. |
| Fri | Design Tibetan calendar plugin structure: conversion functions, observance rules, confidence categories. |
| Sat | Review research with available academic sources (Henning, Schuh). |
| Sun | Buffer |

---

### Week 54 (Apr 5–11) — Implementation

| Day | Deliverables |
|---|---|
| Mon | Implement `engine/plugins/tibetan/plugin.py`: basic month/year conversion between Tibetan and Julian Day. |
| Tue | Implement Tibetan leap month detection logic (differs from Hindu Adhik Maas). |
| Wed | Implement Losar calculation: Sonam Lhosar (Magh Shukla 1), Gyalpo Lhosar (Magh Shukla 3), Tamu Lhosar (fixed BS date 15 Poush). |
| Thu | Implement Saga Dawa calculation: 4th Tibetan month, full moon day. |
| Fri | Add observance rules to `rules/plugins/tibetan_buddhist/`: rule definitions with confidence modes. |
| Sat | Run against reference corpus — check accuracy. |
| Sun | Buffer |

---

### Week 55 (Apr 12–18) — API Integration & Validation

| Day | Deliverables |
|---|---|
| Mon | Wire Tibetan plugin into API: `/v2/convert?calendar=tibetan`, `/v2/festivals?calendar=tibetan`. |
| Tue | Ensure all Tibetan responses include `confidence` and `method`: computed vs table-lookup vs approximate. |
| Wed | Write plugin validation suite for Tibetan module: accuracy against reference dates. |
| Thu | Cross-reference with Nepal Patro/Hamro Patro for Lhosar dates — verify consistency. |
| Fri | Add Tibetan festivals to festivals.json with proper metadata and rule links. |
| Sat | Frontend: display Tibetan festivals in discovery UI with appropriate badges. |
| Sun | Buffer |

---

### Week 56 (Apr 19–25) — M14 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full regression including Tibetan endpoints. |
| Tue | Document Tibetan module limitations and approximation methods. |
| Wed | Plugin validation report generated and stored. |
| Thu | Update technical report with Buddhist/Tibetan coverage. |
| Fri | M14 postmortem. Git tag `v2.2.1-m14`. |
| Sat–Sun | Buffer |

**M14 Definition of Done**: Tibetan/Buddhist observance module operational with documented confidence. Endpoints return method metadata.

---

## M15: Regional Hindu Rule Variants (Apr 26 – May 23, 2027)

### Week 57 (Apr 26 – May 2) — Variant Research

| Day | Deliverables |
|---|---|
| Mon | Document known variant patterns: Amant vs Purnimant, North vs South Indian, Terai vs Hills, Newari vs pan-Hindu. |
| Tue | Identify specific festivals with known regional disagreements: e.g., Ekadashi timing, Shivaratri observance, Chhath calculation. |
| Wed | Design `RuleProfile` schema: `{ profile_id, tradition, region, variant_rules, notes }`. |
| Thu | Implement variant identifier system: same festival ID → multiple `ObservanceVariant` results, each tagged with tradition/region. |
| Fri | Build variant mapping dataset: for each of 15 priority festivals, document known regional variations with sources. `data/variants/regional_map.json`. |
| Sat | Review with available academic sources on Nepali festival variations. |
| Sun | Buffer |

---

### Week 58 (May 3–9) — Variant Engine Implementation

| Day | Deliverables |
|---|---|
| Mon | Implement `calculate_with_variants(festival_id, year, profiles) → list[ObservanceVariant]`: returns all variant results. |
| Tue | Each variant includes: `{ date, profile_id, tradition, region, confidence, rule_used, notes }`. |
| Wed | Add variant support to API: `/v2/festivals/{id}/dates?variants=true` returns array of variant interpretations. |
| Thu | Default behavior (no `variants` flag): return primary/most-common interpretation. |
| Fri | Implement diaspora patterns: "I follow North Indian tradition but live in Kathmandu" → applicable rule profile. |
| Sat | Test with known variant cases. |
| Sun | Buffer |

---

### Week 59 (May 10–16) — Variant Validation & Content

| Day | Deliverables |
|---|---|
| Mon | Validate variant results against regional calendars for 3 test festivals. |
| Tue | Add variant information to festival detail content: "In Bhaktapur, this festival is observed on..." |
| Wed | Update mythology content to acknowledge regional stories and practices. |
| Thu | Frontend: show variant indicators on festival dates when variants exist. |
| Fri | Add "View other observance dates" toggle in FestivalDetail. |
| Sat | UX review of variant display. |
| Sun | Buffer |

---

### Week 60 (May 17–23) — M15 Hardening

| Day | Deliverables |
|---|---|
| Mon | Full regression with variant system enabled. |
| Tue | Verify default (non-variant) behavior unchanged. |
| Wed | Document variant system: `docs/REGIONAL_VARIANTS.md`. |
| Thu | Update evaluation harness to score variants separately. |
| Fri | M15 postmortem. Git tag `v2.2.2-m15`. Old v1 endpoints officially sunset. |
| Sat–Sun | Buffer |

**M15 Definition of Done**: Same festival can return multiple accepted observances with clear labels. Diaspora patterns supported.

---

## M16: Islamic Calendar Integration (May 24 – Jun 20, 2027)

### Week 61 (May 24–30) — Islamic Calendar Research

| Day | Deliverables |
|---|---|
| Mon | Research Hijri calendar: tabular vs astronomical vs Saudi-announced modes. Document in `docs/ISLAMIC_CALENDAR_NOTES.md`. |
| Tue | Research Islamic observances in Nepal: Eid-ul-Fitr, Eid-ul-Adha, Shab-e-Barat, Muharram. Government holiday dates for 2080–2082 BS. |
| Wed | Collect reference dates for Islamic holidays: 2020–2027 from official sources. Store in `tests/fixtures/islamic_reference.json`. |
| Thu | Design Islamic calendar plugin: tabular (Type IIa/IIc) + astronomical (Makkah-based) modes with declared confidence per mode. |
| Fri | Note: Islamic dates in Nepal follow government announcement, not pure calculation. Design override pathway for announced dates. |
| Sat | Review research. |
| Sun | Buffer |

---

### Week 62 (May 31 – Jun 6) — Implementation

| Day | Deliverables |
|---|---|
| Mon | Implement `engine/plugins/islamic/plugin.py`: tabular Hijri conversion (Kuwaiti algorithm). |
| Tue | Implement astronomical mode: Hilal (new crescent moon) visibility calculation using existing ephemeris. |
| Wed | Implement observation rules for key holidays: Eid calculation (1 Shawwal), Eid-ul-Adha (10 Dhul Hijjah), etc. |
| Thu | Wire into API: `/v2/convert?calendar=hijri`, `/v2/festivals?calendar=islamic`. |
| Fri | Each response includes `mode: "tabular"|"astronomical"|"announced"` and `confidence`. |
| Sat | Run against reference corpus. |
| Sun | Buffer |

---

### Week 63 (Jun 7–13) — Validation & Integration

| Day | Deliverables |
|---|---|
| Mon | Validate against official Nepal government Islamic holiday dates. |
| Tue | Cross-reference with international Islamic calendars. |
| Wed | Handle Nepal-specific: government sometimes shifts Islamic holidays for national schedule. Include override mechanism. |
| Thu | Add Islamic festivals to festivals.json with proper metadata. |
| Fri | Frontend: Islamic festival display with appropriate styling. |
| Sat | Plugin validation suite results. |
| Sun | Buffer |

---

### Week 64 (Jun 14–20) — M16 Hardening

| Day | Deliverables |
|---|---|
| Mon–Tue | Full regression and cross-calendar tests. |
| Wed–Thu | Documentation and limitation disclosure for Islamic module. |
| Fri | M16 postmortem. Git tag `v2.2.3-m16`. |
| Sat–Sun | Buffer |

**M16 Definition of Done**: Islamic calendar conversion and observances available with mode + confidence metadata.

---

## M17: Hebrew Calendar Integration (Jun 21 – Jul 18, 2027)

### Week 65–68

**Pattern**: Same 4-week structure as M16, applied to Hebrew calendar.

| Week | Focus |
|---|---|
| Week 65 | Research Hebrew calendar (Metonic cycle, leap years, postponement rules), collect reference dates for major holidays (Rosh Hashanah, Yom Kippur, Passover, Hanukkah). |
| Week 66 | Implement `engine/plugins/hebrew/plugin.py`: full Hebrew-to-JD conversion (accurate — Hebrew calendar is formulaic). Implement observance rules. Wire into API. |
| Week 67 | Validate against reference dates across 30+ years. Cross-reference with hebcal.com. Add to festivals.json. Frontend display. |
| Week 68 | Regression, documentation, M17 postmortem. Git tag `v2.2.4-m17`. |

**M17 Definition of Done**: Hebrew conversion and observances pass acceptance suite across decades.

---

## M18: Chinese Lunisolar Integration (Jul 19 – Aug 15, 2027)

### Week 69–72

**Pattern**: Same 4-week structure.

| Week | Focus |
|---|---|
| Week 69 | Research Chinese lunisolar calendar (solar terms, leap month rules, zodiac year boundaries). Collect reference dates for Chinese New Year, Mid-Autumn, Dragon Boat, Qingming. |
| Week 70 | Implement `engine/plugins/chinese/plugin.py`: solar term calculation (using existing ephemeris), month numbering, leap month detection. Wire into API with confidence metadata. |
| Week 71 | Validate month boundaries and leap month behavior against Hong Kong Observatory data. Add key observances to festivals.json. Frontend display. |
| Week 72 | Regression, documentation, M18 postmortem. Git tag `v2.2.5-m18`. |

**M18 Definition of Done**: Chinese lunisolar module available under same API contract with validated month boundaries.

---

## M19: Cross-Calendar Resolver (Aug 16 – Sep 12, 2027)

### Week 73 (Aug 16–22) — Conflict Analysis

| Day | Deliverables |
|---|---|
| Mon | Identify real-world cross-calendar conflicts: dates where festivals from different traditions overlap or conflict. Build `data/cross_calendar/conflicts.json`. |
| Tue | Classify conflict types: scheduling conflicts (same day, different festivals), disagreements (different calendars give different dates for same-origin observance), complementary (festivals that are related across traditions). |
| Wed | Design `CrossCalendarResolver` interface: given location, date, tradition context → return sorted list of applicable observances. |
| Thu | Design ranking algorithm: priority based on location (Nepal → Hindu/Buddhist first), user preference, official government calendar status. |
| Fri | Write resolver specification: `docs/CROSS_CALENDAR_RESOLVER.md`. |
| Sat–Sun | Buffer |

---

### Week 74 (Aug 23–29) — Resolver Implementation

| Day | Deliverables |
|---|---|
| Mon | Implement `resolve_observances(date, location, preferences) → list[RankedObservance]`. |
| Tue | Each result includes: `{ observance, calendar_family, rank, confidence, reason_code }`. |
| Wed | Implement reason codes: `PRIMARY_TRADITION`, `GOVERNMENT_HOLIDAY`, `ASTRONOMICAL_MATCH`, `USER_PREFERRED`, `REGIONAL_CUSTOM`. |
| Thu | Wire into API: `/v2/observances?date=2027-10-15&location=kathmandu` returns resolved, ranked list. |
| Fri | Handle "what's happening today" query: aggregate all calendars, resolve conflicts, return unified view. |
| Sat–Sun | Buffer |

---

### Week 75 (Aug 30 – Sep 5) — Disagreement Datasets & Testing

| Day | Deliverables |
|---|---|
| Mon | Generate disagreement dataset: for each cross-calendar conflict, document resolution and expected ranking. |
| Tue | Write resolver tests: assert correct rankings for 20+ conflict scenarios. |
| Wed | Test with real-world scenarios: Dashain + Eid overlap year, Buddhist + Hindu Purnima differences. |
| Thu | Frontend: "Today" view shows resolved observances from all loaded calendars. |
| Fri | Frontend: calendar view shows multi-tradition overlay with color-coded badges. |
| Sat–Sun | Buffer |

---

### Week 76 (Sep 6–12) — M19 Hardening

| Day | Deliverables |
|---|---|
| Mon–Tue | Full regression across all calendar modules + resolver. |
| Wed–Thu | Document resolver methodology and ranking algorithm. |
| Fri | M19 postmortem. Git tag `v2.3.0-m19`. |
| Sat–Sun | Buffer |

**M19 Definition of Done**: Cross-calendar resolver returns candidate observances with ranked confidence and reason codes.

---

## M20: Integration Surfaces (Sep 13 – Oct 10, 2027)

### Week 77 (Sep 13–19) — iCal Feed Generation

| Day | Deliverables |
|---|---|
| Mon | Implement iCal event generation: festival → VEVENT with DTSTART, DTEND, SUMMARY, DESCRIPTION, LOCATION, CATEGORIES. |
| Tue | Implement feed endpoint: `GET /v2/feeds/ical?festivals=dashain,tihar&years=2&lang=en` returns valid .ics file. |
| Wed | Implement subscription feeds: `webcal://parva.dev/feed/all.ics`, `webcal://parva.dev/feed/national.ics`, `webcal://parva.dev/feed/newari.ics`. |
| Thu | Add custom feed builder: `webcal://parva.dev/feed/custom?festivals=dashain,tihar,chhath&lang=ne`. |
| Fri | Test: import into Google Calendar, Apple Calendar, Outlook. Verify events appear correctly. |
| Sat | Add bilingual support: events in both English and Nepali (using LANGUAGE property). |
| Sun | Buffer |

---

### Week 78 (Sep 20–26) — Webhook Subscriptions

| Day | Deliverables |
|---|---|
| Mon | Design webhook subscription model: `{ subscriber_url, festivals[], remind_days_before[], format }`. |
| Tue | Implement subscription CRUD: `POST /v2/webhooks/subscribe`, `GET /v2/webhooks/{id}`, `DELETE /v2/webhooks/{id}`. |
| Wed | Implement notification dispatcher: checks upcoming festivals daily, sends webhook for matching subscriptions. |
| Thu | Implement duplicate suppression: don't send same notification twice. Track delivery status. |
| Fri | Implement retry logic: failed deliveries retried with exponential backoff (max 3 attempts). |
| Sat | Write E2E webhook test: subscribe → trigger → verify delivery. |
| Sun | Buffer |

---

### Week 79 (Sep 27 – Oct 3) — Stream Endpoints & Telegram Bot

| Day | Deliverables |
|---|---|
| Mon | Implement "next observance" endpoint: `GET /v2/observances/next?calendar=bs&traditions=hindu` — returns next upcoming observance. |
| Tue | Implement stream-style polling endpoint for apps that can't use webhooks. |
| Wed | Build Telegram bot proof-of-concept: `/panchanga` returns today's panchanga, `/upcoming` returns next 7 days of festivals. |
| Thu | Deploy bot on free tier (Vercel serverless or PythonAnywhere). |
| Fri | Write integration tests for all delivery mechanisms. |
| Sat–Sun | Buffer |

---

### Week 80 (Oct 4–10) — M20 Hardening

| Day | Deliverables |
|---|---|
| Mon | E2E test suite: iCal import, webhook delivery, stream polling. |
| Tue | Calendar app compatibility matrix: test across Google, Apple, Outlook, Thunderbird. |
| Wed | Documentation: `docs/INTEGRATIONS.md` — iCal setup guide, webhook API reference, bot usage. |
| Thu–Fri | M20 postmortem. Git tag `v2.3.1-m20`. |
| Sat–Sun | Buffer |

**M20 Definition of Done**: Third-party apps can subscribe to observance updates via iCal, webhooks, and bot.

---

## M21: SDK Layer (Oct 11 – Nov 7, 2027)

### Week 81 (Oct 11–17) — SDK Design & Code Generation

| Day | Deliverables |
|---|---|
| Mon | Evaluate OpenAPI code generators: openapi-generator, openapi-typescript, datamodel-code-generator. Select best for Python, TypeScript, Go. |
| Tue | Generate Python SDK skeleton from OpenAPI spec. Add typed models, client class, async support. |
| Wed | Generate TypeScript SDK skeleton. Add typed models, fetch-based client, tree-shakeable exports. |
| Thu | Generate Go SDK skeleton. Add typed structs, http.Client wrapper, context support. |
| Fri | Define SDK package names: `parva` (PyPI), `@parva/sdk` (npm), `github.com/parva-dev/parva-go` (Go). |
| Sat–Sun | Buffer |

---

### Week 82 (Oct 18–24) — SDK Implementation & Examples

| Day | Deliverables |
|---|---|
| Mon | Python SDK: enhance generated code with convenience methods (`Parva.today()`, `Parva.upcoming()`, `Parva.convert()`), error handling, retry logic. |
| Tue | TypeScript SDK: same treatment. Add browser and Node.js compatibility. |
| Wed | Go SDK: same treatment. Add context cancellation, structured errors. |
| Thu | Write SDK examples: 3 per language covering panchanga, festival lookup, and date conversion. |
| Fri | Write SDK READMEs with quick-start guides. |
| Sat–Sun | Buffer |

---

### Week 83 (Oct 25–31) — SDK Testing & Publishing

| Day | Deliverables |
|---|---|
| Mon | Write SDK contract parity tests: for each API endpoint, verify SDK method returns correctly typed response matching API contract. |
| Tue | Write golden fixture tests: snapshot API responses → SDK deserialization produces identical typed objects. |
| Wed | Build sample apps: Python CLI tool, TypeScript web widget, Go server middleware. |
| Thu | Publish to test registries: TestPyPI, npm --dry-run, local Go module. |
| Fri | Publish official v1.0.0 of all three SDKs. |
| Sat–Sun | Buffer |

---

### Week 84 (Nov 1–7) — M21 Hardening

| Day | Deliverables |
|---|---|
| Mon | Install published SDKs in clean environments — verify they work. |
| Tue | Add SDK tests to CI: every API change triggers SDK parity check. |
| Wed–Thu | Documentation: SDK reference docs auto-generated and hosted. |
| Fri | M21 postmortem. Git tag `v2.3.2-m21`. |
| Sat–Sun | Buffer |

**M21 Definition of Done**: Python, TypeScript, Go SDKs published and passing integration tests.

---

## M22: Community Governance (Nov 8 – Dec 5, 2027)

### Week 85–88

| Week | Focus |
|---|---|
| Week 85 | Design RFC workflow: proposal template, review criteria, evidence requirements, approval process. Implement as GitHub Issue/PR templates. Write `CONTRIBUTING.md` and `docs/GOVERNANCE.md`. |
| Week 86 | Implement reviewer roles: reviewers sign off on rule changes with GPG signatures. Build `scripts/verify_approval.py`. Create verification checklist per change type (rule fix, new festival, data correction). |
| Week 87 | Dog-food the process: submit 3 rule changes through RFC workflow. Test evidence linking (each change cites sources). Verify audit trail. Write contributor onboarding guide. |
| Week 88 | M22 hardening: CI enforces signed commits on `rules/` changes. Documentation finalized. Git tag `v2.3.3-m22`. |

**M22 Definition of Done**: Every rule change has traceable review + evidence metadata. Community can contribute through documented process.

---

## M23: Public Transparency Logs (Dec 6, 2027 – Jan 2, 2028)

### Week 89–92

| Week | Focus |
|---|---|
| Week 89 | Design transparency log format: append-only log of snapshot hashes, rule changes, and evaluations. Research existing solutions (sigstore, rekor) for optional integration. |
| Week 90 | Implement local transparency log: `data/transparency/log.jsonl` — each entry signed and chained. Implement `scripts/audit_log.py` to verify log integrity. |
| Week 91 | Add optional blockchain anchoring: publish Merkle root to a public chain (e.g., Bitcoin OP_RETURN or Ethereum memo) as a mirror. Document: chain is a mirror, not a dependency. Implement replay audit: reconstruct any historical state from log. |
| Week 92 | Publish transparency log publicly. Write verification instructions. M23 postmortem. Git tag `v2.4.0-m23`. |

**M23 Definition of Done**: Third parties can verify no silent history rewrites. Audit replay operational.

---

## M24: Global Beta Launch (Jan 3 – Feb 1, 2028)

### Week 93 (Jan 3–9) — Infrastructure & Deployment

| Day | Deliverables |
|---|---|
| Mon | Set up production deployment: Render/Railway (backend), Vercel (frontend), Cloudflare (CDN/cache). |
| Tue | Configure custom domain (parva.dev or free alternative). SSL, CORS, rate limiting. |
| Wed | Set up monitoring: uptime checks (free tier UptimeRobot), error tracking (Sentry free tier), basic analytics (Plausible/Umami). |
| Thu | Deploy all calendar modules, SDKs docs, iCal endpoints, webhook system. |
| Fri | Smoke test entire production surface. |
| Sat–Sun | Buffer |

---

### Week 94 (Jan 10–16) — Benchmark Dashboard

| Day | Deliverables |
|---|---|
| Mon | Build public benchmark dashboard page: shows accuracy per calendar, per festival category, trust metrics. |
| Tue | Auto-generated from latest evaluation run. Updates on each deployment. |
| Wed | Add comparison section: Parva vs Nepal Patro vs Hamro Patro (where data available). |
| Thu | Add API status section: uptime, response time, last verification date. |
| Fri | Deploy dashboard. |
| Sat–Sun | Buffer |

---

### Week 95 (Jan 17–23) — Beta Testing & Feedback

| Day | Deliverables |
|---|---|
| Mon | Write launch announcement: blog post/README update explaining what Parva offers. |
| Tue | Share with Nepali developer communities (if applicable). |
| Wed | Monitor: error rates, response times, unexpected inputs. |
| Thu | Collect feedback: what works, what's confusing, what's missing. |
| Fri | Triage feedback into backlog for Year 3. |
| Sat–Sun | Buffer |

---

### Week 96 (Jan 24 – Feb 1) — Year 2 Release

| Day | Deliverables |
|---|---|
| Mon | Fix any critical issues from beta feedback. |
| Tue | Final global beta benchmark run including all calendar families. |
| Wed | Publish uptime, error, and accuracy metrics. |
| Thu | Git tag `v2.5.0-beta`. Year 2 retrospective. |
| Fri | `docs/YEAR_2_RETROSPECTIVE.md`. |
| Sat–Sun | Rest. Plan Year 3 kickoff. |

**M24 Definition of Done**: Public beta stable with published uptime/error/accuracy metrics. Multi-calendar API live. Year 2 complete. 🌍

---

*End of Year 2 Weekly Plan — Weeks 49–96, from plugin architecture through global beta launch.*
