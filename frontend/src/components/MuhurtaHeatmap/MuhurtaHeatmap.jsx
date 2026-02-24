import PropTypes from 'prop-types';

function classNameFor(blockClass) {
  if (blockClass === 'auspicious') return 'muhurta-heatmap__block--good';
  if (blockClass === 'avoid') return 'muhurta-heatmap__block--avoid';
  return 'muhurta-heatmap__block--neutral';
}

function fmt(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return iso;
  }
}

export function MuhurtaHeatmap({ blocks = [], selectedIndex, onSelect }) {
  if (!blocks.length) {
    return (
      <div className="ink-card muhurta-heatmap__empty">
        <p>No muhurta blocks available.</p>
      </div>
    );
  }

  return (
    <div className="muhurta-heatmap" role="list" aria-label="Muhurta heatmap">
      {blocks.map((block) => (
        <button
          key={`${block.index}-${block.start}`}
          type="button"
          role="listitem"
          className={`muhurta-heatmap__block ${classNameFor(block.class)} ${selectedIndex === block.index ? 'is-selected' : ''}`.trim()}
          onClick={() => onSelect?.(block)}
          aria-pressed={selectedIndex === block.index}
        >
          <span className="muhurta-heatmap__name">{block.name}</span>
          <span className="muhurta-heatmap__time">{fmt(block.start)}–{fmt(block.end)}</span>
          <span className="muhurta-heatmap__score">{block.score ?? 0}</span>
        </button>
      ))}
    </div>
  );
}

MuhurtaHeatmap.propTypes = {
  blocks: PropTypes.arrayOf(PropTypes.object),
  selectedIndex: PropTypes.number,
  onSelect: PropTypes.func,
};

export default MuhurtaHeatmap;
