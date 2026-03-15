import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMemberContext } from '../../context/useMemberContext';
import { trackEvent } from '../../services/analytics';
import './SearchSheet.css';

const COMMANDS = [
  { to: '/today', label: 'Today', keywords: 'today daily now', kind: 'Page', meta: 'Daily guidance' },
  { to: '/best-time', label: 'Best Time', keywords: 'muhurta best time timing', kind: 'Page', meta: 'Find the clearest opening' },
  { to: '/festivals', label: 'Festivals', keywords: 'festivals observances calendar', kind: 'Page', meta: 'Browse observances' },
  { to: '/my-place', label: 'My Place', keywords: 'place location sunrise city', kind: 'Page', meta: 'Personal timing context' },
  { to: '/birth-reading', label: 'Birth Reading', keywords: 'birth reading kundali chart', kind: 'Page', meta: 'Interpretive chart reading' },
  { to: '/saved', label: 'Saved', keywords: 'saved reminders places readings integrations', kind: 'Page', meta: 'All retained items' },
  { to: '/profile', label: 'Profile', keywords: 'profile preferences saved local export import backup', kind: 'Page', meta: 'Preferences and local data controls' },
  { to: '/integrations', label: 'Integrations', keywords: 'calendar sync feeds', kind: 'Page', meta: 'Calendar connections' },
  { to: '/methodology', label: 'Methodology', keywords: 'trust method evidence', kind: 'Page', meta: 'Trust and method' },
  { to: '/about', label: 'About', keywords: 'about parva help', kind: 'Page', meta: 'Product overview' },
];

function reminderRoute(reminder) {
  if (reminder?.kind === 'festival' && reminder.id?.startsWith('festival:')) {
    return `/festivals/${reminder.id.split(':')[1]}`;
  }
  return '/saved';
}

function buildMemberResults(state) {
  return [
    ...(state.savedFestivals || []).map((festival) => ({
      to: `/festivals/${festival.id}`,
      label: festival.name,
      keywords: `${festival.name} ${festival.category || ''} saved observance`,
      kind: 'Saved observance',
      meta: festival.startDate || 'Festival detail',
    })),
    ...(state.savedPlaces || []).map((place) => ({
      to: '/my-place',
      label: place.label || 'Saved place',
      keywords: `${place.label || ''} ${place.timezone || ''} saved place`,
      kind: 'Saved place',
      meta: place.timezone || 'Place context',
    })),
    ...(state.reminders || []).map((reminder) => ({
      to: reminderRoute(reminder),
      label: reminder.title || 'Reminder',
      keywords: `${reminder.title || ''} reminder ${reminder.date || ''}`,
      kind: 'Reminder',
      meta: reminder.date || 'Saved reminder',
    })),
    ...(state.savedReadings || []).map((reading) => ({
      to: '/birth-reading',
      label: reading.title || 'Saved reading',
      keywords: `${reading.title || ''} ${reading.summary || ''} saved reading`,
      kind: 'Saved reading',
      meta: 'Open Birth Reading',
    })),
    ...(state.integrations || []).map((integration) => ({
      to: '/integrations',
      label: integration.title || 'Integration',
      keywords: `${integration.title || ''} ${integration.platform || ''} integration calendar`,
      kind: 'Integration',
      meta: integration.platform || 'Calendar integration',
    })),
  ];
}

export function SearchSheet({ open, onClose }) {
  const navigate = useNavigate();
  const { state: memberState } = useMemberContext();
  const [query, setQuery] = useState('');

  const results = useMemo(() => {
    const library = [...COMMANDS, ...buildMemberResults(memberState)];
    const normalized = query.trim().toLowerCase();
    if (!normalized) return library.slice(0, 12);
    return library.filter((item) => `${item.label} ${item.keywords} ${item.meta || ''}`.toLowerCase().includes(normalized));
  }, [memberState, query]);

  if (!open) return null;

  return (
    <div className="search-sheet__overlay" role="presentation" onClick={onClose}>
      <aside
        className="search-sheet"
        role="dialog"
        aria-modal="true"
        aria-label="Search Parva"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="search-sheet__header">
          <div>
            <p className="search-sheet__eyebrow">Search</p>
            <h2>Jump to the part of Parva you need.</h2>
          </div>
          <button type="button" className="search-sheet__close" onClick={onClose}>
            Close
          </button>
        </div>

        <label className="ink-input">
          <span>Find a page or saved item</span>
          <input
            type="search"
            autoFocus
            placeholder="Today, Dashain, My Place, Integrations..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>

        <div className="search-sheet__results" role="list">
          {results.map((item) => (
            <button
              key={`${item.kind}-${item.to}-${item.label}`}
              type="button"
              className="search-sheet__result"
              role="listitem"
              onClick={() => {
                trackEvent('path_card_selected', { destination: item.to, source: 'search', kind: item.kind });
                navigate(item.to);
                onClose();
              }}
            >
              <div className="search-sheet__result-top">
                <small>{item.kind}</small>
                <strong>{item.label}</strong>
              </div>
              <span>{item.meta || item.keywords}</span>
            </button>
          ))}
          {!results.length ? <p className="search-sheet__empty">No matching pages or saved items yet.</p> : null}
        </div>
      </aside>
    </div>
  );
}

export default SearchSheet;
