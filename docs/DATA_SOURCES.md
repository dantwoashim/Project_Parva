# Data Sources & Citations (v2.0)

> **Purpose**: Document all sources used for festival content and astronomical calculations to ensure trustworthiness and academic defensibility.

---

## Primary Sources

### Government & Official Sources

1. **Nepal Government Ministry of Home Affairs**
   - Official public holiday list
   - URL: https://moha.gov.np/
   - Used for: Festival date verification, national holiday classifications

2. **Nepal Rastra Bank (Central Bank)**
   - Banking holiday calendar
   - URL: https://www.nrb.org.np/
   - Used for: Cross-referencing official holiday dates

3. **Rashtriya Panchang (National Almanac)**
   - Published by: Department of Astrology, Nepal
   - Used for: Tithi calculations, auspicious timings, lunar data, BS month lengths
   - Note: Physical publication, referenced through Nepal Patro digitization
   - **Validation: 45-case test suite (15 festivals × 3 years)**

4. **Municipality Official Publications**
   - Kathmandu Metropolitan City (Indra Jatra, Ghode Jatra)
   - Bhaktapur Municipality (Bisket Jatra)
   - Lalitpur Metropolitan City (Rato Machhindranath)
   - Used for: Local festival dates, procession routes

### Academic Sources

5. **Gerard Toffin — "The Indra Jātrā of Kathmandu as a Royal Festival"**
   - Journal: Contributions to Nepalese Studies, 1992
   - Used for: Indra Jatra historical context, ritual sequences

6. **Mary Slusser — "Nepal Mandala: A Cultural Study of the Kathmandu Valley"**
   - Published: 1982, Princeton University Press
   - Used for: Temple locations, historical festival origins, Malla-era context

7. **Dhanavajra Vajracharya & Kamal Mani Dixit — "The Kīrtipur City Inscriptions"**
   - Used for: Nepal Sambat calendar dates, Newari festival origins

8. **Nutan Dhar Sharma — "The Religious Festivals of the Hindus of Nepal"**
   - Used for: Ritual sequences, mythology summaries

### Digital & Contemporary Sources

9. **Nepal Patro (नेपाल पात्रो)**
   - URL: https://www.nepalpatro.com.np/
   - Mobile app with official calendar data
   - Used for: Date verification, BS-Gregorian conversion reference

10. **Hamro Patro**
    - URL: https://www.hamropatro.com/
    - Used for: Cross-referencing festival dates, tithi data

11. **UNESCO Intangible Cultural Heritage Lists**
    - Used for: Bisket Jatra, Indra Jatra cultural significance

12. **Drik Panchang**
    - URL: https://www.drikpanchang.com/
    - Used for: Tithi verification, nakshatra data, panchanga cross-validation

### Temple & Religious Authorities

13. **Pashupatinath Temple Development Trust**
    - Used for: Shivaratri rituals, Pashupatinath-specific information

14. **Swayambhunath Conservation Board**
    - Used for: Buddha Jayanti rituals, Buddhist calendar events

15. **Kumari Ghar (Kumari House), Kathmandu**
    - Used for: Kumari appearance schedules, Indra Jatra specifics

---

## Astronomical Calculation Sources (NEW in v2.0)

### Ephemeris Data

16. **Swiss Ephemeris (pyswisseph)**
    - Runtime mode: Swiss/Moshier (default in current deployment)
    - Range: 13201 BCE to 17191 CE
    - Accuracy: Sub-arcsecond for planetary positions
    - URL: https://www.astro.com/swisseph/
    - Used for: Sun/Moon ecliptic longitudes, precise tithi calculation

17. **JPL DE431 Ephemeris**
    - Published by: NASA Jet Propulsion Laboratory
    - Note: supported as a future optional dataset, not the current default runtime mode

### Astronomical Algorithm References

