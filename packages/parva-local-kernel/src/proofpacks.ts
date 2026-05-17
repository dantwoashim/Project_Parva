import { sha256Hex } from './hash';

export type ProofPack = {
  kind: "proof_pack";
  level: "local" | "audit";
  identityHash: string;
  witnessHash: string;
  sourceSnapshotHash: string;
  resultHash: string;
};

export async function buildProofPack(
  result: unknown,
  identityHash: string,
  witnessHash: string,
  sourceSnapshotHash: string,
): Promise<ProofPack> {
  return {
    kind: "proof_pack",
    level: "local",
    identityHash,
    witnessHash,
    sourceSnapshotHash,
    resultHash: `sha256:${await sha256Hex(JSON.stringify(result))}`,
  };
}
