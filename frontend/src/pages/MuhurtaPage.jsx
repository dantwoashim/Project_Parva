import { useEffect, useMemo, useState } from 'react';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import { MuhurtaHeatmap } from '../components/MuhurtaHeatmap/MuhurtaHeatmap';
import { MUHURTA_GLOSSARY } from '../data/temporalGlossary';
import { glossaryAPI, muhurtaAPI } from '../services/api';
import { useTemporalContext } from '../context/TemporalContext';
import './MuhurtaPage.css';

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

export function MuhurtaPage() {
  const {
    state,
    setDate,
    setLocation,
    setTimezone,
  } = useTemporalContext();

  const [type, setType] = useState('general');
  const [assumptionSet, setAssumptionSet] = useState('np-mainstream-v2');
  const [selectedBlock, setSelectedBlock] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [knowledge, setKnowledge] = useState(MUHURTA_GLOSSARY);

  useEffect(() => {
    if (!navigator.geolocation) return;
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
          // Ignore timezone detection errors.
        }
      },
      () => {
        // Consent denied or unavailable; keep existing context defaults.
      },
      { maximumAge: 600000, timeout: 3500 },
    );
  }, [setLocation, setTimezone]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [envelope, glossary] = await Promise.all([
          muhurtaAPI.getHeatmapEnvelope({
            date: state.date,
            lat: state.location?.latitude,
            lon: state.location?.longitude,
            tz: state.timezone,
            type,
            assumptionSet,
          }),
          glossaryAPI.get({ domain: 'muhurta', lang: state.language }).catch(() => null),
        ]);

        if (!cancelled) {
          setPayload(envelope.data);
          setMeta(envelope.meta);
          setSelectedBlock(envelope.data?.best_window || null);
          setKnowledge(toKnowledge(glossary?.content, MUHURTA_GLOSSARY));
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setMeta(null);
          setSelectedBlock(null);
          setError(err.message || 'Failed to load muhurta heatmap');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone, state.language, type, assumptionSet]);

  const selectedReasons = useMemo(() => {
    if (!selectedBlock?.reason_codes) return '—';
    return selectedBlock.reason_codes.join(' · ');
  }, [selectedBlock]);

  return (
    <section className="muhurta-page animate-fade-in-up">
      <form className="muhurta-controls ink-card" onSubmit={(e) => e.preventDefault()}>
        <label className="ink-input">
          <span>Date</span>
          <input type="date" value={state.date} onChange={(e) => setDate(e.target.value)} required />
        </label>

        <label className="ink-input">
          <span>Ceremony</span>
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="general">General</option>
            <option value="vivah">Wedding</option>
            <option value="griha_pravesh">Griha Pravesh</option>
            <option value="travel">Travel</option>
            <option value="upanayana">Upanayana</option>
          </select>
        </label>

        <label className="ink-input">
          <span>Assumption Set</span>
          <select value={assumptionSet} onChange={(e) => setAssumptionSet(e.target.value)}>
            <option value="np-mainstream-v2">NP Mainstream</option>
            <option value="diaspora-practical-v2">Diaspora Practical</option>
          </select>
        </label>

        <label className="ink-input">
          <span>Timezone</span>
          <input value={state.timezone} onChange={(e) => setTimezone(e.target.value)} />
        </label>
      </form>

      {loading && <div className="skeleton" style={{ height: '180px', borderRadius: '16px' }} />}

      {!loading && error && (
        <div className="ink-card muhurta-error" role="alert">
          <h3>Unable to load muhurta heatmap</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && payload && (
        <>
          <section className="ink-card muhurta-hero-grid">
            <article>
              <h3>Best Window</h3>
              <p>{payload?.best_window?.name || '—'}</p>
              <small>Score: {payload?.best_window?.score ?? '—'}</small>
            </article>
            <article>
              <h3>Rahu Kalam</h3>
              <p>{payload?.rahu_kalam?.start ? `${new Date(payload.rahu_kalam.start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${new Date(payload.rahu_kalam.end).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : '—'}</p>
              <small>Segment {payload?.rahu_kalam?.segment || '—'}</small>
            </article>
            <article>
              <h3>Tara Bala</h3>
              <p>{payload?.tara_bala?.quality || 'unknown'}</p>
              <small>{payload?.tara_bala?.tara?.name || ''}</small>
            </article>
          </section>

          <section className="ink-card muhurta-heatmap-shell">
            <h3>24h Muhurta Heatmap</h3>
            <MuhurtaHeatmap
              blocks={payload.blocks || []}
              selectedIndex={selectedBlock?.index}
              onSelect={setSelectedBlock}
            />
            <div className="muhurta-selected-details">
              <h4>{selectedBlock?.name || 'Select a window'}</h4>
              <p>{selectedBlock?.rank_explanation || payload?.rank_explanation || 'Tap a block to inspect ranking details.'}</p>
              <p><strong>Reason codes:</strong> {selectedReasons}</p>
              <p><strong>Confidence score:</strong> {selectedBlock?.confidence_score ?? payload?.confidence_score ?? '—'}</p>
            </div>
          </section>

          <KnowledgePanel
            title={knowledge.title}
            intro={knowledge.intro}
            sections={knowledge.sections}
            className="muhurta-knowledge"
          />

          {state.mode === 'authority' && (
            <AuthorityInspector
              title="Muhurta Authority"
              meta={meta}
              traceFallbackId={payload?.calculation_trace_id}
            />
          )}
        </>
      )}
    </section>
  );
}

export default MuhurtaPage;
