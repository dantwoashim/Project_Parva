# PROJECT PARVA — 30-Day Roadmap

> **Reference**: Always read PROJECT_BIBLE.md before starting any day's work.

---

## Phase Overview

| Phase | Days | Focus | LLM Handles | You Handle |
|-------|------|-------|-------------|------------|
| **BUILD** | 1-3 | Complete implementation | All code, tests, structure | Review, approve, test |
| **CONTENT** | 4-14 | Festival mythology | Draft generation, data structure | Research, verify, authenticate |
| **POLISH** | 15-25 | Premium experience | Animation code, edge cases | Design decisions, visual QA |
| **DEMO** | 26-30 | Thesis preparation | Docs, slides | Practice, present |

---

## PHASE 1: BUILD (Days 1-3)

### DAY 1 — February 3, 2026 (Tuesday)
**Theme**: Complete Backend in One Day

#### Morning Session (3-4 hours)

**Hour 1: Project Setup**
```
□ Create new git branch: parva-main
□ Clean unnecessary infrastructure code from backend
□ Create directory structure:
  - backend/app/calendar/
  - backend/app/festivals/
  - backend/app/mythology/
  - data/festivals/
□ Update backend/app/main.py to include new routers
```

**Hour 2-3: Bikram Sambat Engine**
```
□ Create backend/app/calendar/__init__.py
□ Create backend/app/calendar/constants.py
  - BS_CALENDAR_DATA dict (2080-2095)
  - BS_MONTH_NAMES list
  - Reference dates for conversion

□ Create backend/app/calendar/bikram_sambat.py
  - bs_to_gregorian(year, month, day) → date
  - gregorian_to_bs(date) → tuple[year, month, day]
  - get_bs_month_name(month) → str
  - get_bs_year_start(year) → date
  - days_in_bs_month(year, month) → int
  - Full docstrings with examples
  - Type hints on all functions

□ Create tests/unit/test_bikram_sambat.py
  - Test BS New Year conversions 2080-2090
  - Test month boundaries
  - Test leap year handling
  - Test invalid date handling
  - Minimum 30 test cases
```

**Hour 4: Tithi Calculator**
```
□ Create backend/app/calendar/tithi.py
  - calculate_julian_day(date) → float
  - calculate_sun_longitude(jd) → float
  - calculate_moon_longitude(jd) → float
  - calculate_tithi(date) → tuple[int, str]  # (tithi 1-15, paksha)
  - find_next_tithi(tithi, paksha, after_date) → date
  - Full docstrings explaining astronomical formulas

□ Create tests/unit/test_tithi.py
  - Test known new moon dates
  - Test known full moon dates
  - Test find_next_tithi for known festivals
  - Minimum 20 test cases
```

**LUNCH BREAK**

#### Afternoon Session (4-5 hours)

**Hour 5: Nepal Sambat & Unified Calculator**
```
□ Create backend/app/calendar/nepal_sambat.py
  - nepal_sambat_to_gregorian(year, month, day) → date
  - gregorian_to_nepal_sambat(date) → tuple
  - is_nepal_new_year(date) → bool
  - Document the Newari lunar calendar specifics

□ Create backend/app/calendar/calculator.py
  - CalendarType enum (BIKRAM_SAMBAT, NEPAL_SAMBAT, TIBETAN, SOLAR)
  - calculate_festival_date(festival_id, year) → DateRange
  - parse_calculation_rule(rule: CalendarRule) → date
  - get_upcoming_festivals(start_date, days) → list[FestivalDate]
  - Full integration with BS and tithi calculators

□ Create tests/unit/test_calculator.py
  - Test Dashain 2026, 2027, 2028 dates
  - Test Tihar dates
  - Test Maghe Sankranti (solar)
  - Test Nepal Sambat New Year
  - Minimum 25 test cases
```

