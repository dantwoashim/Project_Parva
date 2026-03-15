import { useEffect, useMemo, useState } from 'react';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { MuhurtaHeatmap } from '../components/MuhurtaHeatmap/MuhurtaHeatmap';
import { MUHURTA_GLOSSARY } from '../data/temporalGlossary';
import { glossaryAPI, muhurtaAPI } from '../services/api';
import { useTemporalContext } from '../context/useTemporalContext';
import { findPresetByLocation } from '../data/locationPresets';
import { trackEvent } from '../services/analytics';
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

function qualityLabel(block) {
  const score = Number(block?.score) || 0;
  if (block?.class === 'auspicious' || score >= 65) return 'Strong';
  if (score >= 25) return 'Good';
  if (block?.class === 'avoid' || score <= -25) return 'Avoid';
  return 'Mixed';
}

function sortByScore(blocks = []) {
  return [...blocks].sort((a, b) => (Number(b.score) || 0) - (Number(a.score) || 0));
}

function formatTime(iso) {
  if (!iso) return 'Time unavailable';
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.valueOf())) return 'Time unavailable';
  return parsed.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

function formatWindow(block) {
  if (!block?.start) return 'Time to be confirmed';
  return `${formatTime(block.start)} - ${formatTime(block.end)}`;
}

function durationLabel(block) {
  if (!block?.start || !block?.end) return 'Duration to be confirmed';
  const start = new Date(block.start);
  const end = new Date(block.end);
  if (Number.isNaN(start.valueOf()) || Number.isNaN(end.valueOf())) return 'Duration to be confirmed';
  const minutes = Math.max(0, Math.round((end.getTime() - start.getTime()) / 60000));
  if (!minutes) return 'Duration to be confirmed';
  return minutes >= 60 ? `${Math.floor(minutes / 60)}h ${minutes % 60 ? `${minutes % 60}m` : ''}`.trim() : `${minutes} min`;
}

function humanReason(block, payload) {
  if (block?.rank_explanation) return block.rank_explanation;
  if (Array.isArray(block?.reason_codes) && block.reason_codes.length) {
    return block.reason_codes.map((code) => code.replaceAll('_', ' ')).join(', ');
  }
  return payload?.rank_explanation || 'Based on the strongest timing signals available for the current date and place.';
}

function narrativeFor(role, block, payload) {
  const reason = humanReason(block, payload);
  if (role === 'best') return reason || 'This is the clearest opening for fresh starts today.';
  if (role === 'second') return reason || 'This window stays workable when the lead window does not fit your schedule.';
  return reason || 'This period is better for routine or low-stakes tasks than a new beginning.';
}

function guidanceFor(block) {
  const tone = qualityLabel(block);
  if (tone === 'Strong') return 'Use for ceremonies, commitments, and meaningful first steps.';
  if (tone === 'Good') return 'Use for practical tasks, travel, or steady progress.';
  if (tone === 'Avoid') return 'Keep to maintenance, reflection, or lower-stakes tasks.';
  return 'Useful when you need flexibility, but not ideal for symbolic beginnings.';
}

function reasonChips(block, payload) {
  const raw = [
    ...(block?.reason_codes || []),
    ...(payload?.tara_bala?.quality ? [`tara_${payload.tara_bala.quality}`] : []),
  ];

  return [...new Set(raw)]
    .slice(0, 4)
    .map((item) => item.replaceAll('_', ' '));
}

