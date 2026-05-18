---
status: research
audience: operators
---

# Ephemeris Kernel Policy

JPL kernels are optional research inputs. Public verification must pass without
them.

Kernel rules:

- Do not commit large binary kernels.
- Do not expose local kernel paths through public docs, APIs, OpenAPI examples,
  SDK defaults, agent tools, MCP resources, or reports.
- If a configured kernel is present, verify its hash before using it for a
  research report.
- If a kernel is absent, return explicit unavailable behavior and keep the
  public Moshier/Swiss fallback safe.
- Treat JPL output as astronomical evidence only. It does not replace official
  Panchanga, civil calendar, holiday, tax, payroll, banking, or legal authority.

The kernel registry lives in `config/ephemeris-kernels.yaml`. Hash verification
is performed with:

```bash
python scripts/ephemeris/verify_kernel_hashes.py
```

The script reports kernel ids and hash status only. It must not print local
absolute paths.