**Hour 6-7: Festival Models & Repository**
```
□ Create backend/app/festivals/__init__.py

□ Create backend/app/festivals/models.py
  - CalendarRule model (complete from Bible)
  - FestivalMythology model (complete from Bible)
  - RitualEvent model
  - RitualSequence model
  - DaySchedule model
  - Festival model (complete with all fields)
  - FestivalSummary model (for list views)
  - FestivalDate model (for date queries)

□ Create backend/app/festivals/repository.py
  - load_festivals() → list[Festival]
  - get_festival_by_id(id) → Festival | None
  - get_festivals_by_category(category) → list[Festival]
  - get_festivals_by_region(region) → list[Festival]
  - search_festivals(query) → list[Festival]
  - Caching for performance
```

**Hour 8-9: Festival API Routes**
```
□ Create backend/app/festivals/routes.py
  - GET /api/festivals
    - Query params: upcoming, days, category, region
    - Returns list[FestivalSummary]
  - GET /api/festivals/{festival_id}
    - Returns complete Festival
  - GET /api/festivals/{festival_id}/dates
    - Query param: years (default 5)
    - Returns list of date ranges
  - GET /api/festivals/{festival_id}/ritual
    - Returns RitualSequence only

□ Create API tests
  - tests/integration/test_festival_api.py
  - Test all endpoints
  - Test query parameters
  - Test error handling

□ Update backend/app/main.py
  - Import and include festival router
  - Import and include calendar router
```

**Hour 10: Seed Initial Festival Data**
```
□ Create data/festivals/festivals.json
  - Seed 25 festivals with minimum data:
    - id, name_en, name_ne
    - calendar_system, calculation_rule
    - category, region, significance_level
    - tagline, summary (100 words)
    - primary_location_ids (empty for now)
    - related_festivals (connections)
  
  Priority festivals to seed:
    1. indra-jatra
    2. dashain
    3. tihar
    4. gai-jatra
    5. bisket-jatra
    6. buddha-jayanti
    7. teej
    8. maghe-sankranti
    9. holi
    10. ghode-jatra
    11. mha-puja
    12. yomari-punhi
    13. shivaratri
    14. janai-purnima
    15. rato-machhindranath
    16-25: Additional festivals
```

#### Evening Session (2 hours)

**Hour 11: Verification**
```
□ Run all calendar tests: pytest tests/unit/test_*.py -v
□ Run API tests: pytest tests/integration/ -v
□ Start backend: uvicorn app.main:app --reload
□ Test endpoints manually via Swagger UI
□ Verify Dashain 2026 date calculation matches known date
□ Document any bugs found
```

**Hour 12: Day 1 Documentation**
```
□ Update TASK.md with completed items
□ Git commit: "feat: Complete calendar engine and festival API"
□ Document any deviations from plan
□ Note areas needing refinement
```

**DAY 1 SUCCESS CRITERIA**
```
✓ Backend starts without errors
✓ /api/festivals returns list of 25 festivals
✓ /api/festivals/dashain returns correct festival
✓ /api/festivals/dashain/dates?years=3 returns correct dates for 2026-2028
✓ /api/calendar/convert converts BS correctly
✓ All unit tests pass (75+ tests)
```

---

### DAY 2 — February 4, 2026 (Wednesday)
**Theme**: Complete Frontend in One Day

#### Morning Session (4 hours)

**Hour 1: Frontend Cleanup & Setup**
```
□ Remove infrastructure-specific components:
  - Delete or archive: CascadeVisualization.jsx
  - Delete or archive: SimulationControls.jsx
  - Delete or archive: BudgetStudio.jsx, PrioritiesPage.jsx
  - Keep: LivingMap/, layout/, primitives/

□ Create new directory structure:
  - frontend/src/components/Festival/
  - frontend/src/components/Calendar/
  - frontend/src/components/Map/
  - frontend/src/pages/ParvaPage.jsx

□ Update frontend/src/App.jsx
  - Remove old routes
  - Add ParvaPage as main route

□ Install any needed packages:
  - npm install date-fns (if not present)
```

**Hour 2-3: Festival Card Component**
```
□ Create frontend/src/components/Festival/FestivalCard.jsx
  - Props: festival (FestivalSummary), onClick, isActive
  - Structure:
    - Hero image area (with gradient overlay)
    - Festival name (English + Nepali)
    - Date range with countdown
    - Tagline
    - Category badges
    - "Learn More" button
  - Animations:
    - Hover lift effect
    - Active state glow
    - Smooth enter animation
  - Responsive: works at 280px-600px widths

□ Create frontend/src/components/Festival/FestivalCard.css
  - Use design system variables from PROJECT_BIBLE
  - Glass-card effect
  - Gradient overlays
  - Badge styling
  - Animation keyframes
```

