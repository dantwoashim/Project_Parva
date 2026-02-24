import PropTypes from 'prop-types';

export function KundaliGraph({ payload, selectedNode, onSelectNode }) {
  const layout = payload?.layout;

  if (!layout) {
    return (
      <div className="ink-card kundali-graph__empty">
        <p>No kundali graph data available.</p>
      </div>
    );
  }

  const selected = selectedNode || null;
  const houseNodeIds = new Set((layout.house_nodes || []).map((node) => node.id));
  const grahaNodeIds = new Set((layout.graha_nodes || []).map((node) => node.id));

  const isEdgeActive = (edge) => {
    if (!selected) return true;
    return edge.source === selected || edge.target === selected;
  };

  return (
    <figure className="kundali-graph" aria-label="Interactive kundali graph">
      <svg viewBox={layout.viewbox || '0 0 400 400'} role="img">
        <title>Kundali Graph</title>

        {(layout.aspect_edges || []).map((edge) => {
          const source = (layout.graha_nodes || []).find((node) => node.id === edge.source);
          const target = (layout.graha_nodes || []).find((node) => node.id === edge.target);
          if (!source || !target) return null;
          return (
            <line
              key={edge.id}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              className={`kundali-graph__edge ${isEdgeActive(edge) ? 'active' : 'muted'}`}
            />
          );
        })}

        {(layout.house_nodes || []).map((node) => (
          <g key={node.id}>
            <circle
              cx={node.x}
              cy={node.y}
              r={selected === node.id ? 20 : 16}
              className={`kundali-graph__house ${selected === node.id ? 'is-selected' : ''}`}
              onClick={() => onSelectNode?.(node.id)}
              role="button"
              aria-label={`House ${node.house_number}`}
              tabIndex={0}
            />
            <text x={node.x} y={node.y + 4} textAnchor="middle" className="kundali-graph__house-label">
              {node.house_number}
            </text>
          </g>
        ))}

        {(layout.graha_nodes || []).map((node) => (
          <g key={node.id}>
            <circle
              cx={node.x}
              cy={node.y}
              r={selected === node.id ? 10 : 8}
              className={`kundali-graph__graha ${selected === node.id ? 'is-selected' : ''}`}
              onClick={() => onSelectNode?.(node.id)}
              role="button"
              aria-label={node.label}
              tabIndex={0}
            />
            <text x={node.x + 12} y={node.y + 4} className="kundali-graph__graha-label">
              {node.label}
            </text>
          </g>
        ))}
      </svg>

      <figcaption>
        <p>
          {selected
            ? `Selected: ${houseNodeIds.has(selected) ? 'House' : grahaNodeIds.has(selected) ? 'Graha' : 'Node'} ${selected}`
            : 'Select a house or graha to focus related aspect links.'}
        </p>
      </figcaption>
    </figure>
  );
}

KundaliGraph.propTypes = {
  payload: PropTypes.shape({
    layout: PropTypes.object,
  }),
  selectedNode: PropTypes.string,
  onSelectNode: PropTypes.func,
};

export default KundaliGraph;
