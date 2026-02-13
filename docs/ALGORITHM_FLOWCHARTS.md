# Project Parva — Algorithm Flowcharts and Detailed Descriptions

## Table of Contents

1. [Tithi Calculation Algorithm](#1-tithi-calculation-algorithm)
2. [Bikram Sambat Conversion Algorithm](#2-bikram-sambat-conversion-algorithm)
3. [Festival Date Calculation Algorithm](#3-festival-date-calculation-algorithm)
4. [Lunar Month Detection Algorithm](#4-lunar-month-detection-algorithm)
5. [Adhik Maas (Intercalary Month) Detection](#5-adhik-maas-detection-algorithm)
6. [Panchanga Calculation Algorithm](#6-panchanga-calculation-algorithm)
7. [Sankranti (Solar Transit) Algorithm](#7-sankranti-detection-algorithm)

---

## 1. TITHI CALCULATION ALGORITHM

### 1.1 Overview

A **tithi** is one of 30 lunar days in the Hindu lunar month. It is determined by the angular separation between the Moon and Sun. Each tithi spans exactly 12° of elongation.

### 1.2 Mathematical Foundation

```
Phase Angle (θ) = (Moon Longitude - Sun Longitude) mod 360°

Tithi Number = floor(θ / 12°) + 1

Paksha (Fortnight):
  - Shukla (Waxing): θ < 180° (New Moon → Full Moon)
  - Krishna (Waning): θ ≥ 180° (Full Moon → New Moon)
```

### 1.3 Detailed Flowchart

```
                              ┌─────────────────┐
                              │      START      │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   INPUT: Date (YYYY-MM-DD)   │
                        │   INPUT: Time (optional)     │
                        │   INPUT: Location (optional) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 1: Convert to Julian    │
                        │ Day Number (JDN)             │
                        │                              │
                        │ JDN = gregorian_to_jd(date)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 2: Get Sun Position     │
                        │                              │
                        │ L_sun = swe.calc_ut(JDN,     │
                        │         SUN, SIDEREAL)[0]    │
                        │                              │
                        │ Apply Lahiri Ayanamsa        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 3: Get Moon Position    │
                        │                              │
                        │ L_moon = swe.calc_ut(JDN,    │
                        │          MOON, SIDEREAL)[0]  │
                        │                              │
                        │ Apply Lahiri Ayanamsa        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 4: Calculate Elongation │
                        │                              │
                        │ elongation = (L_moon - L_sun)│
                        │              mod 360°        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 5: Calculate Tithi      │
                        │                              │
                        │ tithi_num = floor(elongation │
                        │             / 12) + 1        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │ elongation     │
                              │ < 180° ?       │
                              └───────┬────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
              ┌────────────────┐            ┌────────────────┐
              │     YES        │            │      NO        │
              │                │            │                │
              │ paksha="Shukla"│            │paksha="Krishna"│
              │ (Waxing Moon)  │            │ (Waning Moon)  │
              │                │            │                │
              │ display_tithi  │            │ display_tithi  │
              │ = tithi_num    │            │ = tithi_num-15 │
              └───────┬────────┘            └───────┬────────┘
                      │                             │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────────┐
                        │ Step 6: Get Tithi Name       │
                        │                              │
                        │ TITHI_NAMES = [              │
                        │   "Pratipada", "Dwitiya",    │
                        │   "Tritiya", "Chaturthi",    │
                        │   "Panchami", "Shashthi",    │
                        │   "Saptami", "Ashtami",      │
                        │   "Navami", "Dashami",       │
                        │   "Ekadashi", "Dwadashi",    │
                        │   "Trayodashi","Chaturdashi",│
                        │   "Purnima/Amavasya"         │
                        │ ]                            │
                        │                              │
                        │ name = TITHI_NAMES[          │
                        │        display_tithi - 1]    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 7: Calculate Progress   │
                        │                              │
                        │ tithi_start = (tithi_num-1)  │
                        │               * 12           │
                        │ progress = (elongation -     │
                        │            tithi_start) / 12 │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ OUTPUT:                      │
                        │ {                            │
                        │   number: display_tithi,     │
                        │   paksha: paksha,            │
                        │   name: name,                │
                        │   progress: progress,        │
                        │   elongation: elongation     │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │       END       │
                              └─────────────────┘
```

### 1.4 Pseudocode

```
ALGORITHM CalculateTithi(date, time, location)

INPUT:
  date: Gregorian date (YYYY-MM-DD)
  time: Optional time (HH:MM:SS), defaults to sunrise
  location: Optional coordinates, defaults to Kathmandu

OUTPUT:
  tithi: Object with number, paksha, name, progress

BEGIN
  // Step 1: Convert to Julian Day Number
  jdn = gregorian_to_julian_day(date, time)
  
  // Step 2: Set ayanamsa mode (Lahiri)
  swe.set_sid_mode(LAHIRI_AYANAMSA)
  
  // Step 3: Calculate Sun's sidereal longitude
  sun_result = swe.calc_ut(jdn, SUN, SIDEREAL_FLAGS)
  L_sun = sun_result[0]  // longitude in degrees
  
  // Step 4: Calculate Moon's sidereal longitude
  moon_result = swe.calc_ut(jdn, MOON, SIDEREAL_FLAGS)
  L_moon = moon_result[0]  // longitude in degrees
  
  // Step 5: Calculate elongation (phase angle)
  elongation = (L_moon - L_sun) MOD 360
  IF elongation < 0 THEN
    elongation = elongation + 360
  END IF
  
  // Step 6: Determine tithi number (1-30)
  tithi_num = FLOOR(elongation / 12) + 1
  
  // Step 7: Determine paksha and display number
  IF elongation < 180 THEN
    paksha = "Shukla"
    display_num = tithi_num
  ELSE
    paksha = "Krishna"
    display_num = tithi_num - 15
  END IF
  
  // Step 8: Handle edge cases
  IF display_num == 15 AND paksha == "Shukla" THEN
    name = "Purnima" (Full Moon)
  ELSE IF display_num == 15 AND paksha == "Krishna" THEN
    name = "Amavasya" (New Moon)
  ELSE
    name = TITHI_NAMES[display_num - 1]
  END IF
  
  // Step 9: Calculate progress through current tithi
  tithi_start_angle = (tithi_num - 1) * 12
  progress = (elongation - tithi_start_angle) / 12
  
  RETURN {
    number: display_num,
    paksha: paksha,
    name: name,
    progress: progress,
    elongation: elongation
  }
END
```

---

## 2. BIKRAM SAMBAT CONVERSION ALGORITHM

### 2.1 Overview

Bikram Sambat (BS) is Nepal's official calendar. It is approximately 56 years, 8 months ahead of the Gregorian calendar. Month lengths vary yearly (29-32 days) based on astronomical calculations.

### 2.2 Conversion Method

The system uses a **hybrid approach**:
- **Official Range (2070-2095 BS)**: Uses verified lookup tables
- **Extended Range**: Uses estimated algorithm with sankranti detection

### 2.3 Detailed Flowchart

```
                              ┌─────────────────┐
                              │      START      │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ INPUT: Gregorian Date        │
                        │ (year, month, day)           │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 1: Calculate Reference  │
                        │                              │
                        │ Reference Epoch:             │
                        │ 1943-04-14 = 2000-01-01 BS   │
                        │                              │
                        │ days_diff = date - reference │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 2: Estimate BS Year     │
                        │                              │
                        │ approx_year = gregorian_year │
                        │              + 56            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │   Is year in   │
                              │   official     │
                              │   range?       │
                              │ (2070-2095 BS) │
                              └───────┬────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
              ┌────────────────┐            ┌────────────────┐
              │      YES       │            │       NO       │
              │                │            │                │
              │  Use LOOKUP    │            │ Use ESTIMATED  │
              │  TABLE         │            │ ALGORITHM      │
              └───────┬────────┘            └───────┬────────┘
                      │                             │
                      ▼                             ▼
        ┌─────────────────────────┐   ┌─────────────────────────┐
        │ Step 3A: Lookup Method  │   │ Step 3B: Estimated      │
        │                         │   │                         │
        │ Load BS_MONTH_LENGTHS   │   │ Find Mesh Sankranti     │
        │ for year range          │   │ (Sun enters Aries)      │
        │                         │   │ = BS New Year           │
        │ Iterate through years   │   │                         │
        │ and months to find      │   │ Estimate month lengths  │
        │ exact BS date           │   │ using solar transit     │
        │                         │   │                         │
        │ confidence = "official" │   │ confidence = "estimated"│
        └────────────┬────────────┘   └────────────┬────────────┘
                     │                              │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────────┐
                        │ Step 4: Iterate Years        │
                        │                              │
                        │ bs_year = 2000 (or estimated)│
                        │ remaining_days = days_diff   │
                        │                              │
                        │ WHILE remaining_days >       │
                        │       days_in_year(bs_year): │
                        │                              │
                        │   remaining_days -=          │
                        │       days_in_year(bs_year)  │
                        │   bs_year += 1               │
                        │                              │
                        │ END WHILE                    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 5: Iterate Months       │
                        │                              │
                        │ bs_month = 1                 │
                        │                              │
                        │ WHILE remaining_days >       │
                        │   month_length(bs_year,      │
                        │                bs_month):    │
                        │                              │
                        │   remaining_days -=          │
                        │     month_length(bs_year,    │
                        │                  bs_month)   │
                        │   bs_month += 1              │
                        │                              │
                        │ END WHILE                    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 6: Calculate Day        │
                        │                              │
                        │ bs_day = remaining_days + 1  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 7: Get Month Name       │
                        │                              │
                        │ month_name = BS_MONTH_NAMES[ │
                        │              bs_month - 1]   │
                        │                              │
                        │ BS_MONTH_NAMES = [           │
                        │   "Baishakh", "Jestha",      │
                        │   "Ashadh", "Shrawan",       │
                        │   "Bhadra", "Ashwin",        │
                        │   "Kartik", "Mangsir",       │
                        │   "Poush", "Magh",           │
                        │   "Falgun", "Chaitra"        │
                        │ ]                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ OUTPUT:                      │
                        │ {                            │
                        │   year: bs_year,             │
                        │   month: bs_month,           │
                        │   day: bs_day,               │
                        │   month_name: month_name,    │
                        │   confidence: confidence     │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │       END       │
                              └─────────────────┘
```

### 2.4 Pseudocode

```
ALGORITHM GregorianToBikramSambat(gregorian_date)

INPUT:
  gregorian_date: Date object (year, month, day)

OUTPUT:
  bs_date: Object with year, month, day, month_name, confidence

CONSTANTS:
  REFERENCE_GREGORIAN = Date(1943, 4, 14)
  REFERENCE_BS = (2000, 1, 1)
  BS_MIN_YEAR = 2070
  BS_MAX_YEAR = 2095

BEGIN
  // Step 1: Calculate days from reference
  days_diff = days_between(REFERENCE_GREGORIAN, gregorian_date)
  
  // Step 2: Estimate BS year
  approx_year = gregorian_date.year + 56
  
  // Step 3: Determine method
  IF approx_year >= BS_MIN_YEAR AND approx_year <= BS_MAX_YEAR THEN
    method = "lookup"
    confidence = "official"
  ELSE
    method = "estimated"
    confidence = "estimated"
  END IF
  
  // Step 4: Find exact year
  bs_year = 2000
  remaining = days_diff
  
  WHILE remaining > get_year_days(bs_year, method) DO
    remaining = remaining - get_year_days(bs_year, method)
    bs_year = bs_year + 1
  END WHILE
  
  // Step 5: Find month
  bs_month = 1
  WHILE remaining > get_month_days(bs_year, bs_month, method) DO
    remaining = remaining - get_month_days(bs_year, bs_month, method)
    bs_month = bs_month + 1
  END WHILE
  
  // Step 6: Day is remaining + 1
  bs_day = remaining + 1
  
  // Step 7: Get month name
  month_name = BS_MONTH_NAMES[bs_month - 1]
  
  RETURN {
    year: bs_year,
    month: bs_month,
    day: bs_day,
    month_name: month_name,
    confidence: confidence
  }
END
```

---

## 3. FESTIVAL DATE CALCULATION ALGORITHM

### 3.1 Overview

Festivals are calculated using rules that specify:
- Calendar system (BS/lunar)
- Month or lunar month
- Day or tithi
- Paksha (for lunar festivals)
- Adhik month policy

### 3.2 Rule Types

| Rule Type | Description | Example |
|-----------|-------------|---------|
| `lunar_tithi` | Specific tithi in lunar month | Dashain = Ashwin Shukla 10 |
| `lunar_purnima` | Full moon of lunar month | Buddha Jayanti = Baishakh Purnima |
| `solar_fixed` | Fixed BS date | BS New Year = Baishakh 1 |
| `solar_sankranti` | Solar transit day | Maghe Sankranti = Sun enters Makara |

### 3.3 Detailed Flowchart

```
                              ┌─────────────────┐
                              │      START      │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ INPUT: festival_id           │
                        │ INPUT: year (Gregorian)      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 1: Check Override       │
                        │ Database                     │
                        │                              │
                        │ override = get_override(     │
                        │            festival_id,      │
                        │            year)             │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │   Override     │
                              │   exists?      │
                              └───────┬────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
              ┌────────────────┐            ┌────────────────┐
              │      YES       │            │       NO       │
              │                │            │                │
              │ RETURN {       │            │ Continue to    │
              │   date:override│            │ calculation    │
              │   method:      │            │                │
              │   "override"   │            │                │
              │ }              │            │                │
              └───────┬────────┘            └───────┬────────┘
                      │                             │
                      ▼                             ▼
              ┌────────────────┐   ┌───────────────────────────┐
              │      END       │   │ Step 2: Load Festival     │
              └────────────────┘   │ Rule from JSON            │
                                   │                           │
                                   │ rule = festival_rules[    │
                                   │        festival_id]       │
                                   └─────────────┬─────────────┘
                                                 │
                                                 ▼
                                        ┌────────────────┐
                                        │  Rule Type?    │
                                        └───────┬────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    │                           │                           │
                    ▼                           ▼                           ▼
          ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
          │  lunar_tithi    │         │  solar_fixed    │         │solar_sankranti  │
          └────────┬────────┘         └────────┬────────┘         └────────┬────────┘
                   │                           │                           │
                   ▼                           ▼                           ▼
  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌──────────────────────────┐
  │ Step 3A: Lunar Tithi     │  │ Step 3B: Solar Fixed     │  │ Step 3C: Sankranti       │
  │                          │  │                          │  │                          │
  │ 1. Find lunar month      │  │ 1. Convert BS date to    │  │ 1. Find when Sun enters  │
  │    start (Amavasya)      │  │    Gregorian:            │  │    target rashi:         │
  │                          │  │                          │  │                          │
  │ 2. Check for Adhik Maas  │  │    date = bs_to_greg(    │  │    rashi = rule.rashi    │
  │                          │  │      year, rule.month,   │  │    (e.g., "Makara")      │
  │ 3. Scan days until       │  │      rule.day)           │  │                          │
  │    target tithi found:   │  │                          │  │ 2. Calculate solar       │
  │                          │  │ 2. RETURN date           │  │    longitude for each    │
  │    FOR day = 1 TO 35:    │  │                          │  │    day until longitude   │
  │      tithi = calc_tithi  │  │                          │  │    crosses threshold     │
  │      IF tithi matches:   │  │                          │  │                          │
  │        RETURN date       │  │                          │  │ 3. RETURN date           │
  └────────────┬─────────────┘  └────────────┬─────────────┘  └────────────┬─────────────┘
               │                             │                             │
               └─────────────────────────────┼─────────────────────────────┘
                                             │
                                             ▼
                        ┌──────────────────────────────┐
                        │ Step 4: Apply Duration       │
                        │                              │
                        │ IF rule.duration > 1:        │
                        │   end_date = start_date +    │
                        │              duration - 1    │
                        │ ELSE:                        │
                        │   end_date = start_date      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ OUTPUT:                      │
                        │ {                            │
                        │   start_date: start_date,    │
                        │   end_date: end_date,        │
                        │   method: "calculated",      │
                        │   rule_type: rule.type       │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │       END       │
                              └─────────────────┘
```

### 3.4 Lunar Tithi Sub-Algorithm

```
                              ┌─────────────────┐
                              │ LUNAR TITHI     │
                              │ SUB-ALGORITHM   │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ INPUT:                       │
                        │   lunar_month (e.g., "Ashwin"│
                        │   target_tithi (e.g., 10)    │
                        │   target_paksha ("Shukla")   │
                        │   year (Gregorian)           │
                        │   adhik_policy               │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 1: Find Month Start     │
                        │                              │
                        │ Find Amavasya (New Moon)     │
                        │ that starts the lunar month  │
                        │                              │
                        │ month_start = find_lunar_    │
                        │               month_start(   │
                        │               lunar_month,   │
                        │               year)          │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 2: Check Adhik Maas     │
                        │                              │
                        │ adhik = is_adhik_month(      │
                        │         lunar_month, year)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │  Adhik Maas    │
                              │  detected?     │
                              └───────┬────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
              ┌────────────────┐            ┌────────────────┐
              │      YES       │            │       NO       │
              │                │            │                │
              │ Apply adhik    │            │ Use normal     │
              │ _policy:       │            │ month          │
              │                │            │                │
              │ "skip": +30d   │            │                │
              │ "use_adhik": 0 │            │                │
              │ "both": both   │            │                │
              └───────┬────────┘            └───────┬────────┘
                      │                             │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────────┐
                        │ Step 3: Scan for Target      │
                        │ Tithi                        │
                        │                              │
                        │ FOR day = 0 TO 35:           │
                        │   current_date = month_start │
                        │                 + day        │
                        │   tithi = calculate_tithi(   │
                        │           current_date)      │
                        │                              │
                        │   IF tithi.number ==         │
                        │      target_tithi AND        │
                        │      tithi.paksha ==         │
                        │      target_paksha:          │
                        │                              │
                        │     RETURN current_date      │
                        │   END IF                     │
                        │ END FOR                      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │  Tithi found?  │
                              └───────┬────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
              ┌────────────────┐            ┌────────────────┐
              │      YES       │            │       NO       │
              │                │            │                │
              │ RETURN date    │            │ RETURN None    │
              │                │            │ (not found)    │
              └───────┬────────┘            └───────┬────────┘
                      │                             │
                      ▼                             ▼
              ┌─────────────────┐           ┌─────────────────┐
              │       END       │           │       END       │
              └─────────────────┘           └─────────────────┘
```

---

## 4. LUNAR MONTH DETECTION ALGORITHM

### 4.1 Overview

In the Amanta (Purnimant) lunar month system used in Nepal:
- Month starts at Amavasya (New Moon)
- Month ends at the next Amavasya
- Month is named after the solar month containing the Purnima (Full Moon)

### 4.2 Flowchart

```
                              ┌─────────────────┐
                              │      START      │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ INPUT: Gregorian Date        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 1: Find Previous        │
                        │ Amavasya (New Moon)          │
                        │                              │
                        │ Search backwards until       │
                        │ tithi = Amavasya (30/Krishna │
                        │ 15)                          │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 2: Find Purnima         │
                        │ (Full Moon) in this month    │
                        │                              │
                        │ Search forward ~15 days      │
                        │ until tithi = Purnima (15/   │
                        │ Shukla 15)                   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 3: Get Solar Month      │
                        │ at Purnima                   │
                        │                              │
                        │ solar_month = get_rashi(     │
                        │               sun_longitude) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 4: Map to Lunar Month   │
                        │ Name                         │
                        │                              │
                        │ LUNAR_MONTH_NAMES = {        │
                        │   0: "Chaitra",              │
                        │   1: "Baishakh",             │
                        │   2: "Jestha",               │
                        │   3: "Ashadh",               │
                        │   4: "Shrawan",              │
                        │   5: "Bhadra",               │
                        │   6: "Ashwin",               │
                        │   7: "Kartik",               │
                        │   8: "Mangsir",              │
                        │   9: "Poush",                │
                        │   10: "Magh",                │
                        │   11: "Falgun"               │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ OUTPUT:                      │
                        │ {                            │
                        │   lunar_month: name,         │
                        │   month_start: amavasya_date,│
                        │   purnima: purnima_date,     │
                        │   is_adhik: false            │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │       END       │
                              └─────────────────┘
```

---

## 5. ADHIK MAAS DETECTION ALGORITHM

### 5.1 Overview

An **Adhik Maas** (intercalary month) occurs when a lunar month contains no solar sankranti (Sun entering a new zodiac sign). This happens approximately every 32.5 months.

### 5.2 Rule

```
IF a lunar month has NO sankranti (solar transit):
  → That month is Adhik (intercalary)
  → Named "Adhik [Month Name]" or "Purushottam Maas"
```

### 5.3 Flowchart

```
                              ┌─────────────────┐
                              │      START      │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ INPUT: Lunar Month, Year     │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 1: Find Lunar Month     │
                        │ Boundaries                   │
                        │                              │
                        │ start = Amavasya[month]      │
                        │ end = Amavasya[month+1]      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 2: Count Sankrantis     │
                        │ in Month                     │
                        │                              │
                        │ sankranti_count = 0          │
                        │                              │
                        │ FOR each day in [start, end]:│
                        │   IF sun_enters_new_rashi(): │
                        │     sankranti_count += 1     │
                        │ END FOR                      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │ sankranti_     │
                              │ count == 0 ?   │
                              └───────┬────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │                             │
                       ▼                             ▼
              ┌────────────────┐            ┌────────────────┐
              │      YES       │            │       NO       │
              │                │            │                │
              │ is_adhik = TRUE│            │ is_adhik =     │
              │                │            │ FALSE          │
              │ This is an     │            │                │
              │ intercalary    │            │ Normal month   │
              │ month!         │            │                │
              └───────┬────────┘            └───────┬────────┘
                      │                             │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────────┐
                        │ OUTPUT:                      │
                        │ {                            │
                        │   is_adhik: is_adhik,        │
                        │   month_name: name,          │
                        │   sankranti_count: count     │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │       END       │
                              └─────────────────┘
```

---

## 6. PANCHANGA CALCULATION ALGORITHM

### 6.1 Overview

The **Panchanga** (five limbs) is a Hindu calendar that calculates five elements for each day:

1. **Tithi** — Lunar day (1-30)
2. **Vaara** — Weekday (1-7)
3. **Nakshatra** — Lunar mansion (1-27)
4. **Yoga** — Sun-Moon angular combination (1-27)
5. **Karana** — Half-tithi (1-11)

### 6.2 Flowchart

```
                              ┌─────────────────┐
                              │      START      │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ INPUT: Date                  │
                        └──────────────┬───────────────┘
                                       │
      ┌────────────────────────────────┼────────────────────────────────┐
      │                                │                                │
      ▼                                ▼                                ▼
┌───────────────┐               ┌───────────────┐               ┌───────────────┐
│ Calculate     │               │ Calculate     │               │ Get Weekday   │
│ Sun/Moon      │               │ JDN           │               │               │
│ Positions     │               │               │               │ vaara = dow   │
│               │               │               │               │         + 1   │
│ L_sun, L_moon │               │               │               │               │
└───────┬───────┘               └───────┬───────┘               └───────┬───────┘
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        │
                                        ▼
        ┌───────────────────────────────────────────────────────────────┐
        │                      PARALLEL CALCULATIONS                     │
        └───────────────────────────────────────────────────────────────┘
                │                   │                   │
                ▼                   ▼                   ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │ 1. TITHI        │   │ 2. NAKSHATRA    │   │ 3. YOGA         │
    │                 │   │                 │   │                 │
    │ elongation =    │   │ nakshatra =     │   │ L_sum = L_sun   │
    │ (L_moon-L_sun)  │   │ floor(L_moon /  │   │       + L_moon  │
    │ mod 360         │   │       13.333)   │   │                 │
    │                 │   │       + 1       │   │ yoga = floor(   │
    │ tithi = floor(  │   │                 │   │ L_sum / 13.333) │
    │ elongation/12)  │   │ Range: 1-27     │   │ + 1             │
    │ + 1             │   │                 │   │                 │
    │                 │   │ Names:          │   │ Range: 1-27     │
    │ Range: 1-30     │   │ Ashwini,        │   │                 │
    │                 │   │ Bharani, ...    │   │ Names:          │
    └────────┬────────┘   └────────┬────────┘   │ Vishkumbha,     │
             │                     │            │ Priti, ...      │
             │                     │            └────────┬────────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────────────┐
                        │ 4. KARANA                    │
                        │                              │
                        │ karana_idx = floor(          │
                        │   elongation / 6) + 1        │
                        │                              │
                        │ There are 11 karanas         │
                        │ that repeat in a pattern     │
                        │                              │
                        │ karana = KARANA_CYCLE[       │
                        │          karana_idx % 60]    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ OUTPUT: Panchanga            │
                        │ {                            │
                        │   tithi: {...},              │
                        │   vaara: {...},              │
                        │   nakshatra: {...},          │
                        │   yoga: {...},               │
                        │   karana: {...}              │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │       END       │
                              └─────────────────┘
```

---

## 7. SANKRANTI DETECTION ALGORITHM

### 7.1 Overview

**Sankranti** is the moment when the Sun enters a new zodiac sign (rashi). There are 12 sankrantis per year. Key sankrantis for festivals:

| Sankranti | Zodiac | Festival |
|-----------|--------|----------|
| Mesh | Aries | BS New Year |
| Makara | Capricorn | Maghe Sankranti |

### 7.2 Flowchart

```
                              ┌─────────────────┐
                              │      START      │
                              └────────┬────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ INPUT:                       │
                        │   target_rashi (0-11)        │
                        │   year (Gregorian)           │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 1: Calculate Target     │
                        │ Longitude                    │
                        │                              │
                        │ target_long = rashi * 30°    │
                        │                              │
                        │ RASHI = {                    │
                        │   0: "Mesh" (Aries),         │
                        │   1: "Vrishabha" (Taurus),   │
                        │   2: "Mithun" (Gemini),      │
                        │   ... ,                      │
                        │   9: "Makara" (Capricorn),   │
                        │   ...                        │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 2: Estimate Start Date  │
                        │                              │
                        │ Mesh ~= April 13-14          │
                        │ Makara ~= January 14-15      │
                        │                              │
                        │ search_start = estimate -    │
                        │                5 days        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 3: Binary Search        │
                        │                              │
                        │ FOR day in range(15):        │
                        │   current = search_start +   │
                        │             day              │
                        │   L_sun = get_sun_longitude( │
                        │           current)           │
                        │                              │
                        │   rashi_now = floor(L_sun /  │
                        │               30)            │
                        │                              │
                        │   IF rashi_now == target:    │
                        │     // Found transit day     │
                        │     // Refine to exact time  │
                        │     GO TO Step 4             │
                        │   END IF                     │
                        │ END FOR                      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ Step 4: Refine to Exact      │
                        │ Time (Optional)              │
                        │                              │
                        │ Use binary search within     │
                        │ the transit day to find      │
                        │ exact moment when:           │
                        │                              │
                        │ L_sun crosses target_long    │
                        │                              │
                        │ (Can achieve minute-level    │
                        │ accuracy)                    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ OUTPUT:                      │
                        │ {                            │
                        │   date: sankranti_date,      │
                        │   time: exact_time,          │
                        │   rashi: rashi_name,         │
                        │   sun_longitude: L_sun       │
                        │ }                            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │       END       │
                              └─────────────────┘
```

---

## Summary Table

| Algorithm | Input | Output | Complexity |
|-----------|-------|--------|------------|
| Tithi Calculation | Date | Tithi (1-15), Paksha | O(1) |
| BS Conversion | Gregorian Date | BS Date, Confidence | O(n) years |
| Festival Calculation | Festival ID, Year | Date(s), Method | O(n) days |
| Lunar Month Detection | Date | Month Name, Boundaries | O(n) days |
| Adhik Maas Detection | Lunar Month, Year | Is Adhik (bool) | O(n) days |
| Panchanga | Date | 5-element result | O(1) |
| Sankranti | Rashi, Year | Transit Date/Time | O(n) days |

---

*Document prepared for Project Parva — Algorithm Reference*
