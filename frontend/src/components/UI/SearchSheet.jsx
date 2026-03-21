import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMemberContext } from '../../context/useMemberContext';
import { useDialogA11y } from '../../hooks/useDialogA11y';
import { useCopy } from '../../i18n/useCopy';
import { getSearchCommands } from '../../navigation/routeManifest';
import { trackEvent } from '../../services/analytics';
import './SearchSheet.css';

function reminderRoute(reminder) {
  if (reminder?.kind === 'festival' && reminder.id?.startsWith('festival:')) {
    return `/festivals/${reminder.id.split(':')[1]}`;
  }
  return '/saved';
}

function buildMemberResults(state, copy) {
  return [
    ...(state.savedFestivals || []).map((festival) => ({
      to: `/festivals/${festival.id}`,
      label: festival.name,
      keywords: `${festival.name} ${festival.category || ''} saved observance`,
      kind: copy('search.kind.savedFestival'),
      meta: festival.startDate || 'Festival detail',
    })),
    ...(state.savedPlaces || []).map((place) => ({
      to: '/my-place',
      label: place.label || 'Saved place',
      keywords: `${place.label || ''} ${place.timezone || ''} saved place`,
      kind: copy('search.kind.savedPlace'),
      meta: place.timezone || 'Place context',
    })),
    ...(state.reminders || []).map((reminder) => ({
      to: reminderRoute(reminder),
      label: reminder.title || 'Reminder',
      keywords: `${reminder.title || ''} reminder ${reminder.date || ''}`,
      kind: copy('search.kind.reminder'),
      meta: reminder.date || 'Saved reminder',
    })),
    ...(state.savedReadings || []).map((reading) => ({
      to: '/birth-reading',
      label: reading.title || 'Saved reading',
      keywords: `${reading.title || ''} ${reading.summary || ''} saved reading`,
      kind: copy('search.kind.savedReading'),
      meta: 'Open Birth Reading',
    })),
    ...(state.integrations || []).map((integration) => ({
      to: '/integrations',
      label: integration.title || 'Integration',
      keywords: `${integration.title || ''} ${integration.platform || ''} integration calendar`,
      kind: copy('search.kind.integration'),
      meta: integration.platform || 'Calendar integration',
    })),
  ];
}

export function SearchSheet({ open, onClose }) {
  const navigate = useNavigate();
  const { state: memberState } = useMemberContext();
  const { copy } = useCopy();
  const [query, setQuery] = useState('');
  const { dialogRef } = useDialogA11y(open, onClose);

  const results = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    const library = [
      ...getSearchCommands(copy, { includeSupport: Boolean(normalized) }),
      ...buildMemberResults(memberState, copy),
    ];
    if (!normalized) return library.slice(0, 12);
    return library.filter((item) => `${item.label} ${item.keywords} ${item.meta || ''}`.toLowerCase().includes(normalized));
  }, [copy, memberState, query]);

  if (!open) return null;

  return (
    <div className="search-sheet__overlay" role="presentation" onClick={onClose}>
      <aside
        ref={dialogRef}
        className="search-sheet"
        role="dialog"
        aria-modal="true"
        aria-labelledby="search-sheet-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="search-sheet__header">
          <div>
            <p className="search-sheet__eyebrow">{copy('common.search')}</p>
            <h2 id="search-sheet-title">{copy('search.title')}</h2>
          </div>
          <button type="button" className="search-sheet__close" onClick={onClose}>
            {copy('common.close')}
          </button>
        </div>

        <label className="ink-input">
          <span>{copy('search.inputLabel')}</span>
          <input
            type="search"
            autoFocus
            data-dialog-initial-focus="true"
            placeholder={copy('search.placeholder')}
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
          {!results.length ? <p className="search-sheet__empty">{copy('search.empty')}</p> : null}
        </div>
      </aside>
    </div>
  );
}

export default SearchSheet;
