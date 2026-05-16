---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Source Artifact Storage Policy

Status: storage policy for source artifacts.

This policy decides where source artifacts live and whether they can enter public releases or offline bundles.

| Artifact class | Storage | Public? | Checksum | Retention | Restore | Offline bundle? |
|---|---|---:|---|---|---|---:|
| Public release manifests and source registries | Git under `data/public/releases/` | Yes | Manifest `sha256` and trust verification | Indefinite while release is supported | Git checkout | Yes |
| Public protocol schemas and specs | Git under `schemas/`, `specs/` | Yes | Manifest or offline bundle checksum | Indefinite by protocol version | Git checkout | Yes |
| Public validation artifacts | Git under `data/validation/public/` and `backend/data/public_artifacts/` | Yes | Git hash plus optional artifact hash | As long as referenced by runtime/tests | Git checkout | Only if listed |
| MoHA holiday notices | Prefer public URL plus retained checksum; small redistribution-safe extracts may be in Git | Metadata yes, raw file depends on rights | `sha256` of retained file or source metadata | Keep release metadata indefinitely | Source URL, release artifact, or private archive | Machine-readable public release only |
| NPNS/panchanga source scans | Metadata and derived rows in Git if public-safe; raw scans only if redistribution-safe | Metadata yes, raw file depends on rights | `sha256` of retained source or extracted table | Keep metadata indefinitely | Source URL, publisher archive, or private archive | Derived public-safe rows only |
| NRB/fiscal source notices | Metadata and derived decisions in Git if public-safe | Metadata yes | `sha256` of retained notice or extract | Keep release metadata indefinitely | Source URL or private archive | Derived public-safe rows only |
| Large PDFs | Git LFS, GitHub Releases, or object storage with checksums | Only if redistribution-safe | `sha256` sidecar or manifest row | According to source license and release needs | Object storage URL plus checksum | No raw PDF by default |
| JPL kernels and astronomy ephemerides | Local ignored cache or object storage; do not commit large kernels | No by default | Upstream checksum plus local `sha256` | Re-downloadable from upstream | Download script plus checksum | No |
| Private source archives | Local/private storage outside public repo | No | Local checksum inventory | Operator policy | Private restore process | No |
| Private future-BS model runs | Local/private storage or ignored artifacts | No | Model-run hash if promoted to private registry | Research policy | Private research restore | No |
| Customer/client audit files | Private deployment storage | No | Customer-specific audit hash | Contract-specific | Customer backup | No |

## Rules

- Prefer public metadata plus checksums over raw source dumps.
- Never add private source archives to public release manifests.
- Never require internet access to verify a generated offline bundle.
- Do not commit large binary artifacts unless they are small, public, essential, and redistribution-safe.
- Use object storage, GitHub Releases artifacts, or Git LFS for large public files when a raw file must be retained.
- Keep the local JPL kernel cache ignored; public verification must not require those files.

