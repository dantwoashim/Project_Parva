# PROJECT PARVA — The Complete Bible

> **What is this?** The single source of truth for building Nepal's premium festival discovery system. Every decision, every standard, every deliverable is documented here. When context is lost, return here.

---

## I. THE VISION

### What We're Building
**Parva** (पर्व — Nepali for "festival") is a premium festival discovery system that transforms Nepal's chaotic multi-calendar festival landscape into a living, breathing cultural experience.

### The Core Insight
This is NOT a calendar app. It's a **time machine for culture** where:
- Every festival is a portal to mythology
- Every temple is a point on a living map
- Every ritual sequence is an interactive story
- Every date calculation is algorithmic, not static

### Why This Matters
| For Tourists | For Diaspora | For Young Nepalis |
|--------------|--------------|-------------------|
| Plan trips around festivals | Track traditions from abroad | Rediscover cultural heritage |
| Know where to be, when | Never miss family festivals | Learn the stories behind rituals |
| Authentic cultural immersion | Connection to home | Systems view of their own culture |

### The Feeling We're Creating
When someone uses Parva, they should feel like they've discovered a **secret library** of Nepali culture — rich, atmospheric, authoritative, and alive.

---

## II. QUALITY STANDARDS (READ BEFORE EVERY SESSION)

### Code Quality — Non-Negotiable
```
□ Every function has a docstring explaining what it does
□ Every module has a header comment explaining its purpose
□ Type hints on all Python functions
□ PropTypes or TypeScript on all React components
□ No magic numbers — all constants named and explained
□ Error handling for every API call and user interaction
□ Unit tests for all calendar calculations
□ Integration tests for all API endpoints
```

### Visual Quality — Premium Feel
```
□ No default browser styling visible anywhere
□ Consistent typography using design system fonts
□ All animations have easing (never linear)
□ All transitions are 300-600ms (fast enough to feel snappy, slow enough to feel premium)
□ Loading states for every async operation
□ Error states that are helpful, not generic
□ Responsive at 320px, 768px, 1024px, 1440px breakpoints
□ Glass-card aesthetic from existing design system
```

### Content Quality — Authentic & Deep
```
□ Every mythology claim is verifiable
□ No Wikipedia copy-paste — original synthesis
□ Nepali names include proper diacritics (पार्वती not Parvati)
□ Local variations acknowledged
□ Stories told with narrative craft, not like encyclopedia entries
□ Ritual sequences verified against actual practice
```

### UX Quality — Intuitive Discovery
```
□ User can discover festivals within 3 clicks
□ No dead ends — always a next action available
□ Information revealed progressively (surface → story → detail)
□ Mobile-first but desktop-polished
□ Works offline for core functionality (cached data)
```

---

## III. TECHNICAL ARCHITECTURE

### Stack Confirmation
```
Backend:  Python 3.11+ / FastAPI / Pydantic
Frontend: React 18 / Vite / Leaflet / D3.js / Framer Motion
Data:     JSON files (no database needed for this scale)
Styling:  Vanilla CSS with existing design system tokens
Maps:     Leaflet + MapLibre + existing OSM data

# v2.0 Ephemeris Upgrade
Astronomy: pyswisseph (Swiss Ephemeris / NASA JPL DE431)
Accuracy:  Sub-arcsecond Sun/Moon positions
Range:     2000-2200 BS (computed), 13201 BCE - 17191 CE (ephemeris)
```