**Hour 4: Temporal Navigator Component**
```
□ Create frontend/src/components/Calendar/TemporalNavigator.jsx
  - Props: festivals, selectedDate, onDateChange, onFestivalSelect
  - Structure:
    - Header with current month/year
    - "Next 30 days" / "Next 90 days" toggle
    - Scrollable list of upcoming festivals
    - Festival cards in compact mode
    - Countdown badges (12 days, 3 weeks, etc.)
  - Features:
    - Infinite scroll for more festivals
    - Active festival highlight
    - Empty state if no festivals

□ Create frontend/src/components/Calendar/TemporalNavigator.css
  - Sidebar styling (fixed width or responsive)
  - Scroll behavior
  - Date grouping headers
```

**LUNCH BREAK**

#### Afternoon Session (4 hours)

**Hour 5: Festival Detail Component**
```
□ Create frontend/src/components/Festival/FestivalDetail.jsx
  - Props: festival (full Festival object), onClose
  - Structure:
    - Header: Hero image, name, dates
    - Tabs: Overview | Mythology | Ritual | Connections
    - Overview tab: Summary, locations, quick facts
    - Content area with scroll
    - Close button
  - Animations:
    - Slide in from right (drawer style)
    - Tab switch transitions
    - Content fade

□ Create frontend/src/components/Festival/FestivalDetail.css
  - Full-height drawer on desktop
  - Full-screen on mobile
  - Tab styling
  - Content typography
```

**Hour 6: Mythology Section**
```
□ Create frontend/src/components/Festival/MythologySection.jsx
  - Props: mythology (FestivalMythology)
  - Structure:
    - Origin story (full text, rich formatting)
    - Sacred text references (badges)
    - Key legends (expandable sections)
    - Cultural significance block
  - Features:
    - Image placeholders (for future content)
    - Pull quotes for dramatic moments
    - "Read more" expansion for long stories

□ Create frontend/src/components/Festival/MythologySection.css
  - Mythology typography (serif, larger line height)
  - Quote styling
  - Legend cards
```

**Hour 7: Ritual Timeline Component**
```
□ Create frontend/src/components/Festival/RitualTimeline.jsx
  - Props: ritualSequence, onLocationClick
  - Structure:
    - Day selector (horizontal scroll for multi-day festivals)
    - Vertical timeline with time markers
    - Event cards connected by line
    - Location links (clickable, opens map)
  - Features:
    - Current time indicator (if festival is ongoing)
    - Scroll to current event
    - Compact and expanded modes

□ Create frontend/src/components/Festival/RitualTimeline.css
  - Timeline track styling
  - Event card styling
  - Time marker styling
  - Day selector tabs
```

**Hour 8: Festival Map Component**
```
□ Create frontend/src/components/Map/FestivalMap.jsx
  - Props: festivals, selectedFestival, onFestivalSelect, onTempleClick
  - Features:
    - Leaflet map with existing OSM tiles
    - Temple markers (custom icons)
    - Festival "aura" when selected (glowing radius)
    - Cluster markers for dense areas
    - Smooth fly-to on festival select
  - Reuse from LivingMap:
    - Base map setup
    - Layer management
    - Particle system (adapted for "pilgrimage paths")

□ Create frontend/src/components/Map/FestivalMap.css
  - Custom marker styling
  - Aura animation
  - Popup styling
```

#### Evening Session (3 hours)

**Hour 9: Main Page Assembly**
```
□ Create frontend/src/pages/ParvaPage.jsx
  - Layout:
    - Left sidebar: TemporalNavigator (collapsible on mobile)
    - Center: FestivalMap (primary view)
    - Right drawer: FestivalDetail (opens on select)
  - State management:
    - selectedFestival
    - timeRange (30/90 days)
    - mapCenter, mapZoom
  - Data fetching:
    - useFestivals hook for list
    - Fetch detail on selection




□ Create frontend/src/pages/ParvaPage.css
  - Three-column layout
  - Responsive breakpoints
  - Transition animations
```

