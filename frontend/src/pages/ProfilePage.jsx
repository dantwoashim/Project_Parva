import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMemberContext } from '../context/useMemberContext';
import { serializeMemberState } from '../context/memberContextState';
import { useTemporalContext } from '../context/useTemporalContext';
import { findPresetByLocation } from '../data/locationPresets';
import './ProfilePage.css';

export function ProfilePage() {
  const { state, setLanguage, setTheme } = useTemporalContext();
  const {
    state: memberState,
    updatePreferences,
    importLocalState,
    clearLocalState,
  } = useMemberContext();
  const importInputRef = useRef(null);
  const [localDataStatus, setLocalDataStatus] = useState('');
  const [confirmClear, setConfirmClear] = useState(false);
  const activePreset = findPresetByLocation(state.location);
  const hasLocalState = summaryCount(memberState) > 0;

  const summaryItems = [
    { label: 'Saved places', value: memberState.savedPlaces.length },
    { label: 'Saved observances', value: memberState.savedFestivals.length },
    { label: 'Reminders', value: memberState.reminders.length },
    { label: 'Readings', value: memberState.savedReadings.length },
    { label: 'Integrations', value: memberState.integrations.length },
  ];

  const exportLocalData = () => {
    const payload = {
      schema: 'parva-local-state.v1',
      exportedAt: new Date().toISOString(),
      data: serializeMemberState(memberState),
    };

    try {
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `parva-local-data-${new Date().toISOString().slice(0, 10)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      setLocalDataStatus('Local data exported as JSON for this device.');
    } catch {
      setLocalDataStatus('Local data could not be exported in this browser.');
    }
  };

  const importFromFile = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const parsed = JSON.parse(text);
      importLocalState(parsed?.data || parsed);
      setLocalDataStatus(`${file.name} was imported into local Parva data.`);
      setConfirmClear(false);
    } catch {
      setLocalDataStatus('That file could not be imported. Use a Parva local data export JSON file.');
    } finally {
      event.target.value = '';
    }
  };

  const handleClearLocalData = () => {
    clearLocalState();
    setLocalDataStatus('Local saved items and reminder preferences were cleared from this device.');
    setConfirmClear(false);
  };

  return (
    <section className="profile-page animate-fade-in-up">
      <header className="profile-hero editorial-card">
        <div>
          <p className="landing-eyebrow">Profile</p>
          <h1>Keep Parva personal on this device without turning it into an account product.</h1>
          <p>
            Preferences, saved places, reminders, and integrations stay local for now so the product can remain simple, honest, and guest-first.
          </p>
        </div>
        <article className="profile-session">
          <span className="profile-session__eyebrow">Local profile</span>
          <strong>{hasLocalState ? 'Saved state is active on this device' : 'Guest-first local mode is active'}</strong>
          <p>Parva currently keeps your saved state in this browser so the product can stay simple and guest-first.</p>
          <small className="profile-session__note">Export or import your local data below when you want a manual backup without turning this into a sign-in flow.</small>
        </article>
      </header>

      <section className="profile-summary">
        {summaryItems.map((item) => (
          <article key={item.label} className="ink-card profile-summary-card">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </section>

      <div className="profile-grid">
        <article className="ink-card profile-card">
          <h2>Preferences</h2>
          <div className="profile-controls">
            <label className="ink-input">
              <span>Language</span>
              <select value={state.language} onChange={(event) => setLanguage(event.target.value)}>
                <option value="en">English</option>
                <option value="ne">Nepali</option>
              </select>
            </label>
            <label className="ink-input">
              <span>Appearance</span>
              <select value={state.theme} onChange={(event) => setTheme(event.target.value)}>
                <option value="dawn-paper">Dawn Paper</option>
                <option value="nocturne-ink">Nocturne Ink</option>
              </select>
            </label>
          </div>
        </article>

        <article className="ink-card profile-card">
          <h2>Reminder preferences</h2>
          <div className="profile-controls">
            <label className="ink-input">
              <span>Channel</span>
              <select
                value={memberState.preferences?.reminderChannel || 'in_app'}
                onChange={(event) => updatePreferences({ reminderChannel: event.target.value })}
              >
                <option value="in_app">Saved list on this device</option>
                <option value="off">Off</option>
              </select>
            </label>
            <label className="ink-input">
              <span>Lead time</span>
              <select
                value={memberState.preferences?.reminderLeadTime || '1_day'}
                onChange={(event) => updatePreferences({ reminderLeadTime: event.target.value })}
              >
                <option value="same_day">Same day</option>
                <option value="1_day">1 day before</option>
                <option value="3_days">3 days before</option>
                <option value="1_week">1 week before</option>
              </select>
            </label>
          </div>
          <p className="profile-card__hint">Reminders are currently kept in Saved on this device. Delivery channels can come later without changing the guest-first model.</p>
        </article>

        <article className="ink-card profile-card">
          <h2>Current place</h2>
          <p>{activePreset?.label || 'Custom place in view'}</p>
          <span>{state.timezone}</span>
          <Link className="btn btn-secondary btn-sm" to="/my-place">Open My Place</Link>
        </article>

        <article className="ink-card profile-card">
          <h2>Local data</h2>
          <p className="profile-card__hint">
            Export a backup, restore a previous local snapshot, or clear the saved layer on this device.
          </p>
          <div className="profile-card__actions">
            <button type="button" className="btn btn-secondary btn-sm" onClick={exportLocalData}>
              Export JSON
            </button>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => importInputRef.current?.click()}>
              Import JSON
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm profile-card__danger"
              onClick={() => setConfirmClear((value) => !value)}
            >
              {confirmClear ? 'Cancel reset' : 'Clear local data'}
            </button>
            <input
              ref={importInputRef}
              type="file"
              accept="application/json"
              onChange={importFromFile}
              style={{ display: 'none' }}
            />
          </div>
          {confirmClear ? (
            <div className="profile-card__confirm">
              <p>This clears saved places, observances, readings, reminders, integrations, and reminder preferences from this device.</p>
              <button type="button" className="btn btn-primary btn-sm" onClick={handleClearLocalData}>
                Confirm clear
              </button>
            </div>
          ) : null}
          {localDataStatus ? <p className="profile-card__status">{localDataStatus}</p> : null}
        </article>

        <article className="ink-card profile-card">
          <h2>Open next</h2>
          <div className="profile-links">
            <Link to="/saved">Saved items</Link>
            <Link to="/integrations">Calendar integrations</Link>
            <Link to="/methodology">Method and evidence</Link>
            <Link to="/about">About Parva</Link>
          </div>
        </article>
      </div>
    </section>
  );
}

function summaryCount(memberState) {
  return (
    memberState.savedPlaces.length
    + memberState.savedFestivals.length
    + memberState.reminders.length
    + memberState.integrations.length
    + memberState.savedReadings.length
  );
}

export default ProfilePage;
