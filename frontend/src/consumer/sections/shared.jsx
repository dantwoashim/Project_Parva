export function ConsumerSectionHeader({ eyebrow, title, body, action }) {
  return (
    <div className="consumer-home__section-header">
      <div className="consumer-home__section-copy">
        <span className="consumer-home__eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
      {action ? <div className="consumer-home__section-action">{action}</div> : null}
    </div>
  );
}

export function ConsumerSectionShell({ tone = 'default', children }) {
  return (
    <div className={`consumer-home__section-shell consumer-home__section-shell--${tone}`.trim()}>
      {children}
    </div>
  );
}

export function CompactEmpty({ title, body }) {
  return (
    <article className="consumer-home__surface consumer-home__compact-empty">
      <strong>{title}</strong>
      <p>{body}</p>
    </article>
  );
}