**Hour 10: API Hooks**
```
□ Create frontend/src/hooks/useFestivals.js
  - Fetch upcoming festivals
  - Handle loading/error states
  - Caching with stale-while-revalidate

□ Create frontend/src/hooks/useFestivalDetail.js
  - Fetch single festival
  - Handle loading/error states

□ Create frontend/src/hooks/useCalendar.js
  - Calendar conversion calls
  - Current tithi display

□ Update frontend/src/services/api.js
  - Add festival endpoints
  - Add calendar endpoints
```

**Hour 11: Integration & Testing**
```
□ Start frontend: npm run dev
□ Test full flow:
  - Page loads with festival list
  - Click festival → detail opens
  - Map shows locations
  - Tabs work in detail view
□ Test responsive:
  - Mobile view (320px)
  - Tablet view (768px)
  - Desktop view (1440px)
□ Document bugs
```

**DAY 2 SUCCESS CRITERIA**
```
✓ Frontend starts without errors
✓ Festival list displays in sidebar
✓ Clicking festival opens detail drawer
✓ Map shows temple locations
✓ Tabs work in festival detail
✓ Responsive on mobile and desktop
✓ Countdown badges show correct days remaining
```

---

### DAY 3 — February 5, 2026 (Thursday)
**Theme**: Integration, Polish, Complete MVP

#### Morning Session (3 hours)

**Hour 1-2: Temple Data Preparation**
```
□ Create script: scripts/prepare_temple_data.py
  - Read data/processed/facilities.geojson
  - Filter for religious sites:
    - facility_type: temple, stupa, monastery, shrine
    - Or name contains: mandir, temple, stupa, gumba, bahal
  - Extract relevant fields:
    - id, name, name_ne, coordinates, facility_type
  - Add placeholder festival connections
  - Output: data/festivals/temples.json

□ Create data/festivals/festival_locations.json
  - Map festival IDs to temple IDs
  - Include ritual roles for each location
  - Format:
    {
      "indra-jatra": {
        "primary": ["temple_id_1", "temple_id_2"],
        "roles": {
          "temple_id_1": "Main celebration venue",
          "temple_id_2": "Kumari's residence"
        }
      }
    }
```

**Hour 3: Location API**
```
□ Create backend/app/locations/routes.py
  - GET /api/temples
    - Query params: festival, bounds
    - Returns list of temples
  - GET /api/temples/{temple_id}
    - Returns temple detail
  - GET /api/temples/{temple_id}/festivals
    - Returns festivals at this temple

□ Update main.py to include locations router
□ Test endpoints
```

**BRUNCH BREAK**

#### Midday Session (4 hours)

**Hour 4-5: Lunar Phase Component**
```
□ Create frontend/src/components/Calendar/LunarPhase.jsx
  - Props: date (current date)
  - Features:
    - Shows current lunar phase visually
    - Displays tithi number
    - Shows paksha (shukla/krishna)
    - Tooltip explaining what this means
  - Repurpose KarmaGauge animation for moon phase

□ Create frontend/src/components/Calendar/LunarPhase.css
  - Moon visualization (CSS or SVG)
  - Phase animation (subtle glow)
  - Info tooltip
```

**Hour 5-6: Connections View**
```
□ Create frontend/src/components/Festival/ConnectionsView.jsx
  - Props: festival, allFestivals, deities
  - Features:
    - Related festivals as linked cards
    - Shared deities highlighted
    - Visual graph showing connections (optional)
    - Click to navigate to related festival

□ Create frontend/src/components/Festival/DeityCard.jsx
  - Small card showing deity info
  - Links to festivals featuring this deity
```

**Hour 7: Polish Existing Components**
```
□ Add loading states to all components:
  - Skeleton screens for cards
  - Spinner for map loading
  - Shimmer effect for content areas

□ Add error states:
  - Friendly error messages
  - Retry buttons
  - Fallback content

□ Add empty states:
  - "No festivals in this period"
  - "No temples in view"
```