### Directory Structure (Final State)
```
Project Parva/
├── PROJECT_BIBLE.md          # This file
├── ROADMAP.md                # Detailed daily roadmap
├── TASK.md                   # Current progress tracker
│
backend/
├── app/
│   ├── calendar/             # [NEW] Multi-calendar engine
│   │   ├── __init__.py
│   │   ├── bikram_sambat.py  # BS ↔ Gregorian conversion
│   │   ├── nepal_sambat.py   # NS lunar calculations
│   │   ├── tibetan.py        # Tibetan calendar basics
│   │   ├── tithi.py          # Lunar day calculations
│   │   ├── calculator.py     # Unified calendar API
│   │   └── constants.py      # Calendar data tables
│   │
│   ├── festivals/            # [NEW] Festival discovery
│   │   ├── __init__.py
│   │   ├── models.py         # Pydantic schemas
│   │   ├── repository.py     # Data access layer
│   │   ├── service.py        # Business logic
│   │   └── routes.py         # API endpoints
│   │
│   ├── mythology/            # [NEW] Deity/story data
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   └── main.py               # [MODIFY] Add new routers
│
├── data/
│   ├── festivals/            # [NEW] Festival content
│   │   ├── festivals.json    # 50+ festivals
│   │   ├── mythology.json    # Stories and deities
│   │   └── rituals.json      # Ritual sequences
│   │
│   └── processed/
│       ├── temples.json      # [NEW] Filtered from facilities
│       └── facilities.geojson # [EXISTING] Keep as backup
│
frontend/
├── src/
│   ├── components/
│   │   ├── Festival/         # [NEW] Festival components
│   │   │   ├── FestivalCard.jsx
│   │   │   ├── FestivalCard.css
│   │   │   ├── FestivalDetail.jsx
│   │   │   ├── FestivalDetail.css
│   │   │   ├── MythologyDrawer.jsx
│   │   │   ├── MythologyDrawer.css
│   │   │   ├── RitualTimeline.jsx
│   │   │   ├── RitualTimeline.css
│   │   │   ├── DeityCard.jsx
│   │   │   └── DeityCard.css
│   │   │
│   │   ├── Calendar/         # [NEW] Temporal components
│   │   │   ├── TemporalNavigator.jsx
│   │   │   ├── TemporalNavigator.css
│   │   │   ├── LunarPhase.jsx
│   │   │   ├── LunarPhase.css
│   │   │   ├── CountdownTimer.jsx
│   │   │   └── CountdownTimer.css
│   │   │
│   │   ├── Map/              # [MODIFY] Festival-focused map
│   │   │   ├── FestivalMap.jsx
│   │   │   ├── FestivalMap.css
│   │   │   ├── TempleMarker.jsx
│   │   │   ├── FestivalAura.jsx
│   │   │   └── PilgrimageRoute.jsx
│   │   │
│   │   └── LivingMap/        # [KEEP] Repurpose particles
│   │
│   ├── pages/
│   │   └── ParvaPage.jsx     # [NEW] Main application
│   │
│   ├── hooks/
│   │   ├── useFestivals.js   # [NEW] Festival data hook
│   │   ├── useCalendar.js    # [NEW] Calendar conversion hook
│   │   └── useMythology.js   # [NEW] Mythology data hook
│   │
│   └── services/
│       └── api.js            # [MODIFY] Add festival endpoints
│
tests/
├── unit/
│   ├── test_bikram_sambat.py # [NEW] 50+ test cases
│   ├── test_tithi.py         # [NEW] 30+ test cases
│   ├── test_festivals.py     # [NEW] API tests
│   └── ...
│
└── integration/
    └── test_festival_api.py  # [NEW] E2E tests
```

---

## IV. DATA SCHEMAS

> [!IMPORTANT]
> The schemas below represent the **target design**. The current implementation in `backend/app/festivals/models.py` uses a simplified subset. See the code for the actual fields currently supported. Key differences:
> - Implemented: `name` (not `name_en`/`name_ne` separation), `description`, `calendar_type`, `mythology` (simplified)
> - Not yet implemented: `aliases`, full `RitualSequence` structure, `PreparationGuide`
> 
> The MVP prioritizes working date calculations over complete content structure.

