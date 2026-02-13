# PROJECT PARVA — Task Tracker

> **Current Phase**: CONTENT → Day 4  
> **Current Day**: Dashain & Tihar Complete Content  
> **Last Updated**: February 3, 2026

---

## Quick Status

| Phase | Status | Progress |
|-------|--------|----------|
| **Planning** | ✅ Complete | Bible + Roadmap done |
| **Build (Days 1-3)** | ✅ Complete | All 3 days done |
| **Content (Days 4-14)** | 🔄 In Progress | Day 4 active |
| **Polish (Days 15-25)** | ⏳ Not Started | 0/11 days |
| **Demo (Days 26-30)** | ⏳ Not Started | 0/5 days |

---

## ✅ Day 1 — COMPLETE (February 2, 2026)

### Backend Complete
- [x] Bikram Sambat engine (`bikram_sambat.py`)
- [x] Tithi calculator (`tithi.py`)  
- [x] Nepal Sambat basics (`nepal_sambat.py`)
- [x] Festival calculator (`calculator.py`) — 25 festivals
- [x] Festival API models, repository, routes
- [x] Mythology module (8 deities)

### Tests Complete
- [x] 94 unit tests passing
- [x] Integration tests created

### Verified Dates
- [x] Dashain 2026: **Oct 11-25** (official ✓)
- [x] Tihar 2026: **Nov 7-11** (official ✓)
- [x] BS 2083: **Apr 14, 2026** (official ✓)

### Directory Restructuring Complete
- [x] Moved all code into `Project Parva/backend/`
- [x] Created standalone FastAPI app
- [x] Removed duplicates from parent directory

---

## ✅ Day 2 — COMPLETE (February 2, 2026)

### Festival Components
- [x] FestivalCard (glassmorphism design)
- [x] FestivalDetail (tabbed interface)
- [x] MythologySection (narrative display)
- [x] RitualTimeline (day-by-day events)
- [x] ConnectionsView (festival relationships)
- [x] DeityCard (deity information)

### Calendar Components
- [x] TemporalNavigator (sidebar with upcoming festivals)
- [x] LunarPhase (moon phase display)

### Map Components
- [x] FestivalMap (Leaflet integration)

### Core Pages
- [x] ParvaPage (main application layout)

### API Integration
- [x] useFestivals hook
- [x] useFestivalDetail hook
- [x] useCalendar hook
- [x] useTemples hook
- [x] API service module

### Verification Complete
- [x] Backend running (port 8000)
- [x] Frontend running (port 5173)
- [x] Full integration tested in browser
- [x] 3 festivals displayed in sidebar
- [x] Festival detail view working
- [x] Tab navigation working (Overview, Mythology, Rituals, Connections)
- [x] Lunar phase component showing
- [x] No console errors
- [x] Premium glassmorphism aesthetic verified

### Day 2 Success Criteria — ALL MET ✅
- ✅ Frontend starts without errors
- ✅ Festival list displays in sidebar
- ✅ Clicking festival opens detail drawer
- ✅ Map shows temple locations
- ✅ Tabs work in festival detail
- ✅ Responsive on mobile and desktop
- ✅ Countdown badges show correct days remaining

---

## ✅ Day 3 — Integration & Polish COMPLETE

### Morning Session ✅ COMPLETE
- [x] Temple data preparation (15 temples in database)
- [x] Location API (4 endpoints working: list, detail, by-festival, festivals-at-temple)
- [x] Expanded festival data from 25 to 49 festivals
- [x] Verified all tests passing (94 → 109 tests)

### Afternoon Session ✅ COMPLETE
- [x] Polish loading/error/empty states (all components verified)
- [x] Refine animations (300-600ms transitions with easing confirmed)
- [x] Browser verification (no console errors, 8 festivals, 15 temples, all tabs working)
- [x] Responsive design verified (desktop layout confirmed)

### Evening Session ✅ COMPLETE
- [x] Full integration test (109 tests passing)
- [x] Complete Indra Jatra content (710-char origin story, 8-day ritual sequence, 4 deities)
- [x] Documentation updates (TASK.md, CHANGELOG.md)


---

## ✅ Quality & Documentation Alignment (February 3, 2026)

