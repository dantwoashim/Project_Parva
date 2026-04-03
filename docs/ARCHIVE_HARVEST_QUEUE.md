# Archive Harvest Queue

- BS range: **2000-2083**
- Structured official years: **6**
- Archived raw years: **2**
- Validated secondary years: **8**
- Missing years: **68**

## Separate Digital Fallback

- A decoded secondary digital-provider layer now exists separately for **2000-2100 BS**.
- See `docs/DIGITAL_PROVIDER_POOL.md` and `data/source_archive/ratopati/event_days_2000_2100.json`.
- This does **not** change the archival queue counts below, because the queue is intentionally tracking official/archive discovery rather than provider-derived fallback coverage.

## Earliest Reach

- Earliest structured official year: **2078**
- Earliest archived raw year: **2076**
- Earliest validated secondary year: **2068**

## High-Priority Gaps

| BS Year | Status | Next Action | Sources |
|---|---|---|---|
| 2050 | missing | discover_sources | - |
| 2051 | missing | discover_sources | - |
| 2052 | missing | discover_sources | - |
| 2053 | missing | discover_sources | - |
| 2054 | missing | discover_sources | - |
| 2055 | missing | discover_sources | - |
| 2056 | missing | discover_sources | - |
| 2057 | missing | discover_sources | - |
| 2058 | missing | discover_sources | - |
| 2059 | missing | discover_sources | - |
| 2060 | missing | discover_sources | - |
| 2061 | missing | discover_sources | - |
| 2062 | missing | discover_sources | - |
| 2063 | missing | discover_sources | - |
| 2064 | missing | discover_sources | - |
| 2065 | missing | discover_sources | - |
| 2066 | missing | discover_sources | - |
| 2067 | missing | discover_sources | - |
| 2068 | validated_secondary | cross_validate_and_extract | koirala_2068_holiday_list |
| 2069 | validated_secondary | cross_validate_and_extract | koirala_2069_holiday_list |
| 2070 | validated_secondary | cross_validate_and_extract | koirala_2070_holiday_list |
| 2071 | validated_secondary | cross_validate_and_extract | koirala_2071_holiday_list |
| 2072 | validated_secondary | cross_validate_and_extract | onlinekhabar_2072_holiday_summary |
| 2073 | validated_secondary | cross_validate_and_extract | onlinekhabar_2073_holiday_list |
| 2074 | validated_secondary | cross_validate_and_extract | dnewsnepal_2074_holiday_list, corporatenepal_2074_holiday_list |
| 2075 | validated_secondary | cross_validate_and_extract | kharibot_2075_holiday_list |
| 2076 | archived_raw_pdf | improve_extraction | moha_official_2076 |
| 2077 | archived_raw_pdf | improve_extraction | moha_official_2077 |
