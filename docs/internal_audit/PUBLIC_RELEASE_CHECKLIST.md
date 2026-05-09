# Public Release Checklist

Date: 2026-05-09

| Check | Status | Evidence |
| --- | --- | --- |
| README safe | Complete | README reframed around Nepali temporal infrastructure, source policy, public API boundary, and claim boundary. |
| Public/private route boundary safe | Complete | Private future-BS routers require `PARVA_ENABLE_EXPERIMENTAL_API=true`. |
| OpenAPI safe | Complete | Public OpenAPI does not list private prediction, export, backtest, model-run, residual, compare, or schedule-impact routes. |
| Public capabilities safe | Complete | Capability payloads return methodology and boundary metadata only. |
| Future vectors absent from public examples | Complete | Public examples use safe endpoints and synthetic source-policy data only. |
| Client names absent | Complete | Public docs and README avoid client/prospect names. |
| No broad accuracy overclaims | Complete | 2078-2083 result is narrow and caveated. |
| Env defaults safe | Complete | `.env.example` keeps experimental routes and private schema disabled. |
| CORS documented | Complete | `docs/DEPLOYMENT.md` documents production CORS origins. |
| Render deployment documented | Complete | `docs/DEPLOYMENT.md` documents Render public backend profile. |
| Cloudflare deployment documented | Complete | `docs/DEPLOYMENT.md` and `docs/DEPLOY_CLOUDFLARE_PAGES.md` document Cloudflare Pages config. |
| Source archives untracked | Complete | `data/source_archive/` removed from Git tracking and ignored. |
| Witness artifacts untracked | Complete | `data/future_bs/witnesses/*` removed from Git tracking and ignored. |
| Source inventory untracked | Complete | `data/source_inventory/` removed from Git tracking and ignored. |
| Tests run | Complete | Focused public-safety tests, frontend build, Render blueprint check, public OpenAPI generation, and full pytest passed. |

## Manual Deployment Steps

1. Set Render environment:

```text
PARVA_ENV=public
PARVA_ROUTE_PROFILE=public_demo
PARVA_ENABLE_EXPERIMENTAL_API=false
PARVA_SHOW_PRIVATE_SCHEMA=false
PARVA_SOURCE_URL=https://github.com/dantwoashim/Project_Parva
CORS_ALLOW_ORIGINS=https://prabinghimire1.com.np,https://www.prabinghimire1.com.np
```

2. Set Cloudflare Pages environment:

```text
VITE_API_BASE_URL=https://api.prabinghimire1.com.np
NODE_VERSION=20
```

3. Confirm public OpenAPI does not include private future-BS routes.
4. Confirm `/v4/api/future-bs/capabilities` returns only metadata.
5. Keep private validation, comparison, and schedule-impact workflows in controlled deployment.
