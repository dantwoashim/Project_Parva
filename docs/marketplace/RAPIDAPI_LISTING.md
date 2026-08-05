# RapidAPI Listing

Use the RapidAPI import contract at `docs/marketplace/rapidapi-openapi.json`.
It is generated from `docs/api-docs/openapi.json`, gives every endpoint a clean
display name, and points to `https://api.prabinghimire1.com.np`.

## Project Details

- Name: `Project Parva`
- Version: `3.0.0`
- Category: `Data`
- Website: `https://prabinghimire1.com.np`
- Repository: `https://github.com/dantwoashim/Project_Parva`
- Base URL: `https://api.prabinghimire1.com.np`
- Health check: `GET /health/ready`
- Visibility: `Public`

Short description:

```text
Nepali date conversion, calendar, festival, fiscal, working-day and Panchanga endpoints.
```

Long description:

```markdown
Project Parva provides one HTTP API for software that works with Nepali dates
and calendar rules.

The public surface includes:

- Gregorian and Bikram Sambat conversion
- BS date validation and dual-calendar month views
- fiscal-year and working-day calculations
- upcoming festival dates and festival lookup
- Panchanga summaries based on Nepal-local sunrise
- calendar feeds and bounded planning helpers
- explicitly labelled Future BS research forecasts

Responses preserve source, confidence, warning and review fields where they
matter. Future BS forecasts are published as computed research rather than an
official calendar. Government publications and the responsible institution
remain authoritative for legal, tax, payroll, banking and religious decisions.

The API uses JSON and the public endpoints require no provider-issued API key.
RapidAPI supplies consumer credentials at its gateway.
```

Suggested search terms:

```text
Nepal, Nepali calendar, Bikram Sambat, BS AD conversion, Panchanga, festivals, fiscal year
```

## Studio Submission

1. Open `https://rapidapi.com/studio` and select the personal account.
2. Create an API project named `Project Parva` and import
   `docs/marketplace/rapidapi-openapi.json`.
3. Apply the listing fields above under **Hub Listing > General**.
4. Confirm the imported base URL and test `GET /health/ready` through RapidAPI.
5. Keep provider authentication disabled. The origin already exposes the curated
   public surface; RapidAPI authenticates subscribers at its gateway.
6. Start with a free plan while the public host uses sleep-on-idle infrastructure.
7. Accept the marketplace terms and switch visibility to public.

Do not advertise Future BS output as official or guaranteed. Preserve
`computed_prediction_not_official`, confidence, warnings and review fields in
examples and generated snippets.
