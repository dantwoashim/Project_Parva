import PropTypes from 'prop-types';

export function OrbitalRing({ ratio = 0, label = 'Tithi Progress', number = null }) {
  const clamped = Math.max(0, Math.min(1, Number(ratio) || 0));
  const circumference = 2 * Math.PI * 88;
  const dashOffset = circumference * (1 - clamped);

  return (
    <figure className="orbital-ring" aria-label={label}>
      <svg viewBox="0 0 220 220" role="img">
        <title>{label}</title>
        <circle cx="110" cy="110" r="88" className="orbital-ring__track" />
        <circle
          cx="110"
          cy="110"
          r="88"
          className="orbital-ring__value"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
        />
      </svg>
      <figcaption>
        <strong>{number ?? '—'}</strong>
        <span>{Math.round(clamped * 100)}%</span>
      </figcaption>
    </figure>
  );
}

OrbitalRing.propTypes = {
  ratio: PropTypes.number,
  label: PropTypes.string,
  number: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
};

export default OrbitalRing;
