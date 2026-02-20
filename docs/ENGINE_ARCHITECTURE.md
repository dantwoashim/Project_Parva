# Engine Architecture

## Runtime layers
1. `calendar/*`
   - BS conversion
   - Tithi and Panchanga
   - Sankranti and lunar month logic
2. `rules/*`
   - Festival rule loading and rule catalog
3. `api/*`
   - HTTP route surfaces (v3 public)
4. `bootstrap/*`
   - app factory, middleware, router registration
5. `provenance/*` + `explainability/*`
   - snapshot metadata and deterministic trace storage

## Request flow (v3)
1. Request enters FastAPI app factory.
2. Request-size guard validates query/body limits.
3. Router resolves to v3 endpoint (`/v3/api/*` or `/api/*` alias).
4. Endpoint computes result using engine modules.
5. Response includes engine metadata + policy + provenance.
6. Security/engine headers are attached before return.

## Public/experimental profiles
- Public: `/v3/api/*` + `/api/*` alias.
- Experimental: `/v2`, `/v4`, `/v5` only when `PARVA_ENABLE_EXPERIMENTAL_API=true`.

## Personal stack architecture
- `personal/panchanga` → panchanga + BS + trace.
- `muhurta` → day partition, rahu-kalam, ceremony filters.
- `kundali` → graha positions, lagna, houses, D9, dasha.

All personal endpoints are deterministic for fixed input and snapshot state.