**Hour 8: Animation Polish**
```
□ Review all transitions:
  - Drawer open/close: 400ms ease-out
  - Tab switches: 300ms ease
  - Card hover: 200ms
  - Map fly-to: 600ms

□ Add micro-interactions:
  - Button hover effects
  - Card click feedback
  - Badge bounce on count change

□ Verify animations run at 60fps
```

#### Evening Session (3 hours)

**Hour 9: Full Integration Test**
```
□ Test complete user flow:
  1. Land on page → festivals load
  2. See upcoming festivals in sidebar
  3. Click festival → detail opens with mythology
  4. Switch to Ritual tab → timeline shows
  5. Click location → map zooms
  6. Switch to Connections tab → related festivals show
  7. Click related festival → switches to that festival
  8. Mobile: all above works with drawer/modal patterns

□ Document any issues
```

**Hour 10: Content Seed Expansion**
```
□ Expand festivals.json to 50 festivals
  - All with minimum data
  - Correct calendar rules
  - Category and region tags

□ Add full mythology for Indra Jatra (demo centerpiece)
  - 800-word origin story
  - Complete 8-day ritual sequence
  - Hour-by-hour for Day 1
  - Connected deities: Indra, Kumari, Bhairav
```

**Hour 11: Documentation**
```
□ Update README.md:
  - New project description
  - Setup instructions
  - Architecture overview

□ Update TASK.md with Day 3 completion

□ Git commit: "feat: Complete MVP with full festival discovery flow"

□ Deploy to local preview
```

**DAY 3 SUCCESS CRITERIA (MVP COMPLETE)**
```
✓ Full flow works: browse → select → explore → navigate
✓ 50 festivals in database
✓ 1 festival (Indra Jatra) with complete content
✓ Map shows temple locations for festivals
✓ Mobile responsive
✓ Loading/error/empty states work
✓ Animations feel polished
✓ Can demo the app end-to-end
```

---

## PHASE 2: CONTENT (Days 4-14)

### Content Sprint Overview

| Days | Focus | Deliverable |
|------|-------|-------------|
| 4-5 | Dashain + Tihar | 2 complete festivals (10-day and 5-day rituals) |
| 6-7 | Newari festivals | Gai Jatra, Bisket Jatra, Mha Puja, Yomari Punhi |
| 8-9 | Major national | Buddha Jayanti, Teej, Holi, Shivaratri |
| 10-11 | Rituals + Locations | Complete ritual sequences, temple connections |
| 12-13 | Deities database | All connected deities with mythology |
| 14 | Content QA | Verify accuracy, fix errors |

### DAY 4 — February 6, 2026 (Friday)
**Theme**: Dashain Complete Content

#### Tasks
```
MYTHOLOGY:
□ Research Dashain mythology deep dive:
  - Durga and Mahishasura story
  - Role of Navadurga
  - Historical significance in Nepal
  - Regional variations

□ Write 800-word origin story (narrative style)
□ Write cultural significance section
□ List Puranic references

RITUAL SEQUENCE:
□ Document all 10 main days:
  - Day 1: Ghatasthapana
  - Day 7: Phulpati
  - Day 8: Maha Ashtami
  - Day 9: Maha Navami
  - Day 10: Vijaya Dashami
  - Days 11-15: Receiving tika

□ For each day, document:
  - Key events with times
  - Locations (temple IDs)
  - What families do at home
  - Food traditions

VERIFICATION:
□ Cross-check dates with Nepal government calendar
□ Verify temple IDs against OSM data
□ Review with any Nepali sources available
```

### DAY 5 — February 7, 2026 (Saturday)
**Theme**: Tihar Complete Content

#### Tasks
```
MYTHOLOGY:
□ Research Tihar stories:
  - Yama and Yamuna legend
  - Why we worship dogs, crows, cows
  - Laxmi Puja significance
  - Bhai Tika origin

□ Write 600-word origin story
□ Write cultural significance section

RITUAL SEQUENCE:
□ Document all 5 days:
  - Day 1: Kaag Tihar (crows)
  - Day 2: Kukur Tihar (dogs)
  - Day 3: Gai Tihar + Laxmi Puja
  - Day 4: Goru Tihar + Mha Puja (Newari New Year)
  - Day 5: Bhai Tika

□ Hour-by-hour for Laxmi Puja night
□ Document mandala creation tradition
```