### Festival Schema (Target Design)
```python
class Festival(BaseModel):
    """A single festival with complete metadata and content."""
    
    # Identity
    id: str                          # "indra-jatra"
    name_en: str                     # "Indra Jatra"
    name_ne: str                     # "इन्द्र जात्रा"
    name_newari: str | None          # "येँया:"
    aliases: list[str]               # ["Yenya", "Kumari Jatra"]
    
    # Calendar Calculation
    calendar_system: Literal["bikram_sambat", "nepal_sambat", "tibetan", "solar"]
    calculation_rule: CalendarRule   # Structured rule for date calculation
    duration_days: int               # 8 for Indra Jatra
    
    # Classification
    category: list[str]              # ["newari", "royal", "autumn"]
    region: list[str]                # ["kathmandu_valley"]
    significance_level: int          # 1-5 (5 = major national)
    
    # Content - Surface Level
    tagline: str                     # One compelling sentence
    summary: str                     # 2-3 paragraph overview
    
    # Content - Mythology Level
    mythology: FestivalMythology
    
    # Content - Ritual Level
    ritual_sequence: RitualSequence
    
    # Location
    primary_location_ids: list[str]  # OSM facility IDs
    celebration_areas: list[str]     # ["Basantapur", "Hanuman Dhoka"]
    
    # Connections
    related_festivals: list[str]     # ["dashain", "gai-jatra"]
    connected_deities: list[str]     # ["indra", "kumari", "bhairav"]
    
    # Media
    hero_image: str | None           # Path to hero image
    gallery: list[str]               # Additional images

class CalendarRule(BaseModel):
    """How to calculate this festival's date."""
    base_calendar: str               # "bikram_sambat"
    month: int | str                 # 5 or "bhadra"
    lunar_phase: str | None          # "shukla" | "krishna"
    tithi: int | None                # 1-15 for specific lunar day
    weekday: str | None              # For weekday-based festivals
    solar_day: int | None            # For solar calendar festivals
    notes: str                       # Any special calculation notes

class FestivalMythology(BaseModel):
    """The mythological content for a festival."""
    origin_story: str                # 500-1000 words, narrative style
    origin_story_short: str          # 100 words for preview
    historical_context: str | None   # Real historical background
    puranic_references: list[str]    # ["Skanda Purana", "local legend"]
    key_legends: list[Legend]        # Individual story segments
    cultural_significance: str       # Why this matters to Nepal

class Legend(BaseModel):
    """A single legend or story segment."""
    title: str
    content: str
    source: str | None

class RitualSequence(BaseModel):
    """Complete ritual breakdown for a festival."""
    preparation: PreparationGuide
    main_events: list[DaySchedule]
    post_festival: str | None

class PreparationGuide(BaseModel):
    """What to do before the festival."""
    days_before: int
    activities: list[str]
    required_items: list[str]
    taboos: list[str] | None

class DaySchedule(BaseModel):
    """What happens on a single day."""
    day_number: int                  # 1, 2, 3...
    day_name: str | None             # "Phulpati" for Dashain Day 7
    events: list[RitualEvent]

class RitualEvent(BaseModel):
    """A single event in the ritual sequence."""
    time: str                        # "Dawn", "10:00 AM", "Sunset"
    event_name: str                  # "Kumari procession begins"
    description: str                 # What happens
    location_id: str | None          # OSM facility ID
    location_name: str               # "Hanuman Dhoka"
    significance: str                # Why this moment matters
    tips: str | None                 # Practical advice for attendees
```

### Deity Schema
```python
class Deity(BaseModel):
    """A deity in the Nepali pantheon."""
    id: str                          # "indra"
    name_en: str                     # "Indra"
    name_ne: str                     # "इन्द्र"
    name_sanskrit: str | None        # "इन्द्र"
    
    role: str                        # "King of the Gods, God of Rain"
    domain: list[str]                # ["rain", "storms", "heaven"]
    
    iconography: str                 # How to identify in art
    vahana: str | None               # Vehicle (elephant Airavata)
    consort: str | None              # Shachi
    
    mythology: str                   # Brief mythological background
    nepali_significance: str         # Specific importance in Nepal
    
    associated_festivals: list[str]  # ["indra-jatra"]
    associated_temples: list[str]    # OSM facility IDs
```

