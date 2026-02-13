import { useEffect, useMemo, useState } from 'react';
import { calendarAPI } from '../services/api';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import './PanchangaPage.css';

function todayIso() {
    return new Date().toISOString().slice(0, 10);
}

export function PanchangaPage() {
    const [dateValue, setDateValue] = useState(todayIso());
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [payload, setPayload] = useState(null);
    const [meta, setMeta] = useState(null);
    const [resolveTrace, setResolveTrace] = useState(null);
    const [traceData, setTraceData] = useState(null);
    const [traceLoading, setTraceLoading] = useState(false);
    const [traceError, setTraceError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        async function load() {
            setLoading(true);
            setError(null);
            try {
                const [panchangaEnvelope, resolveEnvelope] = await Promise.all([
                    calendarAPI.getPanchangaEnvelope(dateValue),
                    calendarAPI.getResolveEnvelope(dateValue, { include_trace: 'true' }),
                ]);
                if (!cancelled) {
                    setPayload(panchangaEnvelope.data);
                    setMeta(panchangaEnvelope.meta || null);
                    setResolveTrace(resolveEnvelope?.meta?.trace_id || resolveEnvelope?.data?.trace?.trace_id || null);
                }
            } catch (err) {
                if (!cancelled) {
                    setPayload(null);
                    setMeta(null);
                    setResolveTrace(null);
                    setError(err.message || 'Failed to load panchanga');
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        load();
        return () => {
            cancelled = true;
        };
    }, [dateValue]);

    const tithi = payload?.panchanga?.tithi;
    const nakshatra = payload?.panchanga?.nakshatra;
    const yoga = payload?.panchanga?.yoga;
    const karana = payload?.panchanga?.karana;
    const vaara = payload?.panchanga?.vaara;

    const confidence = useMemo(() => {
        return payload?.panchanga?.confidence || meta?.confidence?.level || 'unknown';
    }, [payload, meta]);

    const handleOpenTrace = async (traceId) => {
        if (!traceId) return;
        setTraceLoading(true);
        setTraceError(null);
        try {
            const trace = await calendarAPI.getResolveEnvelope(dateValue, { include_trace: 'true' });
            setTraceData(trace?.data?.trace || null);
        } catch (err) {
            setTraceError(err.message || 'Failed to load trace');
            setTraceData(null);
        } finally {
            setTraceLoading(false);
        }
    };

    return (
        <section className="panchanga-page">
            <header className="glass-card panchanga-header">
                <div>
                    <h2 className="text-display">Panchanga Viewer</h2>
                    <p>Daily tithi, nakshatra, yoga, karana, and vaara from the astronomical engine.</p>
                </div>
                <label className="panchanga-date-input" htmlFor="panchanga-date">
                    <span>Date</span>
                    <input
                        id="panchanga-date"
                        type="date"
                        value={dateValue}
                        onChange={(e) => setDateValue(e.target.value)}
                    />
                </label>
            </header>

            {loading && (
                <div className="glass-card panchanga-state" data-testid="panchanga-loading">
                    <h3>Calculating...</h3>
                    <div className="skeleton" style={{ height: '180px', marginTop: '1rem' }} />
                </div>
            )}

            {!loading && error && (
                <div className="glass-card panchanga-state" role="alert">
                    <h3>Unable to load panchanga</h3>
                    <p>{error}</p>
                </div>
            )}

            {!loading && !error && payload && (
                <>
                    <section className="panchanga-grid">
                        <article className="glass-card panchanga-card">
                            <h3>Tithi</h3>
                            <p className="value">{tithi?.name || '—'}</p>
                            <p className="meta">#{tithi?.number} · {tithi?.paksha}</p>
                        </article>

                        <article className="glass-card panchanga-card">
                            <h3>Nakshatra</h3>
                            <p className="value">{nakshatra?.name || '—'}</p>
                            <p className="meta">Pada {nakshatra?.pada || '—'}</p>
                        </article>

                        <article className="glass-card panchanga-card">
                            <h3>Yoga</h3>
                            <p className="value">{yoga?.name || '—'}</p>
                            <p className="meta">#{yoga?.number || '—'}</p>
                        </article>

                        <article className="glass-card panchanga-card">
                            <h3>Karana</h3>
                            <p className="value">{karana?.name || '—'}</p>
                            <p className="meta">#{karana?.number || '—'}</p>
                        </article>

                        <article className="glass-card panchanga-card">
                            <h3>Vaara</h3>
                            <p className="value">{vaara?.name_english || '—'}</p>
                            <p className="meta">{vaara?.name_sanskrit || '—'}</p>
                        </article>
                    </section>

                    <section className="glass-card panchanga-metadata">
                        <h3>Engine Metadata</h3>
                        <div className="metadata-grid">
                            <p><strong>Gregorian</strong> {payload.date}</p>
                            <p><strong>BS</strong> {payload.bikram_sambat?.year} {payload.bikram_sambat?.month_name} {payload.bikram_sambat?.day}</p>
                            <p><strong>Panchanga Confidence</strong> {confidence}</p>
                            <p><strong>Tithi Method</strong> {tithi?.method || 'ephemeris'}</p>
                            <p><strong>Sunrise Used</strong> {tithi?.sunrise_used || 'N/A'}</p>
                            <p><strong>Ephemeris Mode</strong> {payload.ephemeris?.mode || 'swiss_moshier'}</p>
                        </div>
                    </section>

                    <AuthorityInspector
                        title="Panchanga Response Authority"
                        meta={meta}
                        traceFallbackId={resolveTrace}
                        onOpenTrace={handleOpenTrace}
                    />

                    {(traceLoading || traceData || traceError) && (
                        <section className="glass-card panchanga-trace">
                            <header>
                                <h3>Trace Explorer</h3>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => {
                                        setTraceData(null);
                                        setTraceError(null);
                                    }}
                                >
                                    Close
                                </button>
                            </header>
                            {traceLoading && <p>Loading trace...</p>}
                            {!traceLoading && traceError && <p role="alert">{traceError}</p>}
                            {!traceLoading && traceData && <pre>{JSON.stringify(traceData, null, 2)}</pre>}
                        </section>
                    )}
                </>
            )}
        </section>
    );
}

export default PanchangaPage;
