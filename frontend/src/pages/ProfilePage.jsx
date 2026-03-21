import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { UtilityPageHeader, UtilityStatGrid } from '../consumer/UtilityPages';
import { serializeMemberState } from '../context/memberContextState';
import { useMemberContext } from '../context/useMemberContext';
import { useTemporalContext } from '../context/useTemporalContext';
import { findPresetByLocation } from '../data/locationPresets';
import { useCopy } from '../i18n/useCopy';
import './ProfilePage.css';

const THEME_OPTIONS = [
  { value: 'ink-black', label: 'Ink Black' },
  { value: 'warm-paper', label: 'Warm Paper' },
];

const NOTIFICATION_STYLES = [
  { value: 'balanced', label: 'Balanced' },
  { value: 'gentle', label: 'Gentle' },
  { value: 'focused', label: 'Focused' },
];

const ACTIVITY_OPTIONS = [
  { value: 'meditation', label: 'Meditation' },
  { value: 'travel', label: 'Travel' },
  { value: 'new_venture', label: 'New venture' },
];

export function ProfilePage() {
  const { state, setLanguage, setTheme } = useTemporalContext();
  const { copy } = useCopy();
  const {
    state: memberState,
    updatePreferences,
    importLocalState,
    clearLocalState,
  } = useMemberContext();
  const activePreset = findPresetByLocation(state.location);
  const importInputRef = useRef(null);
  const [status, setStatus] = useState('');
  const [confirmClear, setConfirmClear] = useState(false);
  const persistenceLabel = memberState.account.mode === 'guest'
    ? copy('profile.cache.guest')
    : copy('profile.cache.accountBacked');

  const summaryItems = [
    { label: 'Saved places', value: memberState.savedPlaces.length },
    { label: 'Saved festivals', value: memberState.savedFestivals.length },
    { label: 'Reminders', value: memberState.reminders.length },
    { label: 'Integrations', value: memberState.integrations.length },
  ];

  const exportLocalData = () => {
    try {
      const payload = {
        schema: 'parva-device-cache.v2',
        exportedAt: new Date().toISOString(),
        data: serializeMemberState(memberState),
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `parva-device-cache-${new Date().toISOString().slice(0, 10)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      setStatus(copy('profile.cache.exported'));
    } catch {
      setStatus(copy('profile.cache.cannotExport'));
    }
  };

  const importFromFile = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const parsed = JSON.parse(text);
      const imported = await importLocalState(parsed?.data || parsed);
      if (imported) {
        setStatus(copy('profile.cache.imported', { filename: file.name }));
        setConfirmClear(false);
      } else {
        setStatus(copy('profile.cache.cannotImport'));
      }
    } catch {
      setStatus(copy('profile.cache.invalidImport'));
    } finally {
      event.target.value = '';
    }
  };

  return (
    <section className="profile-page utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow={copy('profile.eyebrow')}
        title={copy('profile.title')}
        body={copy('profile.body')}
        links={[
          { label: `Open ${copy('common.myPlace')}`, to: '/#my-place' },
          { label: `Open ${copy('common.saved')}`, to: '/#saved' },
          { label: copy('common.methodology'), to: '/methodology' },
        ]}
        aside={(
          <>
            <span className="utility-page__eyebrow">{copy('profile.currentPlace')}</span>
            <strong>{activePreset?.label || 'Custom place'}</strong>
            <p>{state.timezone}</p>
            <Link className="btn btn-secondary btn-sm" to="/my-place">{`Open ${copy('common.myPlace')}`}</Link>
          </>
        )}
      />

      <UtilityStatGrid items={summaryItems} />

      <div className="profile-grid">
        <article className="ink-card profile-card utility-page__panel">
          <h2>{copy('profile.section.appearance')}</h2>
          <div className="profile-controls">
            <label className="ink-input">
              <span>{copy('settings.theme')}</span>
              <select value={state.theme} onChange={(event) => setTheme(event.target.value)}>
                {THEME_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </label>

            <div className="profile-links">
              <button type="button" aria-pressed={state.language === 'en'} className="btn btn-secondary btn-sm" onClick={() => setLanguage('en')}>{copy('common.english')}</button>
              <button type="button" aria-pressed={state.language === 'ne'} className="btn btn-secondary btn-sm" onClick={() => setLanguage('ne')}>{copy('common.nepali')}</button>
            </div>
            <p className="profile-card__hint">{copy('profile.hint.theme')}</p>
          </div>
        </article>

        <article className="ink-card profile-card utility-page__panel">
          <h2>{copy('profile.section.reminderBehavior')}</h2>
          <div className="profile-controls">
            <div className="profile-links">
              {NOTIFICATION_STYLES.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  aria-pressed={memberState.preferences.notificationStyle === option.value}
                  className="btn btn-secondary btn-sm"
                  onClick={() => updatePreferences({ ...memberState.preferences, notificationStyle: option.value })}
                >
                  {option.value === 'balanced' ? copy('profile.style.balanced') : option.value === 'gentle' ? copy('profile.style.gentle') : copy('profile.style.focused')}
                </button>
              ))}
            </div>

            <div className="profile-links">
              {ACTIVITY_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  aria-pressed={memberState.preferences.activityFocus === option.value}
                  className="btn btn-secondary btn-sm"
                  onClick={() => updatePreferences({ ...memberState.preferences, activityFocus: option.value })}
                >
                  {option.value === 'meditation' ? copy('profile.activity.meditation') : option.value === 'travel' ? copy('profile.activity.travel') : copy('profile.activity.newVenture')}
                </button>
              ))}
            </div>

            <div className="profile-links">
              <button
                type="button"
                aria-pressed={memberState.preferences.festivalAlerts}
                className="btn btn-secondary btn-sm"
                onClick={() => updatePreferences({ ...memberState.preferences, festivalAlerts: !memberState.preferences.festivalAlerts })}
              >
                {copy('profile.reminders.festivalAlerts', {
                  state: memberState.preferences.festivalAlerts ? copy('profile.status.on') : copy('profile.status.off'),
                })}
              </button>
              <button
                type="button"
                aria-pressed={memberState.preferences.bestTimeAlerts}
                className="btn btn-secondary btn-sm"
                onClick={() => updatePreferences({ ...memberState.preferences, bestTimeAlerts: !memberState.preferences.bestTimeAlerts })}
              >
                {copy('profile.reminders.bestTimeAlerts', {
                  state: memberState.preferences.bestTimeAlerts ? copy('profile.status.on') : copy('profile.status.off'),
                })}
              </button>
            </div>
          </div>
        </article>

        <article className="ink-card profile-card utility-page__panel">
          <h2>{copy('profile.section.deviceCache')}</h2>
          <div className="profile-card__actions">
            <p className="profile-card__hint">
              {copy('profile.cache.revision', {
                label: persistenceLabel,
                revision: memberState.persistence.revision,
              })}
            </p>
            <button type="button" className="btn btn-secondary btn-sm" onClick={exportLocalData}>{copy('profile.actions.exportJson')}</button>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => importInputRef.current?.click()}>{copy('profile.actions.importJson')}</button>
            <button type="button" className="btn btn-secondary btn-sm profile-card__danger" onClick={() => setConfirmClear((value) => !value)}>
              {confirmClear ? copy('profile.actions.cancelClear') : copy('profile.actions.clearDeviceCache')}
            </button>
            <input
              ref={importInputRef}
              type="file"
              accept="application/json"
              onChange={importFromFile}
              style={{ display: 'none' }}
            />
            {confirmClear ? (
              <div className="profile-card__confirm">
                <p>{copy('profile.cache.confirm')}</p>
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={async () => {
                    const cleared = await clearLocalState();
                    setStatus(
                      cleared
                        ? copy('profile.cache.cleared')
                        : copy('profile.cache.cannotClear'),
                    );
                    setConfirmClear(false);
                  }}
                >
                  {copy('profile.actions.confirmClear')}
                </button>
              </div>
            ) : null}
            {status ? <p className="profile-card__status">{status}</p> : null}
          </div>
        </article>

        <article className="ink-card profile-card utility-page__panel">
          <h2>{copy('profile.section.secondaryUtilities')}</h2>
          <div className="profile-links">
            <Link to="/saved">{`Open ${copy('common.saved')}`}</Link>
            <Link to="/integrations">{`Open ${copy('common.integrations')}`}</Link>
            <Link to="/methodology">{`Open ${copy('common.methodology')}`}</Link>
            <Link to="/about">{`${copy('common.about')} Parva`}</Link>
          </div>
        </article>
      </div>
    </section>
  );
}

export default ProfilePage;
