import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { festivalAPI } from '../../services/api';
import './ExplainPanel.css';

export function ExplainPanel({ data, loading, error, onClose }) {
    const [trace, setTrace] = useState(null);
    const [traceError, setTraceError] = useState(null);

    useEffect(() => {
        let active = true;
        async function loadTrace() {
            if (!data?.calculation_trace_id) {
                setTrace(null);
                return;
            }
            try {
                const payload = await festivalAPI.getTrace(data.calculation_trace_id);
                if (active) {
                    setTrace(payload);
                    setTraceError(null);
                }
            } catch (err) {
                if (active) {
                    setTrace(null);
                    setTraceError(err.message || 'Trace unavailable');
                }
            }
        }
        loadTrace();
        return () => {
            active = false;
        };
    }, [data?.calculation_trace_id]);

    return (
        <div className="explain-panel-overlay" role="dialog" aria-modal="true">
            <div className="explain-panel glass-card">
                <header className="explain-panel__header">
                    <h3>Why This Date?</h3>
                    <button className="btn btn-secondary" onClick={onClose} aria-label="Close explain panel">
                        ✕
                    </button>
                </header>

                {loading && (
                    <div className="explain-panel__loading">
                        <div className="skeleton" style={{ height: '20px', marginBottom: '0.75rem' }} />
                        <div className="skeleton" style={{ height: '14px', marginBottom: '0.5rem' }} />
                        <div className="skeleton" style={{ height: '14px', marginBottom: '0.5rem' }} />
                        <div className="skeleton" style={{ height: '14px' }} />
                    </div>
                )}

                {!loading && error && (
                    <div className="explain-panel__error">
                        <p>{error}</p>
                        <button className="btn btn-secondary" onClick={onClose}>Close</button>
                    </div>
                )}

                {!loading && !error && data && (
                    <div className="explain-panel__content">
                        <p className="explain-panel__summary">{data.explanation}</p>
                        <div className="explain-panel__meta">
                            <span className="badge">Method: {data.method}</span>
                            <span className="badge">Rule: {data.rule_summary}</span>
                            <span className="badge">Trace: {data.calculation_trace_id}</span>
                        </div>
                        <ol className="explain-panel__steps">
                            {(data.steps || []).map((step, idx) => (
                                <li key={idx}>{step}</li>
                            ))}
                        </ol>

                        {trace && (
                            <section className="explain-panel__trace">
                                <h4>Technical Trace</h4>
                                <ul>
                                    {(trace.steps || []).map((step, idx) => (
                                        <li key={`${step.step_type || 'step'}-${idx}`}>
                                            <strong>{step.step_type || 'step'}</strong>
                                            {step.rule_id ? ` • rule: ${step.rule_id}` : ''}
                                            {step.math_expression ? ` • ${step.math_expression}` : ''}
                                        </li>
                                    ))}
                                </ul>
                            </section>
                        )}
                        {!trace && traceError && (
                            <p className="explain-panel__trace-error">Technical trace unavailable: {traceError}</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

ExplainPanel.propTypes = {
    data: PropTypes.shape({
        explanation: PropTypes.string,
        method: PropTypes.string,
        rule_summary: PropTypes.string,
        calculation_trace_id: PropTypes.string,
        steps: PropTypes.arrayOf(PropTypes.string),
    }),
    loading: PropTypes.bool,
    error: PropTypes.string,
    onClose: PropTypes.func.isRequired,
};

export default ExplainPanel;
