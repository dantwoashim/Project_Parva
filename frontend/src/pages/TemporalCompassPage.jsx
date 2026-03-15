import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { temporalAPI, muhurtaAPI } from '../services/api';
import { useTemporalContext } from '../context/useTemporalContext';
import { findPresetByLocation } from '../data/locationPresets';
import { trackEvent } from '../services/analytics';
import './TemporalCompassPage.css';

function safeTime(iso, timeZone, fallback = 'Time unavailable') {
  if (!iso) return fallback;
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.valueOf())) return fallback;

  try {
    return parsed.toLocaleTimeString('en-US', {
      timeZone,
      hour: 'numeric',
      minute: '2-digit',
    });
  } catch {
    return parsed.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }
}

function describePaksha(value) {
  if (value === 'shukla') return 'bright half';
  if (value === 'krishna') return 'waning half';
  return 'lunar cycle';
}

function classifyWindow(block) {
  if (!block) return 'Mixed';
  if (block.class === 'auspicious') return 'Strong';
  if (block.class === 'avoid') return 'Avoid';
  if (typeof block.score === 'number' && block.score >= 65) return 'Strong';
  if (typeof block.score === 'number' && block.score >= 25) return 'Good';
  if (typeof block.score === 'number' && block.score <= -25) return 'Avoid';
  return 'Mixed';
}

function toneLabel(value) {
  if (value === 'auspicious') return 'Favorable now';
  if (value === 'avoid') return 'Avoid new beginnings now';
  return 'Mixed now';
}

function progressLabel(orbital) {
  const number = orbital?.tithi;
  const percent = typeof orbital?.phase_ratio === 'number' ? Math.round(orbital.phase_ratio * 100) : null;
  if (!number && percent === null) return 'A plain-language lunar progress note appears here when the daily summary returns orbital detail.';
  return `The lunar day is well underway, with Tithi ${number || '-'} about ${percent ?? '-'}% complete.`;
}

function summarizeReasons(block, fallback) {
  if (Array.isArray(block?.reason_codes) && block.reason_codes.length) {
    return block.reason_codes.map((code) => code.replaceAll('_', ' ')).join(', ');
  }
  return fallback || 'Based on the current timing signals and the place in view.';
}

function describeLeadFestival(festivals) {
  if (!festivals.length) return 'No major observance is active in the current view.';
  if (festivals.length === 1) return `${festivals[0].name} is the main observance in view today.`;
  return `${festivals[0].name} leads today, with ${festivals.length - 1} more observance${festivals.length - 1 === 1 ? '' : 's'} also in view.`;
}

function buildRhythmSegments(blocks = []) {
  return [...blocks]
    .filter((block) => block?.start)
    .sort((left, right) => new Date(left.start) - new Date(right.start))
    .slice(0, 8)
    .map((block) => ({
      ...block,
      tone: classifyWindow(block),
    }));
}

