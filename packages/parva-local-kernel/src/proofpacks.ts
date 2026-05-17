import { verifyMembrane, type Membrane, type ProofFixture, type VerificationResult } from './membranes.js';

export type ProofPack = {
  level?: string;
  membrane?: Membrane;
  identity_hash?: string;
  witness_hash?: string;
};

export async function verifyProofPack(pack: ProofPack, fixtures: ProofFixture[] = []): Promise<VerificationResult> {
  if (pack.membrane) {
    return verifyMembrane(pack.membrane, { fixtures });
  }
  if (!pack.identity_hash || !pack.witness_hash) {
    return { verified: false, reason: 'proofpack_required_fields_missing' };
  }
  return { verified: true, reason: 'verified_compact_proofpack' };
}
