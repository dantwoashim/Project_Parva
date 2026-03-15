import { useMemo, useState } from 'react';
import { differenceInCalendarDays, format } from 'date-fns';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useFestivalDetail, useFestivalDates } from '../hooks/useFestivals';
import { festivalAPI, feedAPI } from '../services/api';
import { useMemberContext } from '../context/useMemberContext';
import './FestivalDetailPage.css';

const CATEGORY_COLORS = {
  national: 'var(--vermillion)',
  newari: 'var(--gold-soft)',
  hindu: 'var(--saffron)',
  buddhist: 'var(--jade)',
  regional: 'var(--indigo)',
};

function parseYear(value) {
  if (!value) return null;
  const numeric = Number(value);
  if (!Number.isInteger(numeric) || numeric < 1900 || numeric > 2300) return null;
  return numeric;
}

function safeFormatDate(value, pattern = 'MMMM d, yyyy') {
  if (!value) return 'Date announced in app';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.valueOf())) return value;
  return format(parsed, pattern);
}

function formatBsDate(bs) {
  if (!bs) return 'Unavailable';
  if (bs.formatted) return bs.formatted;
  if (bs.year && bs.month_name && bs.day) return `${bs.year} ${bs.month_name} ${bs.day}`;
  return 'Unavailable';
}

function buildCountdown(startDate, endDate) {
  if (!startDate) {
    return { label: 'Date pending', tone: 'pending' };
  }

  const days = differenceInCalendarDays(new Date(startDate), new Date());
  if (days < 0 && endDate && differenceInCalendarDays(new Date(endDate), new Date()) >= 0) {
    return { label: 'Observed now', tone: 'live' };
  }
  if (days === 0) return { label: 'Today', tone: 'today' };
  if (days === 1) return { label: 'Tomorrow', tone: 'soon' };
  if (days > 1) return { label: `${days} days away`, tone: 'future' };
  return { label: 'This observance has passed', tone: 'past' };
}

function buildFestivalSeal(festival) {
  const category = festival?.category || 'festival';
  if (category === 'national') return 'Shared civic rhythm';
  if (category === 'newari') return 'Valley ritual rhythm';
  if (category === 'buddhist') return 'Reflection and observance';
  if (category === 'regional') return 'Place-rooted observance';
  return 'Sacred seasonal rhythm';
}

function buildHeroSummary(festival) {
  return (
    festival?.tagline
    || festival?.description
    || festival?.mythology?.summary
    || 'This observance is part of the Nepal temporal calendar and carries ritual, civic, or seasonal meaning.'
  );
}

function buildDetailFacts(festival, dates, meta) {
  return [
    {
      label: 'Calendar',
      value: festival?.calendar_system || festival?.calendar_type || 'Traditional profile',
    },
    {
      label: 'Duration',
      value: festival?.duration_days ? `${festival.duration_days} day${festival.duration_days === 1 ? '' : 's'}` : 'Single observance',
    },
    {
      label: 'Profile',
      value: meta?.quality_band || 'Current method profile',
    },
  ];
}

function normalizeRitualDays(festival) {
  if (festival?.ritual_sequence?.days?.length) {
    return festival.ritual_sequence.days.map((day, index) => ({
      id: `${day.name || index}`,
      name: day.name || `Day ${index + 1}`,
      significance: day.significance || null,
      events: (day.events || []).map((event, eventIndex) => ({
        id: `${day.name || index}-${event.title || eventIndex}`,
        title: event.title || event.name || 'Ritual step',
        description: event.description || null,
      })),
    }));
  }

  if (Array.isArray(festival?.daily_rituals)) {
    return festival.daily_rituals.map((day, index) => ({
      id: `${day.name || index}`,
      name: day.name || `Day ${day.day || index + 1}`,
      significance: day.significance || null,
      events: (day.rituals || []).map((ritual, ritualIndex) => ({
        id: `${day.name || index}-${ritual.name || ritualIndex}`,
        title: ritual.name || 'Ritual step',
        description: ritual.description || null,
      })),
    }));
  }

  return [];
}

function buildDateNarrative(festival, dates, nextDates) {
  if (nextDates?.length) {
    const first = nextDates[0];
    return `This observance next appears on ${safeFormatDate(first.start_date)} and stays visible in the rolling festival calendar for the coming years.`;
  }

  if (dates?.start_date) {
    return `${festival?.name || 'This observance'} is currently anchored to ${safeFormatDate(dates.start_date)} in the active calendar profile.`;
  }

  return 'The date narrative for this observance will appear when computed dates are available.';
}

