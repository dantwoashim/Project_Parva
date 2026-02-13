# Ephemeris Module Specification (v2.0)

## Overview

This module provides astronomical calculations using **Swiss Ephemeris** (pyswisseph)
with NASA JPL DE431 ephemerides for sub-arcsecond accuracy.

## Library: pyswisseph

- **Version**: 2.10.3.2
- **Ephemeris**: DE431 (built-in, no separate data files needed)
- **Accuracy**: Sub-arcsecond for Sun/Moon positions
- **Range**: 13201 BCE to 17191 CE

## Ayanamsa

- **Standard**: Lahiri (Chitrapaksha)
- **swisseph constant**: `swe.SIDM_LAHIRI`
- **Value at J2000.0**: 23°51'11"

## Coordinate System

- **Ecliptic longitude**: 0-360° measured from vernal equinox
- **Sidereal**: Tropical corrected by ayanamsa
- **Used for**: Tithi, Nakshatra, Yoga, Karana calculations

## Key Functions

### Sun Position
```python
def get_sun_longitude(dt: datetime, sidereal: bool = True) -> float:
    """Get Sun's ecliptic longitude in degrees."""
```

### Moon Position
```python
def get_moon_longitude(dt: datetime, sidereal: bool = True) -> float:
    """Get Moon's ecliptic longitude in degrees."""
```

### Sunrise
```python
def calculate_sunrise(date: date, lat: float, lon: float) -> datetime:
    """Calculate sunrise time for location."""
```

## Constants

- **Kathmandu**: 27.7172°N, 85.3240°E
- **Timezone**: UTC+5:45 (Nepal Standard Time)
- **Ayanamsa epoch**: J2000.0 (1 Jan 2000, 12:00 TT)

## Error Handling

- Invalid dates raise `EphemerisError`
- Out-of-range dates (beyond DE431) raise `EphemerisRangeError`
- All functions log calculation details for debugging

## Performance

- Single position calculation: <1ms
- Caching recommended for repeated queries
- Tithi boundary search: ~10-50ms (binary search)
