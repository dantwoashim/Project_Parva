# Project Parva Local Kernel

Local/offline verification helpers for Project Parva proof artifacts.

This package verifies Project Parva membranes, proof packs, and Timepack-shaped
artifacts without calling the live API. Civil operation replay is formula-based
for the committed proof-supported core: BS/AD conversion, AD/BS conversion,
BS-date validation, holiday membership/non-membership, working-day policy,
fiscal year, and BS month metadata consistency. Fixtures created by
`scripts/release/generate_proof_fixtures.py` are parity vectors, not the replay
engine.

This package does not provide official calendar, Panchanga, legal, tax, payroll,
banking, or religious authority. It verifies bounded proof artifacts and
preserves review-required and not-authority boundaries.

```bash
npm install @project-parva/local-kernel@alpha
```

For local repository development:

```bash
npm install
npm test
npm pack --dry-run
```

```js
import { verifyMembrane, verifyProofPack, verifyTimepack } from "@project-parva/local-kernel";

const result = await verifyProofPack(proofPack, civilFixtures);
console.log(result.verified, result.reason);
```