### Temple Schema (Extended from Facilities)
```python
class Temple(BaseModel):
    """A temple or religious site."""
    id: str                          # From OSM
    facility_type: str               # "temple", "stupa", "shrine"
    name_en: str
    name_ne: str
    
    coordinates: tuple[float, float] # [lng, lat]
    attached_road_id: str           # From existing data
    
    # Festival connections
    associated_festivals: list[str]  # ["indra-jatra", "dashain"]
    primary_deity: str | None        # "kumari"
    
    # Ritual significance
    ritual_role: str | None          # "Kumari's residence"
    visit_times: list[str] | None    # When accessible
    
    # Metadata
    architectural_style: str | None  # "Newari pagoda"
    historical_period: str | None    # "17th century Malla"
```

---

## V. API SPECIFICATIONS

### Calendar Endpoints
```
GET /api/calendar/convert
    ?from=gregorian&to=bs&date=2026-09-15
    Response: { "bs_year": 2083, "bs_month": 5, "bs_day": 30, "bs_month_name": "Bhadra" }

GET /api/calendar/tithi
    ?date=2026-09-15
    Response: { "tithi": 8, "paksha": "shukla", "lunar_month": "bhadra" }

GET /api/calendar/festivals-in-range
    ?start=2026-09-01&end=2026-09-30
    Response: [{ festival_id, name, start_date, end_date, location_summary }]
```

### Festival Endpoints
```
GET /api/festivals
    ?upcoming=true&days=30&category=newari&region=kathmandu_valley
    Response: [FestivalSummary]  # List of upcoming festivals

GET /api/festivals/{festival_id}
    Response: Festival  # Full festival detail including mythology

GET /api/festivals/{festival_id}/ritual
    Response: RitualSequence  # Just the ritual data

GET /api/festivals/{festival_id}/dates
    ?years=5
    Response: [{ year: 2026, start: "2026-09-15", end: "2026-09-22" }]
```

### Mythology Endpoints
```
GET /api/deities
    Response: [DeitySummary]

GET /api/deities/{deity_id}
    Response: Deity

GET /api/deities/{deity_id}/festivals
    Response: [FestivalSummary]  # Festivals associated with this deity
```

### Location Endpoints
```
GET /api/temples
    ?festival={festival_id}&bounds={sw_lng,sw_lat,ne_lng,ne_lat}
    Response: [Temple]

GET /api/temples/{temple_id}
    Response: Temple

GET /api/temples/{temple_id}/festivals
    Response: [FestivalSummary]  # Festivals celebrated at this temple
```

---

## VI. CALENDAR ENGINE SPECIFICATIONS

### Bikram Sambat Conversion
The Bikram Sambat calendar is 56 years, 8 months, and 14 days ahead of Gregorian. However, month lengths vary by year in a non-formulaic way.

**v2.0: Hybrid Approach**
- **Lookup Mode (2070-2095 BS)**: Pre-computed month lengths from Rashtriya Panchang
- **Computed Mode (outside range)**: Astronomical calculation using solar transit detection

```python
# v2.0 Hybrid Calendar Conversion
def gregorian_to_bs(date: date) -> tuple[int, int, int, str]:
    """
    Convert Gregorian to Bikram Sambat.
    
    Returns: (year, month, day, confidence)
    - confidence: "exact" for lookup range, "computed" for astronomical
    """
    if MIN_BS_YEAR <= target_year <= MAX_BS_YEAR:
        # Use lookup table (100% accuracy)
        return lookup_conversion(date), "exact"
    else:
        # Use ephemeris-based sankranti detection
        return computed_conversion(date), "computed"
```

### Tithi Calculation (v2.0 — Ephemeris-Based)
Tithi is the lunar day, calculated from the angular distance between sun and moon using **Swiss Ephemeris**.

