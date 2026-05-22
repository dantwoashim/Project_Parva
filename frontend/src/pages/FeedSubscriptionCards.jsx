import { formatFeedDate, integrationPlatformLabel } from './feedSubscriptionUtils.js';

export function FeedPresetCard({ item, isActive, onSelect }) {
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

export function PlatformPanel({
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

export function AdvancedLinkField({ label, value }) {
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

export function ConnectedIntegrationCard({ integration, onOpen, onCopy, onRemove }) {
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
          <p>{`Next: ${integration.nextEvent.summary}${integration.nextEvent.start_date ? ` - ${formatFeedDate(integration.nextEvent.start_date)}` : ''}`}</p>
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
