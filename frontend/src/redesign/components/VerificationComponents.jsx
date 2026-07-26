import { Link } from '@parva/router';
import { sourceDots } from '../redesignStaticData';

export function Confidence({ value, label = 'Source confidence' }) {
  const score = Number(value);
  const normalizedValue = Number.isFinite(score) ? Math.max(0, Math.min(100, Math.round(score))) : 0;
  return (
    <div className="confidence-meter">
      <span>{label}</span>
      <div><i style={{ width: `${normalizedValue}%` }} /></div>
      <strong>{normalizedValue}%</strong>
    </div>
  );
}

export function SourceDots({ active = 5 }) {
  return (
    <span className="source-dots" aria-label={`${active} of 6 source checks passed`}>
      {sourceDots.map((dot) => <i key={dot} className={dot <= active ? 'is-active' : ''} />)}
    </span>
  );
}

export function VerificationStrip({ items = [] }) {
  return (
    <section className="verification-strip" aria-label="Verification summary">
      {items.map((item) => (
        <div key={item.label}>
          <span>{item.label}</span>
          <strong>{item.value}</strong>
          {item.meta ? <small>{item.meta}</small> : null}
        </div>
      ))}
    </section>
  );
}

export function ScoreRing({ value, label = 'Score' }) {
  return (
    <div className="score-ring" style={{ '--score': `${value}%` }}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

export function InfoCell({ icon, label, value, meta }) {
  return (
    <article className="info-cell">
      {icon ? <span className="cell-icon" aria-hidden="true">{icon}</span> : null}
      <small>{label}</small>
      <strong>{value}</strong>
      {meta ? <em>{meta}</em> : null}
    </article>
  );
}

export function TimelineList({ compact = false, items = [] }) {
  return (
    <div className={compact ? 'timeline-list compact' : 'timeline-list'}>
      {items.length ? items.map((item) => (
        <Link key={`${item.time}-${item.title}`} className={`timeline-item tone-${item.type}`} to="/best-time">
          <span>{item.time}</span>
          <strong>{item.title}</strong>
          <i aria-hidden="true">{item.icon}</i>
        </Link>
      )) : <p className="festival-muted-note">Timeline data is loading from the API.</p>}
    </div>
  );
}