```python
import swisseph as swe

def calculate_tithi_precise(dt: datetime) -> tuple[int, str, float]:
    """
    Calculate tithi using Swiss Ephemeris for sub-arcsecond accuracy.
    
    Returns: (tithi_number 1-15, paksha "shukla"|"krishna", progress 0-1)
    """
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60)
    
    # Get sidereal longitudes (Lahiri ayanamsa)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    sun_long = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL)[0][0]
    moon_long = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)[0][0]
    
    # Calculate elongation
    elongation = (moon_long - sun_long) % 360
    
    # Tithi = elongation / 12°
    tithi_float = elongation / 12
    tithi = int(tithi_float) + 1
    progress = tithi_float % 1
    
    # Determine paksha
    if elongation < 180:
        paksha = "shukla"
        display_tithi = tithi
    else:
        paksha = "krishna"
        display_tithi = tithi - 15 if tithi > 15 else tithi
    
    return (display_tithi, paksha, progress)
```

### Udaya Tithi (Sunrise-Based)
The official tithi for calendrical purposes is determined at sunrise:

```python
def get_udaya_tithi(date: date) -> dict:
    """Get the tithi prevailing at sunrise — the official tithi for the day."""
    sunrise = calculate_sunrise(date, LAT_KATHMANDU, LON_KATHMANDU)
    tithi, paksha, progress = calculate_tithi_precise(sunrise)
    return {
        "tithi": tithi,
        "paksha": paksha,
        "tithi_name": TITHI_NAMES[tithi],
        "progress": progress,
        "method": "udaya_tithi"
    }
```

### Sankranti Detection (v2.0 — Solar Transit)
BS month boundaries are determined by solar transit through zodiac signs:

```python
def find_solar_transit(target_longitude: float, search_start: datetime) -> datetime:
    """
    Find when Sun crosses a specific sidereal longitude.
    
    Args:
        target_longitude: 0°=Mesh (Baishakh), 30°=Vrishabha (Jestha), etc.
        search_start: Approximate search start
    
    Returns: Exact datetime of crossing
    """
    # Binary search for transit
    # ... implementation using Brent's method
```

### Festival Date Calculation Examples
```python
# Dashain - Ashwin Shukla Pratipada to Purnima (15 days)
def calculate_dashain(year: int) -> tuple[date, date]:
    """Find first day of Ashwin Shukla (new moon) and count 15 days."""

# Indra Jatra - Bhadra Shukla Dwadashi
def calculate_indra_jatra(year: int) -> tuple[date, date]:
    """Find Bhadra Shukla 12th tithi, lasts 8 days."""

# Maghe Sankranti - Sun enters Makara (Capricorn)
def calculate_maghe_sankranti(year: int) -> date:
    """Find solar transit into Makara rashi using ephemeris."""
```

---

## VII. DESIGN SYSTEM (PARVA-SPECIFIC)

### Color Palette
```css
/* Base Colors - From existing UI Design System */
--bg-primary: #F5F3EE;
--bg-secondary: #EBE8E0;
--text-primary: #2C2416;
--text-muted: #7A7264;

/* Festival Accent Colors */
--parva-gold: #C49B5A;          /* Primary accent, festival highlights */
--parva-saffron: #E07B3A;       /* Warm festivals (Tihar, Holi) */
--parva-crimson: #C4435A;       /* Dashain, blood rituals */
--parva-forest: #4A6B5C;        /* Harvest festivals */
--parva-indigo: #4A5A7B;        /* Night festivals, Indra */

/* Atmosphere Overlays */
--aura-glow: rgba(196, 155, 90, 0.3);
--festival-pulse: rgba(224, 123, 58, 0.4);
```

### Typography
```css
/* Display - For festival names, big reveals */
.festival-name {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: clamp(32px, 5vw, 56px);
    letter-spacing: -0.02em;
}

/* Nepali Text */
.nepali-text {
    font-family: 'Mukta', 'Noto Sans Devanagari', sans-serif;
    font-weight: 500;
}

/* Mythology Body */
.mythology-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 18px;
    line-height: 1.8;
    color: var(--text-primary);
}

/* Data/Stats */
.data-text {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
}
```

