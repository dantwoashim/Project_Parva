import PropTypes from 'prop-types';
import './AuthorityInspector.css';

function truncate(value, size = 18) {
    if (!value || typeof value !== 'string') return '—';
    if (value.length <= size * 2) return value;
    return `${value.slice(0, size)}…${value.slice(-size)}`;
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

export function AuthorityInspector({
    title = 'Authority Metadata',
    meta,
    traceFallbackId = null,
    onOpenTrace = null,
}) {
    const confidence = normalizeConfidence(meta?.confidence);
    const traceId = meta?.trace_id || traceFallbackId || null;
    const provenance = meta?.provenance || {};
    const uncertainty = meta?.uncertainty || {};
    const policy = meta?.policy || {};

    return (
        <section className="glass-card authority-inspector" data-testid="authority-inspector">
            <header className="authority-inspector__header">
                <div>
                    <h3>{title}</h3>
                    <p>Provenance, confidence, and trace metadata for this response.</p>
                </div>
                <div className="authority-inspector__badges">
                    <span className="badge badge-primary">{confidence.level || 'unknown'}</span>
                    <span className="badge">{meta?.method || 'unknown method'}</span>
                </div>
            </header>

            <div className="authority-inspector__grid">
                <p><strong>Confidence Score</strong> {confidence.score !== null ? confidence.score.toFixed(2) : 'N/A'}</p>
                <p><strong>Boundary Risk</strong> {uncertainty.boundary_risk || 'unknown'}</p>
                <p><strong>Snapshot</strong> <code>{truncate(provenance.snapshot_id)}</code></p>
                <p><strong>Dataset Hash</strong> <code>{truncate(provenance.dataset_hash)}</code></p>
                <p><strong>Rules Hash</strong> <code>{truncate(provenance.rules_hash)}</code></p>
                <p><strong>Signature</strong> <code>{truncate(provenance.signature)}</code></p>
                <p><strong>Verify URL</strong> <code>{provenance.verify_url || '—'}</code></p>
                <p><strong>Policy</strong> {policy.profile || 'np-mainstream'} · {policy.jurisdiction || 'NP'}</p>
            </div>

            <div className="authority-inspector__trace">
                <p><strong>Trace ID</strong> <code>{traceId || 'Not provided in this response'}</code></p>
                {traceId && onOpenTrace && (
                    <button className="btn btn-secondary" onClick={() => onOpenTrace(traceId)}>
                        Open Trace
                    </button>
                )}
            </div>
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
