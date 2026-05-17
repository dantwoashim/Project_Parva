import { stableStringify } from './canonicalize.js';
import { sha256Hex } from './hash.js';
import { verifyProofPack, type ProofPack } from './proofpacks.js';
import type { ProofFixture, VerificationResult } from './membranes.js';

export type Timepack = {
  kind?: string;
  timepack_version?: string;
  proof_packs?: ProofPack[];
  aggregate_witness_hash?: string;
  boundary_summary?: { not_authority?: boolean; review_required?: boolean };
};

export async function verifyTimepack(timepack: Timepack, fixtures: ProofFixture[] = []): Promise<VerificationResult> {
  if (timepack.kind !== 'parva_timepack' || !Array.isArray(timepack.proof_packs)) {
    return { verified: false, reason: 'timepack_schema_invalid' };
  }
  for (const pack of timepack.proof_packs) {
    const result = await verifyProofPack(pack, fixtures);
    if (!result.verified) {
      return { verified: false, reason: `child_${result.reason}` };
    }
  }
  if (!timepack.boundary_summary?.not_authority) {
    return { verified: false, reason: 'timepack_boundary_summary_missing' };
  }
  if (timepack.aggregate_witness_hash) {
    const childHashes = timepack.proof_packs.map((pack) => pack.membrane?.witness_hash ?? pack.witness_hash ?? '');
    const digest = await sha256Hex(stableStringify(childHashes));
    if (timepack.aggregate_witness_hash !== `sha256:${digest}`) {
      return { verified: false, reason: 'timepack_aggregate_hash_mismatch' };
    }
  }
  return { verified: true, reason: 'verified' };
}
