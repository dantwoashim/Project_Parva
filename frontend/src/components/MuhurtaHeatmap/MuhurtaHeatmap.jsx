import PropTypes from 'prop-types';

function classNameFor(blockClass, score) {
  if (blockClass === 'auspicious' || score >= 65) return 'muhurta-heatmap__block--strong';
  if (score >= 25) return 'muhurta-heatmap__block--good';
  if (blockClass === 'avoid' || score <= -25) return 'muhurta-heatmap__block--avoid';
  return 'muhurta-heatmap__block--mixed';
}

function labelFor(blockClass, score) {
  if (blockClass === 'auspicious' || score >= 65) return 'Strong';
  if (score >= 25) return 'Good';
  if (blockClass === 'avoid' || score <= -25) return 'Avoid';
  return 'Mixed';
}

function fmt(iso) {
  if (!iso) return 'Time unavailable';
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.valueOf())) return 'Time unavailable';
  return parsed.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

function durationFor(startIso, endIso) {
  if (!startIso || !endIso) return 'Duration unavailable';
  const start = new Date(startIso);
  const end = new Date(endIso);
  if (Number.isNaN(start.valueOf()) || Number.isNaN(end.valueOf())) return 'Duration unavailable';
  const minutes = Math.max(0, Math.round((end.getTime() - start.getTime()) / 60000));
  if (!minutes) return 'Duration unavailable';
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60);
    const remainder = minutes % 60;
    return remainder ? `${hours}h ${remainder}m` : `${hours}h`;
  }
  return `${minutes} min`;
}

function previewReason(block) {
  if (block?.rank_explanation) return block.rank_explanation;
  if (Array.isArray(block?.reason_codes) && block.reason_codes.length) {
    return block.reason_codes
      .slice(0, 2)
      .map((code) => code.replaceAll('_', ' '))
      .join(' and ');
  }
  return 'Tap for a fuller explanation.';
}

export function MuhurtaHeatmap({ blocks = [], selectedIndex, onSelect, showScores = false }) {
  if (!blocks.length) {
    return (
      <div className="ink-card muhurta-heatmap__empty">
        <p>No muhurta blocks are available for this day.</p>
      </div>
    );
  }

  return (
    <div className="muhurta-heatmap" role="list" aria-label="Muhurta heatmap">
      {blocks.map((block, index) => (
        <button
          key={`${block.index}-${block.start}`}
          type="button"
          role="listitem"
          className={`muhurta-heatmap__block ${classNameFor(block.class, Number(block.score) || 0)} ${selectedIndex === block.index ? 'is-selected' : ''}`.trim()}
          onClick={() => onSelect?.(block)}
          aria-pressed={selectedIndex === block.index}
        >
          <span className="muhurta-heatmap__index">#{index + 1}</span>
          <div className="muhurta-heatmap__content">
            <span className="muhurta-heatmap__name">{block.name}</span>
            <span className="muhurta-heatmap__time">{fmt(block.start)} - {fmt(block.end)}</span>
            <span className="muhurta-heatmap__reason">{previewReason(block)}</span>
          </div>
          <div className="muhurta-heatmap__meta">
            <span className="muhurta-heatmap__quality">{labelFor(block.class, Number(block.score) || 0)}</span>
            <span className="muhurta-heatmap__duration">{durationFor(block.start, block.end)}</span>
            {showScores ? <span className="muhurta-heatmap__score">Score {block.score ?? 0}</span> : null}
          </div>
        </button>
      ))}
    </div>
  );
}

MuhurtaHeatmap.propTypes = {
  blocks: PropTypes.arrayOf(PropTypes.object),
  selectedIndex: PropTypes.number,
  onSelect: PropTypes.func,
  showScores: PropTypes.bool,
};

export default MuhurtaHeatmap;
