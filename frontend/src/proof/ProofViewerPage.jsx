import { useMemo, useState } from 'react';
import { PanchangaProofDrawer } from './PanchangaProofDrawer';

const sampleProofPack = {
  kind: 'parva_proofpack',
  level: 'replay',
  identity_hash: 'parva:id:v1:sha256:sample',
  witness_hash: 'parva:wit:v1:sha256:sample',
  boundary: {
    claim_boundary: 'sample_viewer_not_authority',
    review_state: 'required',
    warnings: ['review_required'],
  },
  membrane: {
    canonical_query: { operation: 'convert_bs_to_ad' },
    result: { ad_date: '2025-04-14' },
    field_provenance: {
      ad_date: { authority: 'static_reference', derivation: 'source_lookup', flags: ['review_required'] },
    },
  },
};

function safeJson(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return '';
  }
}

function parseArtifact(text) {
  try {
    return { artifact: JSON.parse(text), error: null };
  } catch (error) {
    return { artifact: null, error: error instanceof Error ? error.message : 'Invalid JSON' };
  }
}

function artifactMembrane(artifact) {
  if (artifact?.membrane) return artifact.membrane;
  if (artifact?.payload?.membrane) return artifact.payload.membrane;
  if (Array.isArray(artifact?.proof_packs)) return artifact.proof_packs[0]?.membrane;
  if (artifact?.capsule) return artifact.capsule;
  return null;
}

function BoundaryVectorView({ boundary }) {
  if (!boundary) return <p>Boundary unavailable.</p>;
  return (
    <dl className="proof-viewer-grid" aria-label="Boundary vector">
      <div><dt>Claim boundary</dt><dd>{boundary.claim_boundary || 'not specified'}</dd></div>
      <div><dt>Review</dt><dd>{boundary.review_state || String(boundary.review_required ?? 'not specified')}</dd></div>
      <div><dt>Not authority</dt><dd>{String(boundary.not_authority ?? true)}</dd></div>
    </dl>
  );
}

function FieldProvenanceTable({ provenance }) {
  const rows = Object.entries(provenance || {});
  if (!rows.length) return <p>Field provenance missing.</p>;
  return (
    <table className="proof-viewer-table">
      <thead>
        <tr><th>Field</th><th>Authority</th><th>Derivation</th><th>Review</th></tr>
      </thead>
      <tbody>
        {rows.map(([field, value]) => (
          <tr key={field}>
            <td>{field}</td>
            <td>{value.authority || 'unknown'}</td>
            <td>{value.derivation || 'not specified'}</td>
            <td>{value.review_state || (value.flags || []).join(', ') || 'not specified'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function HashView({ membrane }) {
  return (
    <dl className="proof-viewer-grid" aria-label="Witness hashes">
      <div><dt>Identity hash</dt><dd>{membrane?.identity_hash || 'not provided'}</dd></div>
      <div><dt>Witness hash</dt><dd>{membrane?.witness_hash || 'not provided'}</dd></div>
      <div><dt>Operation</dt><dd>{membrane?.canonical_query?.operation || 'unknown'}</dd></div>
    </dl>
  );
}

export function ProofViewerPage() {
  const [text, setText] = useState(safeJson(sampleProofPack));
  const parsed = useMemo(() => parseArtifact(text), [text]);
  const membrane = artifactMembrane(parsed.artifact);
  const isPanchanga = membrane?.canonical_query?.operation === 'panchanga_summary';
  const childCount = Array.isArray(parsed.artifact?.proof_packs) ? parsed.artifact.proof_packs.length : 0;
  const replayStatus = parsed.error ? 'failed_json_parse' : membrane ? 'ready_for_offline_cli_replay' : 'unsupported_artifact_shape';

  return (
    <main className="page-shell proof-viewer-page">
      <section className="proof-viewer-hero">
        <p className="landing-eyebrow">Proof viewer</p>
        <h1>Inspect Parva proof packs and Timepacks</h1>
        <p>
          Paste a civil, Panchanga, payroll audit, proof pack, or Timepack JSON artifact. This browser view is an
          inspection surface; use <code>parva verify-proofpack</code> or <code>parva verify-timepack</code> for offline replay.
        </p>
        <p className="trust-boundary">Public verification status, not live uptime SLA. Not government, legal, tax, payroll, banking, or official Panchanga authority.</p>
      </section>
      <section className="proof-viewer-layout">
        <label className="proof-viewer-input">
          Artifact JSON
          <textarea value={text} onChange={(event) => setText(event.target.value)} spellCheck="false" />
        </label>
        <article className="proof-viewer-output" aria-label="Proof artifact inspection">
          <h2>Replay status</h2>
          <p>{replayStatus}</p>
          {parsed.error ? <p>{parsed.error}</p> : null}
          <HashView membrane={membrane} />
          <BoundaryVectorView boundary={membrane?.boundary || parsed.artifact?.boundary || parsed.artifact?.boundary_summary} />
          <h2>Result</h2>
          <pre>{safeJson(membrane?.result || parsed.artifact?.result_summary || {})}</pre>
          <h2>Field provenance</h2>
          <FieldProvenanceTable provenance={membrane?.field_provenance} />
          {childCount ? <p>{childCount} child proof packs in this Timepack.</p> : null}
          {isPanchanga ? <PanchangaProofDrawer proof={{ capsule: membrane }} /> : null}
        </article>
      </section>
    </main>
  );
}
