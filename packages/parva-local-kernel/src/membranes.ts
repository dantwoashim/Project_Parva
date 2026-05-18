import { stableStringify } from './canonicalize.js';
import { replayCivilResult, verifyBsMonthReplay } from './civil.js';
import { sha256Hex } from './hash.js';

export type Membrane = {
  canonical_query?: unknown;
  identity_hash?: string;
  result?: unknown;
  witness?: Record<string, unknown>;
  witness_hash?: string;
  proof_pack?: { steps?: Array<Record<string, unknown>>; source_artifacts?: Record<string, unknown> };
  source_snapshot_hash?: string;
  boundary?: { authority?: string; review_state?: string; claim_boundary?: string };
  field_provenance?: Record<string, { authority?: string; flags?: string[] }>;
};

export type ProofFixture = {
  operation: string;
  expected_replay_result: unknown;
  membrane: Membrane;
};

export type VerificationResult = { verified: boolean; reason: string };

const PREFIX_IDENTITY = 'parva:id:v1:sha256:';
const PREFIX_WITNESS = 'parva:wit:v1:sha256:';

function canonicalQueryForBackend(query: unknown): string {
  return stableStringify(query);
}

function operationOf(membrane: Membrane): string {
  const query = membrane.canonical_query as { operation?: unknown } | undefined;
  return typeof query?.operation === 'string' ? query.operation : '';
}

function deepEqual(left: unknown, right: unknown): boolean {
  return stableStringify(left) === stableStringify(right);
}

function findFixture(membrane: Membrane, fixtures: ProofFixture[]): ProofFixture | undefined {
  return fixtures.find((fixture) => {
    return fixture.operation === operationOf(membrane) && fixture.membrane.identity_hash === membrane.identity_hash;
  });
}

function hasAuthorityOverclaim(membrane: Membrane): boolean {
  const boundary = membrane.boundary;
  if (!boundary) {
    return true;
  }
  const authority = boundary.authority;
  const sourceDockets = (membrane as { source_docket_ids?: unknown }).source_docket_ids;
  const hasSource = Array.isArray(sourceDockets) && sourceDockets.length > 0;
  const hasSampleSource = Array.isArray(sourceDockets)
    && sourceDockets.some((source) => typeof source === 'string' && source.includes(':sample-'));
  if ((authority === 'structured_official' || authority === 'archived_official') && !hasSource) {
    return true;
  }
  if ((authority === 'structured_official' || authority === 'archived_official') && hasSampleSource) {
    return true;
  }
  for (const provenance of Object.values(membrane.field_provenance ?? {})) {
    const sourceDocketId = (provenance as { source_docket_id?: unknown }).source_docket_id;
    if (
      (provenance.authority === 'structured_official' || provenance.authority === 'archived_official')
      && typeof sourceDocketId === 'string'
      && sourceDocketId.includes(':sample-')
    ) {
      return true;
    }
  }
  if (operationOf(membrane) === 'bs_months' && authority === 'structured_official') {
    const result = membrane.result as { selected_method?: unknown; requested_mode?: unknown } | undefined;
    if (result?.selected_method === 'static_lookup' || result?.requested_mode === 'static_lookup') {
      return true;
    }
  }
  if (operationOf(membrane).startsWith('panchanga') && boundary.claim_boundary !== 'computed_ephemeris_not_panchanga_authority') {
    return true;
  }
  return false;
}

