import { useEffect, useMemo, useState } from 'react';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { CONSUMER_BEST_TIME_OPTIONS, buildConsumerBestTimeViewModel } from '../consumer/consumerViewModels';
import { LOCATION_PRESETS, findPresetByLocation } from '../data/locationPresets';
import { useTemporalContext } from '../context/useTemporalContext';
import { muhurtaAPI } from '../services/api';
import { describeSupportError } from '../services/errorFormatting';
import './MuhurtaPage.css';

function humanizeReason(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function toneClass(item) {
  return `muhurta-page__heat-cell muhurta-page__heat-cell--${item?.tone || 'mixed'}`.trim();
}

export function MuhurtaPage() {
  const { state, setDate, setLocation, setTimezone } = useTemporalContext();
  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const [type, setType] = useState('general');
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const envelope = await muhurtaAPI.getHeatmapEnvelope({
          date: state.date,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          type,
          assumptionSet: 'np-mainstream-v2',
        });

        if (!cancelled) {
          const nextPayload = envelope.data || null;
          setPayload(nextPayload);
          setMeta(envelope.meta || null);
          setSelectedBlock(nextPayload?.best_window || nextPayload?.blocks?.[0] || null);
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setMeta(null);
          setSelectedBlock(null);
          setError(describeSupportError(err, 'Best-time guidance is unavailable right now.'));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone, type]);

  const placeLabel = activePreset?.label || 'Your place';
  const cyclePlace = () => {
    const currentIndex = LOCATION_PRESETS.findIndex((item) => item.id === activePreset?.id);
    const nextPreset = LOCATION_PRESETS[(currentIndex + 1 + LOCATION_PRESETS.length) % LOCATION_PRESETS.length];
    setLocation({ latitude: nextPreset.latitude, longitude: nextPreset.longitude });
    setTimezone(nextPreset.timezone);
  };

  const viewModel = useMemo(
    () => buildConsumerBestTimeViewModel({
      payload,
      meta,
      state,
      type,
      selectedBlock,
      placeLabel,
    }),
    [payload, meta, state, type, selectedBlock, placeLabel],
  );

  const reasons = Array.isArray(selectedBlock?.reason_codes)
    ? selectedBlock.reason_codes.map((item) => humanizeReason(item))
    : [];

  if (loading) {
    return (
      <section className="muhurta-page animate-fade-in-up consumer-route consumer-route--analysis">
        <div className="skeleton muhurta-page__hero-skeleton" />
        <div className="skeleton muhurta-page__heatmap-skeleton" />
      </section>
    );
  }

  if (error) {
    return (
      <section className="muhurta-page animate-fade-in-up consumer-route consumer-route--analysis">
        <article className="muhurta-page__error ink-card" role="alert">
          <p className="muhurta-page__eyebrow">Muhurta</p>
          <h1>Best-time guidance is temporarily unavailable.</h1>
          <p>{error}</p>
        </article>
      </section>
    );
  }

  return (
    <section className="muhurta-page animate-fade-in-up consumer-route consumer-route--analysis">
      <header className="muhurta-page__hero">
        <div>
          <div className="muhurta-page__hero-tag">
            <span className="text-nepali">शुद्ध मुहूर्त</span>
            <span className="muhurta-page__divider" />
            <span>Sacred Timing</span>
          </div>
          <h1>Muhurta Explorer</h1>
        </div>
        <button type="button" className="muhurta-page__date-chip" onClick={() => setDate(state.date)}>
          <span className="material-symbols-outlined">calendar_today</span>
          <div>
            <span>Current Date</span>
            <strong>{state.date}</strong>
          </div>
        </button>
      </header>

      <section className="muhurta-page__activities">
        {CONSUMER_BEST_TIME_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            className={`muhurta-page__activity-pill ${type === option.value ? 'is-active' : ''}`.trim()}
            onClick={() => setType(option.value)}
          >
            {option.label}
          </button>
        ))}
      </section>

      <section className="muhurta-page__heatmap-panel">
        <div className="muhurta-page__heatmap-head">
          <div>
            <h2>Daily Energy Distribution</h2>
            <p>{viewModel.intro}</p>
          </div>
          <div className="muhurta-page__legend">
            <span><i className="is-avoid" /> Avoid</span>
            <span><i className="is-neutral" /> Neutral</span>
            <span><i className="is-strong" /> Auspicious</span>
          </div>
        </div>

        <div className="muhurta-page__heatmap-grid">
          {viewModel.timeline.length ? viewModel.timeline.map((item) => (
            <button
              key={item.id}
              type="button"
              className={toneClass(item)}
              onClick={() => {
                const block = (payload?.blocks || []).find((entry) => entry.index === item.id);
                if (block) setSelectedBlock(block);
              }}
            >
              <strong>{item.time}</strong>
              <span>{item.title}</span>
            </button>
          )) : (
            <div className="muhurta-page__heat-empty">Timing blocks are still loading.</div>
          )}
        </div>
      </section>

      <section className="muhurta-page__windows">
        <div className="muhurta-page__section-head">
          <h2>Recommended Windows</h2>
          <p>Start with the strongest answer, then keep two calmer alternates nearby.</p>
        </div>
        <div className="muhurta-page__window-grid">
          {[viewModel.best, ...(viewModel.alternates || []).slice(0, 2)].filter(Boolean).map((item, index) => (
            <article key={`${item.title}-${index}`} className={`muhurta-page__window-card ${index === 0 ? 'is-primary' : ''}`.trim()}>
              <div className="muhurta-page__window-top">
                <span>{index === 0 ? 'Most auspicious' : index === 1 ? 'Stable' : 'Favorable'}</span>
                <em>{viewModel.activityLabel}</em>
              </div>
              <h3>{item.time}</h3>
              <p>{item.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="muhurta-page__insights">
        <article className="muhurta-page__insight-card glass-panel">
          <div>
            <p className="muhurta-page__eyebrow">Cosmic Influence</p>
            <h2>The Tithi Power</h2>
          </div>
          <div className="muhurta-page__insight-list">
            <div>
              <strong>{viewModel.best?.title || 'Primary window'}</strong>
              <p>{viewModel.best?.note || 'The clearest lead answer appears here.'}</p>
            </div>
            <div>
              <strong>{viewModel.avoid?.title || 'Lower-priority stretch'}</strong>
              <p>{viewModel.avoid?.note || 'Caution guidance will appear here when the live schedule returns.'}</p>
            </div>
          </div>
        </article>

        <article className="muhurta-page__context-card">
          <div className="muhurta-page__context-row">
            <span>Place</span>
            <strong>{placeLabel}</strong>
          </div>
          <div className="muhurta-page__context-row">
            <span>Date</span>
            <strong>{state.date}</strong>
          </div>
          <div className="muhurta-page__context-row">
            <span>Answer style</span>
            <strong>{viewModel.activityLabel}</strong>
          </div>
          {reasons.length ? (
            <div className="muhurta-page__reason-list">
              {reasons.map((reason) => (
                <span key={reason}>{reason}</span>
              ))}
            </div>
          ) : null}
          <div className="muhurta-page__context-actions">
            <button type="button" className="btn btn-secondary" onClick={cyclePlace}>Change Place</button>
            <EvidenceDrawer {...viewModel.evidence} />
          </div>
        </article>
      </section>
    </section>
  );
}

export default MuhurtaPage;
