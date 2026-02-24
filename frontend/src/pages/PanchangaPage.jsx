import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import { PANCHANGA_GLOSSARY } from '../data/temporalGlossary';
import { calendarAPI, festivalAPI, glossaryAPI } from '../services/api';
import { useTemporalContext } from '../context/TemporalContext';
import './PanchangaPage.css';

function toKnowledge(content, fallback) {
  if (!content?.sections) return fallback;
  return {
    title: content.title || fallback.title,
    intro: content.intro || fallback.intro,
    sections: (content.sections || []).map((section) => ({
      id: section.id,
      title: section.title,
      description: section.description,
      terms: (section.terms || []).map((term) => ({
        name: term.name,
        meaning: term.meaning,
        whyItMatters: term.why_it_matters || term.whyItMatters,
      })),
    })),
  };
}

function MoonPhase({ tithi }) {
  const number = tithi?.number || 1;
  const phase = number <= 15 ? number / 15 : (30 - number) / 15;
  const isWaxing = number <= 15;

  return (
    <div className="moon-phase" aria-label="Lunar phase view">
      <div className="moon-phase__orb">
        <div
          className="moon-phase__shadow"
          style={{
            clipPath: phase < 0.5
              ? `inset(0 0 0 ${(1 - phase * 2) * 100}%)`
              : `inset(0 ${(phase * 2 - 1) * 100}% 0 0)`,
            opacity: isWaxing ? 1 : 0.85,
          }}
        />
      </div>
      <span className="moon-phase__label">{isWaxing ? 'Shukla' : 'Krishna'} Paksha</span>
    </div>
  );
}

export function PanchangaPage() {
  const navigate = useNavigate();
  const { state, setDate } = useTemporalContext();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [festivals, setFestivals] = useState([]);
  const [knowledge, setKnowledge] = useState(PANCHANGA_GLOSSARY);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [panchangaEnvelope, resolveEnvelope, festivalsData, glossary] = await Promise.all([
          calendarAPI.getPanchangaEnvelope(state.date),
          calendarAPI.getResolveEnvelope(state.date, { include_trace: 'true' }),
          festivalAPI.getOnDate(state.date).catch(() => []),
          glossaryAPI.get({ domain: 'panchanga', lang: state.language }).catch(() => null),
        ]);
        if (!cancelled) {
          setPayload(panchangaEnvelope.data);
          setMeta(panchangaEnvelope.meta || resolveEnvelope?.meta || null);
          setFestivals(Array.isArray(festivalsData) ? festivalsData : []);
          setKnowledge(toKnowledge(glossary?.content, PANCHANGA_GLOSSARY));
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setMeta(null);
          setFestivals([]);
          setError(err.message || 'Failed to load panchanga');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [state.date, state.language]);

  const tithi = payload?.panchanga?.tithi;
  const nakshatra = payload?.panchanga?.nakshatra;
  const yoga = payload?.panchanga?.yoga;
  const karana = payload?.panchanga?.karana;
  const vaara = payload?.panchanga?.vaara;
  const bs = payload?.bikram_sambat;

  const confidence = useMemo(() => payload?.panchanga?.confidence || meta?.confidence?.level || 'computed', [payload, meta]);

  return (
    <section className="panchanga-page animate-fade-in-up">
      <header className="panchanga-hero">
        <div className="panchanga-hero__left">
          {bs && <h1 className="text-hero">{bs.year} {bs.month_name} {bs.day}</h1>}
          <p className="panchanga-hero__date">
            {new Date(`${state.date}T00:00:00`).toLocaleDateString('en-US', {
              weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
            })}
          </p>
          <label className="panchanga-hero__picker ink-input">
            <span>Date</span>
            <input id="panchanga-date" type="date" value={state.date} onChange={(e) => setDate(e.target.value)} />
          </label>
        </div>
        <div className="panchanga-hero__right">{tithi && <MoonPhase tithi={tithi} />}</div>
      </header>

      {loading && (
        <div className="panchanga-loading">
          <div className="skeleton" style={{ height: '120px', borderRadius: '16px' }} />
          <div className="panchanga-cards stagger-children">
            {Array.from({ length: 5 }).map((_, i) => <div key={i} className="skeleton" style={{ height: '140px', borderRadius: '16px' }} />)}
          </div>
        </div>
      )}

      {!loading && error && (
        <div className="ink-card panchanga-error" role="alert">
          <h3>Unable to load panchanga</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && payload && (
        <>
          {festivals?.length > 0 && (
            <section className="panchanga-festivals animate-fade-in-up">
              <h2 className="panchanga-festivals__title">Festivals on this day</h2>
              <div className="panchanga-festivals__chips">
                {festivals.map((f) => (
                  <button key={f.id} className="festival-chip" onClick={() => navigate(`/festivals/${f.id}`)}>
                    <span className="festival-chip__name">{f.name}</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          <section className="panchanga-cards stagger-children">
            <article className="ink-card ink-card--vermillion panchanga-card"><h3>Tithi</h3><p className="panchanga-card__value">{tithi?.name || '—'}</p><p className="panchanga-card__meta">#{tithi?.number} · {tithi?.paksha}</p></article>
            <article className="ink-card ink-card--saffron panchanga-card"><h3>Nakshatra</h3><p className="panchanga-card__value">{nakshatra?.name || '—'}</p><p className="panchanga-card__meta">Pada {nakshatra?.pada || '—'}</p></article>
            <article className="ink-card ink-card--gold panchanga-card"><h3>Yoga</h3><p className="panchanga-card__value">{yoga?.name || '—'}</p><p className="panchanga-card__meta">#{yoga?.number || '—'}</p></article>
            <article className="ink-card ink-card--jade panchanga-card"><h3>Karana</h3><p className="panchanga-card__value">{karana?.name || '—'}</p><p className="panchanga-card__meta">#{karana?.number || '—'}</p></article>
            <article className="ink-card ink-card--amber panchanga-card"><h3>Vaara</h3><p className="panchanga-card__value">{vaara?.name_english || '—'}</p><p className="panchanga-card__meta">{vaara?.name_sanskrit || '—'}</p></article>
          </section>

          <KnowledgePanel title={knowledge.title} intro={knowledge.intro} sections={knowledge.sections} className="panchanga-knowledge" />

          {state.mode === 'authority' && (
            <AuthorityInspector title="Panchanga Authority" meta={meta} traceFallbackId={payload?.calculation_trace_id} />
          )}

          <section className="ink-card panchanga-details-card">
            <p><strong>Confidence:</strong> {confidence}</p>
            <p><strong>Tithi Method:</strong> {tithi?.method || 'ephemeris_udaya'}</p>
          </section>
        </>
      )}
    </section>
  );
}

export default PanchangaPage;
