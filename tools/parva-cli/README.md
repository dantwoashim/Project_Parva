# Parva CLI Alpha

Public-safe command line wrapper for the Project Parva Python SDK alpha.

## Commands

```bash
python tools/parva-cli/parva_cli.py today
python tools/parva-cli/parva_cli.py convert ad 2026-04-14
python tools/parva-cli/parva_cli.py convert bs 2083-01-01
python tools/parva-cli/parva_cli.py validate bs 2083-01-32
python tools/parva-cli/parva_cli.py capabilities future-bs
```

The CLI uses:

```text
https://api.prabinghimire1.com.np/v3/api
```

for public calendar calls, and:

```text
https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

for the public future-BS capabilities summary.

It does not call private future-BS prediction, export, model-run, backtest, corrected-value, comparison, or schedule-impact endpoints.
