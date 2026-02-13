# Cross-Calendar Resolver (M19)

## Purpose
`CrossCalendarResolver` merges observances from multiple calendar families into one ranked list for a target date and location.

## Endpoint
- `GET /v2/api/observances?date=YYYY-MM-DD&location=kathmandu&preferences=nepali_hindu,islamic`
- `GET /v2/api/observances/today`
- `GET /v2/api/observances/conflicts`

## Ranking Inputs
- Base family priority (Nepali Hindu currently highest in Nepal context)
- Confidence weight (`official`, `computed`, `approximate`, etc.)
- Location boost (Kathmandu, Terai, diaspora hints)
- User preference boost (`preferences` query)
- Government holiday boost where available

## Reason Codes
- `PRIMARY_TRADITION`
- `GOVERNMENT_HOLIDAY`
- `ASTRONOMICAL_MATCH`
- `USER_PREFERRED`
- `REGIONAL_CUSTOM`
- `DIASPORA_CONTEXT`

## Conflict Dataset
Curated conflict scenarios are stored at:
- `/Users/rohanbasnet14/Documents/Project Parva/data/cross_calendar/conflicts.json`

Use this dataset to test expected ranking behavior on overlap years.
