import PropTypes from 'prop-types';
import { useMemo, useState } from 'react';
import { useTemporalContext } from '../../context/useTemporalContext';
import { LOCATION_PRESETS, findPresetByLocation } from '../../data/locationPresets';
import { useDialogA11y } from '../../hooks/useDialogA11y';
import { useCopy } from '../../i18n/useCopy';
import './AdvancedSettingsDrawer.css';

function AdvancedSettingsPanel({
  state,
  setLocation,
  setTheme,
  setTimezone,
  onClose,
}) {
  const { copy } = useCopy();
  const { dialogRef } = useDialogA11y(true, onClose);
  const [deviceStatus, setDeviceStatus] = useState('');
  const [advancedDraft, setAdvancedDraft] = useState({
    timezone: state.timezone,
    latitude: String(state.location?.latitude ?? ''),
    longitude: String(state.location?.longitude ?? ''),
  });

  const activePreset = useMemo(
    () => findPresetByLocation(state.location),
    [state.location],
  );

  const applyPreset = (preset) => {
    setLocation({ latitude: preset.latitude, longitude: preset.longitude });
    setTimezone(preset.timezone);
  };

  const useDeviceLocation = () => {
    if (!navigator.geolocation) {
      setDeviceStatus(copy('settings.deviceUnavailable'));
      return;
    }

    setDeviceStatus(copy('settings.deviceChecking'));
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: Number(position.coords.latitude.toFixed(4)),
          longitude: Number(position.coords.longitude.toFixed(4)),
        });
        try {
          const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
          if (tz) setTimezone(tz);
        } catch {
          // Ignore timezone detection issues.
        }
        setDeviceStatus(copy('settings.deviceApplied'));
        setAdvancedDraft((current) => ({
          ...current,
          latitude: Number(position.coords.latitude.toFixed(4)).toString(),
          longitude: Number(position.coords.longitude.toFixed(4)).toString(),
        }));
      },
      () => {
        setDeviceStatus(copy('settings.deviceUnreadable'));
      },
      { maximumAge: 600000, timeout: 4000 },
    );
  };

  const applyAdvancedSettings = () => {
    const latitude = Number(advancedDraft.latitude);
    const longitude = Number(advancedDraft.longitude);
    const timezone = advancedDraft.timezone?.trim() || 'Asia/Kathmandu';

    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      setDeviceStatus(copy('settings.timezoneInvalid'));
      return;
    }

    setTimezone(timezone);
    setLocation({ latitude, longitude });
    setDeviceStatus(copy('settings.timezoneApplied'));
  };

  return (
    <div className="settings-overlay" role="presentation" onClick={onClose}>
        <aside
          ref={dialogRef}
          className="settings-drawer"
          role="dialog"
          aria-modal="true"
          aria-labelledby="advanced-settings-title"
          onClick={(event) => event.stopPropagation()}
        >
        <header className="settings-drawer__header">
          <div>
            <p className="settings-drawer__eyebrow">{copy('settings.eyebrow')}</p>
            <h2 id="advanced-settings-title">{copy('settings.header')}</h2>
            <p className="settings-drawer__intro">
              {copy('settings.body')}
            </p>
          </div>
          <button
            type="button"
            className="settings-drawer__close"
            data-dialog-initial-focus="true"
            onClick={onClose}
            aria-label="Close settings"
          >
            {copy('settings.close')}
          </button>
        </header>

        <section className="settings-drawer__section">
          <div className="settings-drawer__section-header">
            <div>
              <h3>{copy('settings.appearance')}</h3>
              <p>{copy('settings.header')}</p>
            </div>
          </div>
          <div className="settings-drawer__grid">
            <label className="ink-input">
              <span>{copy('settings.theme')}</span>
              <select value={state.theme} onChange={(event) => setTheme(event.target.value)}>
                <option value="warm-paper">Warm Paper</option>
                <option value="ink-black">Ink Black</option>
              </select>
            </label>
          </div>
        </section>

        <section className="settings-drawer__section">
          <div className="settings-drawer__section-header">
            <div>
              <h3>{copy('settings.locationContext')}</h3>
              <p>{copy('settings.locationHint')}</p>
            </div>
            <button type="button" className="btn btn-secondary btn-sm" onClick={useDeviceLocation}>
              {copy('settings.useDevice')}
            </button>
          </div>

          <div className="settings-preset-grid">
            {LOCATION_PRESETS.map((preset) => (
              <button
                key={preset.id}
                type="button"
                className={`settings-preset ${activePreset?.id === preset.id ? 'is-active' : ''}`.trim()}
                onClick={() => applyPreset(preset)}
              >
                <strong>{preset.label}</strong>
                <span>{preset.description}</span>
              </button>
            ))}
          </div>

          <div className="settings-drawer__summary">
            <article className="settings-drawer__summary-card">
              <span>{copy('settings.currentPlace')}</span>
              <strong>{activePreset?.label || 'Custom place'}</strong>
            </article>
            <article className="settings-drawer__summary-card">
              <span>{copy('settings.timezone')}</span>
              <strong>{state.timezone}</strong>
            </article>
          </div>

          {deviceStatus ? <p className="settings-drawer__status">{deviceStatus}</p> : null}

          <details className="settings-drawer__advanced">
            <summary>{copy('settings.editAdvanced')}</summary>
            <div className="settings-drawer__grid">
              <label className="ink-input">
                <span>{copy('settings.timezone')}</span>
                <input
                  value={advancedDraft.timezone}
                  onChange={(event) => setAdvancedDraft((current) => ({ ...current, timezone: event.target.value }))}
                />
              </label>
              <label className="ink-input">
                <span>{copy('settings.latitude')}</span>
                <input
                  inputMode="decimal"
                  value={advancedDraft.latitude}
                  onChange={(event) => setAdvancedDraft((current) => ({ ...current, latitude: event.target.value }))}
                />
              </label>
              <label className="ink-input">
                <span>{copy('settings.longitude')}</span>
                <input
                  inputMode="decimal"
                  value={advancedDraft.longitude}
                  onChange={(event) => setAdvancedDraft((current) => ({ ...current, longitude: event.target.value }))}
                />
              </label>
              <button type="button" className="btn btn-secondary btn-sm settings-drawer__apply" onClick={applyAdvancedSettings}>
                {copy('settings.editAdvanced')}
              </button>
            </div>
          </details>
        </section>
      </aside>
    </div>
  );
}

export function AdvancedSettingsDrawer({ open, onClose }) {
  const { state, setLocation, setTimezone, setTheme } = useTemporalContext();

  if (!open) return null;

  return (
    <AdvancedSettingsPanel
      state={state}
      setLocation={setLocation}
      setTheme={setTheme}
      setTimezone={setTimezone}
      onClose={onClose}
    />
  );
}

AdvancedSettingsDrawer.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default AdvancedSettingsDrawer;
