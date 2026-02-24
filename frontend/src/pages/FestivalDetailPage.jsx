/**
 * FestivalDetailPage — Nepal × Ink Wash Edition
 * Complete rewrite with immersive hero, clean layout, interactive sections.
 */

import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { differenceInDays, format } from 'date-fns';
import { useFestivalDetail, useFestivals } from '../hooks/useFestivals';
import { festivalAPI } from '../services/api';
import './FestivalDetailPage.css';

const CATEGORY_COLORS = {
    national: 'var(--vermillion)', newari: 'var(--gold-soft)', hindu: 'var(--saffron)',
    buddhist: 'var(--jade)', regional: 'var(--indigo)',
};

function parseYear(value) {
    if (!value) return null;
    const n = Number(value);
    if (!Number.isInteger(n) || n < 1900 || n > 2300) return null;
    return n;
}

function CountdownDisplay({ startDate }) {
    if (!startDate) return null;
    const days = differenceInDays(new Date(startDate), new Date());
    if (days < 0) return <span className="fd-countdown fd-countdown--live">🔴 Ongoing Now</span>;
    if (days === 0) return <span className="fd-countdown fd-countdown--today">✨ Today!</span>;
    if (days === 1) return <span className="fd-countdown">Tomorrow</span>;

    return (
        <span className="fd-countdown">
            <strong>{days}</strong> days away
        </span>
    );
}