export function MuhurtaPage() {
  const { state, setDate } = useTemporalContext();
  const [type, setType] = useState('general');
  const [assumptionSet, setAssumptionSet] = useState('np-mainstream-v2');
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [showScores, setShowScores] = useState(false);
  const [showFullSchedule, setShowFullSchedule] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [knowledge, setKnowledge] = useState(MUHURTA_GLOSSARY);

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
          setSelectedBlock(envelope.data?.best_window || envelope.data?.blocks?.[0] || null);
          setKnowledge(toKnowledge(glossary?.content, MUHURTA_GLOSSARY));
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setMeta(null);
          setSelectedBlock(null);
          setError(err.message || 'Failed to load best-time guidance');
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

  const rankedBlocks = useMemo(() => sortByScore(payload?.blocks || []), [payload]);
  const visibleBlocks = showFullSchedule ? rankedBlocks : rankedBlocks.slice(0, 3);
  const bestWindow = payload?.best_window || rankedBlocks[0] || null;
  const secondWindow = rankedBlocks.find((block) => block.index !== bestWindow?.index) || null;
  const avoidWindow = payload?.rahu_kalam || rankedBlocks.find((block) => qualityLabel(block) === 'Avoid') || null;
  const selectedReasonTokens = reasonChips(selectedBlock, payload);
  const preset = useMemo(() => findPresetByLocation(state.location), [state.location]);

  return (
    <section className="muhurta-page animate-fade-in-up">
      <header className="muhurta-page__hero ink-card">
        <div className="muhurta-page__hero-copy">
          <p className="today-page__eyebrow">Best Time</p>
          <h1 className="text-hero">Find the day&apos;s clearest opening before the details.</h1>
          <p className="muhurta-page__intro">
            Start with the strongest and second-best windows. The full schedule stays behind a deliberate action.
          </p>
        </div>
        <article className="muhurta-page__hero-note">
          <span className="muhurta-page__story-label">Reading posture</span>
          <strong>One clean recommendation first.</strong>
          <p>Use the top window when it fits your schedule, and only open the ranked list when you need more options.</p>
        </article>
      </header>

      {loading ? <div className="skeleton" style={{ minHeight: '240px', borderRadius: '1.4rem' }} /> : null}

      {!loading && error ? (
        <div className="ink-card muhurta-error" role="alert">
          <h2>Timing guidance is unavailable right now</h2>
          <p>{error}</p>
        </div>
      ) : null}

      {!loading && !error && payload ? (
        <>
          <section className="muhurta-page__recommendations">
            <article className="ink-card muhurta-page__recommendation muhurta-page__recommendation--best">
              <span className="muhurta-page__recommendation-label">Best window</span>
              <h2>{bestWindow?.name || 'Not available yet'}</h2>
              <p>{bestWindow ? formatWindow(bestWindow) : 'Check another date or profile.'}</p>
              <small>{narrativeFor('best', bestWindow, payload)}</small>
            </article>
            <article className="ink-card muhurta-page__recommendation">
              <span className="muhurta-page__recommendation-label">Backup window</span>
              <h2>{secondWindow?.name || 'No backup window yet'}</h2>
              <p>{secondWindow ? formatWindow(secondWindow) : 'Strong alternatives will appear here.'}</p>
              <small>{narrativeFor('second', secondWindow, payload)}</small>
            </article>
            <article className="ink-card muhurta-page__recommendation muhurta-page__recommendation--avoid">
              <span className="muhurta-page__recommendation-label">Avoid period</span>
              <h2>{avoidWindow?.name || 'Rahu Kalam'}</h2>
              <p>
                {avoidWindow?.start
                  ? formatWindow(avoidWindow)
                  : 'No avoid period is available for this day.'}
              </p>
              <small>{narrativeFor('avoid', avoidWindow, payload)}</small>
            </article>
          </section>

          <section className="ink-card muhurta-page__controls-shell">
            <form className="muhurta-page__controls" onSubmit={(event) => event.preventDefault()}>
              <label className="ink-input">
                <span>Date</span>
                <input type="date" value={state.date} onChange={(event) => setDate(event.target.value)} required />
              </label>
              <label className="ink-input">
                <span>Ceremony</span>
                <select value={type} onChange={(event) => setType(event.target.value)}>
                  <option value="general">General</option>
                  <option value="vivah">Wedding</option>
                  <option value="griha_pravesh">Griha Pravesh</option>
                  <option value="travel">Travel</option>
                  <option value="upanayana">Upanayana</option>
                </select>
              </label>
              <details className="muhurta-page__advanced">
                <summary>More options</summary>
                <div className="muhurta-page__advanced-grid">
                  <label className="ink-input">
                    <span>Profile</span>
                    <select value={assumptionSet} onChange={(event) => setAssumptionSet(event.target.value)}>
                      <option value="np-mainstream-v2">NP Mainstream</option>
                      <option value="diaspora-practical-v2">Diaspora Practical</option>
                    </select>
                  </label>
                  <label className="ink-input">
                    <span>Timezone</span>
                    <input value={state.timezone} readOnly />
                  </label>
                  <p className="muhurta-page__advanced-note">
                    Coordinate editing now lives in More options from the shell, not in the first layer of this page.
                  </p>
                </div>
              </details>
            </form>
          </section>

          <section className="ink-card muhurta-heatmap-shell">
            <div className="muhurta-heatmap-shell__header">
              <div>
                <p className="today-page__eyebrow">Ranked windows</p>
                <h2>{showFullSchedule ? 'Full day schedule' : 'Top 3 windows in view'}</h2>
              </div>
              <div className="muhurta-page__panel-actions">
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => {
                    const next = !showFullSchedule;
                    setShowFullSchedule(next);
                    trackEvent('full_schedule_opened', { surface: 'best_time', expanded: next });
                  }}
                >
                  {showFullSchedule ? 'Show top 3' : 'Show full day schedule'}
                </button>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowScores((value) => !value)}>
                  {showScores ? 'Hide ranking details' : 'Show ranking details'}
                </button>
              </div>
            </div>

            <MuhurtaHeatmap
              blocks={visibleBlocks}
              selectedIndex={selectedBlock?.index}
              onSelect={setSelectedBlock}
              showScores={showScores}
            />

            <div className="muhurta-selected-details">
              <div className="muhurta-selected-details__lead">
                <div>
                  <h3>{selectedBlock?.name || 'Choose a window'}</h3>
                  <p>{humanReason(selectedBlock, payload)}</p>
                </div>
                <div className="muhurta-selected-details__summary">
                  <span className={`badge ${qualityLabel(selectedBlock) === 'Avoid' ? '' : 'badge-primary'}`.trim()}>
                    {qualityLabel(selectedBlock)}
                  </span>
                  <strong>{selectedBlock ? formatWindow(selectedBlock) : 'Time to be confirmed'}</strong>
                  <small>{selectedBlock ? durationLabel(selectedBlock) : 'Duration to be confirmed'}</small>
                </div>
              </div>

              {selectedReasonTokens.length ? (
                <div className="muhurta-selected-details__chips">
                  {selectedReasonTokens.map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
              ) : null}

              <div className="muhurta-selected-details__meta">
                <span><strong>Use for:</strong> {guidanceFor(selectedBlock)}</span>
                <span><strong>Tara bala:</strong> {payload?.tara_bala?.quality || 'unknown'}</span>
                <span><strong>Confidence:</strong> {payload?.confidence_score ? `${Math.round(payload.confidence_score * 100)}%` : 'General guidance'}</span>
              </div>
            </div>
          </section>

          <EvidenceDrawer
            title="Best Time"
            intro="This drawer keeps method, confidence, and place metadata nearby without forcing it into the main reading flow."
            methodRef={meta?.method || 'Muhurta heatmap profile'}
            confidenceNote={payload?.confidence_score ? `${Math.round(payload.confidence_score * 100)}% confidence in the ranked windows` : (meta?.confidence?.level || meta?.confidence || 'Public guidance')}
            placeUsed={preset?.label || state.timezone}
            computedForDate={state.date}
            availability={[
              { label: 'Best window', available: Boolean(bestWindow), note: 'The lead recommendation is drawn from the highest-ranked available block.' },
              { label: 'Avoid period', available: Boolean(avoidWindow?.start), note: 'Avoid periods depend on the current day and place payload.' },
              { label: 'Full schedule', available: Boolean(rankedBlocks.length), note: 'Only the top three windows are shown by default on smaller screens.' },
            ]}
            meta={meta}
            traceFallbackId={payload?.calculation_trace_id}
          />

          <KnowledgePanel
            title={knowledge.title}
            intro={knowledge.intro}
            sections={knowledge.sections}
            className="muhurta-knowledge"
          />
        </>
      ) : null}
    </section>
  );
}

export default MuhurtaPage;
