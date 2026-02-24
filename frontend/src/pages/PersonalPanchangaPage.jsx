import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import { PANCHANGA_GLOSSARY, PERSONAL_PANCHANGA_GLOSSARY } from '../data/temporalGlossary';
import { festivalAPI, personalAPI } from '../services/api';
import { useTemporalContext } from '../context/TemporalContext';
import './PersonalPanchangaPage.css';

function parseTimeMinutes(iso) {
  if (!iso) return null;
  try {
    const d = new Date(iso);
    return d.getHours() * 60 + d.getMinutes();
  } catch {
    return null;
  }
}

export function PersonalPanchangaPage() {
  const navigate = useNavigate();
  const {
    state,
    setDate,
    setLocation,
    setTimezone,
  } = useTemporalContext();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [festivals, setFestivals] = useState([]);

  const load = async () => {
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
      setPayload(envelope.data);
      setMeta(envelope.meta);
      setFestivals(Array.isArray(festivalsData) ? festivalsData : []);
    } catch (err) {
      setPayload(null);
      setMeta(null);
      setFestivals([]);
      setError(err.message || 'Failed to load personal panchanga');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

  const bs = payload?.bikram_sambat;

  const sunriseDelta = useMemo(() => {
    const localMinutes = parseTimeMinutes(payload?.local_sunrise);
    const kathmanduMinutes = parseTimeMinutes(payload?.sunrise);
    if (localMinutes === null || kathmanduMinutes === null) return null;
    const delta = localMinutes - kathmanduMinutes;
    if (delta === 0) return '0 min';
    const sign = delta > 0 ? '+' : '-';
    return `${sign}${Math.abs(delta)} min`;
  }, [payload]);

  return (
    <section className="personal-page animate-fade-in-up">
      <form className="personal-inputs ink-card" onSubmit={(e) => { e.preventDefault(); load(); }}>
        <label className="ink-input">
          <span>Date</span>
          <input type="date" value={state.date} onChange={(e) => setDate(e.target.value)} required />
        </label>
        <label className="ink-input">
          <span>Latitude</span>
          <input value={state.location?.latitude ?? ''} onChange={(e) => setLocation({ latitude: Number(e.target.value) || 0 })} />
        </label>
        <label className="ink-input">
          <span>Longitude</span>
          <input value={state.location?.longitude ?? ''} onChange={(e) => setLocation({ longitude: Number(e.target.value) || 0 })} />
        </label>
        <label className="ink-input">
          <span>Timezone</span>
          <input value={state.timezone} onChange={(e) => setTimezone(e.target.value)} />
        </label>
        <button type="submit" className="btn btn-primary personal-submit">Compute</button>
      </form>

      {loading && (
        <div className="personal-loading">
          <div className="skeleton" style={{ height: '80px', borderRadius: '16px' }} />
          <div className="personal-cards-grid">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton" style={{ height: '140px', borderRadius: '16px' }} />)}</div>
        </div>
      )}

      {!loading && error && <div className="ink-card personal-error" role="alert"><h3>Unable to load</h3><p>{error}</p></div>}

      {!loading && !error && payload && (
        <>
          <header className="personal-hero">
            <div>
              {bs && <h1 className="text-hero">{bs.year} {bs.month_name} {bs.day}</h1>}
              <p className="personal-hero__sub">{payload.location?.timezone || state.timezone} · {payload.location?.latitude}°N, {payload.location?.longitude}°E</p>
              <p className="personal-hero__delta">Local sunrise delta vs Kathmandu baseline: {sunriseDelta || 'N/A'}</p>
            </div>
          </header>

          {festivals?.length > 0 && (
            <section className="personal-festivals animate-fade-in-up">
              <h2 className="personal-festivals__title">Festivals on this day</h2>
              <div className="personal-festivals__chips">
                {festivals.map((f) => (
                  <button key={f.id} className="festival-chip" onClick={() => navigate(`/festivals/${f.id}`)}>
                    <span className="festival-chip__name">{f.name}</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          <section className="personal-cards-grid stagger-children">
            <article className="ink-card ink-card--vermillion panchanga-card"><h3>Tithi</h3><p className="panchanga-card__value">{payload.tithi?.name || '—'}</p><p className="panchanga-card__meta">#{payload.tithi?.number} · {payload.tithi?.paksha}</p></article>
            <article className="ink-card ink-card--saffron panchanga-card"><h3>Nakshatra</h3><p className="panchanga-card__value">{payload.nakshatra?.name || '—'}</p><p className="panchanga-card__meta">#{payload.nakshatra?.number}</p></article>
            <article className="ink-card ink-card--gold panchanga-card"><h3>Yoga</h3><p className="panchanga-card__value">{payload.yoga?.name || '—'}</p><p className="panchanga-card__meta">#{payload.yoga?.number}</p></article>
            <article className="ink-card ink-card--jade panchanga-card"><h3>Karana</h3><p className="panchanga-card__value">{payload.karana?.name || '—'}</p><p className="panchanga-card__meta">#{payload.karana?.number}</p></article>
            <article className="ink-card ink-card--amber panchanga-card"><h3>Vaara</h3><p className="panchanga-card__value">{payload.vaara?.name_english || '—'}</p><p className="panchanga-card__meta">{payload.vaara?.name_sanskrit}</p></article>
          </section>

          <KnowledgePanel
            title={PERSONAL_PANCHANGA_GLOSSARY.title}
            intro={PERSONAL_PANCHANGA_GLOSSARY.intro}
            sections={[...PERSONAL_PANCHANGA_GLOSSARY.sections, ...PANCHANGA_GLOSSARY.sections.slice(0, 1)]}
            className="personal-knowledge"
          />

          {state.mode === 'authority' && (
            <AuthorityInspector title="Personal Panchanga Authority" meta={meta} traceFallbackId={payload?.calculation_trace_id} />
          )}
        </>
      )}
    </section>
  );
}

export default PersonalPanchangaPage;
