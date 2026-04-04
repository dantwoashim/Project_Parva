import PropTypes from 'prop-types';
import './AuthorityInspector.css';

function truncate(value, size = 18) {
  if (!value || typeof value !== 'string') return 'N/A';
  if (value.length <= size * 2) return value;
  return `${value.slice(0, size)}...${value.slice(-size)}`;
}

function normalizeConfidence(confidence) {
  if (typeof confidence === 'string') {
    return { level: confidence, score: null };
  }
  if (confidence && typeof confidence === 'object') {
    return {
      level: confidence.level || 'unknown',
      score: typeof confidence.score === 'number' ? confidence.score : null,
    };
  }
  return { level: 'unknown', score: null };
}

function formatAttestation(attestation, legacySignature) {
  if (attestation && typeof attestation === 'object') {
    const mode = attestation.mode || 'unsigned';
    const value = typeof attestation.value === 'string' ? attestation.value : null;
    return value ? `${mode}:${value}` : mode;
  }
  if (legacySignature && typeof legacySignature === 'string') {
    return `legacy:${legacySignature}`;
  }
  return null;
}

function buildTechnicalRows(provenance, traceId) {
  return [
    { label: 'Trace ID', value: traceId },
    { label: 'Snapshot', value: provenance.snapshot_id },
    { label: 'Dataset hash', value: provenance.dataset_hash },
    { label: 'Rules hash', value: provenance.rules_hash },
    {
      label: 'Attestation',
      value: formatAttestation(provenance.attestation, provenance.signature),
    },
  ].filter((item) => Boolean(item.value));
}

export function AuthorityInspector({
  title = 'Method metadata',
  meta,
  traceFallbackId = null,
  onOpenTrace = null,
}) {
  const confidence = normalizeConfidence(meta?.confidence);
  const traceId = meta?.trace_id || traceFallbackId || null;
  const provenance = meta?.provenance || {};
  const uncertainty = meta?.uncertainty || {};
  const policy = meta?.policy || {};
  const policyProfile = policy.profile || 'Nepal mainstream profile';
  const jurisdiction = policy.jurisdiction || 'NP';
  const technicalRows = buildTechnicalRows(provenance, traceId);

  return (
    <section className="glass-card authority-inspector" data-testid="authority-inspector">
      <header className="authority-inspector__header">
        <div>
          <h3>{title}</h3>
          <p>Method profile, confidence, and provenance notes for this response.</p>
        </div>
        <div className="authority-inspector__badges">
          <span className="badge badge-primary">{confidence.level || 'profile-based'}</span>
          <span className="badge">{meta?.method || 'method profile available'}</span>
        </div>
      </header>

      <div className="authority-inspector__grid">
        <p><strong>Confidence level</strong> {confidence.level || 'profile-based'}</p>
        <p><strong>Confidence score</strong> {confidence.score !== null ? confidence.score.toFixed(2) : 'Not scored'}</p>
        <p><strong>Boundary risk</strong> {uncertainty.boundary_risk || 'Not noted'}</p>
        <p><strong>Policy profile</strong> {policyProfile}</p>
        <p><strong>Jurisdiction</strong> {jurisdiction}</p>
        {provenance.verify_url ? (
          <p>
            <strong>Verification link</strong>{' '}
            <a href={provenance.verify_url} target="_blank" rel="noreferrer">
              Open reference
            </a>
          </p>
        ) : null}
      </div>

      {technicalRows.length ? (
        <details className="authority-inspector__technical">
          <summary>Technical metadata</summary>
          <div className="authority-inspector__technical-grid">
            {technicalRows.map((item) => (
              <p key={item.label}>
                <strong>{item.label}</strong> <code>{truncate(item.value)}</code>
              </p>
            ))}
          </div>
          {traceId && onOpenTrace ? (
            <div className="authority-inspector__technical-actions">
              <button className="btn btn-secondary" onClick={() => onOpenTrace(traceId)}>
                Open technical trace
              </button>
            </div>
          ) : null}
        </details>
      ) : null}
    </section>
  );
}

AuthorityInspector.propTypes = {
  title: PropTypes.string,
  meta: PropTypes.shape({
    confidence: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        level: PropTypes.string,
        score: PropTypes.number,
      }),
    ]),
    method: PropTypes.string,
    provenance: PropTypes.shape({
      snapshot_id: PropTypes.string,
      dataset_hash: PropTypes.string,
      rules_hash: PropTypes.string,
      verify_url: PropTypes.string,
      attestation: PropTypes.shape({
        mode: PropTypes.string,
        algorithm: PropTypes.string,
        key_id: PropTypes.string,
        value: PropTypes.string,
      }),
      signature: PropTypes.string,
    }),
    uncertainty: PropTypes.shape({
      boundary_risk: PropTypes.string,
      interval_hours: PropTypes.number,
    }),
    trace_id: PropTypes.string,
    policy: PropTypes.shape({
      profile: PropTypes.string,
      jurisdiction: PropTypes.string,
      advisory: PropTypes.bool,
    }),
  }),
  traceFallbackId: PropTypes.string,
  onOpenTrace: PropTypes.func,
};

export default AuthorityInspector;
