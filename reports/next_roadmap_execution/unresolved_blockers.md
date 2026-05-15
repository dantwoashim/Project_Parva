# Unresolved Blockers

## Blocking Repo Issues

None identified in the final public verification run.

## Blocked Local Packaging Command

- Command: `py -3.11 -m build packages/parva-python`
- Error: `No module named build`
- Classification: environment issue
- Detail: repeated `py -3.11 -m pip install build` attempts timed out while reading from PyPI.
- Mitigation evidence: `py -3.11 -m pip wheel packages/parva-python --no-deps --no-build-isolation -w <temp>` passed and produced the Python SDK wheel through installed setuptools/wheel.

## Non-Blocking Environment Caveats

- Ambient `python --version` returns Python 3.10.10, while Project Parva expects Python 3.11.x. Verification used `py -3.11`, which returned Python 3.11.4.
- Ambient `node --version` returns v25.2.1, while Project Parva expects Node 20.x. Verification used the repository-managed Node v20.20.2 path resolved by release tooling.

These are local shell defaults, not repository failures. The reproducibility gate passed because the repository can resolve the expected toolchain.

## Claim Boundaries That Remain

- No government authority.
- No legal, tax, payroll, banking, or religious authority.
- No official future BS date authority.
- No external certification.
- No customer, pilot, or adoption proof.
- No public exact unsupported Future-BS predictions.
