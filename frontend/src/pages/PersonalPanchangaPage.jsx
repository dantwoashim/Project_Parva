import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { PANCHANGA_GLOSSARY, PERSONAL_PANCHANGA_GLOSSARY } from '../data/temporalGlossary';
import { festivalAPI, personalAPI } from '../services/api';
import { useTemporalContext } from '../context/useTemporalContext';
import { useMemberContext } from '../context/useMemberContext';
import { LOCATION_PRESETS, findPresetByLocation } from '../data/locationPresets';
import './PersonalPanchangaPage.css';

function parseTimeMinutes(iso) {
  if (!iso) return null;
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.valueOf())) return null;
  return parsed.getHours() * 60 + parsed.getMinutes();
}

function safeTime(iso, fallback = 'Time unavailable') {
  if (!iso) return fallback;
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.valueOf())) return fallback;
  return parsed.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

export function PersonalPanchangaPage() {
  const navigate = useNavigate();
  const { state, setDate, setLocation, setTimezone } = useTemporalContext();
  const { savePlace } = useMemberContext();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [festivals, setFestivals] = useState([]);
  const [deviceStatus, setDeviceStatus] = useState('');

  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);

  const applyPreset = (presetId) => {
    const preset = LOCATION_PRESETS.find((item) => item.id === presetId);
    if (!preset) return;
    setLocation({ latitude: preset.latitude, longitude: preset.longitude });
    setTimezone(preset.timezone);
  };

  const useDeviceLocation = () => {
    if (!navigator.geolocation) {
      setDeviceStatus('Device location is unavailable here.');
      return;
    }

    setDeviceStatus('Checking your device location...');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: Number(position.coords.latitude.toFixed(4)),
          longitude: Number(position.coords.longitude.toFixed(4)),
        });
        try {
          const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
          if (tz) setTimezone(tz);
        } catch {
          // Ignore timezone detection issues.
        }
        setDeviceStatus('Device location applied.');
      },
      () => {
        setDeviceStatus('We could not read your device location.');
      },
      { maximumAge: 600000, timeout: 4000 },
    );
  };

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [envelope, festivalsData] = await Promise.all([
          personalAPI.getPanchangaEnvelope({
            date: state.date,
            lat: state.location?.latitude,
            lon: state.location?.longitude,
            tz: state.timezone,
          }),
          festivalAPI.getOnDate(state.date).catch(() => []),
        ]);
        if (!cancelled) {
          setPayload(envelope.data);
          setMeta(envelope.meta);
          setFestivals(Array.isArray(festivalsData) ? festivalsData : []);
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setMeta(null);
          setFestivals([]);
          setError(err.message || 'Failed to load personal place guidance');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

  const bs = payload?.bikram_sambat;
  const sunriseDelta = useMemo(() => {
    const localMinutes = parseTimeMinutes(payload?.local_sunrise);
    const kathmanduMinutes = parseTimeMinutes(payload?.sunrise);
    if (localMinutes === null || kathmanduMinutes === null) return null;
    const delta = localMinutes - kathmanduMinutes;
    if (delta === 0) return 'Same as Kathmandu';
    return `${delta > 0 ? '+' : '-'}${Math.abs(delta)} min vs Kathmandu`;
  }, [payload]);

  return (
    <section className="personal-page animate-fade-in-up">
      <header className="personal-page__hero ink-card">
        <div className="personal-page__hero-copy">
          <p className="today-page__eyebrow">My Place</p>
          <h1 className="text-hero">See how the day shifts for your place.</h1>
          <p className="personal-page__intro">
            Start with a city or your device location. Advanced coordinates stay tucked away in More options.
          </p>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => savePlace({
              label: activePreset?.label || 'My place',
              latitude: state.location?.latitude,
              longitude: state.location?.longitude,
              timezone: state.timezone,
            })}
          >
            Save this place
          </button>
        </div>

        <form className="personal-page__controls" onSubmit={(event) => event.preventDefault()}>
          <label className="ink-input">
            <span>Date</span>
            <input type="date" value={state.date} onChange={(event) => setDate(event.target.value)} required />
          </label>
          <label className="ink-input">
            <span>Place</span>
            <select value={activePreset?.id || ''} onChange={(event) => applyPreset(event.target.value)}>
              <option value="">Choose a city preset</option>
              {LOCATION_PRESETS.map((preset) => (
                <option key={preset.id} value={preset.id}>{preset.label}</option>
              ))}
            </select>
          </label>
          <button type="button" className="btn btn-secondary" onClick={useDeviceLocation}>Use my device</button>
          {deviceStatus ? <p className="personal-page__status">{deviceStatus}</p> : null}
        </form>
      </header>

      {loading ? (
        <div className="personal-loading">
          <div className="skeleton" style={{ minHeight: '220px', borderRadius: '1.4rem' }} />
          <div className="personal-cards-grid">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="skeleton" style={{ minHeight: '140px', borderRadius: '1.2rem' }} />
            ))}
          </div>
        </div>
      ) : null}

      {!loading && error ? (
        <div className="ink-card personal-error" role="alert">
          <h2>My Place guidance is unavailable right now</h2>
          <p>{error}</p>
        </div>
      ) : null}

      {!loading && !error && payload ? (
        <>
          <section className="personal-summary-grid">
            <article className="ink-card personal-summary-card">
              <span className="today-page__eyebrow">Date</span>
              <strong>{bs ? `${bs.year} ${bs.month_name} ${bs.day}` : state.date}</strong>
              <p>{activePreset?.label || payload.location?.timezone || state.timezone}</p>
            </article>
            <article className="ink-card personal-summary-card">
              <span className="today-page__eyebrow">Local sunrise</span>
              <strong>{safeTime(payload.local_sunrise)}</strong>
              <p>Compared against Kathmandu timing for the same day.</p>
            </article>
            <article className="ink-card personal-summary-card">
              <span className="today-page__eyebrow">What changes here</span>
              <strong>{sunriseDelta || 'No sunrise shift available yet'}</strong>
              <p>Useful when the day starts materially earlier or later for your place.</p>
            </article>
          </section>

          {festivals?.length > 0 ? (
            <section className="personal-festivals animate-fade-in-up">
              <h2 className="personal-festivals__title">Festivals on this day</h2>
              <div className="personal-festivals__chips">
                {festivals.map((festival) => (
                  <button key={festival.id} className="festival-chip" onClick={() => navigate(`/festivals/${festival.id}`)}>
                    <span className="festival-chip__name">{festival.name}</span>
                  </button>
                ))}
              </div>
            </section>
          ) : null}

          <section className="personal-cards-grid stagger-children">
            <article className="ink-card ink-card--vermillion panchanga-card"><h3>Tithi</h3><p className="panchanga-card__value">{payload.tithi?.name || 'Pending'}</p><p className="panchanga-card__meta">{payload.tithi?.paksha || 'Lunar phase pending'}</p></article>
            <article className="ink-card ink-card--saffron panchanga-card"><h3>Nakshatra</h3><p className="panchanga-card__value">{payload.nakshatra?.name || 'Pending'}</p><p className="panchanga-card__meta">Number {payload.nakshatra?.number || '-'}</p></article>
            <article className="ink-card ink-card--gold panchanga-card"><h3>Yoga</h3><p className="panchanga-card__value">{payload.yoga?.name || 'Pending'}</p><p className="panchanga-card__meta">Number {payload.yoga?.number || '-'}</p></article>
            <article className="ink-card ink-card--jade panchanga-card"><h3>Karana</h3><p className="panchanga-card__value">{payload.karana?.name || 'Pending'}</p><p className="panchanga-card__meta">Number {payload.karana?.number || '-'}</p></article>
            <article className="ink-card ink-card--amber panchanga-card"><h3>Weekday</h3><p className="panchanga-card__value">{payload.vaara?.name_english || 'Pending'}</p><p className="panchanga-card__meta">{payload.vaara?.name_sanskrit || ''}</p></article>
          </section>

          <EvidenceDrawer
            title="My Place"
            intro="This drawer shows the place used, timing basis, and how much personal timing context was available for the selected day."
            methodRef={meta?.method || payload?.method_profile || 'Personal place profile'}
            confidenceNote={meta?.confidence?.level || meta?.confidence || payload?.quality_band || 'Public guidance'}
            placeUsed={activePreset?.label || state.timezone}
            computedForDate={state.date}
            availability={[
              { label: 'Local sunrise', available: Boolean(payload?.local_sunrise), note: 'Sunrise shifts are shown only when both local and Kathmandu comparison values are available.' },
              { label: 'Festival overlap', available: Boolean(festivals?.length), note: 'Same-day observances appear when the selected date intersects current festival coverage.' },
              { label: 'Signal set', available: Boolean(payload?.tithi?.name || payload?.nakshatra?.name), note: 'Tithi, nakshatra, yoga, and karana are grouped into one place-aware reading.' },
            ]}
            meta={meta}
            traceFallbackId={payload?.calculation_trace_id}
          />

          <KnowledgePanel
            title={PERSONAL_PANCHANGA_GLOSSARY.title}
            intro={PERSONAL_PANCHANGA_GLOSSARY.intro}
            sections={[...PERSONAL_PANCHANGA_GLOSSARY.sections, ...PANCHANGA_GLOSSARY.sections.slice(0, 1)]}
            className="personal-knowledge"
          />
        </>
      ) : null}
    </section>
  );
}

export default PersonalPanchangaPage;
