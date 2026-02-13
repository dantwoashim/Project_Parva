import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { FestivalDetail } from '../components/Festival';
import { useFestivalDetail, useFestivals } from '../hooks/useFestivals';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import { festivalAPI } from '../services/api';
import './FestivalDetailPage.css';

function parseYear(value) {
    if (!value) return null;
    const n = Number(value);
    if (!Number.isInteger(n) || n < 1900 || n > 2300) return null;
    return n;
}

export function FestivalDetailPage() {
    const navigate = useNavigate();
    const { festivalId } = useParams();
    const [searchParams] = useSearchParams();
    const year = useMemo(() => parseYear(searchParams.get('year')), [searchParams]);

    const { festival, dates, meta, loading, error } = useFestivalDetail(festivalId, year);
    const { festivals: allFestivals } = useFestivals();
    const [traceId, setTraceId] = useState(null);
    const [tracePayload, setTracePayload] = useState(null);
    const [traceError, setTraceError] = useState(null);
    const [traceLoading, setTraceLoading] = useState(false);

    useEffect(() => {
        let cancelled = false;
        async function bootstrapTraceId() {
            if (!festivalId) {
                if (!cancelled) setTraceId(null);
                return;
            }

            const selectedYear = year || (dates?.start_date ? new Date(dates.start_date).getFullYear() : new Date().getFullYear());
            try {
                const explain = await festivalAPI.getExplain(festivalId, selectedYear);
                if (!cancelled) {
                    setTraceId(explain?.calculation_trace_id || null);
                }
            } catch {
                if (!cancelled) setTraceId(null);
            }
        }
        bootstrapTraceId();
        return () => {
            cancelled = true;
        };
    }, [festivalId, year, dates?.start_date]);

    const handleOpenTrace = async (id) => {
        if (!id) return;
        setTraceLoading(true);
        setTraceError(null);
        try {
            const trace = await festivalAPI.getTrace(id);
            setTracePayload(trace);
        } catch (err) {
            setTraceError(err.message || 'Failed to load trace');
            setTracePayload(null);
        } finally {
            setTraceLoading(false);
        }
    };

    const handleClose = () => navigate('/');
    const handleFestivalClick = (relatedFestival) => {
        if (relatedFestival?.id) {
            navigate(`/festivals/${relatedFestival.id}`);
        }
    };

    return (
        <section className="festival-detail-page" aria-live="polite">
            {loading && (
                <div className="glass-card festival-detail-page__state" data-testid="detail-loading">
                    <h2>Loading festival detail...</h2>
                    <div className="skeleton" style={{ height: '220px', marginTop: '1rem' }} />
                </div>
            )}

            {!loading && error && (
                <div className="glass-card festival-detail-page__state" role="alert">
                    <h2>Could not load festival</h2>
                    <p>{error}</p>
                    <button className="btn btn-secondary" onClick={() => navigate('/')}>Back to Explorer</button>
                </div>
            )}

            {!loading && !error && festival && (
                <div className="festival-detail-page__content">
                    <FestivalDetail
                        festival={festival}
                        dates={dates}
                        onClose={handleClose}
                        onLocationClick={() => {}}
                        allFestivals={allFestivals}
                        onFestivalClick={handleFestivalClick}
                    />
                    <AuthorityInspector
                        title="Festival Response Authority"
                        meta={meta}
                        traceFallbackId={traceId}
                        onOpenTrace={handleOpenTrace}
                    />
                    {(tracePayload || traceError || traceLoading) && (
                        <section className="glass-card festival-detail-page__trace-panel">
                            <header>
                                <h3>Trace Explorer</h3>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => {
                                        setTracePayload(null);
                                        setTraceError(null);
                                    }}
                                >
                                    Close
                                </button>
                            </header>
                            {traceLoading && <p>Loading trace...</p>}
                            {!traceLoading && traceError && <p role="alert">{traceError}</p>}
                            {!traceLoading && tracePayload && (
                                <pre>{JSON.stringify(tracePayload, null, 2)}</pre>
                            )}
                        </section>
                    )}
                </div>
            )}
        </section>
    );
}

export default FestivalDetailPage;
