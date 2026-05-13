# Protocol Conformance

Compatibility levels:

- `parva_core`
- `parva_source_aware`
- `parva_trust`
- `parva_timegraph`
- `parva_rulelang`
- `parva_impact`
- `parva_agent_safe`
- `parva_offline`
- `parva_full`

A conformance report includes implementation name, protocol version, level, pass/fail status, test counts, test results, warnings, and report hash.

The CLI can also evaluate an explicit fixture artifact:

```bash
python scripts/parva_conformance.py --target local --level parva_core --artifact conformance/corpus/core/date_conversion.json
```

Invalid fixtures must fail with a structured report. This is intentional and proves the conformance runner does not pass every artifact by default.
