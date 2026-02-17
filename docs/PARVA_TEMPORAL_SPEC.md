# Parva Temporal Spec v1.0

## The Formal Specification for Nepal's Temporal Infrastructure

---

## 1. Overview

The Parva Temporal Spec defines the computation models, data formats, confidence tiers, provenance protocol, calendar plugin interface, and benchmark methodology for Nepal's multi-calendar temporal infrastructure.

This specification is the canonical reference for:
- Calendar engine implementers
- API consumers
- Data providers
- Verification tool authors

## 2. Computation Models

### 2.1 Ephemeris Engine

**Model**: Moshier analytical (via `pyswisseph`)
**Ayanamsa**: Lahiri (Indian government standard, aligned with Nepal usage)
**Coordinate system**: Sidereal (tropical positions corrected by ayanamsa)

| Parameter | Specification |
|-----------|--------------|
| Sun longitude accuracy | < 1 arcsecond (1950–2100 CE) |
| Moon longitude accuracy | < 3 arcseconds |
| Sunrise calculation | Geometric center, 34' refraction |
| Reference location | Kathmandu (27.7172°N, 85.3240°E) |

### 2.2 Tithi Calculation

**Definition**: Udaya Tithi — the tithi prevailing at local sunrise.

```
tithi_number = floor(elongation / 12°) + 1
elongation = (moon_longitude - sun_longitude) mod 360°
```

| Tithi Range | Paksha |
|-------------|--------|
| 1-15 | Shukla (waxing) |
| 16-30 | Krishna (waning), displayed as 1-15 |

**Special cases**:
- **Vriddhi** (doubled): Tithi spans two sunrises → celebrated on first occurrence
- **Ksheepana** (skipped): Tithi starts and ends between sunrises → not observed

### 2.3 Bikram Sambat Conversion

| Year Range | Method | Confidence |
|------------|--------|------------|
| 2070–2095 BS | Official lookup table | `official` (100%) |
| 2000–2069, 2096–2150 BS | Astronomical projection | `computed` (95%) |
| Outside range | Historical extrapolation | `estimated` (80%) |

### 2.4 Festival Date Calculation

Priority order:
1. **Government gazette overrides** (exact dates for current year)
2. **Ground truth overrides** (verified historical data)
3. **V2 calculator** (lunar month model + tithi rules)
4. **V1 fallback** (legacy rule-based)

### 2.5 Adhik Maas Detection

A lunar month is Adhik (intercalary) when **no sankranti occurs** during it — the Sun stays in the same rashi for the entire new-moon-to-new-moon period. Festivals are **not celebrated** during Adhik Maas.

## 3. Data Formats

### 3.1 Calendar Date (Universal)

```json
{
  "year": 2082,
  "month": 11,
  "day": 4,
  "calendar_id": "bikram_sambat",
  "month_name": "Magh",
  "era": "BS"
}
```

### 3.2 Panchanga Entry

```json
{
  "tithi": {"number": 5, "name": "Panchami", "paksha": "shukla"},
  "nakshatra": {"number": 14, "name": "Chitra"},
  "yoga": {"number": 7, "name": "Siddha"},
  "karana": {"number": 3, "name": "Taitila"},
  "vaara": {"name_english": "Monday", "name_sanskrit": "Somavara"}
}
```

### 3.3 Festival Date

```json
{
  "festival_id": "dashain",
  "start": "2025-10-02",
  "end": "2025-10-11",
  "method": "override",
  "confidence": "official",
  "lunar_month": "Ashwin"
}
```

## 4. Confidence Tiers

| Tier | Confidence | Source |
|------|-----------|--------|
| `exact` | 100% | Government gazette, verified override |
| `official` | 99%+ | Official BS lookup table |
| `computed` | 95%+ | Ephemeris-based calculation |
| `estimated` | 80%+ | Projection model |

## 5. Provenance Protocol

### 5.1 Dataset Hashing

Every response includes `dataset_hash` — SHA-256 of the input data.

### 5.2 Merkle Proofs

Each `(year, festival_id) → date` mapping is a leaf in a Merkle tree. Consumers verify:
1. Leaf is part of canonical dataset
2. Dataset wasn't tampered with since root was published

### 5.3 Snapshot Anchoring

Periodic snapshots with timestamps and Merkle roots create an immutable audit trail.

## 6. Calendar Plugin Interface

```python
class CalendarPlugin(ABC):
    calendar_id: str        # "islamic", "hebrew", etc.
    display_name: str       # Human-readable name
    calendar_type: str      # "solar", "lunar", "lunisolar"

    def from_gregorian(date) -> CalendarDate
    def to_gregorian(year, month, day) -> date
    def month_names() -> List[str]
    def months_in_year(year) -> int
    def days_in_month(year, month) -> int
```

### Registered Calendars

| ID | Name | Type | Epoch |
|----|------|------|-------|
| `bikram_sambat` | Bikram Sambat | Solar | 57 BCE |
| `nepal_sambat` | Nepal Sambat | Lunisolar | 879 CE |
| `islamic` | Hijri | Lunar | 622 CE |
| `hebrew` | Hebrew | Lunisolar | 3761 BCE |
| `chinese` | Chinese | Lunisolar | 2637 BCE |
| `tibetan` | Phuglugs | Lunisolar | 127 BCE |

## 7. Uncertainty Model

```
uncertainty(tithi_boundary) = sqrt(
    uncertainty(ephemeris)² + uncertainty(sunrise)²
)
```

| Component | Error | Confidence |
|-----------|-------|-----------|
| Ephemeris (Moshier) | ±0.1 min | 99.99% |
| Sunrise (geometric) | ±2.0 min | 98% |
| Tithi boundary | ±2.0 min | 98% |
| BS conversion (official) | 0 | 100% |
| BS conversion (computed) | ±1 day possible | 95% |

## 8. Benchmark Standard

The Parva Benchmark defines 3 test suites:
1. **BS Round-Trip**: Gregorian → BS → Gregorian idempotency
2. **Tithi Consistency**: Valid udaya tithi for 365 consecutive days
3. **Festival Calculation**: Non-null results for all registered festivals

Ratings: GOLD (≥95%), SILVER (≥85%), BRONZE (≥70%).

## 9. API Endpoints

See [OPENAPI_SPEC.md](./OPENAPI_SPEC.md) for complete endpoint inventory.

## 10. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-16 | Initial specification |

---

*Parva Temporal Spec is maintained by Project Parva as part of the Nepal as a System initiative.*
