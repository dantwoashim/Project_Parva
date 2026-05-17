# Project Parva External Reviewer Packet

This packet prepares external review. It does not claim that external review has
already happened.

Review scope:

- replay-verifiable civil temporal proof fixtures
- method-docketed Panchanga proof fixture
- local-kernel npm package
- proof pack and Timepack verification paths
- payroll/date-risk audit Timepack flow

Reviewers should run:

```bash
py -3.11 scripts/release/generate_proof_fixtures.py
py -3.11 -m pytest tests/integration/test_shared_proof_fixtures.py -q
pushd packages/parva-local-kernel && npm install && npm test && popd
```

Parva is not government, legal, tax, payroll, banking, religious, or official
Panchanga authority.
