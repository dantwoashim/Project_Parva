import PropTypes from 'prop-types';
import { useTemporalContext } from '../../context/TemporalContext';
import './ModeSwitch.css';

export function ModeSwitch({ compact = false }) {
  const {
    state,
    setMode,
    setLanguage,
    setQualityBand,
  } = useTemporalContext();

  return (
    <div className={`mode-switch ${compact ? 'mode-switch--compact' : ''}`.trim()}>
      <div className="mode-switch__toggle" role="group" aria-label="Experience mode">
        <button
          type="button"
          className={`mode-switch__btn ${state.mode === 'observance' ? 'active' : ''}`}
          onClick={() => setMode('observance')}
        >
          Observance
        </button>
        <button
          type="button"
          className={`mode-switch__btn ${state.mode === 'authority' ? 'active' : ''}`}
          onClick={() => setMode('authority')}
        >
          Authority
        </button>
      </div>

      <label className="mode-switch__field">
        <span>Lang</span>
        <select value={state.language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="en">EN</option>
          <option value="ne">ने</option>
        </select>
      </label>

      <label className="mode-switch__field">
        <span>Quality</span>
        <select value={state.qualityBand} onChange={(e) => setQualityBand(e.target.value)}>
          <option value="computed">Computed</option>
          <option value="provisional">Provisional</option>
          <option value="inventory">Inventory</option>
          <option value="all">All</option>
        </select>
      </label>
    </div>
  );
}

ModeSwitch.propTypes = {
  compact: PropTypes.bool,
};

export default ModeSwitch;