export function FestivalDetailPage() {
    const navigate = useNavigate();
    const { festivalId } = useParams();
    const [searchParams] = useSearchParams();
    const year = useMemo(() => parseYear(searchParams.get('year')), [searchParams]);

    const { festival, dates, nearbyFestivals, meta, loading, error } = useFestivalDetail(festivalId, year);
    const { festivals: allFestivals } = useFestivals({ qualityBand: 'all', algorithmicOnly: false });

    const [showTrace, setShowTrace] = useState(false);
    const [traceData, setTraceData] = useState(null);
    const [traceLoading, setTraceLoading] = useState(false);

    const relatedFestivals = useMemo(() => {
        if (!festival?.related_festivals?.length || !allFestivals?.length) return [];
        return festival.related_festivals
            .map((id) => allFestivals.find((f) => f.id === id))
            .filter(Boolean)
            .slice(0, 6);
    }, [festival, allFestivals]);

    const accentColor = festival ? (CATEGORY_COLORS[festival.category] || 'var(--gold)') : 'var(--gold)';

    const ritualDays = festival?.ritual_sequence?.days
        || (Array.isArray(festival?.daily_rituals)
            ? festival.daily_rituals.map((day, idx) => ({
                name: day.name || `Day ${day.day || idx + 1}`,
                events: (day.rituals || []).map((ritual) => ({
                    title: ritual.name,
                    description: ritual.description,
                })),
            }))
            : null);

    const handleLoadTrace = async () => {
        if (traceData) { setShowTrace(!showTrace); return; }
        setTraceLoading(true);
        try {
            const selectedYear = year || (dates?.start_date ? new Date(dates.start_date).getFullYear() : new Date().getFullYear());
            const explain = await festivalAPI.getExplain(festivalId, selectedYear);
            if (explain?.calculation_trace_id) {
                const trace = await festivalAPI.getTrace(explain.calculation_trace_id);
                setTraceData(trace);
            } else {
                setTraceData(explain);
            }
            setShowTrace(true);
        } catch {
            setTraceData({ error: 'Could not load trace data' });
            setShowTrace(true);
        } finally {
            setTraceLoading(false);
        }
    };

    if (loading) {
        return (
            <section className="fd-page animate-fade-in-up">
                <div className="fd-hero-skeleton skeleton" />
                <div style={{ display: 'flex', gap: '16px', marginTop: '24px' }}>
                    <div className="skeleton" style={{ height: '200px', flex: 2, borderRadius: '16px' }} />
                    <div className="skeleton" style={{ height: '200px', flex: 1, borderRadius: '16px' }} />
                </div>
            </section>
        );
    }

    if (error) {
        return (
            <section className="fd-page animate-fade-in-up">
                <div className="ink-card fd-error">
                    <h2>Festival not found</h2>
                    <p>{error}</p>
                    <button className="btn btn-primary" onClick={() => navigate('/festivals')}>← Back to Festivals</button>
                </div>
            </section>
        );
    }

    if (!festival) return null;

    return (
        <section className="fd-page animate-fade-in-up" style={{ '--accent': accentColor }}>
            {/* ── Back Button ── */}
            <button className="fd-back btn btn-secondary" onClick={() => navigate('/festivals')}>
                ← Back
            </button>

            {/* ── Immersive Hero ── */}
            <header className="fd-hero ink-card">
                <div className="fd-hero__accent" />

                <div className="fd-hero__content">
                    <div className="fd-hero__badges">
                        <span className={`badge badge-${festival.category || 'national'}`}>
                            {festival.category}
                        </span>
                        {festival.significance_level && (
                            <span className="fd-significance">
                                {'★'.repeat(Math.min(festival.significance_level, 5))}
                            </span>
                        )}
                    </div>

                    <h1 className="fd-hero__title">{festival.name}</h1>

                    {festival.name_nepali && (
                        <p className="fd-hero__nepali text-nepali">{festival.name_nepali}</p>
                    )}

                    {festival.tagline && (
                        <p className="fd-hero__tagline">{festival.tagline}</p>
                    )}
                </div>

                <div className="fd-hero__dates">
                    <CountdownDisplay startDate={dates?.start_date} />
                    <div className="fd-date-display">
                        {dates?.start_date && (
                            <span className="fd-date-main">
                                {format(new Date(dates.start_date), 'MMMM d, yyyy')}
                                {dates.end_date && dates.end_date !== dates.start_date && (
                                    <> — {format(new Date(dates.end_date), 'MMMM d, yyyy')}</>
                                )}
                            </span>
                        )}
                        {festival.duration_days > 1 && (
                            <span className="fd-duration">{festival.duration_days} day festival</span>
                        )}
                    </div>
                </div>
            </header>

            {/* ── Content Grid ── */}
            <div className="fd-grid">
                {/* Main Content */}
                <div className="fd-main">
                    {/* Description */}
                    {festival.description && (
                        <article className="ink-card fd-description">
                            <h2>About {festival.name}</h2>
                            <p>{festival.description}</p>
                        </article>
                    )}

                    {/* Quick Facts */}
                    <section className="fd-facts stagger-children">
                        {festival.calendar_system && (
                            <div className="ink-card fd-fact clickable">
                                <span className="fd-fact__icon">📅</span>
                                <span className="fd-fact__label">Calendar</span>
                                <span className="fd-fact__value">{festival.calendar_system}</span>
                            </div>
                        )}
                        {festival.duration_days && (
                            <div className="ink-card fd-fact clickable">
                                <span className="fd-fact__icon">⏱</span>
                                <span className="fd-fact__label">Duration</span>
                                <span className="fd-fact__value">{festival.duration_days} days</span>
                            </div>
                        )}
                        {festival.regions?.length > 0 && (
                            <div className="ink-card fd-fact clickable">
                                <span className="fd-fact__icon">📍</span>
                                <span className="fd-fact__label">Regions</span>
                                <span className="fd-fact__value">{festival.regions.join(', ')}</span>
                            </div>
                        )}
                        {festival.deities?.length > 0 && (
                            <div className="ink-card fd-fact clickable">
                                <span className="fd-fact__icon">🙏</span>
                                <span className="fd-fact__label">Deities</span>
                                <span className="fd-fact__value">{festival.deities.join(', ')}</span>
                            </div>
                        )}
                    </section>

                    {/* Mythology Section */}
                    {festival.mythology?.summary && (
                        <article className="ink-card fd-mythology">
                            <h3>Mythology & Origin</h3>
                            <p>{festival.mythology.summary}</p>
                            {festival.mythology.significance && (
                                <p className="fd-mythology__sig">{festival.mythology.significance}</p>
                            )}
                        </article>
                    )}

                    {/* Rituals */}
                    {ritualDays?.length > 0 && (
                        <article className="ink-card fd-rituals">
                            <h3>Rituals & Practices</h3>
                            <div className="fd-rituals__list">
                                {ritualDays.map((day, i) => (
                                    <div key={day.name || i} className="fd-ritual-item">
                                        <span className="fd-ritual-item__day">{day.name || `Day ${i + 1}`}</span>
                                        <div className="fd-ritual-item__content">
                                            <strong>{day.events?.[0]?.title || 'Ritual sequence'}</strong>
                                            {day.significance && <p>{day.significance}</p>}
                                            {day.events?.slice(1, 3).map((event) => (
                                                <p key={event.title}>{event.title}</p>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </article>
                    )}
                </div>

                {/* Sidebar */}
                <aside className="fd-sidebar">
                    {/* Related Festivals */}
                    {relatedFestivals.length > 0 && (
                        <div className="ink-card fd-related">
                            <h3>Related Festivals</h3>
                            <div className="fd-related__list">
                                {relatedFestivals.map((f) => (
                                    <button
                                        key={f.id}
                                        className="fd-related__item"
                                        onClick={() => navigate(`/festivals/${f.id}`)}
                                    >
                                        <span className="fd-related__dot" style={{ background: CATEGORY_COLORS[f.category] || 'var(--gold)' }} />
                                        <span>{f.name}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Date Calculation Info */}
                    <div className="ink-card fd-calculation">
                        <h3>Calculation</h3>
                        <div className="fd-calculation__rows">
                            <div className="fd-calc-row">
                                <span>Method</span>
                                <span>{dates?.calculation_method || festival.calculation_method || '—'}</span>
                            </div>
                            <div className="fd-calc-row">
                                <span>Calendar</span>
                                <span>{festival.calendar_system || '—'}</span>
                            </div>
                            <div className="fd-calc-row">
                                <span>Confidence</span>
                                <span>{meta?.confidence?.level || dates?.confidence || '—'}</span>
                            </div>
                            <div className="fd-calc-row">
                                <span>Quality</span>
                                <span>{meta?.quality_band || '—'}</span>
                            </div>
                        </div>

                        <button
                            className="btn btn-secondary fd-trace-btn"
                            onClick={handleLoadTrace}
                            disabled={traceLoading}
                        >
                            {traceLoading ? 'Loading...' : showTrace ? 'Hide Trace' : 'View Trace'}
                        </button>

                        {showTrace && traceData && (
                            <pre className="fd-trace-pre">
                                {JSON.stringify(traceData, null, 2)}
                            </pre>
                        )}
                    </div>
                </aside>
            </div>
        </section>
    );
}

export default FestivalDetailPage;
