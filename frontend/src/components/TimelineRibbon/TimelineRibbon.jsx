import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';

function QualityMarker({ band }) {
  return <span className={`quality-marker quality-marker--${band || 'inventory'}`} aria-label={band || 'inventory'} />;
}

QualityMarker.propTypes = {
  band: PropTypes.string,
};

function formatDualDate(item) {
  const ad = `${item.start_date} → ${item.end_date}`;
  const bsStart = item.bs_start?.formatted;
  const bsEnd = item.bs_end?.formatted;
  const bs = bsStart ? (bsStart === bsEnd ? bsStart : `${bsStart} → ${bsEnd}`) : null;
  return { ad, bs };
}

export function TimelineRibbon({ groups = [] }) {
  const navigate = useNavigate();

  if (!groups.length) {
    return (
      <div className="ink-card timeline-empty">
        <h3>No festivals in this range</h3>
        <p>Try widening date window or switching quality band.</p>
      </div>
    );
  }

  return (
    <div className="timeline-ribbon" aria-label="Festival timeline">
      {groups.map((group) => (
        <section key={group.month_key} className="timeline-month">
          <header className="timeline-month__header sticky-month">{group.month_label}</header>
          <ul className="timeline-month__list">
            {(group.items || []).map((item) => {
              const dual = formatDualDate(item);
              return (
              <li key={`${item.id}-${item.start_date}`}>
                <button
                  type="button"
                  className="timeline-card"
                  onClick={() => navigate(`/festivals/${item.id}`)}
                >
                  <div className="timeline-card__title-row">
                    <h3>{item.display_name || item.name}</h3>
                    <QualityMarker band={item.quality_band} />
                  </div>
                  <p className="timeline-card__meta">
                    {dual.ad} · {item.category}
                  </p>
                  {dual.bs && <p className="timeline-card__meta timeline-card__meta--bs">BS: {dual.bs}</p>}
                  {item.ritual_preview?.days?.[0] && (
                    <p className="timeline-card__ritual">
                      {item.ritual_preview.days[0].name}: {item.ritual_preview.days[0].events?.[0]?.title || 'Ritual sequence'}
                    </p>
                  )}
                </button>
              </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}

TimelineRibbon.propTypes = {
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      month_key: PropTypes.string,
      month_label: PropTypes.string,
      items: PropTypes.arrayOf(PropTypes.object),
    }),
  ),
};

export default TimelineRibbon;
