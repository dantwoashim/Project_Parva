import { useMemo } from 'react';
import { UtilityPageHeader } from '../consumer/UtilityPages';
import { feedAPI } from '../services/api';
import { useFestivals } from '../hooks/useFestivals';
import { useMemberContext } from '../context/useMemberContext';
import {
  detectDeviceProfile,
  FALLBACK_PLATFORM_GUIDES,
  formatDateWindow,
  formatFeedDate,
  integrationPlatformLabel,
} from './feedSubscriptions/feedHelpers';
import { useFeedSubscriptionsState } from './feedSubscriptions/useFeedSubscriptionsState';
import './FeedSubscriptionsPage.css';

function FeedPresetCard({ item, isActive, onSelect }) {
  return (
    <button
      type="button"
      className={`feeds-preset ${isActive ? 'feeds-preset--active' : ''}`}
      onClick={() => onSelect(item.key)}
    >
      <span className="feeds-preset__eyebrow">
        {item.key === 'all' ? 'Recommended' : item.category || 'Preset'}
      </span>
      <strong>{item.title}</strong>
      <p>{item.description}</p>
    </button>
  );
}

function PlatformPanel({
  platformKey,
  guide,
  onConnect,
  onCopy,
  onDownload,
  onShare,
  copied,
  recommended,
}) {
  return (
    <article className={`ink-card feeds-platform feeds-platform--${platformKey}`}>
      <div className="feeds-platform__hero">
        <div className="feeds-platform__badges">
          <span className="feeds-platform__badge">{guide.badge}</span>
          {recommended ? <span className="feeds-platform__badge feeds-platform__badge--recommended">Best for this device</span> : null}
        </div>
        <h2>{guide.title}</h2>
        <p>{guide.description}</p>
        {guide.sync_expectation ? <p className="feeds-platform__sync">{guide.sync_expectation}</p> : null}
      </div>

      <div className="feeds-platform__actions">
        <button type="button" className="btn btn-primary btn-sm" onClick={() => onConnect(platformKey)}>
          {guide.cta_label || (platformKey === 'apple' ? 'Open subscription' : platformKey === 'google' ? 'Copy link and open Google Calendar' : 'Open download')}
        </button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => onCopy(platformKey)}>
          {copied === platformKey ? 'Copied' : guide.copy_label || 'Copy link'}
        </button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={onDownload}>
          Download .ics
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={onShare}>
          Share
        </button>
      </div>

      <ol className="feeds-platform__steps">
        {guide.steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
    </article>
  );
}

function AdvancedLinkField({ label, value }) {
  return (
    <details className="feed-card__advanced">
      <summary>{label}</summary>
      <label className="ink-input feed-card__advanced-field">
        <span>Calendar link</span>
        <input readOnly value={value} onFocus={(event) => event.target.select()} />
      </label>
    </details>
  );
}

function ConnectedIntegrationCard({ integration, onOpen, onCopy, onRemove }) {
  return (
    <article className="ink-card feeds-connection-card">
      <div className="feeds-connection-card__copy">
        <div className="feeds-connection-card__head">
          <span className="feeds-page__eyebrow">Connected</span>
          <strong>{integration.title}</strong>
        </div>
        <p>{integrationPlatformLabel(integration)}</p>
        <div className="feeds-connection-card__meta">
          {integration.feedKind ? <span>{integration.feedKind === 'custom' ? 'Custom feed' : 'Preset feed'}</span> : null}
          {integration.feedTitle ? <span>{integration.feedTitle}</span> : null}
          {integration.selectionCount ? <span>{integration.selectionCount} selected</span> : null}
        </div>
        {integration.nextEvent?.summary ? (
          <p>{`Next: ${integration.nextEvent.summary}${integration.nextEvent.start_date ? ` • ${formatFeedDate(integration.nextEvent.start_date)}` : ''}`}</p>
        ) : null}
        {integration.syncExpectation ? <p>{integration.syncExpectation}</p> : null}
      </div>
      <div className="feeds-connection-card__actions">
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => onOpen(integration)}>
          Reopen
        </button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => onCopy(integration)}>
          Copy link
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => onRemove(integration)}>
          Remove
        </button>
      </div>
    </article>
  );
}

