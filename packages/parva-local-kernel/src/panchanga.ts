import { stableStringify } from './canonicalize.js';

export type PanchangaMembrane = {
  canonical_query?: unknown;
  identity_hash?: string;
  result?: Record<string, unknown>;
  boundary?: Record<string, unknown>;
  ephemeris_metadata?: Record<string, unknown>;
  method_dockets?: Array<Record<string, unknown>>;
  method_docket_refs?: string[];
  proof_pack?: { method_parameters?: Record<string, unknown>; source_artifacts?: Record<string, unknown> };
};

export type PanchangaFixture = {
  operation: string;
  expected_replay_result: Record<string, unknown>;
  membrane: PanchangaMembrane;
};

export type PanchangaReplayResult = { verified: boolean; reason: string };

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function getPath(value: unknown, path: string): unknown {
  let current: unknown = value;
  for (const part of path.split('.')) {
    current = asRecord(current)[part];
  }
  return current;
}

function numericClose(left: unknown, right: unknown, tolerance = 0.0001): boolean {
  if (typeof left !== 'number' || typeof right !== 'number') {
    return false;
  }
  return Math.abs(left - right) <= tolerance;
}

function valueMatches(left: unknown, right: unknown, path: string): boolean {
  if (typeof right === 'number') {
    const tolerance = path.includes('longitude') ? 0.0001 : 0.0005;
    return numericClose(left, right, tolerance);
  }
  return stableStringify(left) === stableStringify(right);
}

function requireCanonicalContext(membrane: PanchangaMembrane): string | null {
  const query = asRecord(membrane.canonical_query);
  const context = asRecord(query.context);
  const required = [
    'latitude',
    'longitude',
    'timezone',
    'ephemeris_provider',
    'ephemeris_fixture_id',
    'ayanamsa',
    'sidereal_mode',
    'sunrise_rule',
    'policy_id',
  ];
  for (const field of required) {
    if (context[field] === undefined || context[field] === null || context[field] === '') {
      return `panchanga_canonical_context_missing:${field}`;
    }
  }
  return null;
}

function requireBoundary(membrane: PanchangaMembrane): string | null {
  const boundary = asRecord(membrane.boundary);
  if (boundary.claim_boundary !== 'computed_ephemeris_not_panchanga_authority') {
    return 'panchanga_claim_boundary_missing';
  }
  if (boundary.not_authority !== true || boundary.not_panchanga_authority !== true) {
    return 'panchanga_not_authority_missing';
  }
  if (boundary.not_ritual_final_authority !== true) {
    return 'panchanga_not_ritual_final_authority_missing';
  }
  if (boundary.location_sensitive !== true || boundary.ephemeris_method_dependent !== true) {
    return 'panchanga_sensitivity_boundary_missing';
  }
  return null;
}

function requireEphemerisMetadata(membrane: PanchangaMembrane, fixture?: PanchangaFixture): string | null {
  const metadata = asRecord(membrane.ephemeris_metadata);
  for (const field of ['provider_id', 'provider_kind', 'fixture_id', 'kernel_hash', 'time_scale', 'coordinate_frame']) {
    if (!metadata[field]) {
      return `ephemeris_metadata_missing:${field}`;
    }
  }
  if (metadata.fallback_used === true && metadata.jpl_backed === true) {
    return 'fallback_provider_claims_jpl';
  }
  const providerKind = String(metadata.provider_kind);
  if (metadata.jpl_backed === true && !providerKind.toLowerCase().includes('jpl')) {
    return 'non_jpl_provider_claims_jpl';
  }
  const sourceArtifacts = asRecord(membrane.proof_pack?.source_artifacts);
  const proofMetadata = asRecord(sourceArtifacts.ephemeris_metadata);
  if (stableStringify(proofMetadata) !== stableStringify(metadata)) {
    return 'ephemeris_metadata_proof_mismatch';
  }
  if (fixture) {
    const fixtureMetadata = asRecord(fixture.membrane.ephemeris_metadata);
    if (stableStringify(fixtureMetadata) !== stableStringify(metadata)) {
      return 'ephemeris_metadata_fixture_mismatch';
    }
  }
  return null;
}

function requireMethodDockets(membrane: PanchangaMembrane): string | null {
  const refs = membrane.method_docket_refs ?? [];
  const dockets = membrane.method_dockets ?? [];
  if (refs.length < 4 || dockets.length < 4) {
    return 'method_dockets_missing';
  }
  for (const required of ['sunrise', 'tithi', 'nakshatra', 'yoga_karana']) {
    if (!refs.some((ref) => ref.includes(required))) {
      return `method_docket_ref_missing:${required}`;
    }
  }
  const proofRefs = membrane.proof_pack?.method_parameters?.method_docket_refs;
  if (stableStringify(proofRefs) !== stableStringify(refs)) {
    return 'method_docket_proof_mismatch';
  }
  return null;
}

function findPanchangaFixture(membrane: PanchangaMembrane, fixtures: PanchangaFixture[]): PanchangaFixture | undefined {
  return fixtures.find((fixture) => {
    return fixture.operation === 'panchanga_summary' && fixture.membrane.identity_hash === membrane.identity_hash;
  });
}

function comparePinnedComponents(membrane: PanchangaMembrane, fixture: PanchangaFixture): string | null {
  const actual = membrane.result ?? {};
  const expected = fixture.expected_replay_result;
  const paths = [
    'date',
    'publication_status',
    'review_required',
    'claim_boundary',
    'sunrise.utc',
    'sunrise.local',
    'sunrise.local_time',
    'sunrise.timezone',
    'sunset.utc',
    'tithi.number',
    'tithi.display_number',
    'tithi.name',
    'tithi.paksha',
    'tithi.end_time',
    'tithi.progress',
    'nakshatra.number',
    'nakshatra.name',
    'nakshatra.progress',
    'yoga.number',
    'yoga.name',
    'yoga.progress',
    'karana.number',
    'karana.name',
    'sun.longitude',
    'moon.longitude',
    'vaara.name_english',
  ];
  for (const path of paths) {
    if (!valueMatches(getPath(actual, path), getPath(expected, path), path)) {
      return `panchanga_component_mismatch:${path}`;
    }
  }
  return null;
}

export async function replayPanchangaMembrane(
  membrane: PanchangaMembrane,
  fixtures: PanchangaFixture[],
): Promise<PanchangaReplayResult> {
  const canonicalProblem = requireCanonicalContext(membrane);
  if (canonicalProblem) {
    return { verified: false, reason: canonicalProblem };
  }
  const boundaryProblem = requireBoundary(membrane);
  if (boundaryProblem) {
    return { verified: false, reason: boundaryProblem };
  }
  const fixture = findPanchangaFixture(membrane, fixtures);
  if (!fixture) {
    return { verified: false, reason: 'panchanga_fixture_missing' };
  }
  const metadataProblem = requireEphemerisMetadata(membrane, fixture);
  if (metadataProblem) {
    return { verified: false, reason: metadataProblem };
  }
  const methodProblem = requireMethodDockets(membrane);
  if (methodProblem) {
    return { verified: false, reason: methodProblem };
  }
  const componentProblem = comparePinnedComponents(membrane, fixture);
  if (componentProblem) {
    return { verified: false, reason: componentProblem };
  }
  return { verified: true, reason: 'panchanga_replayed' };
}
