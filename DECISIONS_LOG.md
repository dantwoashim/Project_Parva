# PROJECT PARVA — Decisions Log

> **Purpose**: Track WHY decisions were made. When you (LLM) see a choice and wonder "why was this done this way?", check here first.

---

## Format
```
## [Date] - [Decision Title]
**Context**: What situation led to this decision
**Decision**: What was decided
**Alternatives Considered**: What else was considered
**Rationale**: Why this choice was made
**Implications**: What this affects
```

---

## [February 2, 2026] - Demo Centerpiece Festival

**Context**: Need to choose one festival to fully develop as the showcase for thesis demo.

**Decision**: **Indra Jatra** is the demo centerpiece.

**Alternatives Considered**:
- Dashain (more nationally significant)
- Tihar (more widely known)
- Bisket Jatra (most dramatic)

**Rationale**:
1. Visually dramatic — living goddess procession, chariot
2. Newari cultural depth — aligns with mythology interest
3. Clear 8-day ritual sequence — easy to visualize
4. Happens in September — recent enough to research
5. Multiple locations — good for map demonstration
6. Unique to Kathmandu — distinctive value proposition

**Implications**: 
- Indra Jatra gets hour-by-hour ritual detail
- Kumari Jatra route gets map visualization
- Demo script focuses on Indra → Dashain → Tihar autumn cycle

---

## [February 2, 2026] - 15 Priority Festivals

**Context**: Can't fully develop all 50+ Nepal festivals. Need to prioritize.

**Decision**: 15 festivals get full mythology + ritual treatment.

**Priority List**:
1. Indra Jatra (demo centerpiece)
2. Dashain
3. Tihar
4. Gai Jatra
5. Bisket Jatra
6. Buddha Jayanti
7. Teej
8. Maghe Sankranti
9. Holi
10. Ghode Jatra
11. Mha Puja
12. Yomari Punhi
13. Rato Machhindranath
14. Shivaratri
15. Janai Purnima

**Rationale**:
- Covers major national festivals (Dashain, Tihar, Holi)
- Covers significant Newari festivals (Indra Jatra, Bisket, Gai Jatra, Mha Puja)
- Covers multiple calendar systems
- Geographic spread (Valley, Terai, national)
- Seasonal spread (all seasons represented)

**Implications**:
- Content sprint days 4-14 focus on these 15
- Remaining 35 festivals get minimum data only
- Can expand later if time permits

---

## [February 2, 2026] - Calendar Implementation Approach

**Context**: Need to convert between Bikram Sambat, Nepal Sambat, and Gregorian calendars.

**Decision**: Use lookup table approach for BS conversion, astronomical calculation for tithi.

**Rationale**:
1. BS month lengths are non-formulaic — vary by year unpredictably
2. Lookup table is accurate and simple
3. Tithi calculation uses standard astronomical formulas
4. Nepal Sambat is lunar — ties to tithi calculation
5. No need for external APIs — works offline

**Alternatives Considered**:
- External calendar API (rejected: dependency, latency)
- Formula-based BS (rejected: inaccurate for Nepal)
- Hard-code all festival dates (rejected: doesn't scale to future years)

**Implications**:
- Need BS data table from 2080-2095 in constants.py
- Tithi calculation may have ±1 day accuracy (acceptable)
- Can verify against Nepal government calendar

---

## [February 2, 2026] - No Database, JSON Only

**Context**: Need to store festival, deity, and temple data.

**Decision**: Use JSON files, no database.

**Rationale**:
1. 50 festivals, ~50 deities, ~100 temples — small dataset
2. JSON is human-readable and git-trackable
3. No database setup complexity
4. Loads in memory at startup — fast queries
5. Easy to edit and verify content
6. Thesis project, not production system

**Implications**:
- All data in `data/festivals/` folder as JSON
- Repository pattern loads from JSON files
- In-memory caching at startup
- If dataset grows, migrate to SQLite

---

## [February 2, 2026] - Build Phase is 3 Days Only

**Context**: Traditional roadmaps allocate weeks to implementation.

**Decision**: Complete all code in 3 days, use remaining 27 days for content/polish.

**Rationale**:
1. LLM (me) can implement features quickly
2. Content research/creation is the actual bottleneck
3. Visual polish takes iteration time
4. Code can always be fixed; content needs human curation
5. Premium feel comes from content + polish, not code

**Implications**:
- Day 1: Complete backend (calendar engine + APIs)
- Day 2: Complete frontend (all components)
- Day 3: Integration and MVP
- Days 4-14: Content sprint
- Days 15-25: Polish sprint
- Days 26-30: Demo preparation

---

## Template for Future Decisions

```markdown
## [Date] - [Decision Title]
**Context**: 
**Decision**: 
**Alternatives Considered**:
**Rationale**:
**Implications**:
```
