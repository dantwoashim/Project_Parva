export function ProofPacketView({ proofPack }) {
  if (!proofPack) {
    return null;
  }

  return (
    <section aria-label="Proof packet">
      <h2>Proof packet</h2>
      <dl>
        <dt>Identity</dt>
        <dd>{proofPack.identity_hash || proofPack.identityHash}</dd>
        <dt>Witness</dt>
        <dd>{proofPack.witness_hash || proofPack.witnessHash}</dd>
        <dt>Source snapshot</dt>
        <dd>{proofPack.source_snapshot_hash || proofPack.sourceSnapshotHash}</dd>
      </dl>
    </section>
  );
}