### DAY 6 — February 8, 2026 (Sunday)
**Theme**: Newari Festivals Part 1

#### Tasks
```
GAI JATRA:
□ Full mythology: Pratap Malla and his queen
□ 500-word origin story
□ Procession route documentation
□ Comedy/satire tradition explanation
□ Temple connections

BISKET JATRA:
□ Serpent demon legend
□ New Year significance (Nepal Sambat crossover)
□ Chariot battle tradition
□ Tongue-piercing ritual documentation
□ Bhaktapur locations
```

### DAY 7 — February 9, 2026 (Monday)
**Theme**: Newari Festivals Part 2

#### Tasks
```
MHA PUJA:
□ Self-worship concept explanation
□ Mandala creation ritual
□ Nepal Sambat New Year
□ Connection to Tihar

YOMARI PUNHI:
□ Origin legend (Yomari creation story)
□ Harvest significance
□ Annapurna worship
□ Food preparation ritual (yomari making)
```

### DAY 8 — February 10, 2026 (Tuesday)
**Theme**: National Festivals Part 1

#### Tasks
```
BUDDHA JAYANTI:
□ Birth-enlightenment-death unified celebration
□ Lumbini connection
□ Swayambhunath rituals
□ Buddhist calendar specifics

TEEJ:
□ Parvati's devotion to Shiva
□ Women's festival significance
□ Fasting rituals documentation
□ Dar khane din to Rishi Panchami
□ Red color symbolism
```

### DAY 9 — February 11, 2026 (Wednesday)
**Theme**: National Festivals Part 2

#### Tasks
```
HOLI:
□ Holika and Prahlad story
□ Krishna and Radha connection
□ Regional variations (Terai vs Hills)
□ Basantapur celebration

SHIVARATRI:
□ Multiple origin legends
□ Night vigil tradition
□ Pashupatinath as center
□ Sadhu gathering documentation
```

### DAY 10 — February 12, 2026 (Thursday)
**Theme**: Complete Ritual Sequences

#### Tasks
```
□ Complete ritual sequences for remaining priority festivals:
  - Maghe Sankranti (solar, simpler)
  - Ghode Jatra (horse parade focus)
  - Rato Machhindranath (chariot journey)
  - Janai Purnima (sacred thread)
  - Sithi Nakha (if included)

□ Ensure all 15 priority festivals have:
  - Preparation section
  - Day-by-day breakdown
  - At least 3 events per day
  - Location connections
```

### DAY 11 — February 13, 2026 (Friday)
**Theme**: Temple & Location Connections

#### Tasks
```
□ Verify all temple IDs in festivals.json exist in temples.json
□ Add ritual roles for each temple in each festival
□ Create pilgrimage route data for:
  - Rato Machhindranath chariot route
  - Kumari Jatra route
  - Bisket Jatra route
□ Add temple visiting tips (hours, dress code, etc.)
```

### DAY 12 — February 14, 2026 (Saturday)
**Theme**: Deity Database Part 1

#### Tasks
```
□ Create data/festivals/deities.json
□ Add deity entries for major figures:
  - Durga/Parvati family
  - Shiva family
  - Vishnu avatars (Buddha, Krishna)
  - Indra
  - Kumari

□ Each deity includes:
  - Names (English, Nepali, Sanskrit)
  - Role and domain
  - Iconography description
  - Nepali-specific significance
  - Connected festivals
  - Connected temples
```

### DAY 13 — February 15, 2026 (Sunday)
**Theme**: Deity Database Part 2 + Connections

#### Tasks
```
□ Complete deity entries:
  - Bhairav (multiple forms)
  - Laxmi
  - Ganesh
  - Local deities (Machhindranath, etc.)
  - Ancestral spirits (for Gai Jatra)

□ Build connection graph:
  - Festival → Deity links verified
  - Deity → Temple links added
  - Festival → Festival relationships complete
```

### DAY 14 — February 16, 2026 (Monday)
**Theme**: Content QA Day

