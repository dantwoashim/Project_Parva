import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { buildConsumerTodayViewModel } from '../consumer/consumerViewModels';
import { TodaySection } from '../consumer/ConsumerSections';
import { festivalAPI, muhurtaAPI, temporalAPI } from '../services/api';
import { useTemporalContext } from '../context/useTemporalContext';
import { findPresetByLocation } from '../data/locationPresets';
import { trackEvent } from '../services/analytics';
import { describeSupportError, pickRejectedReason } from '../services/errorFormatting';
import './TemporalCompassPage.css';

export function TemporalCompassPage() {
  const { state, setDate } = useTemporalContext();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [compass, setCompass] = useState(null);
  const [compassMeta, setCompassMeta] = useState(null);
  const [muhurta, setMuhurta] = useState(null);
  const [muhurtaMeta, setMuhurtaMeta] = useState(null);
  const [onDateFestivals, setOnDateFestivals] = useState([]);
  const [upcomingFestivals, setUpcomingFestivals] = useState([]);
  const preset = useMemo(() => findPresetByLocation(state.location), [state.location]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      const [compassResult, muhurtaResult, onDateResult, upcomingResult] = await Promise.allSettled([
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
        festivalAPI.getOnDate(state.date),
        festivalAPI.getUpcoming(120, 'computed'),
      ]);

      if (cancelled) return;

      if (compassResult.status === 'fulfilled') {
        setCompass(compassResult.value.data || null);
        setCompassMeta(compassResult.value.meta || null);
      } else {
        setCompass(null);
        setCompassMeta(null);
      }

      if (muhurtaResult.status === 'fulfilled') {
        setMuhurta(muhurtaResult.value.data || null);
        setMuhurtaMeta(muhurtaResult.value.meta || null);
      } else {
        setMuhurta(null);
        setMuhurtaMeta(null);
      }

      if (onDateResult.status === 'fulfilled') {
        setOnDateFestivals(Array.isArray(onDateResult.value) ? onDateResult.value : []);
      } else {
        setOnDateFestivals([]);
      }

      if (upcomingResult.status === 'fulfilled') {
        setUpcomingFestivals(Array.isArray(upcomingResult.value?.festivals) ? upcomingResult.value.festivals : []);
      } else {
        setUpcomingFestivals([]);
      }

      if (compassResult.status === 'rejected' && muhurtaResult.status === 'rejected') {
        setError(
          describeSupportError(
            pickRejectedReason(compassResult, muhurtaResult),
            'We could not build today\'s live reading right now. Please try again in a moment.',
          ),
        );
      }

      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

  useEffect(() => {
    if (muhurta?.best_window?.start) {
      trackEvent('today_best_window_viewed', {
        date: state.date,
        place: preset?.label || 'custom_place',
      });
    }
  }, [muhurta?.best_window?.start, preset?.label, state.date]);

  const viewModel = useMemo(
    () => buildConsumerTodayViewModel({
      state,
      placeLabel: preset?.label,
      compass,
      compassMeta,
      muhurta,
      muhurtaMeta,
      onDateFestivals,
      upcomingFestivals,
    }),
    [state, preset?.label, compass, compassMeta, muhurta, muhurtaMeta, onDateFestivals, upcomingFestivals],
  );

  if (loading) {
    return (
      <section className="today-page animate-fade-in-up consumer-route consumer-route--overview">
        <div className="today-page__loading">
          <div className="skeleton today-page__hero" />
          <div className="today-page__insights-grid">
            <div className="skeleton today-page__panel" />
            <div className="skeleton today-page__panel" />
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="today-page animate-fade-in-up consumer-route consumer-route--overview">
        <article className="ink-card today-page__error" role="alert">
          <p className="today-page__eyebrow">Today</p>
          <h1 className="text-hero">Today is temporarily unavailable.</h1>
          <p className="today-page__summary">{error}</p>
        </article>
      </section>
    );
  }

  return (
    <section className="today-page animate-fade-in-up consumer-route consumer-route--overview">
      <TodaySection
        id={undefined}
        viewModel={viewModel}
        dateValue={state.date}
        onDateChange={setDate}
        showDateInput={false}
        showEvidence={false}
        bestTimeActionLabel="Open Best Time"
        action={<Link className="btn btn-secondary btn-sm" to="/#best-time">Jump to Best Time on home</Link>}
      />

      <section className="ink-card today-page__route-card">
        <div className="today-page__panel-header">
          <div>
            <p className="today-page__eyebrow">Read further only when you need it</p>
            <h2>The rest of today in one compact pass</h2>
          </div>
          <div className="today-page__panel-actions">
            <span className="today-page__meta-pill">{viewModel.rhythm}</span>
          </div>
        </div>

        <div className="today-page__route-meta">
          <label className="ink-input today-page__date-field">
            <span>Date</span>
            <input type="date" value={state.date} onChange={(event) => setDate(event.target.value)} />
          </label>

          <article className="today-page__meta-card">
            <span className="today-page__label">Place basis</span>
            <strong>{viewModel.placeLabel}</strong>
            <p className="today-page__subsummary">Change the place when the timing answer materially shifts.</p>
          </article>

          <article className="today-page__meta-card">
            <span className="today-page__label">Day tone</span>
            <strong>{viewModel.dayTone.value}</strong>
            <p className="today-page__subsummary">{viewModel.dayTone.note}</p>
          </article>
        </div>

        {viewModel.timeline.length ? (
          <div className="today-page__timeline-grid">
            {viewModel.timeline.map((segment) => (
              <article
                key={segment.id}
                className={`today-page__timeline-segment today-page__timeline-segment--${segment.tone}`.trim()}
              >
                <span className="today-page__label">{segment.title}</span>
                <strong>{segment.time}</strong>
                <p>{segment.note}</p>
              </article>
            ))}
          </div>
        ) : null}

        <details className="today-page__accordion">
          <summary>How this was calculated</summary>
          <div className="today-page__accordion-body">
            <div className="today-page__signal-grid">
              {viewModel.signals.map((item) => (
                <div key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                  <p className="today-page__subsummary">{item.note}</p>
                </div>
              ))}
            </div>
            <EvidenceDrawer {...viewModel.evidence} />
          </div>
        </details>
      </section>

      <div className="today-page__insights-grid">
        <section className="ink-card today-page__panel">
          <div className="today-page__panel-header">
            <div>
              <p className="today-page__eyebrow">What&apos;s active</p>
              <h2>Observances in view</h2>
            </div>
          </div>
          <div className="today-page__festival-list">
            {viewModel.observances.length ? viewModel.observances.map((item) => (
              <Link key={item.id} className="today-page__festival-item" to={`/festivals/${item.id}`}>
                <strong>{item.title}</strong>
                <span>{item.dateLabel}</span>
                <p className="today-page__subsummary">{item.summary}</p>
              </Link>
            )) : (
              <article className="today-page__festival-item">
                <strong>No major observance is active in this view.</strong>
                <span>The day reading still stays useful when the calendar is quiet.</span>
              </article>
            )}
          </div>
        </section>

        <section className="ink-card today-page__panel">
          <div className="today-page__panel-header">
            <div>
              <p className="today-page__eyebrow">Act on it</p>
              <h2>How to use today</h2>
            </div>
          </div>
          <dl className="today-page__timing-notes">
            <div>
              <dt>Lead with</dt>
              <dd>{viewModel.bestWindow.note}</dd>
            </div>
            <div>
              <dt>Keep light</dt>
              <dd>{viewModel.avoidWindow.note}</dd>
            </div>
            <div>
              <dt>Place context</dt>
              <dd>{viewModel.placeLabel} is the current place basis for today&apos;s answer.</dd>
            </div>
          </dl>
        </section>
      </div>
    </section>
  );
}

export default TemporalCompassPage;
