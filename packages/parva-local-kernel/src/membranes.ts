export function verifyMembrane(membrane: { identity_hash?: string; witness_hash?: string }) {
  return Boolean(membrane.identity_hash && membrane.witness_hash);
}
