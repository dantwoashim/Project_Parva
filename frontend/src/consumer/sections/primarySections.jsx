import { Link } from 'react-router-dom';
import { EvidenceDrawer } from '../../components/UI/EvidenceDrawer';
import { CONSUMER_BEST_TIME_OPTIONS, CONSUMER_FESTIVAL_FILTERS } from '../consumerViewModels';
import { CompactEmpty, ConsumerSectionHeader, ConsumerSectionShell } from './shared';

export function TodaySection({
  id = 'today',
  viewModel,
  dateValue,
  onDateChange,
  action,
  title,
  body,
  showDateInput = true,
  showEvidence = true,
  bestTimeHref = '/best-time',
  bestTimeActionLabel,
}) {
  const supportCards = [];

  if (viewModel?.sunrise || viewModel?.sunset) {
    supportCards.push(
      <article key="sun" className="consumer-home__surface consumer-home__support-card">
        <span className="consumer-home__kicker">Sun rhythm</span>
        <div className="consumer-home__support-split">
          {viewModel?.sunrise ? <strong>Sunrise: {viewModel.sunrise}</strong> : null}
          {viewModel?.sunset ? <strong>Sunset: {viewModel.sunset}</strong> : null}
        </div>
        <p>{viewModel?.dayTone?.value || 'Balanced'}</p>
      </article>,
    );
  }

  if (viewModel?.supporting || viewModel?.dayTone?.value) {
    supportCards.push(
      <article key="highlights" className="consumer-home__surface consumer-home__support-card">
        <span className="consumer-home__kicker">Highlights</span>
        <strong>{viewModel?.dayTone?.value || 'Balanced day tone'}</strong>
        <p>{viewModel?.supporting || 'Live timing highlights will appear here when available.'}</p>
      </article>,
    );
  }

  if (showEvidence && viewModel?.evidence) {
    supportCards.push(
      <article key="method" className="consumer-home__surface consumer-home__support-card">
        <span className="consumer-home__kicker">Method</span>
        <EvidenceDrawer {...viewModel.evidence} />
      </article>,
    );
  }

  return (
    <section id={id} className="consumer-home__section consumer-home__section--hero">
      <ConsumerSectionHeader
        eyebrow="Today"
        title={title || viewModel?.headline || 'Today'}
        body={body || viewModel?.summary || 'Start with the meaning of the day, then open the strongest timing window only if you need it.'}
        action={action}
      />

      <ConsumerSectionShell tone="hero">
        <div className="consumer-home__today-grid">
          <article className="consumer-home__surface consumer-home__surface--hero-card">
            <div className="consumer-home__date-stack">
              <span className="consumer-home__kicker">{viewModel?.bsDate || 'Bikram Sambat date pending'}</span>
              <strong className="consumer-home__hero-date">{viewModel?.gregorianDate || dateValue || 'Date pending'}</strong>
            </div>
            <p className="consumer-home__hero-story">
              {viewModel?.summary || 'The day reading will appear here as soon as the live compass returns.'}
            </p>
            {viewModel?.observances?.[0] ? (
              <div className="consumer-home__observance-row">
                <span>Today&apos;s observance</span>
                <strong>{viewModel.observances[0].title}</strong>
              </div>
            ) : null}
            <div className="consumer-home__hero-actions">
              <Link className="btn btn-primary" to={bestTimeHref}>
                {bestTimeActionLabel || (viewModel?.bestWindow?.value ? `Best time today: ${viewModel.bestWindow.value}` : 'Open Best Time')}
              </Link>
              {showDateInput ? (
                <label className="ink-input consumer-home__date-input">
                  <span>Date</span>
                  <input type="date" value={dateValue} onChange={(event) => onDateChange(event.target.value)} />
                </label>
              ) : null}
            </div>
          </article>

          {supportCards.length ? (
            <div className="consumer-home__today-rail">{supportCards}</div>
          ) : null}
        </div>
      </ConsumerSectionShell>
    </section>
  );
}