### Animation Standards
```css
/* Timing */
--duration-instant: 100ms;     /* Micro-feedback */
--duration-fast: 250ms;        /* UI transitions */
--duration-medium: 400ms;      /* Panel slides */
--duration-slow: 700ms;        /* Reveals */
--duration-ambient: 4000ms;    /* Background motion */

/* Easing */
--ease-out: cubic-bezier(0.0, 0.0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);

/* Festival Aura Animation */
@keyframes festival-pulse {
    0%, 100% { 
        box-shadow: 0 0 20px var(--aura-glow);
        transform: scale(1);
    }
    50% { 
        box-shadow: 0 0 50px var(--festival-pulse);
        transform: scale(1.02);
    }
}
```

### Component Patterns
```
FestivalCard
├── Hero Image (16:9 aspect, gradient overlay)
├── Content Block
│   ├── Festival Name (Nepali + English)
│   ├── Date Range with Countdown
│   ├── Tagline
│   └── Category Badges
└── Action Area
    ├── "Learn More" Button
    └── "Add to Calendar" Button

MythologyDrawer
├── Tab Navigation (Story | Ritual | Connections)
├── Content Area (scrollable)
│   ├── Section Headers with Icons
│   ├── Mythology Text (rich formatting)
│   └── Inline Images
└── Close Button (fixed top-right)

RitualTimeline
├── Day Selector (horizontal scroll)
├── Timeline Track
│   ├── Time Markers
│   └── Event Cards (connected by line)
└── Map Preview (shows locations)
```

---

## VIII. CONTENT SPECIFICATIONS

### 15 Priority Festivals (Full Treatment)

| # | Festival | Type | Season | Showcase Feature |
|---|----------|------|--------|------------------|
| 1 | **Indra Jatra** | Newari | Autumn | Living goddess procession, demo centerpiece |
| 2 | **Dashain** | National | Autumn | 15-day sequence, Durga mythology |
| 3 | **Tihar** | National | Autumn | 5-day sequence, brother-sister bond |
| 4 | **Gai Jatra** | Newari | Summer | Grief/comedy duality, ancestor worship |
| 5 | **Bisket Jatra** | Newari | Spring | New Year chariot, most dramatic |
| 6 | **Buddha Jayanti** | Buddhist | Summer | Birth-enlightenment-death cycle |
| 7 | **Teej** | National | Monsoon | Women's fasting, sacred femininity |
| 8 | **Maghe Sankranti** | National | Winter | Solar transition, food traditions |
| 9 | **Holi** | National | Spring | Color festival, Krishna mythology |
| 10 | **Ghode Jatra** | Kathmandu | Spring | Horse parade, demon suppression |
| 11 | **Mha Puja** | Newari | Autumn | Self-worship, Nepal Sambat New Year |
| 12 | **Yomari Punhi** | Newari | Winter | Harvest, Annapurna, food ritual |
| 13 | **Rato Machhindranath** | Newari | Spring | Longest chariot festival, rain deity |
| 14 | **Shivaratri** | National | Winter | Night vigil, Pashupatinath |
| 15 | **Janai Purnima** | National | Monsoon | Sacred thread, Raksha Bandhan |

### Content Requirements Per Festival

**Minimum (all 50 festivals):**
- Name in English, Nepali, local dialect
- Category tags
- Calendar calculation rule
- 100-word summary
- Primary locations (OSM IDs)
- Related festivals

**Standard (35 additional festivals):**
- All minimum fields
- 300-word origin story
- 3+ ritual moments
- Connected deities

**Premium (15 priority festivals):**
- All standard fields
- 800-1000 word origin story (narrative style)
- Complete day-by-day ritual breakdown
- Hour-by-hour for peak day
- Full preparation guide
- Associated legends (2-3 per festival)
- Temple mapping with ritual roles
- Practical visitor tips

