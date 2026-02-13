# Free Deployment Guide (GitHub + Static + API)

Last updated: 2026-02-13

This document describes a zero-budget deployment strategy for Project Parva.

## 1) GitHub Repository (required first)
1. Create an empty GitHub repo.
2. Add remote and push:

```bash
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## 2) Static Artifacts on GitHub Pages (free)
This repository includes workflow:
- `/Users/rohanbasnet14/Documents/Project Parva/.github/workflows/deploy-pages.yml`

What it does:
1. Generates precomputed artifacts (`output/precomputed/*.json`).
2. Runs conformance and authority dashboard generation.
3. Builds static site with links to artifacts and reports.
4. Deploys to GitHub Pages.

Enable in GitHub:
1. Repo Settings -> Pages.
2. Source: GitHub Actions.
3. Run `deploy-pages` workflow (manual or push to main).

Site output folder:
- `output/deploy/site`

## 3) API Endpoint Exposure (free tier)
Use Render Free Web Service with:
- `/Users/rohanbasnet14/Documents/Project Parva/render.yaml`

Deploy steps:
1. In Render: New + Web Service.
2. Connect GitHub repo.
3. Render auto-detects `render.yaml`.
4. Deploy.

Expected API base:
- `https://<service-name>.onrender.com`

Primary endpoints:
- `/v5/api/resolve`
- `/v5/api/spec/conformance`
- `/v5/api/public/artifacts/manifest`
- `/v5/api/public/artifacts/dashboard`
- `/v5/api/public/artifacts/precomputed/{filename}`

## 4) Frontend/API Wiring
Set frontend environment variable:

```bash
VITE_API_BASE=https://<service-name>.onrender.com/v5/api
```

## 5) Post-deploy sanity checks
1. `GET /health` returns healthy.
2. `GET /v5/api/spec/conformance` returns report metadata.
3. `GET /v5/api/public/artifacts/manifest` returns non-empty file list.
4. GitHub Pages site serves precomputed files and authority dashboard.
