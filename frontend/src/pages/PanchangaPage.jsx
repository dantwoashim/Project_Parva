import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { PANCHANGA_GLOSSARY } from '../data/temporalGlossary';
import { calendarAPI, festivalAPI, glossaryAPI } from '../services/api';
import { useTemporalContext } from '../context/useTemporalContext';
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
            opacity: isWaxing ? 1 : 0.88,
          }}
        />
      </div>
      <span className="moon-phase__label">{isWaxing ? 'Shukla Paksha' : 'Krishna Paksha'}</span>
    </div>
  );
}

function formatDisplayDate(value, timeZone) {
  const parsed = new Date(`${value}T00:00:00`);
  if (Number.isNaN(parsed.valueOf())) return value;

  try {
    return parsed.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timeZone,
    });
  } catch {
    return parsed.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
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
  const confidence = useMemo(() => payload?.panchanga?.confidence || meta?.confidence?.level || 'Computed guidance', [payload, meta]);
  const introLine = useMemo(() => {
    if (!tithi && !vaara) {
      return 'The daily reading appears here with the lunar tone first and deeper mechanics one step lower.';
    }

    return `${tithi?.name || 'Today'} sets the lunar tone${tithi?.paksha ? ` in the ${tithi.paksha} half` : ''}, while ${vaara?.name_english || 'the weekday'} holds the civic rhythm.`;
  }, [tithi, vaara]);
  const displayDate = useMemo(() => formatDisplayDate(state.date, state.timezone), [state.date, state.timezone]);

  return (
    <section className="panchanga-page animate-fade-in-up">
      <header className="panchanga-hero ink-card">
        <div className="panchanga-hero__copy">
          <p className="today-page__eyebrow">Panchanga</p>
          <h1 className="text-hero">{bs ? `${bs.year} ${bs.month_name} ${bs.day}` : 'Daily lunar reading'}</h1>
          <p className="panchanga-hero__date">{displayDate}</p>
          <p className="panchanga-hero__intro">{introLine}</p>
        </div>

        <div className="panchanga-hero__side">
          <label className="panchanga-hero__picker ink-input">
            <span>Date</span>
            <input id="panchanga-date" type="date" value={state.date} onChange={(event) => setDate(event.target.value)} />
          </label>
          {tithi ? <MoonPhase tithi={tithi} /> : null}
        </div>
      </header>

      {loading && (
        <div className="panchanga-loading">
          <div className="skeleton" style={{ minHeight: '180px', borderRadius: '1.4rem' }} />
          <div className="panchanga-cards stagger-children">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="skeleton" style={{ minHeight: '150px', borderRadius: '1.1rem' }} />
            ))}
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
          <section className="panchanga-summary-grid">
            <article className="ink-card panchanga-summary-card">
              <span className="today-page__eyebrow">Lunar tone</span>
              <strong>{tithi?.name || 'Appears when available'}</strong>
              <p>{tithi?.paksha ? `${tithi.paksha} half of the cycle` : 'Lunar phase detail appears when available.'}</p>
            </article>
            <article className="ink-card panchanga-summary-card">
              <span className="today-page__eyebrow">Weekday</span>
              <strong>{vaara?.name_english || 'Appears when available'}</strong>
              <p>{vaara?.name_sanskrit || 'Weekday detail appears when available.'}</p>
            </article>
            <article className="ink-card panchanga-summary-card">
              <span className="today-page__eyebrow">Confidence note</span>
              <strong>{confidence}</strong>
              <p>Method and supporting notes stay below the main answer.</p>
            </article>
          </section>

          {festivals?.length > 0 && (
            <section className="panchanga-festivals animate-fade-in-up">
              <h2 className="panchanga-festivals__title">Festivals on this day</h2>
              <div className="panchanga-festivals__chips">
                {festivals.map((festival) => (
                  <button key={festival.id} className="festival-chip" onClick={() => navigate(`/festivals/${festival.id}`)}>
                    <span className="festival-chip__name">{festival.name}</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          <section className="panchanga-cards stagger-children">
            <article className="ink-card panchanga-card">
              <h3>Tithi</h3>
              <p className="panchanga-card__value">{tithi?.name || 'Appears when available'}</p>
              <p className="panchanga-card__meta">#{tithi?.number || '-'} | {tithi?.paksha || 'Lunar phase detail appears when available.'}</p>
            </article>
            <article className="ink-card panchanga-card">
              <h3>Nakshatra</h3>
              <p className="panchanga-card__value">{nakshatra?.name || 'Appears when available'}</p>
              <p className="panchanga-card__meta">Pada {nakshatra?.pada || '-'}</p>
            </article>
            <article className="ink-card panchanga-card">
              <h3>Yoga</h3>
              <p className="panchanga-card__value">{yoga?.name || 'Appears when available'}</p>
              <p className="panchanga-card__meta">#{yoga?.number || '-'}</p>
            </article>
            <article className="ink-card panchanga-card">
              <h3>Karana</h3>
              <p className="panchanga-card__value">{karana?.name || 'Appears when available'}</p>
              <p className="panchanga-card__meta">#{karana?.number || '-'}</p>
            </article>
            <article className="ink-card panchanga-card">
              <h3>Vaara</h3>
              <p className="panchanga-card__value">{vaara?.name_english || 'Appears when available'}</p>
              <p className="panchanga-card__meta">{vaara?.name_sanskrit || 'Weekday detail appears when available.'}</p>
            </article>
          </section>

          <KnowledgePanel title={knowledge.title} intro={knowledge.intro} sections={knowledge.sections} className="panchanga-knowledge" />

          <section className="ink-card panchanga-details-card">
            <div className="panchanga-details-card__header">
              <div>
                <p className="today-page__eyebrow">Method available</p>
                <h2>Inspect the daily reading only when you want to go deeper.</h2>
              </div>
              <EvidenceDrawer
                title="Panchanga"
                intro="This drawer keeps place, date, confidence, and method context nearby without forcing the page into an expert mode."
                methodRef={tithi?.method || meta?.method || 'Panchanga daily profile'}
                confidenceNote={confidence}
                placeUsed={state.timezone}
                computedForDate={state.date}
                availability={[
                  { label: 'Daily panchanga', available: Boolean(payload?.panchanga), note: 'The summary cards only appear when the daily reading is present.' },
                  { label: 'Festival context', available: Boolean(festivals?.length), note: 'Festival chips only appear when the on-date service returns observances.' },
                  { label: 'Glossary guidance', available: Boolean(knowledge?.sections?.length), note: 'Glossary sections stay available as a secondary learning surface.' },
                ]}
                meta={meta}
                traceFallbackId={payload?.calculation_trace_id}
              />
            </div>
            <p><strong>Confidence note:</strong> {confidence}</p>
            <p><strong>Method profile:</strong> {tithi?.method || meta?.method || 'Panchanga daily profile'}</p>
          </section>
        </>
      )}
    </section>
  );
}

export default PanchangaPage;
