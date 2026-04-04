import { Link } from 'react-router-dom';
import { SavedSection } from '../consumer/ConsumerSections';
import { useMemberContext } from '../context/useMemberContext';
import './SavedPage.css';

function EmptyState({ title, body, linkTo, linkLabel }) {
  return (
    <article className="ink-card saved-card saved-card--empty">
      <h3>{title}</h3>
      <p>{body}</p>
      <Link className="btn btn-secondary btn-sm" to={linkTo}>{linkLabel}</Link>
    </article>
  );
}

function reminderLink(reminder) {
  if (reminder?.kind === 'festival' && reminder.id?.startsWith('festival:')) {
    return `/festivals/${reminder.id.split(':')[1]}`;
  }
  return null;
}

function formatSavedDate(value) {
  if (!value) return null;
  try {
    return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
  } catch {
    return value;
  }
}

function integrationLabel(integration) {
  if (integration.platformFamily === 'apple') return 'Apple Calendar';
  if (integration.platformFamily === 'google') return 'Google Calendar';
  return 'Calendar file or direct feed';
}

export function SavedPage() {
  const {
    state,
    removeFestival,
    removePlace,
    removeReading,
    removeReminder,
    removeIntegration,
  } = useMemberContext();

  async function copyIntegrationLink(integration) {
    const value = integration.feedUrl || integration.link;
    if (!value || typeof navigator?.clipboard?.writeText !== 'function') return;
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      // Ignore clipboard failures in this lightweight saved-state view.
    }
  }

  return (
    <section className="saved-page animate-fade-in-up consumer-route">
      <SavedSection
        id={undefined}
        memberState={state}
        action={<Link className="btn btn-secondary btn-sm" to="/#saved">Jump to home section</Link>}
        title="Keep places, observances, reminders, and readings close at hand."
        body="Parva stays guest-first, and saved state now lives locally in this browser. Use Profile when you want to back it up or clear it deliberately."
      />

      <div className="saved-grid">
        <section className="saved-column">
          <div className="saved-section-head">
            <h2>Places</h2>
            <span>{state.savedPlaces.length}</span>
          </div>
          {state.savedPlaces.length ? state.savedPlaces.map((place) => (
            <article key={place.id} className="ink-card saved-card">
              <div>
                <strong>{place.label}</strong>
                <p>{place.timezone}</p>
              </div>
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => removePlace(place.id)}>
                Remove
              </button>
            </article>
          )) : (
            <EmptyState
              title="No saved places yet"
              body="Save your place from My Place when you want Parva to remember how timing shifts for you."
              linkTo="/my-place"
              linkLabel="Open My Place"
            />
          )}
        </section>

        <section className="saved-column">
          <div className="saved-section-head">
            <h2>Observances</h2>
            <span>{state.savedFestivals.length}</span>
          </div>
          {state.savedFestivals.length ? state.savedFestivals.map((festival) => (
            <article key={festival.id} className="ink-card saved-card">
              <div>
                <strong>{festival.name}</strong>
                <p>{festival.startDate || festival.category || 'Festival'}</p>
              </div>
              <div className="saved-card__actions">
                <Link className="btn btn-secondary btn-sm" to={`/festivals/${festival.id}`}>Open</Link>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => removeFestival(festival.id)}>
                  Remove
                </button>
              </div>
            </article>
          )) : (
            <EmptyState
              title="No saved observances yet"
              body="Save a festival from its detail page when you want to come back later or set a reminder."
              linkTo="/festivals"
              linkLabel="Browse festivals"
            />
          )}
        </section>

        <section className="saved-column">
          <div className="saved-section-head">
            <h2>Reminders</h2>
            <span>{state.reminders.length}</span>
          </div>
          {state.reminders.length ? state.reminders.map((reminder) => {
            const to = reminderLink(reminder);
            return (
              <article key={reminder.id} className="ink-card saved-card">
                <div>
                  <strong>{reminder.title}</strong>
                  <p>{reminder.date || 'Date appears when available'}</p>
                </div>
                <div className="saved-card__actions">
                  {to ? <Link className="btn btn-secondary btn-sm" to={to}>Open</Link> : null}
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => removeReminder(reminder.id)}>
                    Remove
                  </button>
                </div>
              </article>
            );
          }) : (
            <EmptyState
              title="No reminders yet"
              body="Add a reminder from an observance or profile flow when you want Parva to keep it in view."
              linkTo="/festivals"
              linkLabel="Find an observance"
            />
          )}
        </section>

        <section className="saved-column">
          <div className="saved-section-head">
            <h2>Birth readings</h2>
            <span>{state.savedReadings.length}</span>
          </div>
          {state.savedReadings.length ? state.savedReadings.map((reading) => (
            <article key={reading.id} className="ink-card saved-card">
              <div>
                <strong>{reading.title}</strong>
                <p>{reading.summary}</p>
              </div>
              <div className="saved-card__actions">
                <Link className="btn btn-secondary btn-sm" to="/birth-reading">Open</Link>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => removeReading(reading.id)}>
                  Remove
                </button>
              </div>
            </article>
          )) : (
            <EmptyState
              title="No saved readings yet"
              body="Save a reading from Birth Reading when you want to revisit the summary without re-entering details."
              linkTo="/birth-reading"
              linkLabel="Open Birth Reading"
            />
          )}
        </section>

        <section className="saved-column">
          <div className="saved-section-head">
            <h2>Integrations</h2>
            <span>{state.integrations.length}</span>
          </div>
          {state.integrations.length ? state.integrations.map((integration) => (
            <article key={integration.platform} className="ink-card saved-card">
              <div className="saved-integration">
                <strong>{integration.title}</strong>
                <p>{integrationLabel(integration)}</p>
                <div className="saved-integration__meta">
                  {integration.feedKind ? <span>{integration.feedKind === 'custom' ? 'Custom feed' : 'Preset feed'}</span> : null}
                  {integration.feedTitle ? <span>{integration.feedTitle}</span> : null}
                  {integration.selectionCount ? <span>{integration.selectionCount} selected</span> : null}
                </div>
                {integration.nextEvent?.summary ? (
                  <p>{`Next: ${integration.nextEvent.summary}${integration.nextEvent.start_date ? ` • ${formatSavedDate(integration.nextEvent.start_date)}` : ''}`}</p>
                ) : null}
                {integration.dateWindow?.start && integration.dateWindow?.end ? (
                  <p>{`Window: ${formatSavedDate(integration.dateWindow.start)} - ${formatSavedDate(integration.dateWindow.end)}`}</p>
                ) : null}
                {integration.syncExpectation ? <p>{integration.syncExpectation}</p> : null}
                {integration.selectedFestivalNames?.length ? (
                  <div className="saved-integration__chips">
                    {integration.selectedFestivalNames.slice(0, 4).map((name) => (
                      <span key={`${integration.platform}-${name}`}>{name}</span>
                    ))}
                  </div>
                ) : null}
              </div>
              <div className="saved-card__actions">
                {integration.link ? (
                  <a className="btn btn-secondary btn-sm" href={integration.link} target="_blank" rel="noreferrer">
                    Open
                  </a>
                ) : null}
                {(integration.feedUrl || integration.link) ? (
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => copyIntegrationLink(integration)}>
                    Copy link
                  </button>
                ) : null}
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => removeIntegration(integration.platform)}>
                  Remove
                </button>
              </div>
            </article>
          )) : (
            <EmptyState
              title="No integrations yet"
              body="Connect a calendar from Integrations when you want Parva to travel with your existing tools."
              linkTo="/integrations"
              linkLabel="Open integrations"
            />
          )}
        </section>
      </div>
    </section>
  );
}

export default SavedPage;