export function FeedSubscriptionsPage() {
  const { state, startIntegration, removeIntegration } = useMemberContext();
  const { festivals, loading, error } = useFestivals({ qualityBand: 'all', algorithmicOnly: false });
  const deviceProfile = useMemo(() => detectDeviceProfile(), []);
  const subscriptions = useFeedSubscriptionsState({
    festivals,
    deviceProfile,
    integrations: state.integrations,
    startIntegration,
    removeIntegration,
  });

  const {
    years,
    setYears,
    lang,
    setLang,
    selectedIds,
    copied,
    query,
    setQuery,
    filtered,
    presets,
    platformGuides,
    effectiveActivePreset,
    setActivePreset,
    selectedPreset,
    recommendedPlatform,
    orderedPlatforms,
    customLink,
    selectedFestivalNames,
    savedIntegrations,
    setupState,
    resolvedCustomPlan,
    toggleFestival,
    copyLink,
    shareLink,
    handlePresetPlatform,
    handleCustomPlatform,
    reopenSavedIntegration,
    copySavedIntegrationLink,
  } = subscriptions;

  return (
    <section className="feeds-page utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow="Calendar integrations"
        title="Connect Parva without dealing with raw calendar plumbing first."
        body="Choose the calendar you already use, pick a preset, and follow the shortest path. Apple opens directly. Google gets the link copied first because Google still asks for the URL in a desktop browser."
        links={[
          { label: 'Saved', to: '/#saved' },
          { label: 'Profile', to: '/profile' },
          { label: 'Methodology', to: '/methodology' },
        ]}
        aside={(
          <div className="feeds-hero__controls">
            <label className="ink-input">
              <span>Years</span>
              <select value={years} onChange={(event) => setYears(Number(event.target.value))}>
                {[1, 2, 3, 4, 5].map((value) => (
                  <option key={value} value={value}>{value}</option>
                ))}
              </select>
            </label>
            <label className="ink-input">
              <span>Language</span>
              <select value={lang} onChange={(event) => setLang(event.target.value)}>
                <option value="en">English</option>
                <option value="ne">Nepali</option>
              </select>
            </label>
          </div>
        )}
      />

      <section className="ink-card feeds-premium-panel">
        <div className="feeds-premium-panel__top">
          <div>
            <p className="feeds-page__eyebrow">Pick your calendar pack</p>
            <h2>Start with a polished preset, then switch to a custom feed only if you need it.</h2>
          </div>
          <div className="feeds-premium-panel__meta">
            <span>{years} year sync window</span>
            <span>{lang === 'ne' ? 'Nepali labels' : 'English labels'}</span>
          </div>
        </div>

        <div className="feeds-presets" role="tablist" aria-label="Calendar feed presets">
          {presets.map((item) => (
            <FeedPresetCard key={item.key} item={item} isActive={item.key === effectiveActivePreset} onSelect={setActivePreset} />
          ))}
        </div>

        {selectedPreset ? (
          <section className="feeds-selected">
            <div className="feeds-selected__summary">
              <span className="feeds-page__eyebrow">Selected preset</span>
              <h3>{selectedPreset.title}</h3>
              <p>{selectedPreset.description}</p>
            </div>

            <section className="ink-card feeds-device-spotlight">
              <div className="feeds-device-spotlight__copy">
                <span className="feeds-page__eyebrow">Recommended next step</span>
                <h3>{deviceProfile.title}</h3>
                <p>{deviceProfile.description}</p>
              </div>
              <div className="feeds-device-spotlight__actions">
                <span className="feeds-platform__badge">{deviceProfile.badge}</span>
                <button type="button" className="btn btn-primary btn-sm" onClick={() => handlePresetPlatform(recommendedPlatform)}>
                  {(platformGuides[recommendedPlatform] || FALLBACK_PLATFORM_GUIDES[recommendedPlatform])?.cta_label || 'Continue'}
                </button>
              </div>
            </section>

            {selectedPreset.stats ? (
              <div className="feeds-selected__stats">
                <article className="ink-card feeds-stat">
                  <span>Events in this feed</span>
                  <strong>{selectedPreset.stats.event_count}</strong>
                </article>
                <article className="ink-card feeds-stat">
                  <span>Calendar window</span>
                  <strong>{formatDateWindow(selectedPreset.stats.date_window)}</strong>
                </article>
                <article className="ink-card feeds-stat">
                  <span>Next observance</span>
                  <strong>
                    {selectedPreset.stats.next_event
                      ? `${selectedPreset.stats.next_event.summary} • ${formatFeedDate(selectedPreset.stats.next_event.start_date)}`
                      : 'No upcoming event in this window'}
                  </strong>
                </article>
              </div>
            ) : null}

            {selectedPreset.stats?.highlights?.length ? (
              <div className="feeds-highlights" aria-label="Feed highlights">
                {selectedPreset.stats.highlights.map((highlight) => (
                  <span key={`${highlight.summary}-${highlight.start_date}`} className="feeds-highlight-chip">
                    {highlight.summary} • {formatFeedDate(highlight.start_date)}
                  </span>
                ))}
              </div>
            ) : null}

            <div className="feeds-platform-grid">
              {orderedPlatforms.map((platformKey) => {
                const guide = platformGuides[platformKey] || FALLBACK_PLATFORM_GUIDES[platformKey];
                const copyValue = selectedPreset.platform_links?.[platformKey]?.copy_url
                  || (platformKey === 'google' ? selectedPreset.google_copy_url : selectedPreset.feed_url)
                  || selectedPreset.feed_url;
                return (
                  <PlatformPanel
                    key={platformKey}
                    platformKey={platformKey}
                    guide={guide}
                    copied={copied}
                    recommended={platformKey === recommendedPlatform}
                    onConnect={handlePresetPlatform}
                    onCopy={() => copyLink(platformKey, copyValue, `${guide.title} link copied.`, {
                      platform: platformKey,
                      title: `${guide.title} link copied`,
                    })}
                    onDownload={() => handlePresetPlatform('manual')}
                    onShare={() => shareLink(`${selectedPreset.title} calendar`, selectedPreset.feed_url)}
                  />
                );
              })}
            </div>

            <div className="feeds-manual-grid">
              <article className="ink-card feeds-manual-card">
                <span className="feeds-page__eyebrow">Direct links</span>
                <h3>Manual and advanced setup</h3>
                <p>Use these when you want the raw feed or a downloaded ICS file for another app.</p>
                <div className="feeds-manual-card__actions">
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => copyLink('manual', selectedPreset.feed_url, 'Direct calendar link copied.', {
                    platform: 'manual',
                    title: 'Direct feed copied',
                  })}>
                    {copied === 'manual' ? 'Copied' : 'Copy direct link'}
                  </button>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => window.open(selectedPreset.download_url || feedAPI.getDownloadLink(selectedPreset.feed_url), '_blank', 'noreferrer')}>
                    Download .ics
                  </button>
                </div>
                <AdvancedLinkField label="Show advanced manual setup" value={selectedPreset.feed_url} />
              </article>

              {setupState ? (
                <aside className="feeds-setup-note" role="status" aria-live="polite">
                  <span className="feeds-page__eyebrow">Setup note</span>
                  <strong>{setupState.title}</strong>
                  <p>{setupState.body}</p>
                </aside>
              ) : null}
            </div>
          </section>
        ) : null}
      </section>

      <section className="ink-card feeds-connections">
        <div className="feeds-connections__header">
          <div>
            <p className="feeds-page__eyebrow">Connected calendars</p>
            <h2>Reopen, copy, or clean up the calendars you already connected.</h2>
          </div>
          <span className="feeds-platform__badge">{savedIntegrations.length} saved</span>
        </div>

        {savedIntegrations.length ? (
          <div className="feeds-connections__grid">
            {savedIntegrations.map((integration) => (
              <ConnectedIntegrationCard
                key={integration.id || integration.platform}
                integration={integration}
                onOpen={reopenSavedIntegration}
                onCopy={copySavedIntegrationLink}
                onRemove={(entry) => removeIntegration(entry.id || entry.platform)}
              />
            ))}
          </div>
        ) : (
          <article className="feeds-connections__empty">
            <strong>No calendar connections yet</strong>
            <p>Use one of the Apple, Google, or manual actions above and it will show up here with the next step, feed details, and quick reopen actions.</p>
          </article>
        )}
      </section>

      <section className="ink-card feeds-custom utility-page__panel">
        <div className="feeds-custom__header">
          <div>
            <p className="feeds-page__eyebrow">Build your own</p>
            <h2>Make a smaller calendar for the observances you follow closely.</h2>
          </div>
          <p>Choose specific observances, then use the same Apple, Google, or manual setup flow with a custom feed.</p>
        </div>

        <label className="ink-input feeds-custom__search">
          <span>Search festivals</span>
          <input
            type="search"
            placeholder="Dashain, Teej, Shivaratri..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>

        {loading ? <p className="feeds-custom__status">Loading festivals...</p> : null}
        {!loading && error ? <p className="feeds-custom__status" role="alert">{error}</p> : null}
        {!loading && !error ? (
          <div className="feeds-picker" role="group" aria-label="Festival selector">
            {filtered.slice(0, 60).map((festival) => (
              <label key={festival.id} className="feeds-picker__item">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(festival.id)}
                  onChange={() => toggleFestival(festival.id)}
                />
                <span>{festival.name}</span>
              </label>
            ))}
          </div>
        ) : null}

        <div className="feeds-custom__output">
          <div className="feeds-custom__summary">
            <span>Selected festivals</span>
            <strong>{selectedIds.length}</strong>
          </div>

          {customLink ? (
            <div className="feeds-custom__actions">
              <div className="ink-card feeds-custom-plan">
                <div className="feeds-custom-plan__copy">
                  <span className="feeds-page__eyebrow">Custom feed ready</span>
                  <h3>{resolvedCustomPlan?.title || 'Custom Calendar'}</h3>
                  <p>{resolvedCustomPlan?.description || 'Use the same polished Apple, Google, and manual flow for the observances you selected.'}</p>
                </div>
                <div className="feeds-custom-plan__stats">
                  <span>{resolvedCustomPlan?.selection_count || selectedIds.length} selected</span>
                  <span>{formatDateWindow(resolvedCustomPlan?.stats?.date_window)}</span>
                  <span>
                    {resolvedCustomPlan?.stats?.next_event
                      ? `${resolvedCustomPlan.stats.next_event.summary} • ${formatFeedDate(resolvedCustomPlan.stats.next_event.start_date)}`
                      : 'Building your next observance preview'}
                  </span>
                </div>
                {selectedFestivalNames.length ? (
                  <div className="feeds-highlights">
                    {selectedFestivalNames.slice(0, 6).map((name) => (
                      <span key={name} className="feeds-highlight-chip">{name}</span>
                    ))}
                  </div>
                ) : null}
              </div>
              <div className="feeds-custom__cta-row">
                <button type="button" className="btn btn-primary btn-sm" onClick={() => handleCustomPlatform('apple')}>
                  Open in Apple Calendar
                </button>
                <button type="button" className="btn btn-primary btn-sm" onClick={() => handleCustomPlatform('google')}>
                  Copy for Google Calendar
                </button>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => handleCustomPlatform('manual')}>
                  Download .ics
                </button>
              </div>
              <div className="feeds-custom__secondary-row">
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => copyLink('Custom feed', customLink, 'Custom feed copied.', {
                  platform: 'manual',
                  title: 'Custom feed copied',
                })}>
                  {copied === 'Custom feed' ? 'Copied' : 'Copy direct link'}
                </button>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => shareLink('Custom calendar', customLink)}>
                  Share custom link
                </button>
              </div>
              <AdvancedLinkField label="Advanced manual setup" value={customLink} />
            </div>
          ) : (
            <p className="feeds-custom__hint">Select at least one festival above to generate a custom feed.</p>
          )}
        </div>
      </section>
    </section>
  );
}

export const IntegrationsPage = FeedSubscriptionsPage;

export default FeedSubscriptionsPage;
