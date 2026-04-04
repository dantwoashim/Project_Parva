import PropTypes from 'prop-types';

function fmt(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return iso;
  }
}

export function HorizonStrip({ sunrise, sunset, currentMuhurta }) {
  return (
    <div className="horizon-strip" role="status" aria-live="polite">
      <p><span>Sunrise</span> {fmt(sunrise)}</p>
      <p><span>Sunset</span> {fmt(sunset)}</p>
      <p>
        <span>Current Muhurta</span>{' '}
        {currentMuhurta?.name || '—'}
      </p>
      <p><span>Class</span> {currentMuhurta?.class || '—'}</p>
    </div>
  );
}

HorizonStrip.propTypes = {
  sunrise: PropTypes.string,
  sunset: PropTypes.string,
  currentMuhurta: PropTypes.shape({
    name: PropTypes.string,
    class: PropTypes.string,
  }),
};

export default HorizonStrip;
