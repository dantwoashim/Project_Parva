import { Link } from 'react-router-dom';
import { CompactEmpty, ConsumerSectionHeader, ConsumerSectionShell } from './shared';

export function BirthReadingSection({
  id = 'birth-reading',
  viewModel,
  birthDateTime,
  onBirthDateTimeChange,
  placeLabel,
  timezoneLabel,
  action,
  title = 'Start with the reading, not the chart wiring.',
  body,
  onSaveReading,
  loading,
  error,
}) {
  return (
    <section id={id} className="consumer-home__section">
      <ConsumerSectionHeader
        eyebrow="Birth Reading"
        title={title}
        body={body || viewModel?.thesis || 'The first-page reading should stay interpretive and human before the graph and detail tables.'}
        action={action}
      />

      <ConsumerSectionShell tone="birth">
        <div className="consumer-home__control-bar consumer-home__surface">
          <label className="ink-input">
            <span>Birth date and time</span>
            <input type="datetime-local" value={birthDateTime} onChange={(event) => onBirthDateTimeChange(event.target.value)} />
          </label>
          <div className="consumer-home__birth-meta">
            <span>Place</span>
            <strong>{placeLabel}</strong>
          </div>
          <div className="consumer-home__birth-meta">
            <span>Timezone</span>
            <strong>{timezoneLabel}</strong>
          </div>
        </div>

        {viewModel ? (
          <div className="consumer-home__birth-grid">
            <article className="consumer-home__surface consumer-home__birth-hero">
              <span className="consumer-home__kicker">Chart thesis</span>
              <h3>{viewModel.title}</h3>
              <p>{viewModel.thesis}</p>
              {onSaveReading ? (
                <button type="button" className="btn btn-primary btn-sm" onClick={onSaveReading}>
                  Save reading
                </button>
              ) : null}
            </article>

            <div className="consumer-home__birth-patterns">
              {viewModel.patterns.map((item) => (
                <article key={item.label} className="consumer-home__surface consumer-home__birth-card">
                  <span className="consumer-home__kicker">{item.label}</span>
                  <h3>{item.value}</h3>
                  <p>{item.note}</p>
                </article>
              ))}
            </div>
          </div>
        ) : (
          <CompactEmpty
            title={loading ? 'Building a live birth summary...' : error || 'Birth Reading is not ready yet.'}
            body={loading ? 'The compact thesis appears here when the chart payload returns.' : 'Try another birth time or open the full Birth Reading route.'}
          />
        )}
      </ConsumerSectionShell>
    </section>
  );
}

export function SavedSection({
  id = 'saved',
  memberState,
  action,
  title = 'Keep what matters close.',
  body = 'Saved places, observances, reminders, and readings should stay visible without taking over the whole product.',
}) {
  const savedSummary = [
    { label: 'Places', value: memberState.savedPlaces.length || 0 },
    { label: 'Observances', value: memberState.savedFestivals.length || 0 },
    { label: 'Reminders', value: memberState.reminders.length || 0 },
    { label: 'Readings', value: memberState.savedReadings.length || 0 },
  ];
  const hasSavedState = Boolean(
    memberState.savedPlaces.length
    || memberState.savedFestivals.length
    || memberState.reminders.length
    || memberState.savedReadings.length,
  );

  return (
    <section id={id} className="consumer-home__section">
      <ConsumerSectionHeader eyebrow="Saved" title={title} body={body} action={action} />

      <ConsumerSectionShell tone="saved">
        {hasSavedState ? (
          <div className="consumer-home__saved-summary">
            {savedSummary.map((item) => (
              <article key={item.label} className="consumer-home__surface consumer-home__saved-card">
                <span className="consumer-home__kicker">{item.label}</span>
                <strong>{item.value}</strong>
              </article>
            ))}
          </div>
        ) : null}

        <div className="consumer-home__saved-grid">
          {memberState.savedFestivals.slice(0, 2).map((festival) => (
            <article key={festival.id} className="consumer-home__surface consumer-home__saved-item">
              <h3>{festival.name}</h3>
              <p>{festival.startDate || festival.category || 'Saved observance'}</p>
              <Link className="consumer-home__text-link" to={`/festivals/${festival.id}`}>Open observance</Link>
            </article>
          ))}
          {memberState.savedPlaces.slice(0, 1).map((place) => (
            <article key={place.id} className="consumer-home__surface consumer-home__saved-item">
              <h3>{place.label}</h3>
              <p>{place.timezone}</p>
              <Link className="consumer-home__text-link" to="/my-place">Open My Place</Link>
            </article>
          ))}
          {memberState.savedReadings.slice(0, 1).map((reading) => (
            <article key={reading.id} className="consumer-home__surface consumer-home__saved-item">
              <h3>{reading.title}</h3>
              <p>{reading.summary}</p>
              <Link className="consumer-home__text-link" to="/birth-reading">Open Birth Reading</Link>
            </article>
          ))}
          {!hasSavedState ? (
            <CompactEmpty
              title="Saved stays quiet until you need it."
              body="Save a place, an observance, or a reading and it will appear here instead of a giant empty dashboard block."
            />
          ) : null}
        </div>
      </ConsumerSectionShell>
    </section>
  );
}
