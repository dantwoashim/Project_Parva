# Digital Provider Pool

This document tracks non-official digital calendar providers that can be used as large-scale secondary cross-validation sources.

## Ratopati Calendar

- Homepage: [https://calendar.ratopati.com/ad](https://calendar.ratopati.com/ad)
- API base: `https://calapp.ratopati.com/api`
- Source type: `secondary_digital_provider`
- Frontend-supported BS range: **1990-2100**
- Frontend-supported AD range: **1944-2039**
- Harvested into this repo: **2000-2100 BS**

## Decoding Notes

- Ratopati returns encrypted JSON in API responses.
- The public frontend exposes both the encryption flag and the client key material in its page config.
- The repo now includes a reproducible harvester at:
  - `backend/tools/harvest_ratopati_calendar.py`
- The harvester decodes month payloads and stores normalized event-day archives rather than pretending the provider is an official publication.

## Current Artifacts

- Provider inventory:
  - `data/source_inventory/digital_calendar_providers.json`
- Month coverage summary:
  - `data/source_inventory/ratopati_month_coverage_2000_2100.json`
- Event-day archive:
  - `data/source_archive/ratopati/event_days_2000_2100.json`

## Current Harvest Totals

- Decoded monthly payloads: **1,212**
- Harvested BS years: **101**
- Archived event-day records: **5,483**
- Archived total events: **6,326**
- Holiday-tagged event records: **730**

## Important Use Guidance

- Use this pool for:
  - broad historical backfill
  - cross-checking older-year event placement
  - discovering candidate festival and holiday dates to review
- Do not treat this pool as:
  - official MoHA evidence
  - Rajpatra evidence
  - Rashtriya Panchang evidence

It is a valuable scale source, but it remains a provider-derived secondary layer.
