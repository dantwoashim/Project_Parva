# Historical Source Pool

This document tracks how far the repo currently reaches with durable holiday-source evidence.

## Current Reach

- Structured official MoHA data: **2078-2083 BS**
- Archived raw official MoHA PDFs: **2076-2077 BS**
- Archived validated secondary sources: **2068-2075 BS**
- Decoded digital provider coverage: **2000-2100 BS** via Ratopati archive harvest
- Explicit queue coverage: **2000-2083 BS**

## Archived Secondary Sources

| BS Year | Source | Coverage | Local Artifact |
|---|---|---|---|
| 2068 | Koirala archive blog | Annual full holiday list | `data/source_archive/secondary/2068_koirala_holiday_list.html` |
| 2069 | Koirala archive blog | Annual full holiday list | `data/source_archive/secondary/2069_koirala_holiday_list.html` |
| 2070 | Koirala archive blog | Annual full holiday list | `data/source_archive/secondary/2070_koirala_holiday_list.html` |
| 2071 | Koirala archive blog | Annual full holiday list | `data/source_archive/secondary/2071_koirala_holiday_list.html` |
| 2072 | Online Khabar | Annual holiday summary | `data/source_archive/secondary/2072_onlinekhabar_holiday_summary.html` |
| 2073 | Online Khabar | Annual full holiday list | `data/source_archive/secondary/2073_onlinekhabar_holiday_list.html` |
| 2074 | DNews Nepal | Annual full holiday list | `data/source_archive/secondary/2074_dnewsnepal_holiday_list.html` |
| 2074 | Corporate Nepal | Annual full holiday list backup | `data/source_archive/secondary/2074_corporatenepal_holiday_list.html` |
| 2075 | Kharibot | Annual full holiday list | `data/source_archive/secondary/2075_kharibot_holiday_list.html` |

## What This Means

- We have pushed the durable online evidence floor from **2076 BS** down to **2068 BS**.
- We now also have a machine-readable secondary provider layer across **2000-2100 BS** from decoded Ratopati month payloads.
- We still do **not** have verified, structured official or archival annual data all the way to **2000 BS**.
- The remaining archival-verification gap from **2000-2067 BS** is now a source-discovery and extraction problem, not a pipeline problem.

## Decoded Digital Provider Layer

- Provider: Ratopati Calendar
- Supported range surfaced by frontend options: **1990-2100 BS** and **1944-2039 AD**
- Harvested into the repo: **2000-2100 BS**
- Decoded month payloads archived: **1,212**
- Event-day records archived: **5,483**
- Holiday-tagged day records archived: **690**
- Artifacts:
  - `data/source_inventory/digital_calendar_providers.json`
  - `data/source_inventory/ratopati_month_coverage_2000_2100.json`
  - `data/source_archive/ratopati/event_days_2000_2100.json`

This layer is useful for broad historical cross-validation and bulk calendar backfill, but it should be treated as a **secondary digital provider**, not as the same authority class as MoHA PDFs, Rajpatra notices, or Rashtriya Panchang publications.

## Next Collection Priorities

1. Find Rajpatra or MoHA mirrors for **2067** and earlier.
2. Recover structured rows from the archived **2076-2077** official PDFs.
3. Add Rashtriya Panchang and library/archive scans for the **2060s** and earlier.

## Institutional Acquisition Channels

- National Archives portal: [https://narchives.gov.np/Archival.aspx](https://narchives.gov.np/Archival.aspx)
- National Archives digital repository: [https://repository.narchives.gov.np/](https://repository.narchives.gov.np/)
- Nepal National Library catalog: [https://archive.nnl.gov.np/](https://archive.nnl.gov.np/)
- Madan Puraskar Pustakalaya catalog: [https://madanpuraskar.org/search/monographslist.php?start=43801](https://madanpuraskar.org/search/monographslist.php?start=43801)

These are the most realistic next places to push the queue below **2071 BS** and eventually toward **2000 BS**.