### Writing Style Guide
```
DO:
✓ Write mythologies as stories, not encyclopedia entries
  "When Indra descended to steal flowers from the garden of a mortal..."
  NOT: "Indra Jatra commemorates the capture of Indra."

✓ Include sensory details
  "The smell of incense mixes with marigold garlands as the chariot creaks forward."

✓ Acknowledge local variations
  "In Bhaktapur, the emphasis shifts from Indra to Machhindranath..."

✓ Connect to human experience
  "Every family who lost someone that year joins the procession—a city mourning together."

DON'T:
✗ Copy Wikipedia verbatim
✗ Use passive voice for narratives
✗ Make unsourced claims about "ancient" origins
✗ Ignore the lived experience of festivals
```

---

## IX. VERIFICATION REQUIREMENTS

### Calendar Accuracy Tests
```python
# Must pass before any code is considered complete

# Dashain 2083/2026 (Official: Ghatasthapana Ashwin 25 = October 11)
def test_dashain_2026():
    result = calculate_festival_date("dashain", 2026)
    assert result.start == date(2026, 10, 11)  # Ghatasthapana
    assert result.end == date(2026, 10, 25)    # Kojagrat Purnima area

# Tihar 2083/2026 (Official: Kaag Tihar Kartik 21 = November 7)
def test_tihar_2026():
    result = calculate_festival_date("tihar", 2026)
    assert result.start == date(2026, 11, 7)   # Kaag Tihar
    assert result.end == date(2026, 11, 11)    # Bhai Tika

# BS Conversion (known: 2083-01-01 BS = April 14, 2026)
def test_bs_new_year_2083():
    result = bs_to_gregorian(2083, 1, 1)
    assert result == date(2026, 4, 14)

# Cross-verify with government holiday list
```

### Visual Quality Checklist
Run before any demo or user review:
```
□ All fonts loaded (no FOUT)
□ All images loaded (no broken images)
□ Animations run at 60fps
□ No layout shifts on load
□ Works on iPhone SE (320px width)
□ Works in dark mode (if implemented)
□ All clickable elements have hover states
□ All form inputs have focus states
□ Tab navigation works correctly
□ Screen reader can navigate content
```

### Content Quality Checklist
For each mythology entry:
```
□ Story flows narratively (not choppy facts)
□ Nepali names spelled correctly with diacritics
□ No factual errors (cross-referenced)
□ Sources cited for non-obvious claims
□ No cultural insensitivity
□ Ritual times verified against actual practice
□ Temple IDs verified against OSM data
```

---

## X. DEMO SCRIPT (FINAL)

### Setup
- Chrome maximized on 1440p display
- Dev server running: `npm run dev`
- Backend running: `uvicorn app.main:app --reload`
- Pre-scroll to reset state
- Nepali ambient music ready (optional)

### Script (6 minutes)

**[0:00-0:30] Opening**
```
[Dark screen]
[Text fades in: "कहिले मनाउने?"]
[English appears below: "When to celebrate?"]
[3 seconds hold]
[Map materializes from center outward]
[Temples glow softly]
[Narrator]: "Nepal has over 50 major festivals. Multiple calendars. Shifting dates."
```

**[0:30-1:00] The Problem**
```
[Narrator]: "Try to find when Dashain is next year. Or Gai Jatra. Or Bisket Jatra."
[Show Google results - inconsistent dates]
[Narrator]: "Websites disagree. Dates are wrong. Smaller festivals aren't listed at all."
[Pause]
[Narrator]: "We built something different."
```

**[1:00-2:00] Discovery**
```
[Click "What's Happening" in sidebar]
[Timeline animates in showing next 30 days]
[3 festivals visible with countdown badges]
[Narrator]: "Twelve days until Indra Jatra. One of the oldest festivals in the valley."
[Indra Jatra card pulses with golden aura]
[Click on Indra Jatra card]
```

**[2:00-3:30] Festival Deep Dive**
```
[Card expands smoothly to full detail view]
[Hero image fades in with gradient]
[Narrator]: "Indra Jatra. The festival of the captive god."
[Scroll to mythology section]
[Narrator]: "Long ago, Indra, king of the heavens, descended to Earth..."
[Read first paragraph of origin story]
[Narrator]: "But there's more than story here."
[Click "Ritual" tab]
```