export async function verifyMembrane(
  membrane: Membrane,
  options: { fixtures?: ProofFixture[] } = {},
): Promise<VerificationResult> {
  if (!membrane.canonical_query || !membrane.identity_hash || !membrane.witness || !membrane.witness_hash) {
    return { verified: false, reason: 'required_fields_missing' };
  }

  const identityDigest = await sha256Hex(canonicalQueryForBackend(membrane.canonical_query));
  if (membrane.identity_hash !== `${PREFIX_IDENTITY}${identityDigest}`) {
    return { verified: false, reason: 'identity_hash_mismatch' };
  }

  const resultDigest = await sha256Hex(stableStringify(membrane.result ?? {}));
  if (membrane.witness.output_hash !== `sha256:${resultDigest}`) {
    return { verified: false, reason: 'witness_output_hash_mismatch' };
  }

  const { witness_id: _witnessId, ...witnessWithoutId } = membrane.witness;
  const witnessDigest = await sha256Hex(stableStringify(witnessWithoutId));
  const expectedWitnessId = `${PREFIX_WITNESS}${witnessDigest}`;
  if (membrane.witness.witness_id !== expectedWitnessId || membrane.witness_hash !== expectedWitnessId) {
    return { verified: false, reason: 'witness_hash_mismatch' };
  }

  if (!membrane.boundary?.authority || !membrane.boundary.claim_boundary) {
    return { verified: false, reason: 'boundary_or_provenance_missing' };
  }
  if (hasAuthorityOverclaim(membrane)) {
    return { verified: false, reason: 'authority_overclaim' };
  }

  const result = membrane.result;
  if (!result || typeof result !== 'object' || Array.isArray(result)) {
    return { verified: false, reason: 'result_object_required' };
  }
  const fieldProvenance = membrane.field_provenance ?? {};
  for (const field of Object.keys(result as Record<string, unknown>)) {
    const provenance = fieldProvenance[field];
    if (!provenance?.authority) {
      return { verified: false, reason: 'field_provenance_missing' };
    }
    if (membrane.boundary.review_state === 'required' && !(provenance.flags ?? []).includes('review_required')) {
      return { verified: false, reason: 'field_review_required_missing' };
    }
  }

  const steps = membrane.proof_pack?.steps ?? [];
  if (!Array.isArray(steps) || steps.length < 2) {
    return { verified: false, reason: 'proof_pack_steps_missing' };
  }
  const lastStep = steps[steps.length - 1];
  if (lastStep.output_hash !== `sha256:${resultDigest}`) {
    return { verified: false, reason: 'proof_pack_result_hash_mismatch' };
  }
  if (
    typeof membrane.source_snapshot_hash === 'string'
    && membrane.proof_pack?.source_artifacts?.source_snapshot_hash !== membrane.source_snapshot_hash
  ) {
    return { verified: false, reason: 'source_snapshot_hash_mismatch' };
  }
  const witnessSourceSnapshotHash = (membrane.witness.method_parameters as { source_snapshot_hash?: unknown } | undefined)
    ?.source_snapshot_hash;
  if (typeof membrane.source_snapshot_hash === 'string' && witnessSourceSnapshotHash !== membrane.source_snapshot_hash) {
    return { verified: false, reason: 'source_snapshot_hash_mismatch' };
  }

  if (options.fixtures) {
    const replay = await replayMembrane(membrane, options.fixtures);
    if (!replay.verified) {
      return replay;
    }
  }

  return { verified: true, reason: 'verified' };
}

export async function replayMembrane(membrane: Membrane, fixtures: ProofFixture[]): Promise<VerificationResult> {
  const operation = operationOf(membrane);
  try {
    const replayed = await replayCivilResult(operation, membrane.canonical_query);
    if (replayed !== null && !deepEqual(membrane.result, replayed)) {
      return { verified: false, reason: 'replayed_result_mismatch' };
    }
    verifyBsMonthReplay(operation, membrane.canonical_query, membrane.result);
  } catch (error) {
    const reason = error instanceof Error ? error.message : 'replay_failed';
    return { verified: false, reason };
  }

  if (fixtures.length > 0) {
    const fixture = findFixture(membrane, fixtures);
    if (fixture && !deepEqual(membrane.canonical_query, fixture.membrane.canonical_query)) {
      return { verified: false, reason: 'canonical_query_mismatch' };
    }
  }
  return { verified: true, reason: 'replayed' };
}

export async function verifyCivilOperation(membrane: Membrane, fixtures: ProofFixture[]): Promise<VerificationResult> {
  return verifyMembrane(membrane, { fixtures });
}

export async function verifyPanchangaMembrane(membrane: Membrane, fixtures: ProofFixture[]): Promise<VerificationResult> {
  const operation = operationOf(membrane);
  if (operation !== 'panchanga_summary') {
    return { verified: false, reason: 'not_panchanga_membrane' };
  }
  const ephemerisMetadata = (membrane as { ephemeris_metadata?: Record<string, unknown> }).ephemeris_metadata;
  if (!ephemerisMetadata?.provider_id || !ephemerisMetadata.provider_kind) {
    return { verified: false, reason: 'ephemeris_metadata_missing' };
  }
  return verifyMembrane(membrane, { fixtures });
}