#### Tasks
```
□ Review all 15 priority festival entries:
  - Read each mythology aloud (sounds like a story?)
  - Verify all dates calculate correctly
  - Check all temple IDs are valid
  - Verify no cultural insensitivities

□ Spelling and grammar check:
  - All Nepali words have correct diacritics
  - English text is proofread
  - Consistent terminology

□ Cross-reference check:
  - Mythology claims traceable to sources
  - Ritual times match actual practice
  - Temple names match OSM data
```

**END OF PHASE 2 CRITERIA**
```
✓ 50 festivals have minimum data
✓ 15 festivals have complete mythology + ritual
✓ All deity connections established
✓ All temple connections verified
✓ Content passes quality review
```

---

## PHASE 3: POLISH (Days 15-25)

### DAY 15 — February 17, 2026 (Tuesday)
**Theme**: Visual Design Refinement

#### Tasks
```
COLORS:
□ Finalize festival-specific color palettes
□ Test color accessibility (contrast ratios)
□ Implement dark mode (optional)

TYPOGRAPHY:
□ Verify all fonts load correctly
□ Test Nepali font rendering
□ Adjust line heights for readability

SPACING:
□ Audit all component padding/margins
□ Ensure consistent 8px grid
□ Fix any alignment issues
```

### DAY 16 — February 18, 2026 (Wednesday)
**Theme**: Animation Excellence

#### Tasks
```
□ Add page transition animations
□ Polish tab switching animations
□ Add scroll-triggered animations for content
□ Implement parallax on festival hero images
□ Add subtle particle effects on map
□ Performance audit: all animations at 60fps
```

### DAY 17 — February 19, 2026 (Thursday)
**Theme**: Festival Atmosphere Effects

#### Tasks
```
□ Implement festival "aura" on map:
  - Glowing radius around festival locations
  - Pulsing animation
  - Color matched to festival category

□ Add atmospheric overlays:
  - Warm tones for autumn festivals
  - Cool tones for winter festivals
  - Vibrant for spring/Holi

□ Time-of-day effects (optional):
  - Dawn/dusk lighting on map
  - Night mode for evening festivals
```

### DAY 18 — February 20, 2026 (Friday)
**Theme**: Mobile Optimization

#### Tasks
```
□ Full mobile testing at 320px, 375px, 414px widths
□ Fix any touch issues:
  - Touch targets minimum 44px
  - Swipe gestures for drawer
  - Pull-to-refresh
  
□ Mobile-specific features:
  - Bottom sheet for festival detail
  - Collapsible sidebar
  - Simplified map on small screens

□ Performance on mobile:
  - Reduce animation complexity
  - Lazy load images
  - Minimize JS bundle
```

### DAY 19 — February 21, 2026 (Saturday)
**Theme**: Ritual Timeline Polish

#### Tasks
```
□ Enhance RitualTimeline:
  - Animated line connecting events
  - Current time indicator
  - Location previews on hover
  - Smooth scrolling to current event

□ Add ritual illustration placeholders
□ Make timeline printable (CSS print styles)
```

### DAY 20 — February 22, 2026 (Sunday)
**Theme**: Map Enhancements

#### Tasks
```
□ Add pilgrimage route visualization:
  - Animated path for procession routes
  - Route info popup

□ Temple clusters:
  - Group nearby temples
  - Expand on click

□ Search on map:
  - Search by temple name
  - Search by deity

□ Map controls styling:
  - Custom zoom buttons
  - Layer toggle (temples, routes)
```

### DAY 21 — February 23, 2026 (Monday)
**Theme**: Mythology Presentation

#### Tasks
```
□ Enhance MythologySection:
  - Pull quote styling
  - Expandable sections for long stories
  - Image galleries (placeholder for now)
  - Related story cards

□ Add "Read aloud" markers (visual pacing)
□ Add source citations display
```

### DAY 22 — February 24, 2026 (Tuesday)
**Theme**: Connections & Discovery

#### Tasks
```
□ Enhance ConnectionsView:
  - Visual graph of festival relationships
  - Deity connection visualization
  - Seasonal groupings

□ Add discovery features:
  - "Surprise me" random festival
  - Festival of the day
  - Featured festival banner
```

### DAY 23 — February 25, 2026 (Wednesday)
**Theme**: Performance Optimization

