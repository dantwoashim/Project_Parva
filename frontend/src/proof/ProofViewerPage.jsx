import { useMemo, useState } from 'react';
import { PanchangaProofDrawer } from './PanchangaProofDrawer';
import {
  Braces,
  FileJson2,
  ShieldAlert,
  ShieldCheck,
  Upload,
} from 'lucide-react';

const sampleArtifacts = {
  civil: {
    kind: 'parva_proofpack',
    proofpack_version: 'v1',
    level: 'replay',
    identity_hash: 'parva:id:v1:sha256:sample',
    witness_hash: 'parva:wit:v1:sha256:sample',
    boundary: {
      claim_boundary: 'sample_viewer_not_authority',
      review_state: 'required',
      not_authority: true,
      warnings: ['review_required'],
    },
    membrane: {
      canonical_query: { operation: 'convert_bs_to_ad' },
      identity_hash: 'parva:id:v1:sha256:sample',
      witness_hash: 'parva:wit:v1:sha256:sample',
      result: { ad_date: '2025-04-14' },
      field_provenance: {
        ad_date: { authority: 'static_reference', derivation: 'source_lookup', flags: ['review_required'] },
      },
    },
  },
  panchanga: {
    kind: 'parva_proofpack',
    proofpack_version: 'v1',
    level: 'replay',
    identity_hash: 'parva:id:v1:sha256:panchanga-sample',
    witness_hash: 'parva:wit:v1:sha256:panchanga-sample',
    boundary: {
      claim_boundary: 'computed_ephemeris_not_panchanga_authority',
      review_state: 'required',
      not_authority: true,
      not_panchanga_authority: true,
      not_ritual_final_authority: true,
    },
    membrane: {
      canonical_query: { operation: 'panchanga_summary', context: { timezone: 'Asia/Kathmandu' } },
      identity_hash: 'parva:id:v1:sha256:panchanga-sample',
      witness_hash: 'parva:wit:v1:sha256:panchanga-sample',
      result: {
        date: '2025-04-14',
        sunrise: { local_time: '05:40:28', timezone: 'Asia/Kathmandu' },
        tithi: { name: 'Pratipada', number: 16 },
        nakshatra: { name: 'Swati', number: 15 },
        review_required: true,
        claim_boundary: 'computed_ephemeris_not_panchanga_authority',
      },
      field_provenance: {
        sunrise: {
          authority: 'computed_uncertified',
          derivation: 'panchanga_ephemeris_method_replay',
          flags: ['review_required'],
        },
        tithi: {
          authority: 'computed_uncertified',
          derivation: 'panchanga_ephemeris_method_replay',
          flags: ['review_required'],
        },
        nakshatra: {
          authority: 'computed_uncertified',
          derivation: 'panchanga_ephemeris_method_replay',
          flags: ['review_required'],
        },
      },
      method_docket_refs: [
        'parva.panchanga.sunrise.v1',
        'parva.panchanga.tithi.v1',
        'parva.panchanga.nakshatra.v1',
      ],
      method_dockets: [
        { method_id: 'parva.panchanga.sunrise.v1', precision_tolerance: 'fixture replay exact' },
        { method_id: 'parva.panchanga.tithi.v1', precision_tolerance: 'fixture replay exact' },
      ],
      ephemeris_metadata: {
        provider_id: 'pinned_panchanga_fixture',
        provider_kind: 'pinned_fixture',
        fixture_id: 'kathmandu_2025_04_14_lahiri',
        jpl_backed: false,
        fallback_used: false,
        kernel_hash: 'sha256:sample',
      },
    },
  },
  timepack: {
    kind: 'parva_timepack',
    timepack_version: 'v1',
    artifact_type: 'payroll_date_risk_audit',
    aggregate_witness_hash: 'sha256:sample',
    boundary_summary: {
      claim_boundary: 'payroll_date_risk_not_authority',
      not_authority: true,
      review_required: true,
    },
    result_summary: { rows: 1, review_required: 1 },
    proof_packs: [],
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

function validateArtifact(artifact) {
  if (!artifact || typeof artifact !== 'object') return { ok: false, reason: 'schema_invalid' };
  if (artifact.kind === 'parva_proofpack' && artifact.membrane) return { ok: true, reason: 'proofpack_shape_ok' };
  if (artifact.kind === 'parva_timepack' && Array.isArray(artifact.proof_packs)) return { ok: true, reason: 'timepack_shape_ok' };
  if (artifact.kind === 'parva_membrane' || artifact.capsule) return { ok: true, reason: 'membrane_shape_ok' };
  return { ok: false, reason: 'unsupported_proof_type' };
}

function artifactMembrane(artifact) {
  if (artifact?.membrane) return artifact.membrane;
  if (artifact?.payload?.membrane) return artifact.payload.membrane;
  if (Array.isArray(artifact?.proof_packs)) return artifact.proof_packs[0]?.membrane;
  if (artifact?.capsule) return artifact.capsule;
  return null;
}

function childMembrane(artifact, childIndex) {
  if (!Array.isArray(artifact?.proof_packs)) return artifactMembrane(artifact);
  return artifact.proof_packs[childIndex]?.membrane || artifactMembrane(artifact);
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

function SourceDocketView({ membrane }) {
  const refs = membrane?.source_docket_ids || membrane?.source_docket_refs || [];
  if (!refs.length) return <p>Source docket refs: none or method-backed.</p>;
  return <p>Source docket refs: {refs.join(', ')}</p>;
}

function MethodDocketView({ membrane }) {
  const refs = membrane?.method_docket_refs || [];
  if (!refs.length) return <p>Method dockets: none declared.</p>;
  return <p>Method dockets: {refs.join(', ')}</p>;
}

function EphemerisMetadataView({ metadata }) {
  if (!metadata) return null;
  return (
    <dl className="proof-viewer-grid" aria-label="Ephemeris metadata">
      <div><dt>Provider</dt><dd>{metadata.provider_id || 'not specified'}</dd></div>
      <div><dt>Kind</dt><dd>{metadata.provider_kind || 'not specified'}</dd></div>
      <div><dt>Fixture/kernel</dt><dd>{metadata.fixture_id || metadata.kernel_hash || 'not specified'}</dd></div>
      <div><dt>JPL backed</dt><dd>{String(metadata.jpl_backed === true)}</dd></div>
    </dl>
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
  const [text, setText] = useState(safeJson(sampleArtifacts.civil));
  const [mode, setMode] = useState('detailed');
  const [childIndex, setChildIndex] = useState(0);
  const parsed = useMemo(() => parseArtifact(text), [text]);
  const validation = useMemo(() => (parsed.artifact ? validateArtifact(parsed.artifact) : null), [parsed.artifact]);
  const membrane = childMembrane(parsed.artifact, childIndex);
  const isPanchanga = membrane?.canonical_query?.operation === 'panchanga_summary';
  const childCount = Array.isArray(parsed.artifact?.proof_packs) ? parsed.artifact.proof_packs.length : 0;
  const replayStatus = parsed.error
    ? 'failed_json_parse'
    : validation?.ok && membrane
      ? 'ready_for_offline_cli_replay'
      : validation?.reason || 'unsupported_artifact_shape';

  function loadSample(name) {
    setChildIndex(0);
    setText(safeJson(sampleArtifacts[name]));
  }

  function onFile(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    file.text().then((content) => {
      setChildIndex(0);
      setText(content);
    });
  }

  return (
    <main className="page-shell proof-viewer-page">
      <section className="proof-viewer-hero">
        <div className="proof-viewer-hero__copy">
          <p className="landing-eyebrow">Proof viewer</p>
          <h1>Inspect Parva proof packs and Timepacks</h1>
          <p>
            Paste a civil, Panchanga, payroll audit, proof pack, or Timepack JSON artifact. Use
            <code>parva verify-proofpack</code> or <code>parva verify-timepack</code> when you need offline replay.
          </p>
        </div>
        <div className="proof-viewer-hero__mark" aria-hidden="true">
          <FileJson2 />
          <span>JSON</span>
        </div>
        <p className="trust-boundary">Public verification status, not live uptime SLA. Not government, legal, tax, payroll, banking, or official Panchanga authority.</p>
      </section>
      <section className="proof-viewer-layout">
        <label className="proof-viewer-input">
          <span className="proof-viewer-input__label"><Braces aria-hidden="true" /> Artifact JSON</span>
          <div className="proof-viewer-actions" aria-label="Proof viewer examples">
            <button type="button" onClick={() => loadSample('civil')}>Civil sample</button>
            <button type="button" onClick={() => loadSample('panchanga')}>Panchanga sample</button>
            <button type="button" onClick={() => loadSample('timepack')}>Timepack sample</button>
            <button type="button" onClick={() => setMode(mode === 'compact' ? 'detailed' : 'compact')}>
              {mode === 'compact' ? 'Detailed' : 'Compact'}
            </button>
            <span className="proof-viewer-upload"><Upload aria-hidden="true" /> Upload JSON
              <input aria-label="Upload proof JSON" type="file" accept="application/json,.json" onChange={onFile} />
            </span>
          </div>
          <textarea value={text} onChange={(event) => setText(event.target.value)} spellCheck="false" />
        </label>
        <article className="proof-viewer-output" aria-label="Proof artifact inspection">
          <div className={`proof-replay-banner ${parsed.error || (validation && !validation.ok) ? 'is-warning' : 'is-ready'}`} aria-live="polite">
            {parsed.error || (validation && !validation.ok) ? <ShieldAlert aria-hidden="true" /> : <ShieldCheck aria-hidden="true" />}
            <div>
              <span>Replay status</span>
              <strong>{replayStatus}</strong>
              <small>Artifact shape checked in the browser.</small>
            </div>
          </div>
          {parsed.error ? <p>{parsed.error}</p> : null}
          {validation && !validation.ok ? <p>{validation.reason}</p> : null}
          {membrane?.boundary?.not_authority || parsed.artifact?.boundary?.not_authority || parsed.artifact?.boundary_summary?.not_authority ? (
            <p className="trust-boundary">Not authority. Use CLI/local-kernel replay for verification.</p>
          ) : null}
          {membrane?.boundary?.review_state === 'required'
            || parsed.artifact?.boundary?.review_state === 'required'
            || parsed.artifact?.boundary_summary?.review_required ? (
            <p className="trust-boundary">Review required.</p>
          ) : null}
          {childCount ? (
            <label>
              Child artifact
              <select value={childIndex} onChange={(event) => setChildIndex(Number(event.target.value))}>
                {parsed.artifact.proof_packs.map((_, index) => (
                  <option key={index} value={index}>Child {index + 1}</option>
                ))}
              </select>
            </label>
          ) : null}
          <HashView membrane={membrane} />
          <BoundaryVectorView boundary={membrane?.boundary || parsed.artifact?.boundary || parsed.artifact?.boundary_summary} />
          <h2>Result</h2>
          <pre>{safeJson(membrane?.result || parsed.artifact?.result_summary || {})}</pre>
          {mode === 'detailed' ? (
            <>
              <h2>Field provenance</h2>
              <FieldProvenanceTable provenance={membrane?.field_provenance} />
              <h2>Source and method</h2>
              <SourceDocketView membrane={membrane} />
              <MethodDocketView membrane={membrane} />
              <EphemerisMetadataView metadata={membrane?.ephemeris_metadata} />
            </>
          ) : null}
          {childCount ? <p>{childCount} child proof packs in this Timepack.</p> : null}
          {isPanchanga ? <PanchangaProofDrawer proof={{ capsule: membrane }} /> : null}
        </article>
      </section>
    </main>
  );
}
