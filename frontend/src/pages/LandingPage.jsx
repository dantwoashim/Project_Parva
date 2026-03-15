import { Link } from 'react-router-dom';
import { useUpcomingFestivals } from '../hooks/useFestivals';
import { trackEvent } from '../services/analytics';
import './LandingPage.css';

const TRUST_NOTES = [
  'Built for Nepal-focused observances, timing, and reading use cases.',
  'Method detail stays available, but never blocks the first answer.',
];

const INTENT_CARDS = [
  { to: '/today', title: 'Today', body: 'What matters right now?' },
  { to: '/best-time', title: 'Best Time', body: 'When is the clearest opening?' },
  { to: '/festivals', title: 'Festivals', body: 'What is coming up next?' },
  { to: '/birth-reading', title: 'Birth Reading', body: 'What does the reading say first?' },
];

const DEFAULT_RHYTHM_STORIES = [
  {
    tag: 'Season watch',
    title: 'The next observance should feel easy to notice.',
    body: 'Parva should keep the next meaningful date visible without forcing a dense calendar first.',
    meta: 'Calm annual rhythm',
  },
  {
    tag: 'Meaning first',
    title: 'Context should arrive before taxonomy.',
    body: 'People should understand why a day matters before they see system detail.',
    meta: 'Trust through clarity',
  },
];

function formatFestivalDate(date) {
  if (!date) return 'Date announced in app';
  const parsed = new Date(date);
  if (Number.isNaN(parsed.valueOf())) return date;
  return parsed.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
}

export function LandingPage() {
  const { festivals, loading } = useUpcomingFestivals(45, 'computed');
  const featured = (festivals || []).slice(0, 3);
  const nextFestival = featured[0] || null;
  const supportingFestivals = featured.slice(1, 3);
  const rhythmStories = supportingFestivals.length
    ? supportingFestivals.map((festival, index) => ({
        tag: index === 0 ? 'Also in view' : 'Keep in sight',
        title: festival.name,
        body: 'Open the observance when you want the story, timing, and seasonal context together.',
        meta: formatFestivalDate(festival.start_date),
        to: `/festivals/${festival.id}`,
      }))
    : DEFAULT_RHYTHM_STORIES;

  return (
    <section className="landing-page animate-fade-in-up">
      <section className="landing-hero editorial-card">
        <div className="landing-hero__copy">
          <div className="landing-hero__intro">
            <p className="landing-eyebrow">Project Parva</p>
            <span className="landing-hero__status">A calm guide to Nepal&apos;s sacred time</span>
          </div>
          <h1 className="landing-title">A calm guide to Nepal&apos;s sacred time.</h1>
          <p className="landing-subtitle">
            See what matters today, find the best time for a plan, and follow upcoming observances with clarity instead of clutter.
          </p>
          <div className="landing-actions">
            <Link className="btn btn-primary" to="/today" onClick={() => trackEvent('landing_cta_clicked', { cta: 'see_today' })}>See today</Link>
            <Link className="btn btn-secondary" to="/my-place" onClick={() => trackEvent('landing_cta_clicked', { cta: 'set_my_place' })}>Set my place</Link>
          </div>
        </div>

        <div className="landing-hero__visual">
          <article className="landing-seal-card">
            <div className="landing-seal-card__art">
              <svg viewBox="0 0 180 180" className="landing-seal-card__svg">
                <circle cx="90" cy="90" r="66" className="landing-seal-card__ring landing-seal-card__ring--outer" />
                <circle cx="90" cy="90" r="42" className="landing-seal-card__ring landing-seal-card__ring--inner" />
                <path d="M90 34 L105 90 L90 146 L75 90 Z" className="landing-seal-card__petal" />
                <path d="M34 90 L90 105 L146 90 L90 75 Z" className="landing-seal-card__petal landing-seal-card__petal--soft" />
              </svg>
            </div>
            <span>One clear answer</span>
            <strong>Meaning first</strong>
            <small>Details only when asked for.</small>
          </article>

          <article className="landing-trust-card">
            <p className="landing-trust-card__eyebrow">Why trust Parva</p>
            <h2>Built for Nepal-focused use cases, with method available when you want it.</h2>
            <ul className="landing-trust-list">
              {TRUST_NOTES.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <p className="landing-trust-card__note">
              {nextFestival
                ? `${nextFestival.name} is the next observance in view on ${formatFestivalDate(nextFestival.start_date)}.`
                : 'Upcoming observances appear here when the current calendar feed is available.'}
            </p>
          </article>
        </div>
      </section>

      <section className="landing-intents">
        <div className="landing-section-header">
          <p className="landing-eyebrow">Choose your path</p>
          <h2>Start with one clear question.</h2>
        </div>
        <div className="landing-intent-grid stagger-children">
          {INTENT_CARDS.map((card) => (
            <Link
              key={card.to}
              className="landing-intent-card editorial-card"
              to={card.to}
              onClick={() => trackEvent('path_card_selected', { destination: card.to, source: 'landing' })}
            >
              <strong>{card.title}</strong>
              <span>{card.body}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="landing-rhythm editorial-card">
        <div className="landing-section-header">
          <p className="landing-eyebrow">Festival rhythm</p>
          <h2>Keep the next observance in view without opening the full calendar first.</h2>
        </div>
        {loading ? (
          <div className="landing-rhythm__grid">
            <div className="skeleton landing-featured__skeleton" />
            <div className="landing-rhythm__stack">
              {Array.from({ length: 2 }).map((_, index) => (
                <div key={index} className="skeleton landing-featured__skeleton" />
              ))}
            </div>
          </div>
        ) : (
          <div className="landing-rhythm__grid stagger-children">
            {nextFestival ? (
              <Link className="landing-rhythm__lead" to={`/festivals/${nextFestival.id}`}>
                <span className="landing-featured__tag">Next observance</span>
                <strong>{nextFestival.name}</strong>
                <p>
                  Open the observance when you want the story, timing, and calendar context together.
                </p>
                <div className="landing-rhythm__lead-meta">
                  <span>{nextFestival.category || 'Festival'}</span>
                  <span>{formatFestivalDate(nextFestival.start_date)}</span>
                </div>
              </Link>
            ) : (
              <article className="landing-rhythm__lead landing-rhythm__lead--fallback">
                <span className="landing-featured__tag">Festival rhythm</span>
                <strong>Festival highlights will appear here when the current feed is available.</strong>
                <p>Use the full festival view when the home feed is quiet.</p>
                <div className="landing-rhythm__lead-actions">
                  <Link className="btn btn-secondary" to="/festivals">Open festivals</Link>
                </div>
              </article>
            )}

            <div className="landing-rhythm__stack">
              {rhythmStories.map((story) => {
                const Card = story.to ? Link : 'article';
                return (
                  <Card
                    key={`${story.title}-${story.meta}`}
                    className="landing-rhythm__story"
                    {...(story.to ? { to: story.to } : {})}
                  >
                    <span>{story.tag}</span>
                    <strong>{story.title}</strong>
                    <p>{story.body}</p>
                    <small>{story.meta}</small>
                  </Card>
                );
              })}
            </div>
          </div>
        )}
      </section>
    </section>
  );
}

export default LandingPage;