#### Tasks
```
□ Bundle analysis and optimization
□ Code splitting for routes
□ Image optimization
□ API response caching
□ Service worker for offline (optional)
□ Lighthouse audit: aim for 90+ score
```

### DAY 24 — February 26, 2026 (Thursday)
**Theme**: Error Handling & Edge Cases

#### Tasks
```
□ Comprehensive error handling:
  - Network failures
  - Invalid festival IDs
  - Calendar calculation edge cases

□ Empty states for all views
□ 404 page styling
□ Error boundary components
□ Graceful degradation on JS disabled
```

### DAY 25 — February 27, 2026 (Friday)
**Theme**: Final Integration Testing

#### Tasks
```
□ Full regression test:
  - Every feature works
  - Every animation runs smoothly
  - All data loads correctly

□ Cross-browser testing:
  - Chrome
  - Firefox
  - Safari
  - Edge

□ Fix critical bugs only (freeze features)
```

**END OF PHASE 3 CRITERIA**
```
✓ Visual design is premium quality
✓ All animations at 60fps
✓ Mobile experience is smooth
✓ Performance scores 90+ on Lighthouse
✓ No critical bugs
```

---

## PHASE 4: DEMO (Days 26-30)

### DAY 26 — February 28, 2026 (Saturday)
**Theme**: Demo Flow Implementation

#### Tasks
```
□ Create demo mode in app:
  - Scripted sequence of interactions
  - Smooth camera movements
  - Timed reveals

□ Record screen capture of demo:
  - 1080p quality
  - Clear narration points
  - Backup for presentation

□ Prepare demo environment:
  - Disable random elements
  - Pre-cache all data
  - Test on presentation laptop
```

### DAY 27 — March 1, 2026 (Sunday)
**Theme**: Documentation & Presentation

#### Tasks
```
□ Create presentation slides:
  - Problem definition
  - Solution overview
  - Technical architecture
  - Demo section
  - Future possibilities

□ Update all documentation:
  - README completion
  - Architecture diagrams
  - API documentation

□ Prepare Q&A answers:
  - Calendar algorithm questions
  - Data sourcing questions
  - Scalability questions
  - Cultural accuracy questions
```

### DAY 28 — March 2, 2026 (Monday)
**Theme**: Demo Rehearsal

#### Tasks
```
□ Full demo rehearsal (3 times):
  - Time each section
  - Identify any awkward transitions
  - Practice narration

□ Gather feedback if possible
□ Fix any demo flow issues
□ Finalize presentation flow
```

### DAY 29 — March 3, 2026 (Tuesday)
**Theme**: Final Polish

#### Tasks
```
□ Any last-minute fixes
□ Deploy final version
□ Backup everything:
  - Code on GitHub
  - Demo video saved locally
  - Presentation exported as PDF

□ Prepare demo environment
□ Charge all devices
□ Rest before presentation
```

### DAY 30 — March 4, 2026 (Wednesday)
**Theme**: THESIS PRESENTATION DAY

#### Tasks
```
MORNING:
□ Final tech check
□ Demo dry run
□ Arrive early

PRESENTATION:
□ Present with confidence
□ Follow demo script
□ Answer questions thoughtfully

POST-PRESENTATION:
□ Celebrate!
```

---

## Daily Stand-Up Template

Copy this at the start of each day:

```markdown
## Day [X] — [Date]

### Yesterday
- [ ] What was completed
- [ ] Any blockers encountered

### Today
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

### Blockers
- None | [Description]

### Notes
- 
```

---

## Emergency Protocols

### If Behind Schedule
1. Cut "Nice-to-Have" features first
2. Focus on 15 priority festivals only
3. Reduce animation complexity
4. Use placeholder images throughout

### If Major Bug Found
1. Document the bug clearly
2. Assess impact on demo
3. Implement workaround if possible
4. Fix properly only if time permits

### If Content Research Stalls
1. Use LLM-generated drafts as placeholders
2. Mark uncertain facts clearly
3. Focus on festivals with more available info
4. Add "research needed" notes

---

> **Remember**: Read PROJECT_BIBLE.md at the start of every session. Check TASK.md for current progress. Quality standards are non-negotiable.
