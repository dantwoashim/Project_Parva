import { canonicalize } from './canonicalize';
import { sha256Hex } from './hash';

type Membrane = {
  canonical_query?: unknown;
  identity_hash?: string;
  result?: unknown;
  witness?: Record<string, unknown>;
  witness_hash?: string;
  boundary?: { authority?: string; review_state?: string };
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

  const provenance = membrane.field_provenance?.ad_date;
  if (!membrane.boundary?.authority || !provenance?.authority) {
    return { verified: false, reason: 'boundary_or_provenance_missing' };
  }
  if (membrane.boundary.authority !== provenance.authority) {
    return { verified: false, reason: 'boundary_authority_mismatch' };
  }
  if (membrane.boundary.review_state === 'required' && !(provenance.flags ?? []).includes('review_required')) {
    return { verified: false, reason: 'field_review_required_missing' };
  }

  return { verified: true, reason: 'verified' };
}