### Bug Fixes (P1-P3)
- [x] Fixed `to_date` crash on month boundaries (using timedelta)
- [x] Fixed CORS wildcard + credentials invalid config
- [x] Fixed field mismatches: `summary→description`, `calendar_system→calendar_type`, `region→regional_focus`
- [x] Fixed `ritual_sequence` → `daily_rituals|simple_rituals`
- [x] Fixed mythology fields: `sacred_texts→scriptural_references`, `key_legends→legends`
- [x] Added `festivals` field to TempleSummary for map highlighting
- [x] Fixed mutable defaults in Pydantic models
- [x] Removed fake dates fallback (returns null instead)

### Documentation Alignment
- [x] Fixed all weekday labels in ROADMAP.md (Feb 3, 2026 is Tuesday, not Monday)
- [x] Replaced Vite boilerplate README with project-specific documentation
- [x] Added API URL configuration via environment variable (VITE_API_BASE)
- [x] Added `.env.example` for deployment configuration
- [x] Added reality-check note to PROJECT_BIBLE.md schemas section
- [x] Marked client-side tithi/BS date as "approximate" in UI

### New Documentation Created
- [x] `docs/DATE_ACCURACY_EVALUATION.md` — Compares 19 festival dates against official sources (94.7% accuracy)
- [x] `docs/DATA_SOURCES.md` — Citations for all mythology, dates, and cultural claims

---

## 🔄 Day 4 — Content Phase (February 3, 2026)

**Theme**: Dashain & Tihar Complete Content

### Dashain Content ✅
- [x] 800+ word origin story (Durga vs. Mahishasura, narrative style)
- [x] Scriptural references (Devi Mahatmya, Durga Saptashati, Devi Bhagavata Purana)
- [x] 3 legend snippets (Navadurga, Taleju temple, kite flying)
- [x] Historical context (Malla/Shah royalty, military campaigns)
- [x] Regional variations (Kathmandu, Gorkha, Terai)
- [x] 6 main days with detailed rituals:
  - Day 1: Ghatasthapana (jamara planting)
  - Day 7: Phulpati (sacred flowers procession)
  - Day 8: Maha Ashtami (Kaal Ratri, animal sacrifice)
  - Day 9: Maha Navami (vehicle/weapon blessing)
  - Day 10: Vijaya Dashami (tika, jamara, kite flying)
  - Day 15: Kojagrat Purnima (final tika)

### Tihar Content ✅
- [x] 600+ word origin story (Yama-Yamuna legend)
- [x] Scriptural references (Skanda Purana, Padma Purana, Kathasaritsagara)
- [x] 3 legend snippets (Laxmi visits, deusi-bhailo, dog guardians)
- [x] Historical context (unique Nepali traditions)
- [x] 5 days with complete rituals:
  - Day 1: Kaag Tihar (crow offering)
  - Day 2: Kukur Tihar (dog worship)
  - Day 3: Gai Tihar + Laxmi Puja (cow worship, oil lamps, bhailo)
  - Day 4: Govardhan Puja + Mha Puja (ox worship, Nepal Sambat New Year)
  - Day 5: Bhai Tika (oil circle, 7-color tika, gifts)

### In Progress
- [ ] Verify temple IDs against OSM data
- [ ] Add food tradition details
- [ ] Cross-check dates with Nepal government calendar

---

## Quick Commands

```bash
# From Project Parva directory:

# Start backend
cd backend && python3 -m uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev

# Run tests
python3 -m pytest tests/ -v

# Check test count
python3 -m pytest tests/ --collect-only -q
```

---

## File Locations

```
Project Parva/
├── backend/app/
│   ├── calendar/     # BS, NS, tithi, calculator
│   ├── festivals/    # API routes + repository
│   └── mythology/    # Deities
├── data/festivals/   # festivals.json (25)
├── tests/            # 94 unit tests
├── frontend/src/
│   ├── components/
│   │   ├── Festival/ # 13 files
│   │   ├── Calendar/ # 5 files
│   │   └── Map/      # 3 files
│   ├── pages/        # ParvaPage
│   └── hooks/        # 4 API hooks
└── pyproject.toml
```