export function TemporalCompassPage() {
  const navigate = useNavigate();
  const { state, setDate } = useTemporalContext();
  const [loading, setLoading] = useState(true);
  const [partialNotice, setPartialNotice] = useState('');
  const [showFullSchedule, setShowFullSchedule] = useState(false);
  const [compass, setCompass] = useState(null);
  const [muhurta, setMuhurta] = useState(null);
  const [meta, setMeta] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      setPartialNotice('');

      const [compassResult, muhurtaResult] = await Promise.allSettled([
        temporalAPI.getCompassEnvelope({
          date: state.date,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          qualityBand: 'computed',
        }),
        muhurtaAPI.getHeatmapEnvelope({
          date: state.date,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          type: 'general',
        }),
      ]);

      if (cancelled) return;

      if (compassResult.status === 'fulfilled') {
        setCompass(compassResult.value.data || null);
        setMeta(compassResult.value.meta || null);
      } else {
        setCompass(null);
        setMeta(null);
      }

      if (muhurtaResult.status === 'fulfilled') {
        setMuhurta(muhurtaResult.value.data || null);
      } else {
        setMuhurta(null);
      }

      if (compassResult.status === 'rejected' && muhurtaResult.status === 'rejected') {
        setError('We could not build today\'s view right now. Please try again in a moment.');
      } else if (compassResult.status === 'rejected') {
        setPartialNotice('Daily summary detail is limited right now, but timing guidance is still available.');
      } else if (muhurtaResult.status === 'rejected') {
        setPartialNotice('Timing guidance is limited right now, but today\'s calendar summary is still available.');
      }

      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

  const preset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const festivalsToday = compass?.today?.festivals || [];
  const bestWindow = muhurta?.best_window || null;
  const avoidWindow = muhurta?.rahu_kalam || null;
  const currentMuhurta = compass?.horizon?.current_muhurta || null;
  const rhythmSegments = useMemo(() => buildRhythmSegments(muhurta?.blocks || []), [muhurta]);
  const visibleSegments = showFullSchedule ? rhythmSegments : rhythmSegments.slice(0, 3);
  const sunrise = compass?.horizon?.sunrise ? safeTime(compass.horizon.sunrise, state.timezone, '') : '';
  const sunset = compass?.horizon?.sunset ? safeTime(compass.horizon.sunset, state.timezone, '') : '';
  const summaryLine = compass?.primary_readout
    ? `${compass.primary_readout.tithi_name || 'Today'} in the ${describePaksha(compass.primary_readout.paksha)}.`
    : 'Today\'s lunar context will appear here when the daily summary is available.';
  const festivalLead = describeLeadFestival(festivalsToday);

  return (
    <section className="today-page animate-fade-in-up">
      <header className="today-page__hero ink-card">
        <div className="today-page__hero-copy">
          <p className="today-page__eyebrow">Today</p>
          <h1 className="text-hero">
            What today means in {preset?.label || 'your place'}
          </h1>
          <p className="today-page__summary">{summaryLine}</p>
          <p className="today-page__subsummary">{festivalLead}</p>
          <p className="today-page__hero-context">
            {currentMuhurta?.name
              ? `${currentMuhurta.name} is active now, and the current tone is ${toneLabel(currentMuhurta.class).toLowerCase()}.`
              : `Date in view: ${state.date}.`}
          </p>
        </div>

        <aside className="today-page__hero-side">
          <div className="today-page__hero-grid">
            <article className="today-page__hero-panel today-page__hero-panel--accent">
              <span className="today-page__label">Best window</span>
              <strong>{bestWindow?.name || 'Best window will appear with the next successful timing pass'}</strong>
              <p>
                {bestWindow?.start
                  ? `${safeTime(bestWindow.start, state.timezone)} - ${safeTime(bestWindow.end, state.timezone)}`
                  : 'Open Best Time for the fuller day view when timing returns.'}
              </p>
            </article>
            <article className="today-page__hero-panel">
              <span className="today-page__label">Avoid period</span>
              <strong>
                {avoidWindow?.start
                  ? `${safeTime(avoidWindow.start, state.timezone)} - ${safeTime(avoidWindow.end, state.timezone)}`
                  : 'Use normal caution'}
              </strong>
              <p>{avoidWindow?.segment ? `Rahu Kalam segment ${avoidWindow.segment}` : 'Use normal caution.'}</p>
            </article>
            {sunrise && sunset ? (
              <article className="today-page__hero-panel today-page__hero-panel--sun">
                <div>
                  <span className="today-page__label">Sunrise</span>
                  <strong>{sunrise}</strong>
                </div>
                <div>
                  <span className="today-page__label">Sunset</span>
                  <strong>{sunset}</strong>
                </div>
              </article>
            ) : null}
          </div>
        </aside>
      </header>

      <section className="today-page__utility-bar ink-card">
        <label className="ink-input today-page__date-field">
          <span>Date</span>
          <input type="date" value={state.date} onChange={(event) => setDate(event.target.value)} />
        </label>
        <Link className="btn btn-secondary" to="/my-place">Set my place</Link>
        <button type="button" className="btn btn-secondary" onClick={() => navigate('/festivals')}>
          Explore festivals
        </button>
        <EvidenceDrawer
          title="Today view"
          intro="This drawer shows the place, date, method profile, and what data was available when today was computed."
          methodRef={meta?.method || 'Daily compass profile'}
          confidenceNote={meta?.confidence?.level || meta?.confidence || 'Public guidance'}
          placeUsed={preset?.label || state.timezone}
          computedForDate={state.date}
          availability={[
            { label: 'Daily summary', available: Boolean(compass), note: 'The top-line reading depends on the calendar summary payload.' },
            { label: 'Timing windows', available: Boolean(muhurta?.blocks?.length), note: 'Best and avoid windows appear only when the timing service returns ranked blocks.' },
            { label: 'Sunrise and sunset', available: Boolean(sunrise && sunset), note: 'Sunrise data stays out of the hero when it is missing or not useful.' },
          ]}
          meta={meta}
          traceFallbackId={compass?.calculation_trace_id}
        />
      </section>

      {partialNotice ? <p className="today-page__notice">{partialNotice}</p> : null}

      {loading ? (
        <div className="today-page__loading">
          <div className="skeleton" style={{ minHeight: '320px', borderRadius: '1.5rem' }} />
          <div className="today-page__grid">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="skeleton" style={{ minHeight: '180px', borderRadius: '1.2rem' }} />
            ))}
          </div>
        </div>
      ) : null}

      {!loading && error ? (
        <div className="ink-card today-page__error" role="alert">
          <h2>Today&apos;s view is temporarily unavailable</h2>
          <p>{error}</p>
        </div>
      ) : null}

      {!loading && !error ? (
        <>
          <section className="ink-card today-page__rhythm">
            <div className="today-page__panel-header">
              <div>
                <p className="today-page__eyebrow">Day rhythm</p>
                <h2>How the day opens and tightens</h2>
              </div>
              <div className="today-page__panel-actions">
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => {
                    const next = !showFullSchedule;
                    setShowFullSchedule(next);
                    trackEvent('full_schedule_opened', { surface: 'today', expanded: next });
                  }}
                >
                  {showFullSchedule ? 'Show less' : 'View full schedule'}
                </button>
                <Link to="/best-time">Open Best Time</Link>
              </div>
            </div>

            <div className="today-page__rhythm-track" role="list" aria-label="Day rhythm">
              {visibleSegments.length ? visibleSegments.map((segment) => (
                <article
                  key={`${segment.index}-${segment.start}`}
                  className={`today-page__rhythm-segment today-page__rhythm-segment--${segment.tone.toLowerCase()}`.trim()}
                  role="listitem"
                >
                  <span className="today-page__label">{segment.tone}</span>
                  <strong>{segment.name}</strong>
                  <p>{safeTime(segment.start, state.timezone)} - {safeTime(segment.end, state.timezone)}</p>
                </article>
              )) : <p className="muted">A fuller rhythm view appears here when the timing service is available.</p>}
            </div>

            <p className="today-page__rhythm-caption">
              {bestWindow
                ? `${bestWindow.name} is the clearest opening today, while ${avoidWindow?.segment ? `Rahu Kalam segment ${avoidWindow.segment}` : 'the avoid period'} is best kept clear.`
                : 'Timing guidance will appear here once the daily windows are available.'}
            </p>
          </section>

          <section className="today-page__grid">
            <article className="ink-card today-page__panel today-page__panel--wide">
              <div className="today-page__panel-header">
                <div>
                  <p className="today-page__eyebrow">Today&apos;s festivals</p>
                  <h2>What is active today</h2>
                </div>
                <Link to="/festivals">See full festival calendar</Link>
              </div>
              <div className="today-page__festival-list">
                {festivalsToday.length ? festivalsToday.map((festival) => (
                  <button
                    key={`${festival.id}-${festival.start_date || festival.name}`}
                    type="button"
                    className="today-page__festival-item"
                    onClick={() => navigate(`/festivals/${festival.id}`)}
                  >
                    <strong>{festival.name}</strong>
                    <span>{festival.start_date || 'Date available in details'}</span>
                  </button>
                )) : <p className="muted">No observance is active in the current view.</p>}
              </div>
            </article>

            <article className="ink-card today-page__panel">
              <div className="today-page__panel-header">
                <div>
                  <p className="today-page__eyebrow">How the day is formed</p>
                  <h2>Today&apos;s lunar context</h2>
                </div>
              </div>
              <div className="today-page__signal-grid">
                <div><span>Nakshatra</span><strong>{compass?.signals?.nakshatra?.name || 'Pending'}</strong></div>
                <div><span>Yoga</span><strong>{compass?.signals?.yoga?.name || 'Pending'}</strong></div>
                <div><span>Karana</span><strong>{compass?.signals?.karana?.name || 'Pending'}</strong></div>
                <div><span>Weekday</span><strong>{compass?.signals?.vaara?.name_english || 'Pending'}</strong></div>
              </div>
              <div className="today-page__progress">
                <div className="today-page__progress-bar">
                  <span style={{ width: `${Math.max(8, Math.min(100, Math.round((compass?.orbital?.phase_ratio || 0) * 100)))}%` }} />
                </div>
                <p>{progressLabel(compass?.orbital)}</p>
              </div>
            </article>

            <article className="ink-card today-page__panel today-page__panel--wide">
              <div className="today-page__panel-header">
                <div>
                  <p className="today-page__eyebrow">Timing guidance</p>
                  <h2>Why today&apos;s window ranks this way</h2>
                </div>
                <Link to="/best-time">Open Best Time</Link>
              </div>
              <dl className="today-page__timing-notes">
                <div>
                  <dt>Best window</dt>
                  <dd>{bestWindow?.name || 'Best window pending'}</dd>
                </div>
                <div>
                  <dt>Ranking note</dt>
                  <dd>{summarizeReasons(bestWindow, muhurta?.rank_explanation)}</dd>
                </div>
                <div>
                  <dt>Rahu Kalam</dt>
                  <dd>
                    {avoidWindow?.start
                      ? `${safeTime(avoidWindow.start, state.timezone)} - ${safeTime(avoidWindow.end, state.timezone)}`
                      : 'Use normal caution'}
                  </dd>
                </div>
              </dl>
            </article>
          </section>
        </>
      ) : null}
    </section>
  );
}

export default TemporalCompassPage;
