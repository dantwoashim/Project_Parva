import { useMemo, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { buildConsumerFestivalDetailViewModel } from '../consumer/consumerViewModels';
import { useFestivalDates, useFestivalDetail } from '../hooks/useFestivals';
import { useMemberContext } from '../context/useMemberContext';
import { useTemporalContext } from '../context/useTemporalContext';
import { feedAPI, festivalAPI } from '../services/api';
import { describeSupportError } from '../services/errorFormatting';
import './FestivalDetailPage.css';

function parseYear(value) {
  const year = Number(value);
  return Number.isInteger(year) ? year : null;
}

function ritualLabel(index) {
  return ['First Prahara', 'Second Prahara', 'Third Prahara', 'Fourth Prahara'][index] || `Ritual ${index + 1}`;
}

function artTone(value) {
  return `festival-detail__art festival-detail__art--${value || 'lamp'}`.trim();
}

function startCaseTruth(value) {
  return String(value || 'unknown')
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function truthTone(value) {
  return `festival-detail__truth-chip festival-detail__truth-chip--${value || 'default'}`.trim();
}

export function FestivalDetailPage() {
  const navigate = useNavigate();
  const { festivalId } = useParams();
  const [searchParams] = useSearchParams();
  const [trace, setTrace] = useState(null);
  const [traceLoading, setTraceLoading] = useState(false);
  const year = useMemo(() => parseYear(searchParams.get('year')), [searchParams]);
  const { state: temporalState } = useTemporalContext();
  const { state: memberState, saveFestival, toggleReminder, startIntegration } = useMemberContext();
  const {
    festival,
    dates,
    nearbyFestivals,
    completeness,
    meta,
    loading,
    error,
  } = useFestivalDetail(festivalId, year);
  const { dates: nextDates } = useFestivalDates(festivalId, 4);

  const viewModel = useMemo(
    () => buildConsumerFestivalDetailViewModel({
      festival,
      dates,
      nextDates,
      nearbyFestivals,
      completeness,
      temporalState: {
        language: temporalState.language,
        timezone: temporalState.timezone,
      },
    }),
    [completeness, dates, festival, nearbyFestivals, nextDates, temporalState.language, temporalState.timezone],
  );

  const isSaved = memberState.savedFestivals.some((item) => item.id === festivalId);
  const alternateCandidates = dates?.alternate_candidates || dates?.authority_alternates || [];
  const truthChips = [
    dates?.support_tier ? { label: startCaseTruth(dates.support_tier), tone: dates.support_tier } : null,
    dates?.source_family ? { label: startCaseTruth(dates.source_family), tone: 'source' } : null,
    dates?.selection_policy ? { label: startCaseTruth(dates.selection_policy), tone: 'policy' } : null,
    dates?.fallback_used ? { label: 'Fallback Used', tone: 'fallback' } : null,
    dates?.calibration_status ? { label: startCaseTruth(dates.calibration_status), tone: 'calibration' } : null,
  ].filter(Boolean);
  const calendarLink = useMemo(
    () => feedAPI.getCustomLink(festivalId ? [festivalId] : [], 3, 'en'),
    [festivalId],
  );

  async function handleShare() {
    try {
      await navigator.clipboard.writeText(window.location.href);
    } catch {
      // Ignore clipboard issues in unsupported environments.
    }
  }

  async function handleCalendar() {
    const allowed = await startIntegration({
      platform: `festival:${festivalId}`,
      title: festival?.name || 'Festival calendar',
      link: calendarLink,
      createdAt: new Date().toISOString(),
    });

    if (allowed && typeof window.open === 'function') {
      window.open(calendarLink, '_blank', 'noreferrer');
    }
  }

  async function handleLoadTrace() {
    if (!festivalId) return;
    if (trace) {
      setTrace(null);
      return;
    }

    setTraceLoading(true);
    try {
      const explain = await festivalAPI.getExplain(festivalId, year || undefined, 'authority_compare');
      if (explain?.calculation_trace_id) {
        setTrace(await festivalAPI.getTrace(explain.calculation_trace_id));
      } else {
        setTrace(explain);
      }
    } catch (err) {
      setTrace({ error: describeSupportError(err, 'Technical trace is unavailable right now.') });
    } finally {
      setTraceLoading(false);
    }
  }

  if (loading) {
    return (
      <section className="festival-detail animate-fade-in-up consumer-route consumer-route--detail">
        <div className="skeleton festival-detail__hero-skeleton" />
        <div className="skeleton festival-detail__block-skeleton" />
        <div className="skeleton festival-detail__block-skeleton" />
      </section>
    );
  }

  if (error || !festival) {
    return (
      <section className="festival-detail animate-fade-in-up consumer-route consumer-route--detail">
        <article className="festival-detail__error ink-card" role="alert">
          <p className="festival-detail__eyebrow">Festival detail</p>
          <h1>This observance could not be loaded.</h1>
          <p>{error || 'The requested observance is unavailable in the current profile.'}</p>
          <button type="button" className="btn btn-secondary" onClick={() => navigate('/festivals')}>
            Back to festivals
          </button>
        </article>
      </section>
    );
  }

  return (
    <section className="festival-detail animate-fade-in-up consumer-route consumer-route--detail">
      <header className="festival-detail__hero">
        <div className={artTone(viewModel.artKey)} aria-hidden="true" />
        <div className="festival-detail__hero-overlay">
          <div className="festival-detail__hero-copy">
            <div className="festival-detail__hero-meta">
              <span>{viewModel.dateLabel}</span>
              <span>{viewModel.subtitle || festival.category || 'Observance'}</span>
              <span>{viewModel.profileStatusLabel}</span>
            </div>
            <h1>{viewModel.title}</h1>
            <p>{viewModel.summary}</p>
            <div className="festival-detail__hero-actions">
              <button type="button" className="btn btn-primary" onClick={handleCalendar}>Add to Calendar</button>
              <button type="button" className="btn btn-secondary" onClick={handleShare}>Share Insight</button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => saveFestival({
                  id: festival.id,
                  name: festival.name,
                  category: festival.category,
                  startDate: dates?.start_date,
                })}
              >
                {isSaved ? 'Saved' : 'Save observance'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <section className="festival-detail__origin">
        <div className="festival-detail__origin-side">
          <h2>The Celestial Origin</h2>
          <div className="festival-detail__origin-marker">
            <span className="material-symbols-outlined">flare</span>
            <span>Sacred heritage</span>
          </div>
        </div>
        <div className="festival-detail__origin-story">
          <p className="festival-detail__lead">{viewModel.originStory}</p>
          <blockquote>{viewModel.whyItMatters}</blockquote>
          <p className="festival-detail__status-note">{viewModel.originStatusNote}</p>
          <p>{viewModel.summary}</p>
        </div>
      </section>

      <section className="festival-detail__timeline">
        <div className="festival-detail__section-head">
          <h2>The Ritual Timeline</h2>
          <p>Vedic ceremonies spanning the living observance rhythm.</p>
        </div>
        <div className="festival-detail__timeline-list">
          {viewModel.rituals.length ? viewModel.rituals.map((item, index) => (
            <article key={item.id} className={`festival-detail__timeline-item ${index % 2 ? 'is-reverse' : ''}`.trim()}>
              <div className="festival-detail__timeline-copy">
                <span>{ritualLabel(index)}</span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>
              <div className="festival-detail__timeline-dot" />
            </article>
          )) : (
            <article className="festival-detail__timeline-item">
              <div className="festival-detail__timeline-copy">
                <span>{viewModel.ritualEmpty.kicker}</span>
                <h3>{viewModel.ritualEmpty.title}</h3>
                <p>{viewModel.ritualEmpty.body}</p>
              </div>
              <div className="festival-detail__timeline-dot" />
            </article>
          )}
        </div>
      </section>

      <section className="festival-detail__presence">
        <div className="festival-detail__section-head">
          <h2>Sacred Presence</h2>
          <p>Related observances and future occurrences that keep the wider ritual context in view.</p>
        </div>
        <div className="festival-detail__presence-grid">
          {viewModel.related.length ? viewModel.related.map((item, index) => (
            <Link key={item.id} to={item.href} className={`festival-detail__presence-card ${index === 1 ? 'is-offset' : ''}`.trim()}>
              <div className={artTone(index % 2 ? 'mandala' : 'moon')} />
              <div>
                <h3>{item.title}</h3>
                <p>{item.dateLabel}</p>
              </div>
            </Link>
          )) : (
            <article className="festival-detail__presence-card">
              <div className={artTone('lamp')} />
              <div>
                <h3>{viewModel.relatedEmpty.title}</h3>
                <p>{viewModel.relatedEmpty.body}</p>
              </div>
            </article>
          )}
        </div>
      </section>

      <section className="festival-detail__offerings">
        <div className="festival-detail__section-head">
          <h2>Essential Offerings</h2>
          <p>Quick facts, future dates, and method details for this observance.</p>
        </div>
        <div className="festival-detail__offerings-row">
          {viewModel.quickFacts.map((fact) => (
            <article key={fact.label} className="festival-detail__offering-card">
              <div className="festival-detail__offering-icon">
                <span className="material-symbols-outlined">temple_hindu</span>
              </div>
              <h3>{fact.label}</h3>
              <p>{fact.value}</p>
            </article>
          ))}
          {viewModel.occurrences.map((occurrence) => (
            <article key={occurrence.year} className="festival-detail__offering-card">
              <div className="festival-detail__offering-icon">
                <span className="material-symbols-outlined">calendar_month</span>
              </div>
              <h3>{occurrence.year}</h3>
              <p>{occurrence.label}</p>
            </article>
          ))}
        </div>
      </section>

      {dates ? (
        <section className="festival-detail__truth">
          <div className="festival-detail__section-head">
            <h2>Truth Surface</h2>
            <p>Authority selection, fallback state, and alternate candidates stay visible instead of disappearing behind one confidence badge.</p>
          </div>
          <div className="festival-detail__truth-grid">
            <article className="festival-detail__truth-panel">
              <p className="festival-detail__eyebrow">Resolution contract</p>
              <div className="festival-detail__truth-chip-row">
                {truthChips.map((chip) => (
                  <span key={`${chip.tone}-${chip.label}`} className={truthTone(chip.tone)}>
                    {chip.label}
                  </span>
                ))}
              </div>
              <div className="festival-detail__truth-copy">
                <p><strong>Engine path:</strong> {dates.engine_path || 'Unavailable'}</p>
                <p><strong>Source family:</strong> {dates.source_family || 'Computed rule profile'}</p>
                <p><strong>Selection policy:</strong> {startCaseTruth(dates.selection_policy || 'public_default')}</p>
                <p><strong>Authority conflict:</strong> {dates.authority_conflict ? 'Present' : 'No conflict published'}</p>
                {dates.authority_note ? (
                  <p className="festival-detail__truth-note">{dates.authority_note}</p>
                ) : null}
              </div>
            </article>

            <article className="festival-detail__truth-panel festival-detail__truth-panel--ledger">
              <p className="festival-detail__eyebrow">Authority ledger</p>
              {alternateCandidates.length ? (
                <div className="festival-detail__truth-ledger">
                  <div className="festival-detail__truth-ledger-item is-primary">
                    <span className="festival-detail__truth-ledger-date">{dates.start_date}</span>
                    <div>
                      <strong>Public default</strong>
                      <p>{dates.source_family || 'Current authority precedence'}</p>
                    </div>
                  </div>
                  {alternateCandidates.map((candidate) => (
                    <div
                      key={`${candidate.start}-${candidate.source || candidate.source_family || 'candidate'}`}
                      className="festival-detail__truth-ledger-item"
                    >
                      <span className="festival-detail__truth-ledger-date">{candidate.start}</span>
                      <div>
                        <strong>{candidate.source_family || candidate.source || 'Alternate authority'}</strong>
                        <p>{candidate.notes || 'Published as an alternate authority-backed candidate.'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="festival-detail__truth-note">
                  No alternate authority-backed candidates are published for this festival-year.
                </p>
              )}
            </article>
          </div>
        </section>
      ) : null}

      <section className="festival-detail__technical">
        <div className="festival-detail__technical-copy">
          <div>
            <p className="festival-detail__eyebrow">Method details</p>
            <h2>Open the evidence only when you want it.</h2>
          </div>
          <p>The main page stays editorial. Trace and technical detail remain available without overwhelming the ritual story.</p>
        </div>
        <div className="festival-detail__technical-actions">
          <button type="button" className="btn btn-secondary" onClick={handleLoadTrace}>
            {traceLoading ? 'Loading technical trace...' : trace ? 'Hide technical trace' : 'View technical trace'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => toggleReminder({
              id: `festival:${festival.id}`,
              title: festival.name,
              kind: 'festival',
              date: dates?.start_date,
            })}
          >
            {memberState.reminders.some((item) => item.id === `festival:${festival.id}`) ? 'Reminder saved' : 'Remind me'}
          </button>
          <EvidenceDrawer {...viewModel.evidence} meta={meta} />
        </div>
        {trace ? <pre className="festival-detail__trace">{JSON.stringify(trace, null, 2)}</pre> : null}
      </section>
    </section>
  );
}

export default FestivalDetailPage;
