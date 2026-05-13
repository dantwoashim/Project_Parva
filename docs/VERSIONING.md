# Versioning

Project Parva uses separate version lines for application code, SDK packages,
protocol contracts, and public data releases. Keeping these separate prevents a
code release from being mistaken for an official calendar publication.

## Application Version

The backend application version is read from Python package metadata when the
package is installed. Local source runs fall back to `0+local`.

The public API exposes version metadata only as software metadata. It does not
mean a calendar source has been promoted or that future dates are official.

## SDK Versions

SDKs use their own package versions:

- JavaScript and TypeScript: `packages/parva-js`
- Python: `packages/parva-python`

SDK versions describe client library compatibility. They do not imply authority
over calendar data.

## Protocol Version

Parva Protocol is currently a protocol draft. Protocol schemas and conformance
reports describe interoperability contracts for public-safe calendar evidence,
credentials, TimeGraph facts, RuleLang rules, impact reports, and offline
bundles.

Protocol version changes should be reviewed alongside:

- schema validation
- conformance output
- public safety checks
- trust verification
- offline bundle verification

## Public Data Release Version

Public release manifests under `data/public/releases/` carry their own release
ids and artifact hashes. These release ids identify public-safe metadata,
schemas, source registry records, and historical examples.

Public data releases must not expose private future-BS vectors, private source
archives, client-specific audit artifacts, or corrected future values.

## Future-BS Research Status

Future-BS research outputs are always labeled:

```text
computed_prediction_not_official
```

Changing a software, SDK, protocol, or data-release version does not turn a
computed future output into an official publication. Official publications and
organization-approved source policies override computed research outputs.
