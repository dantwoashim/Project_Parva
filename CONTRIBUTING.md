# Contributing to Project Parva

Thanks for helping improve Project Parva.

## Before you start

- Read [README.md](README.md), [docs/STABILITY.md](docs/STABILITY.md), and [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).
- Use `/v3/api/*` as the canonical API surface in tests, docs, and examples.
- Treat `/api/*` as legacy compatibility only.
- Do not commit generated artifacts, `node_modules`, virtualenvs, local reports, or secrets.

## Local setup

Recommended:

```bash
make install
```

Manual:

```bash
python3.11 -m pip install -e .[test,dev]
python3.11 -m pip install -e sdk/python
npm --prefix frontend ci
```

If your local `npm` is not running on Node 20:

```bash
make NPM="npx -y -p node@20 -p npm@10 npm" install-frontend
```

## Contribution workflow

1. Open an issue using the most relevant template in `.github/ISSUE_TEMPLATE/`.
2. Keep changes scoped and reviewable.
3. Update docs when behavior, support posture, or setup changes.
4. Run `make verify` before you open a PR.
5. Use the PR template and explain the scope, risks, and validation results.

## Date, festival, and rule changes need evidence

If your change affects festival dates, calendrical calculations, source review, or trust claims, include:

- Source references such as MoHA notices, Panchang references, or other primary material
- A short accuracy or behavior impact summary
- Any affected profiles, jurisdictions, or date ranges
- Notes on whether the change is authoritative, computed, heuristic, or provisional

If evidence is incomplete, say so clearly. Do not upgrade claims in docs or product copy without stronger backing.

## Validation expectations

Minimum:

```bash
make verify
```

If your change is narrow, include the targeted commands you ran in the PR description.

## Style and review expectations

- Prefer truthful docs over optimistic docs.
- Preserve public interfaces unless the change is deliberate and documented.
- Keep compatibility wrappers thin.
- Do not add product claims that the runtime or data cannot justify.
- If a file looks stale but risky to delete, document it in `docs/STALE_AND_DEPRECATED_ITEMS.md` instead of guessing.
