import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { MyPlaceSection } from '../consumer/ConsumerSections';
import { buildConsumerMyPlaceViewModel } from '../consumer/consumerViewModels';
import { PANCHANGA_GLOSSARY, PERSONAL_PANCHANGA_GLOSSARY } from '../data/temporalGlossary';
import { LOCATION_PRESETS, findPresetByLocation } from '../data/locationPresets';
import { useMemberContext } from '../context/useMemberContext';
import { useTemporalContext } from '../context/useTemporalContext';
import { usePersonalPlaceBundle } from '../hooks/usePersonalPlaceBundle';
import './PersonalPanchangaPage.css';

export function PersonalPanchangaPage() {
  const { state, setDate, setLocation, setTimezone } = useTemporalContext();
  const { state: memberState, savePlace, setLocalSaveConsent, clearLocalState } = useMemberContext();
  const [deviceStatus, setDeviceStatus] = useState('');
  const localSaveEnabled = Boolean(memberState.persistence?.localSaveEnabled);

  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const {
    loading,
    error,
    payload,
    contextPayload,
    meta,
    contextMeta,
    festivals,
  } = usePersonalPlaceBundle({
    date: state.date,
    latitude: state.location?.latitude,
    longitude: state.location?.longitude,
    timezone: state.timezone,
  });

  function applyPreset(presetId) {
    const preset = LOCATION_PRESETS.find((item) => item.id === presetId);
    if (!preset) return;
    setLocation({ latitude: preset.latitude, longitude: preset.longitude });
    setTimezone(preset.timezone);
  }

  function useDeviceLocation() {
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
  }

  const viewModel = useMemo(
    () => buildConsumerMyPlaceViewModel({
      temporalState: state,
      memberState,
      activePreset,
      panchanga: payload,
      contextPayload,
      contextMeta,
      festivals,
      meta,
    }),
    [state, memberState, activePreset, payload, contextPayload, contextMeta, festivals, meta],
  );

  const preferencesSummary = [
    'English',
    state.timezone,
    memberState.preferences.notificationStyle,
  ].join(' / ');

  if (loading) {
    return (
      <section className="personal-page animate-fade-in-up consumer-route consumer-route--utility">
        <div className="skeleton personal-page__hero" />
        <div className="personal-summary-grid">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="skeleton" style={{ minHeight: '140px', borderRadius: '1.2rem' }} />
          ))}
        </div>
        <div className="skeleton" style={{ minHeight: '240px', borderRadius: '1.2rem' }} />
      </section>
    );
  }

  if (error || !payload) {
    return (
      <section className="personal-page animate-fade-in-up consumer-route consumer-route--utility">
        <article className="ink-card personal-error" role="alert">
          <p className="today-page__eyebrow">My Place</p>
          <h1 className="text-hero">Place-aware guidance is temporarily unavailable.</h1>
          <p className="personal-page__intro">{error || 'The selected place could not be resolved right now.'}</p>
        </article>
      </section>
    );
  }

  return (
    <section className="personal-page animate-fade-in-up consumer-route consumer-route--utility">
      <MyPlaceSection
        id={undefined}
        viewModel={viewModel}
        languageLabel={state.language === 'ne' ? 'Nepali' : 'English'}
        timezoneLabel={state.timezone}
        notificationStyle={memberState.preferences.notificationStyle}
        activityFocus={memberState.preferences.activityFocus}
        placeLabel={viewModel.placeLabel}
        title="Keep the place that changes your day in view."
        body={viewModel.subtitle}
        action={<Link className="btn btn-secondary btn-sm" to="/#my-place">Jump to home section</Link>}
        onSavePlace={() => savePlace({
          label: viewModel.placeLabel,
          latitude: state.location?.latitude,
          longitude: state.location?.longitude,
          timezone: state.timezone,
        }).then((saved) => {
          if (!localSaveEnabled) {
            setDeviceStatus('Enable local save first if you want this browser to remember the place later.');
          } else {
            setDeviceStatus(saved ? 'Place saved to this browser only.' : 'This browser could not save the place.');
          }
        })}
        onCyclePlace={() => {
          const currentIndex = LOCATION_PRESETS.findIndex((item) => item.id === activePreset?.id);
          const nextPreset = LOCATION_PRESETS[(currentIndex + 1 + LOCATION_PRESETS.length) % LOCATION_PRESETS.length];
          applyPreset(nextPreset.id);
        }}
      />

      <section className="ink-card personal-page__route-card">
        <div className="personal-page__route-header">
          <div>
            <p className="today-page__eyebrow">Place controls</p>
            <h2>Adjust the place only when the answer needs to change.</h2>
          </div>
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

          <button type="button" className="btn btn-secondary" onClick={useDeviceLocation}>
            Use my device
          </button>
        </form>

        {deviceStatus ? <p className="personal-page__status">{deviceStatus}</p> : null}
      </section>

      <section className="ink-card personal-page__route-card">
        <div className="personal-page__route-header">
          <div>
            <p className="today-page__eyebrow">Privacy</p>
            <h2>Local saving is explicit, local-only, and reversible.</h2>
          </div>
        </div>
        <p className="personal-page__privacy-copy">
          Personal place details, saved reminders, and readings stay on this browser only. Turn local save on only if you want this device to remember them later.
        </p>
        <div className="personal-page__privacy-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={async () => {
              const nextEnabled = !localSaveEnabled;
              const ok = await setLocalSaveConsent(nextEnabled);
              setDeviceStatus(
                ok
                  ? (nextEnabled ? 'Local save is now enabled for this browser.' : 'Local save is paused and future writes will stay in-memory only.')
                  : 'This browser could not update the local-save setting.',
              );
            }}
          >
            {localSaveEnabled ? 'Pause local save' : 'Enable local save'}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={async () => {
              const ok = await clearLocalState();
              setDeviceStatus(
                ok
                  ? 'Saved local data was purged from this browser.'
                  : 'This browser could not purge the saved local data.',
              );
            }}
          >
            Purge local data
          </button>
        </div>
        <p className="personal-page__privacy-state">
          {localSaveEnabled
            ? 'Status: local save enabled on this browser only.'
            : 'Status: local save is off by default until you explicitly enable it.'}
        </p>
      </section>

      <section className="personal-summary-grid">
        <article className="ink-card personal-summary-card">
          <span className="today-page__eyebrow">Local sunrise</span>
          <strong>{viewModel.localSunrise}</strong>
          <p>Use this when your place materially shifts the start of the day.</p>
        </article>
        <article className="ink-card personal-summary-card">
          <span className="today-page__eyebrow">Local sunset</span>
          <strong>{viewModel.localSunset}</strong>
          <p>Keep the close of the day visible alongside sunrise when timing is place-sensitive.</p>
        </article>
        <article className="ink-card personal-summary-card">
          <span className="today-page__eyebrow">What changes here</span>
          <strong>{viewModel.sunriseShift}</strong>
          <p>{viewModel.savedStatus}</p>
        </article>
        <article className="ink-card personal-summary-card">
          <span className="today-page__eyebrow">Preferences</span>
          <strong>{memberState.preferences.activityFocus}</strong>
          <p>{preferencesSummary}</p>
        </article>
      </section>

      <section className="personal-page__story-grid">
        <article className="ink-card personal-context-card personal-context-card--primary">
          <span className="today-page__eyebrow">Current context</span>
          <strong>{viewModel.contextTitle}</strong>
          <p>{viewModel.contextSummary}</p>

          {viewModel.festivals.length ? (
            <div className="personal-festivals">
              <h3 className="personal-festivals__title">Observances active for this place</h3>
              <div className="personal-festivals__chips">
                {viewModel.festivals.map((festival) => (
                  <Link key={festival.id} className="festival-chip" to={`/festivals/${festival.id}`}>
                    <span className="festival-chip__name">{festival.title}</span>
                  </Link>
                ))}
              </div>
              {viewModel.festivals.some((festival) => festival.truthNote) ? (
                <div className="personal-page__truth-list">
                  {viewModel.festivals
                    .filter((festival) => festival.truthNote)
                    .map((festival) => (
                      <p key={`${festival.id}-truth`} className="personal-page__truth-note">
                        {festival.title}: {festival.truthNote}
                      </p>
                    ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </article>

        <article className="ink-card personal-context-card">
          <span className="today-page__eyebrow">Saved reminders</span>
          <strong>{viewModel.reminders.length ? `${viewModel.reminders.length} in view` : 'No reminders yet'}</strong>
          {viewModel.reminders.length ? (
            <ul className="personal-reminders">
              {viewModel.reminders.map((item) => (
                <li key={item.id}>
                  <strong>{item.title}</strong>
                  <span>{item.note}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>Festival and best-time reminders will appear here when you save them locally.</p>
          )}

          <dl className="personal-page__mini-facts">
            <div>
              <dt>Place basis</dt>
              <dd>{viewModel.placeLabel}</dd>
            </div>
            <div>
              <dt>Sunrise shift</dt>
              <dd>{viewModel.sunriseShift}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{viewModel.savedStatus}</dd>
            </div>
          </dl>

          {viewModel.truthSurface?.sources?.length ? (
            <div className="today-page__truth-sources">
              {viewModel.truthSurface.sources.map((source) => (
                <article key={source.label} className="today-page__truth-card">
                  <span className="today-page__label">{source.label}</span>
                  <strong>{source.qualityBand}</strong>
                  <p className="today-page__subsummary">
                    Method {source.method}. Confidence {source.confidence}.
                    {source.degraded ? ' Defaults were applied.' : ' No defaults were applied.'}
                  </p>
                  {source.boundaryRadar ? (
                    <p className="today-page__subsummary">
                      Boundary radar {source.boundaryRadar}
                      {typeof source.stabilityScore === 'number' ? `. Stability ${source.stabilityScore}.` : '.'}
                    </p>
                  ) : null}
                  {source.recommendedAction ? (
                    <p className="today-page__subsummary">{source.recommendedAction}</p>
                  ) : null}
                </article>
              ))}
            </div>
          ) : null}
        </article>
      </section>

      {viewModel.truthSurface?.chips?.length ? (
        <section className="ink-card personal-page__truth-card">
          <div className="personal-page__route-header">
            <div>
              <p className="today-page__eyebrow">Truth surface</p>
              <h2>Place-aware method and fallback state</h2>
            </div>
          </div>
          <div className="personal-page__truth-strip">
            {viewModel.truthSurface.chips.map((chip) => (
              <span
                key={`${chip.tone}-${chip.label}`}
                className={`personal-page__truth-chip personal-page__truth-chip--${chip.tone}`.trim()}
              >
                {chip.label}
              </span>
            ))}
          </div>
          <div className="personal-page__truth-grid">
            {viewModel.truthSurface.sources.map((source) => (
              <article key={source.label} className="personal-page__truth-source">
                <span className="today-page__eyebrow">{source.label}</span>
                <strong>{source.qualityBand}</strong>
                <p>
                  Method {source.method}. Confidence {source.confidence}.
                  {source.degraded ? ' Defaults were applied.' : ' No defaults were applied.'}
                </p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      <details className="personal-page__accordion">
        <summary>Place signals and method</summary>
        <div className="personal-page__accordion-body">
          <section className="personal-cards-grid stagger-children">
            {viewModel.cards.map((card) => (
              <article key={card.label} className="ink-card panchanga-card">
                <h3>{card.label}</h3>
                <p className="panchanga-card__value">{card.value}</p>
                <p className="panchanga-card__meta">{card.note}</p>
              </article>
            ))}
          </section>

          <EvidenceDrawer {...viewModel.evidence} />

          <KnowledgePanel
            title={PERSONAL_PANCHANGA_GLOSSARY.title}
            intro={PERSONAL_PANCHANGA_GLOSSARY.intro}
            sections={[...PERSONAL_PANCHANGA_GLOSSARY.sections, ...PANCHANGA_GLOSSARY.sections.slice(0, 1)]}
            className="personal-knowledge"
          />
        </div>
      </details>
    </section>
  );
}

export default PersonalPanchangaPage;
