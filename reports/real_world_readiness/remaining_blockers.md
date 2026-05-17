# Remaining Blockers

Final verification found one reproducible local command mismatch:

- Command: `npx -y -p node@20 -p npm@10 npm --prefix packages/parva-js pack --dry-run`
- Error: npm looks for `D:\Project_Parva-main\package.json` and exits with
  `ENOENT` on this Windows npm invocation.
- Classification: local npm command semantics issue, not a package-content
  issue.
- Evidence: the package-directory equivalent passed:
  `Push-Location packages/parva-js; npx -y -p node@20 -p npm@10 npm pack --dry-run; Pop-Location`.
- Proposed fix: use the package-directory command in Windows release docs/CI, or
  run npm pack from `packages/parva-js` directly. Do not add a root
  `package.json` just to make the wrong command pass.

Expected external blockers that must not be represented as completed:

- PyPI publication requires registry access and trusted publishing setup.
- npm publication requires registry access and trusted publishing/provenance
  setup.
- MCP registry acceptance requires an external registry submission and merged
  entry.
- JPL kernel-backed high-accuracy reports require private or externally supplied
  kernel files configured through policy.
- Domain/DNS changes require domain ownership and provider access.
