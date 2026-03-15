import PropTypes from 'prop-types';
import { useMemo, useState } from 'react';
import { useTemporalContext } from '../../context/useTemporalContext';
import { LOCATION_PRESETS, findPresetByLocation } from '../../data/locationPresets';
import './AdvancedSettingsDrawer.css';

export function AdvancedSettingsDrawer({ open, onClose }) {
  const { state, setLocation, setTimezone, setTheme } = useTemporalContext();
  const [deviceStatus, setDeviceStatus] = useState('');

  const activePreset = useMemo(
    () => findPresetByLocation(state.location),
    [state.location],
  );

  if (!open) return null;

  const applyPreset = (preset) => {
    setLocation({ latitude: preset.latitude, longitude: preset.longitude });
    setTimezone(preset.timezone);
  };

  const useDeviceLocation = () => {
    if (!navigator.geolocation) {
      setDeviceStatus('Device location is unavailable in this browser.');
      return;
    }

    setDeviceStatus('Checking your device location...');
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
        setDeviceStatus('Device location applied.');
      },
      () => {
        setDeviceStatus('We could not read your device location.');
      },
      { maximumAge: 600000, timeout: 4000 },
    );
  };

  return (
    <div className="settings-overlay" role="presentation" onClick={onClose}>
        <aside
          className="settings-drawer"
          role="dialog"
          aria-modal="true"
          aria-label="More options"
          onClick={(event) => event.stopPropagation()}
        >
        <header className="settings-drawer__header">
          <div>
            <p className="settings-drawer__eyebrow">More options</p>
            <h2>Adjust place and appearance without crowding the main flow.</h2>
            <p className="settings-drawer__intro">
              City presets stay first. Raw coordinates remain one step lower for expert cases.
            </p>
          </div>
          <button type="button" className="settings-drawer__close" onClick={onClose} aria-label="Close settings">
            Close
          </button>
        </header>

        <section className="settings-drawer__section">
          <div className="settings-drawer__section-header">
            <div>
              <h3>Appearance</h3>
              <p>Choose the reading atmosphere that feels right for your day.</p>
            </div>
          </div>
          <div className="settings-drawer__grid">
            <label className="ink-input">
              <span>Theme</span>
              <select value={state.theme} onChange={(event) => setTheme(event.target.value)}>
                <option value="dawn-paper">Dawn Paper</option>
                <option value="nocturne-ink">Nocturne Ink</option>
              </select>
            </label>
          </div>
        </section>

        <section className="settings-drawer__section">
          <div className="settings-drawer__section-header">
            <div>
              <h3>Location context</h3>
              <p>Choose a city preset first, then open advanced coordinates only when needed.</p>
            </div>
            <button type="button" className="btn btn-secondary btn-sm" onClick={useDeviceLocation}>
              Use my device
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

          {deviceStatus ? <p className="settings-drawer__status">{deviceStatus}</p> : null}

          <details className="settings-drawer__advanced">
            <summary>Edit advanced location settings</summary>
            <div className="settings-drawer__grid">
              <label className="ink-input">
                <span>Timezone</span>
                <input value={state.timezone} onChange={(event) => setTimezone(event.target.value)} />
              </label>
              <label className="ink-input">
                <span>Latitude</span>
                <input
                  value={state.location?.latitude ?? ''}
                  onChange={(event) => setLocation({ latitude: Number(event.target.value) || 0 })}
                />
              </label>
              <label className="ink-input">
                <span>Longitude</span>
                <input
                  value={state.location?.longitude ?? ''}
                  onChange={(event) => setLocation({ longitude: Number(event.target.value) || 0 })}
                />
              </label>
            </div>
          </details>
        </section>
      </aside>
    </div>
  );
}

AdvancedSettingsDrawer.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default AdvancedSettingsDrawer;