**[3:30-4:30] Ritual Timeline**
```
[Ritual timeline animates in]
[Day selector shows 8 days]
[Click Day 1]
[Timeline shows hour-by-hour]
[Narrator]: "Day one. Dawn. The raising of the Indra Dhwaja pole..."
[Map highlights Hanuman Dhoka]
[Click a ritual event]
[Location card appears showing temple]
[Narrator]: "You know exactly where to be, when."
```

**[4:30-5:15] The Web of Connections**
```
[Click "Connections" tab]
[Related festivals appear as connected nodes]
[Narrator]: "Indra Jatra connects to Dashain, which connects to Tihar..."
[Click shared deity: Kumari]
[Deity card appears]
[Narrator]: "The same living goddess appears in multiple festivals."
[Show deity-festival-temple relationship]
```

**[5:15-5:45] The Algorithm**
```
[Narrator]: "And all of this calculates itself."
[Open calendar panel]
[Show: "Based on Bhadra Shukla Dwadashi in Bikram Sambat calendar..."
[Click "Next 5 Years"]
[Dates animate in: 2026, 2027, 2028, 2029, 2030]
[Narrator]: "Algorithmic. Not guessed. Not copied."
```

**[5:45-6:00] Closing**
```
[Zoom out to full map]
[All festival locations glow]
[Narrator]: "Parva. Know when to celebrate."
[Logo fade in]
[End]
```

---

## XI. TROUBLESHOOTING & CONTEXT RECOVERY

### If You (LLM) Lose Context
1. Read this entire PROJECT_BIBLE.md first
2. Check TASK.md for current progress
3. Run `npm run dev` and `uvicorn app.main:app --reload` to see current state
4. Re-read the quality standards in Section II before writing any code

### Common Issues

**Calendar dates are wrong**
- Check BS_CALENDAR_DATA lookup table
- Verify tithi calculation with online panchang
- Cross-reference with Nepal government holiday list

**Map doesn't show temples**
- Check temples.json exists and has valid GeoJSON
- Verify facility IDs match between festivals.json and temples.json
- Check console for Leaflet errors

**Animations are janky**
- Check if will-change is used appropriately
- Verify animation duration isn't too short
- Test on production build, not dev mode

**Content seems shallow**
- Return to Content Specifications section
- Check if you're meeting "Premium" requirements
- Run Writing Style Guide checklist

---

## XII. SUCCESS METRICS

### Must-Have for Thesis (Day 30)
- [ ] Calendar engine calculates correct dates for all 50 festivals
- [ ] 15 festivals have complete mythology treatment
- [ ] Map shows all festival locations with correct temple connections
- [ ] Demo runs smoothly for 6 minutes without errors
- [ ] Responsive design works on mobile and desktop
- [ ] All code has tests and documentation

### v2.0 Ephemeris Must-Have
- [ ] Swiss Ephemeris (pyswisseph) integrated
- [ ] Tithi calculation using proper ephemeris (not synodic approximation)
- [ ] Extended date range beyond lookup table (2000-2200 BS)
- [ ] Confidence flags on date conversions (exact vs computed)
- [ ] 45-case evaluation showing ≥95% accuracy

### Nice-to-Have (If Time Permits)
- [ ] Browser notifications for festival reminders
- [ ] Offline mode with cached data
- [ ] Share festival dates to social media
- [ ] "Add to Calendar" export (ICS format)
- [ ] Dark mode

### Impressive-to-Have (Above and Beyond)
- [ ] 3D temple visualizations
- [ ] Audio guide for ritual sequences
- [ ] AR temple overlay (experimental)
- [ ] Multi-language support (English, Nepali, Newari)

---

> **Final Note**: This document is the law. Every implementation decision should trace back to something specified here. When in doubt, re-read the Vision and Quality Standards.

---

*Project Parva — पर्व — A thesis project by Rohan Basnet*
*Started: February 2, 2026*
*Deadline: March 4, 2026*