18. **Jean Meeus — "Astronomical Algorithms" (1991)**
    - Publisher: Willmann-Bell
    - Used for: Julian Day calculations, coordinate transformations

19. **VSOP87 Theory (Bretagnon & Francou, 1988)**
    - Used for: Solar longitude calculations (backup)
    - Accuracy: 1 arcsecond for 2000 BCE to 6000 CE

20. **ELP2000-82 Lunar Theory**
    - Used for: Lunar longitude calculations (backup)
    - Accuracy: 2 arcseconds for modern era

### Ayanamsa Reference

21. **Lahiri Ayanamsa**
    - Standard used: Indian Government standard (Chitrapaksha)
    - Value at J2000.0: 23°51'11"
    - Used for: Converting tropical to sidereal coordinates

---

## Mythology Source Attributions

| Festival | Mythology Sources |
|----------|-------------------|
| Dashain | Devi Mahatmya (Markandeya Purana), Chapter 81-93; local oral traditions |
| Tihar | Skanda Purana; Kathasaritsagara (Yama-Yamuna legend) |
| Indra Jatra | Gopal Vamsavali; Prithvi Narayan Shah chronicles |
| Bisket Jatra | Local legend documented by Bhaktapur Municipality; Nepal Mandala (Slusser) |
| Gai Jatra | Pratap Malla historical records; Toffin 1992 |
| Shivaratri | Shiva Purana; Linga Purana |
| Buddha Jayanti | Lalitavistara Sutra; Theravada & Mahayana traditions |
| Teej | Skanda Purana; Brahma Vaivarta Purana |
| Janai Purnima | Yajurveda ritual texts; local Brahmin traditions |

---

## Calendar Calculation Sources

### Bikram Sambat Calendar Data

1. **Official Lookup Table (2070-2095 BS)**
   - Source: Digitized from Rashtriya Panchang
   - Accuracy: 100% match with official publications
   - Method: Lookup table for verified range

2. **Estimated Mode (Outside 2070-2095 BS)** *(NEW in v2.0)*
   - Method: Swiss Ephemeris-based solar transit detection
   - Accuracy: Matches lookup table pattern
   - Confidence: Marked as "estimated" in API response

### Tithi Calculation *(UPGRADED in v2.0)*

**Previous (v1.0):** Synodic approximation
```
tithi ≈ floor((days_since_new_moon mod 29.53) × 30 / 29.53) + 1
```

**Current (v2.0):** Ephemeris-based calculation
```
tithi = floor((lunar_longitude - solar_longitude) / 12°) + 1
```

- Uses Swiss Ephemeris for precise Sun/Moon positions
- Accuracy: ±10 seconds at tithi boundaries
- Verified against Rashtriya Panchang for 2080-2082 BS

### Udaya Tithi

- **Definition**: Tithi prevailing at sunrise in Nepal (Kathmandu)
- **Location**: 27.7172°N, 85.3240°E
- **Timezone**: Nepal Standard Time (UTC+5:45)
- **Source**: Traditional Hindu calendar practice

---

## Content Verification Process

1. **Primary claim** → Verified against at least 2 independent sources
2. **Mythology** → Cited to specific Purana or academic source
3. **Dates** → Tested against government calendar
4. **Rituals** → Cross-checked with local practitioners where possible
5. **Astronomical** → Validated against ephemeris reference data *(NEW)*

---

## Disclaimer

> While every effort has been made to ensure accuracy, festival practices may vary by region, family tradition, and year. Rato Machhindranath and certain local festivals have dates announced by traditional authorities (Guthi) and cannot be calculated algorithmically. For official event planning, always verify with local government announcements.

> **v2.0 Note**: Dates calculated using ephemeris for years outside the official lookup range (2070-2095 BS) are marked with `confidence: estimated` and may differ slightly from eventual official publications.

---

*This document is part of Project Parva's academic integrity framework.*
*Last updated: February 2026*
*Version: 2.0 (Ephemeris Upgrade)*
