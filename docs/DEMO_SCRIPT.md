# Demo Script: Project Parva

## 30-second explanation

Project Parva is a Nepal-focused temporal API platform. It exposes BS/AD conversion, panchanga and festival timing endpoints, API docs, widgets, feeds, and a Python SDK while clearly documenting which surfaces are stable and which are experimental.

## 2-minute walkthrough

1. Open the README and point to the status table.
2. Open the hosted API docs or local `/docs`.
3. Show a BS/AD conversion request.
4. Show a festival or panchanga endpoint.
5. Show `docs/KNOWN_LIMITATIONS.md` to explain accuracy boundaries.
6. Show the SDK README and one test file.

## 5-minute technical walkthrough

Explain the FastAPI route layer, domain services, source inventory docs, SDK packaging, test structure, and the API lifecycle decision to keep `/v3/api/*` stable while treating aliases/labs as experimental.

## What to show in an interview

- Stable API docs
- A concrete `curl` request
- Accuracy/limitations docs
- A representative Pytest test
- The SDK package structure

## What not to overclaim

- Do not call it an official calendar source.
- Do not claim every festival output is equally validated.
- Do not present experimental aliases as independent stable APIs.

## Likely interviewer questions

### How do you handle correctness?

By combining official overlap data in supported ranges, Swiss Ephemeris calculations where relevant, curated source inventories, tests, and public limitation docs.

### Why FastAPI?

It gives strong API ergonomics, OpenAPI docs, Pydantic validation, and a good Python ecosystem for scientific/calendar work.

### What would you improve next?

More validation fixtures, more observability, clearer source comparison pages, and more SDK examples.

