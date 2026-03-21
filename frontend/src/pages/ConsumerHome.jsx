import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { buildConsumerTodayViewModel } from '../consumer/consumerViewModels';
import { findPresetByLocation } from '../data/locationPresets';
import { useTemporalContext } from '../context/useTemporalContext';
import { useTodayBundle } from '../hooks/useTodayBundle';
import { formatProductDate } from '../utils/productDateTime';
import './ConsumerHome.css';

function splitPrimaryTitle(value) {
  const parts = String(value || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) {
    return ['Sacred', 'Alignment'];
  }
  if (parts.length === 1) {
    return [parts[0], ''];
  }
  return [parts.slice(0, -1).join(' '), parts.at(-1)];
}

function formatFestivalSummary(item) {
  return item?.summary || 'Open the observance for the story, timing, and household rhythm.';
}

export function ConsumerHome() {
  const { state } = useTemporalContext();
  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const {
    loading,
    error,
    compass,
    compassMeta,
    muhurta,
    muhurtaMeta,
    onDateFestivals,
    upcomingFestivals,
  } = useTodayBundle({
    date: state.date,
    latitude: state.location?.latitude,
    longitude: state.location?.longitude,
    timezone: state.timezone,
    upcomingDays: 6,
    fallbackErrorMessage: 'Home guidance is temporarily unavailable.',
  });

  const todayViewModel = useMemo(
    () => buildConsumerTodayViewModel({
      state,
      placeLabel: activePreset?.label || 'Kathmandu',
      compass,
      compassMeta,
      muhurta,
      muhurtaMeta,
      onDateFestivals,
      upcomingFestivals,
    }),
    [
      activePreset?.label,
      compass,
      compassMeta,
      muhurta,
      muhurtaMeta,
      onDateFestivals,
      state,
      upcomingFestivals,
    ],
  );
  const [titleLineOne, titleLineTwo] = splitPrimaryTitle(
    todayViewModel?.signals?.[0]?.value || todayViewModel?.headline || 'Sacred Alignment',
  );

  if (loading) {
    return (
      <section className="almanac-home consumer-route consumer-route--overview animate-fade-in-up">
        <div className="skeleton almanac-home__hero-skeleton" />
        <div className="almanac-home__festival-grid">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="skeleton almanac-home__festival-skeleton" />
          ))}
        </div>
        <div className="skeleton almanac-home__banner-skeleton" />
      </section>
    );
  }

  if (error || !todayViewModel) {
    return (
      <section className="almanac-home consumer-route consumer-route--overview animate-fade-in-up">
        <article className="almanac-home__error ink-card" role="alert">
          <p className="almanac-home__eyebrow">Home</p>
          <h1>Sacred guidance is temporarily unavailable.</h1>
          <p>{error || 'The editorial landing view could not be assembled from the live calendar payload.'}</p>
        </article>
      </section>
    );
  }

  return (
    <section className="almanac-home consumer-route consumer-route--overview animate-fade-in-up">
      <header className="almanac-home__hero">
        <article className="almanac-home__alignment glass-panel">
          <div className="almanac-home__alignment-head">
            <div>
              <p className="almanac-home__eyebrow">Today&apos;s Alignment</p>
              <h1>
                <span>{titleLineOne}</span>
                {titleLineTwo ? <span>{titleLineTwo}</span> : null}
              </h1>
            </div>
            <div className="almanac-home__lunar-mark">
              <span className="material-symbols-outlined">brightness_3</span>
              <p>{todayViewModel.signals?.[0]?.label || 'Tithi'}</p>
            </div>
          </div>

          <div className="almanac-home__signal-grid">
            {todayViewModel.signals.slice(0, 4).map((signal) => (
              <article key={signal.label}>
                <p>{signal.label}</p>
                <strong>{signal.value}</strong>
              </article>
            ))}
          </div>

          <div className="almanac-home__alignment-foot">
            <div className="almanac-home__date-mark">
              <strong>{formatProductDate(state.date, { day: 'numeric' }, state)}</strong>
              <span>{formatProductDate(state.date, { month: 'long', year: 'numeric' }, state)}</span>
            </div>
            <div className="almanac-home__calendar-note">
              <span>{todayViewModel.bsDate}</span>
              <strong>{activePreset?.label || todayViewModel.placeLabel}</strong>
            </div>
          </div>
        </article>

        <aside className="almanac-home__glimpse">
          <div className="almanac-home__glimpse-head">
            <h2>Daily Glimpse</h2>
          </div>
          <div className="almanac-home__glimpse-list">
            <div>
              <span className="almanac-home__glimpse-icon"><span className="material-symbols-outlined" style={{ color: '#735c00' }}>wb_twilight</span>Sunrise</span>
              <strong>{todayViewModel.sunrise || 'Unavailable'}</strong>
            </div>
            <div>
              <span className="almanac-home__glimpse-icon"><span className="material-symbols-outlined" style={{ color: '#9c3f00' }}>wb_sunny</span>Sunset</span>
              <strong>{todayViewModel.sunset || 'Unavailable'}</strong>
            </div>
            <div className="is-warning">
              <span className="almanac-home__glimpse-icon"><span className="material-symbols-outlined" style={{ color: '#ba1a1a' }}>warning</span>Rahu Kaal</span>
              <strong>{todayViewModel.avoidWindow?.value || 'Unavailable'}</strong>
            </div>
            <div>
              <span className="almanac-home__glimpse-icon"><span className="material-symbols-outlined" style={{ color: '#595f66' }}>schedule</span>Gulika Kaal</span>
              <strong>{todayViewModel.bestWindow?.value || 'Unavailable'}</strong>
            </div>
          </div>
          <blockquote className="almanac-home__quote">
            <p>{todayViewModel.summary}</p>
            <cite>Parva daily reading</cite>
          </blockquote>
        </aside>
      </header>

      <section className="almanac-home__festivals">
        <div className="almanac-home__section-row">
          <h2>Upcoming Festivals</h2>
          <Link to="/festivals">View Full Calendar</Link>
        </div>
        <div className="almanac-home__festival-grid">
          {upcomingFestivals.length ? upcomingFestivals.slice(0, 3).map((festival) => (
            <Link key={festival.id} to={`/festivals/${festival.id}`} className="almanac-home__festival-card">
              <span>{formatProductDate(festival.start_date || festival.start, { month: 'short', day: 'numeric' }, state)}</span>
              <h3>{festival.display_name || festival.name}</h3>
              <p>{formatFestivalSummary(festival)}</p>
            </Link>
          )) : (
            <article className="almanac-home__festival-card">
              <span>Upcoming</span>
              <h3>Festival dates are loading</h3>
              <p>The next observances will appear here as soon as the calendar feed returns.</p>
            </article>
          )}
        </div>
      </section>

      <section className="almanac-home__banner">
        <div className="almanac-home__banner-art" aria-hidden="true">
          <span className="almanac-home__banner-orb almanac-home__banner-orb--sun" />
          <span className="almanac-home__banner-orb almanac-home__banner-orb--moon" />
          <span className="almanac-home__banner-ridge almanac-home__banner-ridge--far" />
          <span className="almanac-home__banner-ridge almanac-home__banner-ridge--mid" />
          <span className="almanac-home__banner-ridge almanac-home__banner-ridge--near" />
        </div>
        <div className="almanac-home__banner-overlay" />
        <div className="almanac-home__banner-copy">
          <p className="almanac-home__eyebrow">Space for Reflection</p>
          <h2>Embrace the Divine Rhythm</h2>
          <p>Let the answer arrive first, then open the deeper method only when you want the full reasoning.</p>
        </div>
      </section>
    </section>
  );
}

export default ConsumerHome;