export function BestTimeSection({
  id = 'best-time',
  viewModel,
  type,
  onTypeChange,
  dateValue,
  onDateChange,
  placeLabel,
  onCyclePlace,
  action,
  title = 'Open the answer before the schedule.',
  body,
  showEvidenceInSidebar = true,
  timelineLimit = 4,
}) {
  const alternateCards = (viewModel?.alternates || []).slice(0, 2);

  return (
    <section id={id} className="consumer-home__section">
      <ConsumerSectionHeader
        eyebrow="Best Time"
        title={title}
        body={body || viewModel?.intro || 'The first answer should be clear: one best window, one alternate, one caution, and a visual rhythm of the day.'}
        action={action}
      />

      <ConsumerSectionShell tone="timing">
        <div className="consumer-home__control-bar consumer-home__surface">
          <label className="ink-input">
            <span>Activity</span>
            <select value={type} onChange={(event) => onTypeChange(event.target.value)}>
              {CONSUMER_BEST_TIME_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
          <label className="ink-input">
            <span>Date</span>
            <input type="date" value={dateValue} onChange={(event) => onDateChange(event.target.value)} />
          </label>
          <button type="button" className="consumer-home__place-pill" onClick={onCyclePlace}>
            <span>Place</span>
            <strong>{placeLabel}</strong>
          </button>
        </div>

        <div className="consumer-home__best-grid">
          <article className="consumer-home__surface consumer-home__surface--best">
            <span className="consumer-home__kicker">Primary window</span>
            <h3>{viewModel?.best?.title || 'Window pending'}</h3>
            <p>{viewModel?.best?.note || 'The clearest timing answer will appear here.'}</p>
            {viewModel?.avoid?.title ? (
              <div className="consumer-home__warning-row">
                <strong>Keep light:</strong>
                <span>{viewModel.avoid.title}</span>
              </div>
            ) : null}
          </article>

          <article className="consumer-home__surface consumer-home__sidebar">
            <span className="consumer-home__kicker">Alternates and context</span>
            <div className="consumer-home__mini-stack">
              {alternateCards.length ? (
                alternateCards.map((item) => (
                  <div key={item.id} className="consumer-home__mini-card">
                    <strong>{item.title}</strong>
                    <p>{item.note}</p>
                  </div>
                ))
              ) : (
                <div className="consumer-home__mini-card">
                  <strong>No alternate is stronger than the lead window.</strong>
                  <p>When the schedule is clean, the first answer should stay simple.</p>
                </div>
              )}
              {showEvidenceInSidebar && viewModel?.evidence ? <EvidenceDrawer {...viewModel.evidence} /> : null}
            </div>
          </article>
        </div>

        {viewModel?.timeline?.length ? (
          <article className="consumer-home__surface consumer-home__timeline-card">
            <div className="consumer-home__timeline-header">
              <h3>Full-day visual timeline</h3>
              <p>{viewModel.activityLabel} for {viewModel.placeLabel}</p>
            </div>
            <div className="consumer-home__timeline-track">
              {viewModel.timeline.slice(0, timelineLimit).map((item) => (
                <div
                  key={item.id}
                  className={`consumer-home__timeline-segment consumer-home__timeline-segment--${item.tone} ${item.compact ? 'is-compact' : ''}`.trim()}
                  style={{
                    left: item.left,
                    right: item.right,
                    top: `${18 + (item.lane || 0) * 56}px`,
                  }}
                >
                  <strong>{item.time}</strong>
                  <span className="consumer-home__timeline-label">{item.title}</span>
                  <span className="consumer-home__timeline-tone">
                    {item.tone === 'strong'
                      ? 'Recommended'
                      : item.tone === 'good'
                        ? 'Alternate'
                        : item.tone === 'avoid'
                          ? 'Avoid'
                          : 'Mixed'}
                  </span>
                </div>
              ))}
            </div>
            <div className="consumer-home__timeline-footer">
              <div>
                <strong>Guidance</strong>
                <p>{viewModel?.best?.note || 'Timing guidance will appear here.'}</p>
              </div>
              <div>
                <strong>Outcome</strong>
                <p>{viewModel?.selection?.note || 'Use the first answer before scanning the full ranking.'}</p>
              </div>
            </div>
          </article>
        ) : null}
      </ConsumerSectionShell>
    </section>
  );
}

export function FestivalsSection({
  id = 'festivals',
  viewModel,
  search,
  onSearchChange,
  category,
  onCategoryChange,
  action,
  title = 'Keep the next observance in view.',
  body,
  onSaveFestival,
  onToggleReminder,
}) {
  return (
    <section id={id} className="consumer-home__section">
      <ConsumerSectionHeader
        eyebrow="Festivals"
        title={title}
        body={body || viewModel?.subtitle || 'Browse the next observance with guided search and compact filters, then open the full explorer only when you need the wider calendar.'}
        action={action}
      />

      <ConsumerSectionShell tone="festival">
        <div className="consumer-home__festival-controls consumer-home__surface">
          <label className="consumer-home__search">
            <span>Search</span>
            <input
              type="search"
              value={search}
              placeholder="Search observances"
              onChange={(event) => onSearchChange(event.target.value)}
            />
          </label>
          <div className="consumer-home__chip-row">
            {CONSUMER_FESTIVAL_FILTERS.map((option) => (
              <button
                key={option.value || 'all'}
                type="button"
                className={`consumer-home__chip ${category === option.value ? 'is-active' : ''}`.trim()}
                onClick={() => onCategoryChange(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {viewModel?.featured ? (
          <div className="consumer-home__festival-grid">
            <article className="consumer-home__surface consumer-home__festival-feature">
              <div className="consumer-home__art-slot consumer-home__art-slot--festival">
                <span>{viewModel.featured.title}</span>
              </div>
              <div className="consumer-home__festival-copy">
                <span className="consumer-home__kicker">{viewModel.featured.dateLabel}</span>
                <h3>{viewModel.featured.title}</h3>
                <p>{viewModel.featured.summary}</p>
                <div className="consumer-home__festival-actions">
                  <Link className="btn btn-primary btn-sm" to={viewModel.featured.href}>Open observance</Link>
                  {onSaveFestival ? (
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => onSaveFestival(viewModel.featured)}>
                      Save
                    </button>
                  ) : null}
                  {onToggleReminder ? (
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => onToggleReminder(viewModel.featured)}>
                      Reminder
                    </button>
                  ) : null}
                </div>
              </div>
            </article>

            <div className="consumer-home__festival-list">
              {(viewModel.supporting.length ? viewModel.supporting : viewModel.timelineCards.slice(1, 4)).length ? (
                (viewModel.supporting.length ? viewModel.supporting : viewModel.timelineCards.slice(1, 4)).map((item) => (
                  <article key={item.id} className="consumer-home__surface consumer-home__festival-item">
                    <div className="consumer-home__art-slot consumer-home__art-slot--mini">
                      <span>{item.title}</span>
                    </div>
                    <div>
                      <span className="consumer-home__kicker">{item.dateLabel}</span>
                      <h3>{item.title}</h3>
                      <p>{item.summary}</p>
                      <Link className="consumer-home__text-link" to={item.href}>Open</Link>
                    </div>
                  </article>
                ))
              ) : (
                <CompactEmpty
                  title="The featured observance is the clearest next step."
                  body="More supporting observances will appear here when the current timeline slice is fuller."
                />
              )}
            </div>
          </div>
        ) : (
          <CompactEmpty
            title={viewModel?.emptyState?.title || 'No observances are in view yet.'}
            body={viewModel?.emptyState?.body || 'Try a broader search or open the full festival explorer.'}
          />
        )}
      </ConsumerSectionShell>
    </section>
  );
}

export function MyPlaceSection({
  id = 'my-place',
  viewModel,
  languageLabel,
  timezoneLabel,
  notificationStyle,
  activityFocus,
  placeLabel,
  action,
  title = 'Let place change the answer, not the complexity.',
  body,
  onSavePlace,
  onCyclePlace,
}) {
  return (
    <section id={id} className="consumer-home__section">
      <ConsumerSectionHeader
        eyebrow="My Place"
        title={title}
        body={body || viewModel?.subtitle || 'Your saved place, current context, and timing shift should stay visible without exposing raw coordinates first.'}
        action={action}
      />

      <ConsumerSectionShell tone="place">
        <div className="consumer-home__place-grid">
          <article className="consumer-home__surface consumer-home__place-hero">
            <div className="consumer-home__art-slot consumer-home__art-slot--sanctuary">
              <span>{viewModel?.placeLabel || placeLabel}</span>
            </div>
            <div className="consumer-home__place-copy">
              <h3>{viewModel?.placeLabel || placeLabel}</h3>
              <p>{viewModel?.savedStatus || 'Saved place details remain local-first on this device.'}</p>
              <div className="consumer-home__festival-actions">
                {onSavePlace ? (
                  <button type="button" className="btn btn-primary btn-sm" onClick={onSavePlace}>
                    Save this place
                  </button>
                ) : null}
                {onCyclePlace ? (
                  <button type="button" className="btn btn-secondary btn-sm" onClick={onCyclePlace}>
                    Change place
                  </button>
                ) : null}
              </div>
            </div>
          </article>

          <article className="consumer-home__surface consumer-home__place-context">
            <div className="consumer-home__art-slot consumer-home__art-slot--context">
              <span>{viewModel?.contextTitle || 'Current context'}</span>
            </div>
            <h3>{viewModel?.contextTitle || 'Current context'}</h3>
            <p>{viewModel?.contextSummary || 'Place-aware context will appear here when available.'}</p>
          </article>
        </div>

        <div className="consumer-home__place-secondary">
          <article className="consumer-home__surface consumer-home__place-panel">
            <span className="consumer-home__kicker">Preferences</span>
            <h3>{languageLabel} / {timezoneLabel}</h3>
            <p>{notificationStyle} notifications with {activityFocus} focus.</p>
          </article>

          <article className="consumer-home__surface consumer-home__place-panel">
            <span className="consumer-home__kicker">Festival reminders</span>
            <div className="consumer-home__mini-stack">
              {viewModel?.reminders?.length ? (
                viewModel.reminders.map((item) => (
                  <div key={item.id} className="consumer-home__mini-card">
                    <strong>{item.title}</strong>
                    <p>{item.note}</p>
                  </div>
                ))
              ) : (
                <div className="consumer-home__mini-card">
                  <strong>No reminders yet</strong>
                  <p>Saved observances and best-time reminders will stay here without taking over the whole page.</p>
                </div>
              )}
            </div>
          </article>

          <article className="consumer-home__surface consumer-home__place-panel">
            <span className="consumer-home__kicker">Daily inspiration</span>
            <h3>{viewModel?.cards?.[2]?.label || 'Daily inspiration'}</h3>
            <p>{viewModel?.cards?.[2]?.value || 'Quiet ritual space changes how the day is felt.'}</p>
          </article>
        </div>
      </ConsumerSectionShell>
    </section>
  );
}