function significanceLabel(level) {
  if (!level) return null;
  return `Significance ${Math.min(level, 5)}/5`;
}

export function FestivalDetailPage() {
  const navigate = useNavigate();
  const { saveFestival, toggleReminder, startIntegration } = useMemberContext();
  const { festivalId } = useParams();
  const [searchParams] = useSearchParams();
  const [showTrace, setShowTrace] = useState(false);
  const [traceData, setTraceData] = useState(null);
  const [traceLoading, setTraceLoading] = useState(false);
  const year = useMemo(() => parseYear(searchParams.get('year')), [searchParams]);

  const { festival, dates, nearbyFestivals, meta, loading, error } = useFestivalDetail(festivalId, year);
  const { dates: nextDates, loading: nextDatesLoading, error: nextDatesError } = useFestivalDates(festivalId, 3);

  const accentColor = festival ? (CATEGORY_COLORS[festival.category] || 'var(--gold)') : 'var(--gold)';
  const ritualDays = useMemo(() => normalizeRitualDays(festival), [festival]);
  const detailFacts = useMemo(() => buildDetailFacts(festival, dates, meta), [festival, dates, meta]);
  const countdown = useMemo(() => buildCountdown(dates?.start_date, dates?.end_date), [dates]);
  const heroSummary = useMemo(() => buildHeroSummary(festival), [festival]);
  const dateNarrative = useMemo(() => buildDateNarrative(festival, dates, nextDates), [festival, dates, nextDates]);
  const calculationYear = year || (dates?.start_date ? new Date(dates.start_date).getFullYear() : new Date().getFullYear());
  const addToCalendarLink = useMemo(() => feedAPI.getCustomLink(festival?.id ? [festival.id] : [], 2, 'en'), [festival?.id]);

  const handleLoadTrace = async () => {
    if (traceData) {
      setShowTrace((value) => !value);
      return;
    }

    setTraceLoading(true);
    try {
      const explain = await festivalAPI.getExplain(festivalId, calculationYear);
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

  const handleShare = async () => {
    const shareUrl = window.location.href;
    try {
      await navigator.clipboard.writeText(shareUrl);
    } catch {
      // Ignore clipboard issues.
    }
  };

  const handleAddToCalendar = () => {
    const allowed = startIntegration({
      id: festival?.id || 'festival',
      platform: 'festival_calendar',
      title: festival?.name || 'Festival calendar',
      link: addToCalendarLink,
      createdAt: new Date().toISOString(),
    });

    if (allowed) {
      if (typeof window.open === 'function') {
        window.open(addToCalendarLink, '_blank', 'noreferrer');
      }
    }
  };

  if (loading) {
    return (
      <section className="fd-page animate-fade-in-scale">
        <div className="fd-shell">
          <div className="fd-hero-skeleton skeleton" />
          <div className="fd-loading-grid">
            <div className="skeleton fd-loading-card" />
            <div className="skeleton fd-loading-card" />
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="fd-page animate-fade-in-scale">
        <div className="fd-shell">
          <div className="ink-card fd-error">
            <h2>Festival not found</h2>
            <p>{error}</p>
            <button className="btn btn-primary" type="button" onClick={() => navigate('/festivals')}>
              Back to festivals
            </button>
          </div>
        </div>
      </section>
    );
  }

  if (!festival) return null;

  return (
    <section className="fd-page animate-fade-in-scale" style={{ '--accent': accentColor }}>
      <div className="fd-shell">
        <button className="btn btn-secondary fd-back" type="button" onClick={() => navigate('/festivals')}>
          Back to festivals
        </button>

        <header className="fd-hero ink-card">
          <div className="fd-hero__copy">
            <div className="fd-hero__eyebrow-row">
              <span className="badge">{festival.category || 'Festival'}</span>
              {significanceLabel(festival.significance_level) ? (
                <span className="fd-hero__meta-pill">{significanceLabel(festival.significance_level)}</span>
              ) : null}
            </div>

            <h1 className="fd-hero__title">{festival.name}</h1>
            {festival.name_nepali ? <p className="fd-hero__nepali text-nepali">{festival.name_nepali}</p> : null}
            <p className="fd-hero__summary">{heroSummary}</p>

            <div className="fd-hero__actions">
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => saveFestival({
                  id: festival.id,
                  name: festival.name,
                  category: festival.category,
                  startDate: dates?.start_date,
                })}
              >
                Save
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => toggleReminder({
                  id: `festival:${festival.id}`,
                  title: festival.name,
                  kind: 'festival',
                  date: dates?.start_date,
                })}
              >
                Remind me
              </button>
              <button type="button" className="btn btn-secondary btn-sm" onClick={handleShare}>
                Share
              </button>
            </div>

            <div className="fd-hero__facts">
              {detailFacts.map((fact) => (
                <article key={fact.label} className="fd-hero__fact">
                  <span>{fact.label}</span>
                  <strong>{fact.value}</strong>
                </article>
              ))}
            </div>
          </div>

          <div className="fd-hero__side">
            <article className="fd-seal-card">
              <div className="fd-seal-card__art" aria-hidden="true">
                <svg viewBox="0 0 120 120" className="fd-seal-card__svg">
                  <circle cx="60" cy="60" r="44" className="fd-seal-card__ring fd-seal-card__ring--outer" />
                  <circle cx="60" cy="60" r="28" className="fd-seal-card__ring fd-seal-card__ring--inner" />
                  <path d="M60 26 L70 60 L60 94 L50 60 Z" className="fd-seal-card__petal" />
                  <path d="M26 60 L60 70 L94 60 L60 50 Z" className="fd-seal-card__petal fd-seal-card__petal--soft" />
                </svg>
              </div>
              <span className="fd-seal-card__eyebrow">Festival seal</span>
              <strong>{buildFestivalSeal(festival)}</strong>
              <p>{dateNarrative}</p>
            </article>

            <article className="fd-date-card">
              <span className={`fd-countdown fd-countdown--${countdown.tone}`}>{countdown.label}</span>
              <strong>{safeFormatDate(dates?.start_date)}</strong>
              <small>
                {dates?.end_date && dates.end_date !== dates.start_date
                  ? `${safeFormatDate(dates.end_date)} end`
                  : 'Single-day anchor shown in this profile'}
              </small>
              <div className="fd-date-card__row">
                <span>Bikram Sambat</span>
                <span>
                  {formatBsDate(dates?.bs_start)}
                  {dates?.bs_end && formatBsDate(dates.bs_end) !== formatBsDate(dates.bs_start)
                    ? ` - ${formatBsDate(dates.bs_end)}`
                    : ''}
                </span>
              </div>
              <div className="fd-date-card__row">
                <span>Method</span>
                <span>{dates?.calculation_method || festival.calculation_method || 'Current method profile'}</span>
              </div>
              <div className="fd-date-card__actions">
                <button type="button" className="btn btn-secondary btn-sm" onClick={handleAddToCalendar}>
                  Add to calendar
                </button>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => document.getElementById('future-years')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
                >
                  Future years
                </button>
              </div>
            </article>
          </div>
        </header>

        <div className="fd-layout">
          <div className="fd-main">
            <article className="ink-card fd-story">
              <div className="fd-section-head">
                <div>
                  <p className="today-page__eyebrow">Meaning</p>
                  <h2>Why it matters</h2>
                </div>
              </div>
              <p>{festival.description || heroSummary}</p>
              {festival.mythology?.summary ? <p>{festival.mythology.summary}</p> : null}
              {festival.mythology?.significance ? (
                <div className="fd-story__highlight">
                  <span>Context</span>
                  <strong>{festival.mythology.significance}</strong>
                </div>
              ) : null}
            </article>

            {ritualDays.length ? (
              <article className="ink-card fd-practice">
                <div className="fd-section-head">
                  <div>
                    <p className="today-page__eyebrow">Observance</p>
                    <h2>How it is practiced</h2>
                  </div>
                </div>
                <div className="fd-practice__list">
                  {ritualDays.map((day, index) => (
                    <article key={day.id} className="fd-practice__item">
                      <span className="fd-practice__index">{String(index + 1).padStart(2, '0')}</span>
                      <div className="fd-practice__content">
                        <h3>{day.name}</h3>
                        {day.significance ? <p>{day.significance}</p> : null}
                        <ul className="fd-practice__events">
                          {(day.events || []).map((event) => (
                            <li key={event.id}>
                              <strong>{event.title}</strong>
                              {event.description ? <span>{event.description}</span> : null}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </article>
                  ))}
                </div>
              </article>
            ) : null}

            <article className="ink-card fd-rhythm" id="future-years">
              <div className="fd-section-head">
                <div>
                  <p className="today-page__eyebrow">Date rhythm</p>
                  <h2>How the observance moves over time</h2>
                </div>
              </div>

              <p className="fd-rhythm__intro">{dateNarrative}</p>

              {nextDatesLoading ? <div className="skeleton fd-rhythm__skeleton" /> : null}
              {!nextDatesLoading && nextDatesError ? <p className="muted">{nextDatesError}</p> : null}
              {!nextDatesLoading && !nextDatesError && nextDates?.length ? (
                <div className="fd-rhythm__rows">
                  {nextDates.map((row) => (
                    <article key={`${row.gregorian_year}-${row.start_date}`} className="fd-rhythm__row">
                      <div>
                        <span>{row.gregorian_year}</span>
                        <strong>
                          {safeFormatDate(row.start_date, 'MMM d, yyyy')}
                          {row.end_date && row.end_date !== row.start_date
                            ? ` - ${safeFormatDate(row.end_date, 'MMM d, yyyy')}`
                            : ''}
                        </strong>
                      </div>
                      <small>
                        {formatBsDate(row.bs_start)}
                        {row.bs_end && formatBsDate(row.bs_end) !== formatBsDate(row.bs_start)
                          ? ` - ${formatBsDate(row.bs_end)}`
                          : ''}
                      </small>
                    </article>
                  ))}
                </div>
              ) : null}
            </article>
          </div>

          <aside className="fd-sidebar">
            <article className="ink-card fd-summary-panel">
              <div className="fd-section-head">
                <div>
                  <p className="today-page__eyebrow">Profile</p>
                  <h2>At a glance</h2>
                </div>
              </div>
              <div className="fd-summary-panel__rows">
                {festival.calendar_system ? (
                  <div className="fd-summary-panel__row">
                    <span>Calendar</span>
                    <strong>{festival.calendar_system}</strong>
                  </div>
                ) : null}
                {festival.regions?.length ? (
                  <div className="fd-summary-panel__row">
                    <span>Regions</span>
                    <strong>{festival.regions.join(', ')}</strong>
                  </div>
                ) : null}
                {festival.deities?.length ? (
                  <div className="fd-summary-panel__row">
                    <span>Deities</span>
                    <strong>{festival.deities.join(', ')}</strong>
                  </div>
                ) : null}
                {festival.duration_days ? (
                  <div className="fd-summary-panel__row">
                    <span>Duration</span>
                    <strong>{festival.duration_days} days</strong>
                  </div>
                ) : null}
              </div>
            </article>

            {nearbyFestivals?.length ? (
              <article className="ink-card fd-related">
                <div className="fd-section-head">
                  <div>
                    <p className="today-page__eyebrow">Nearby</p>
                    <h2>Related festivals</h2>
                  </div>
                </div>
                <div className="fd-related__list">
                  {nearbyFestivals.slice(0, 6).map((item) => (
                    <button
                      key={item.id || item.name}
                      type="button"
                      className="fd-related__item"
                      onClick={() => item.id && navigate(`/festivals/${item.id}`)}
                    >
                      <span className="fd-related__dot" style={{ background: CATEGORY_COLORS[item.category] || 'var(--gold)' }} />
                      <div>
                        <strong>{item.name || item.display_name || item.id}</strong>
                        <span>{item.category || 'Festival'}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </article>
            ) : null}

            <details className="ink-card fd-technical">
              <summary>Method and technical details</summary>
              <div className="fd-technical__body">
                <div className="fd-calculation__rows">
                  <div className="fd-calc-row">
                    <span>Method</span>
                    <span>{dates?.calculation_method || festival.calculation_method || 'Current method profile'}</span>
                  </div>
                  <div className="fd-calc-row">
                    <span>Calendar</span>
                    <span>{festival.calendar_system || festival.calendar_type || 'Traditional profile'}</span>
                  </div>
                  <div className="fd-calc-row">
                    <span>Confidence</span>
                    <span>{meta?.confidence?.level || dates?.confidence || 'Profile-based'}</span>
                  </div>
                  <div className="fd-calc-row">
                    <span>Quality</span>
                    <span>{meta?.quality_band || 'Profile-based guidance'}</span>
                  </div>
                </div>

                <button className="btn btn-secondary fd-trace-btn" type="button" onClick={handleLoadTrace} disabled={traceLoading}>
                  {traceLoading ? 'Loading trace...' : showTrace ? 'Hide technical trace' : 'View technical trace'}
                </button>

                {showTrace && traceData ? (
                  <pre className="fd-trace-pre">{JSON.stringify(traceData, null, 2)}</pre>
                ) : null}
              </div>
            </details>
          </aside>
        </div>
      </div>
    </section>
  );
}

export default FestivalDetailPage;
