import { canonicalize } from './canonicalize';
import { sha256Hex } from './hash';

type Membrane = {
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

const PREFIX_IDENTITY = 'parva:id:v1:sha256:';
const PREFIX_WITNESS = 'parva:wit:v1:sha256:';

function canonicalQueryForBackend(query: unknown): string {
  return canonicalize(query);
}

export async function verifyMembrane(membrane: Membrane): Promise<{ verified: boolean; reason: string }> {
  if (!membrane.canonical_query || !membrane.identity_hash || !membrane.witness || !membrane.witness_hash) {
    return { verified: false, reason: 'required_fields_missing' };
  }

  const identityDigest = await sha256Hex(canonicalQueryForBackend(membrane.canonical_query));
  if (membrane.identity_hash !== `${PREFIX_IDENTITY}${identityDigest}`) {
    return { verified: false, reason: 'identity_hash_mismatch' };
  }

  const resultDigest = await sha256Hex(canonicalize(membrane.result ?? {}));
  if (membrane.witness.output_hash !== `sha256:${resultDigest}`) {
    return { verified: false, reason: 'witness_output_hash_mismatch' };
  }

  const { witness_id: _witnessId, ...witnessWithoutId } = membrane.witness;
  const witnessDigest = await sha256Hex(canonicalize(witnessWithoutId));
  const expectedWitnessId = `${PREFIX_WITNESS}${witnessDigest}`;
  if (membrane.witness.witness_id !== expectedWitnessId || membrane.witness_hash !== expectedWitnessId) {
    return { verified: false, reason: 'witness_hash_mismatch' };
  }

  if (!membrane.boundary?.authority || !membrane.boundary.claim_boundary) {
    return { verified: false, reason: 'boundary_or_provenance_missing' };
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

  return { verified: true, reason: 'verified' };
}
