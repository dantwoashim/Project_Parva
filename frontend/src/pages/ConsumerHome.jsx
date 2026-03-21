import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { buildConsumerTodayViewModel } from '../consumer/consumerViewModels';
import { findPresetByLocation } from '../data/locationPresets';
import { useTemporalContext } from '../context/useTemporalContext';
import { festivalAPI, muhurtaAPI, temporalAPI } from '../services/api';
import { describeSupportError, pickRejectedReason } from '../services/errorFormatting';
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [todayViewModel, setTodayViewModel] = useState(null);
  const [upcomingFestivals, setUpcomingFestivals] = useState([]);

  useEffect(() => {
    let cancelled = false;

    async function loadHome() {
      setLoading(true);
      setError(null);

      const placeLabel = activePreset?.label || 'Kathmandu';
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
        festivalAPI.getUpcoming(6, 'computed'),
      ]);

      if (cancelled) return;

      const compassEnvelope = compassResult.status === 'fulfilled' ? compassResult.value : null;
      const muhurtaEnvelope = muhurtaResult.status === 'fulfilled' ? muhurtaResult.value : null;
      const onDateFestivals = onDateResult.status === 'fulfilled' && Array.isArray(onDateResult.value) ? onDateResult.value : [];
      const upcomingPayload = upcomingResult.status === 'fulfilled' ? upcomingResult.value : null;
      const upcoming = Array.isArray(upcomingPayload?.festivals) ? upcomingPayload.festivals : [];

      setTodayViewModel(
        buildConsumerTodayViewModel({
          state,
          placeLabel,
          compass: compassEnvelope?.data || null,
          compassMeta: compassEnvelope?.meta || null,
          muhurta: muhurtaEnvelope?.data || null,
          muhurtaMeta: muhurtaEnvelope?.meta || null,
          onDateFestivals,
          upcomingFestivals: upcoming,
        }),
      );
      setUpcomingFestivals(upcoming.slice(0, 3));
      setError(
        !compassEnvelope && !muhurtaEnvelope
          ? describeSupportError(
              pickRejectedReason(compassResult, muhurtaResult),
              'Home guidance is temporarily unavailable.',
            )
          : null,
      );
      setLoading(false);
    }

    loadHome();
    return () => {
      cancelled = true;
    };
  }, [activePreset?.label, state, state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

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
                <p>
                  {signal.label}
                  <span className="text-nepali">
                    {signal.label === 'Nakshatra' ? 'नक्षत्र' : signal.label === 'Yoga' ? 'योग' : signal.label === 'Karana' ? 'करण' : 'तिथि'}
                  </span>
                </p>
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
              <strong>{todayViewModel.sunrise || 'Pending'}</strong>
            </div>
            <div>
              <span className="almanac-home__glimpse-icon"><span className="material-symbols-outlined" style={{ color: '#9c3f00' }}>wb_sunny</span>Sunset</span>
              <strong>{todayViewModel.sunset || 'Pending'}</strong>
            </div>
            <div className="is-warning">
              <span className="almanac-home__glimpse-icon"><span className="material-symbols-outlined" style={{ color: '#ba1a1a' }}>warning</span>Rahu Kaal</span>
              <strong>{todayViewModel.avoidWindow?.value || 'Pending'}</strong>
            </div>
            <div>
              <span className="almanac-home__glimpse-icon"><span className="material-symbols-outlined" style={{ color: '#595f66' }}>schedule</span>Gulika Kaal</span>
              <strong>{todayViewModel.bestWindow?.value || 'Pending'}</strong>
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
          {upcomingFestivals.length ? upcomingFestivals.map((festival) => (
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
        <img
          className="almanac-home__banner-img"
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuDRA3vB7U5NjLNm3WAGSamnpazqNxiQknPYlR7IX0PvVUzNqJDs9-vSvc12vTuu7ucRD5HX0UEOHBOjbsCLJd0ULtinx-pxmNu9LRsIIoO0EQY1ef7LTK5Qm5tWUDUt4D3wqnS0b0deP-PN_ljEGo412B74cRBbwUdueWv6cOTluwxr5pMlRUIF7IGKyb7ndUHt95cEOEPV4D_ToDtEhfAzpGwJgb3PuaVa5zXT8A5_n_814H8RifKuP2IKKKbUDmVJ9W47DaUIt9NQ"
          alt="Serene Himalayan landscape with soft morning light"
        />
        <div className="almanac-home__banner-overlay" />
        <div className="almanac-home__banner-copy">
          <p className="almanac-home__eyebrow">Space for Reflection</p>
          <h2>Embrace the Divine Rhythm</h2>
        </div>
      </section>
    </section>
  );
}

export default ConsumerHome;
