import PropTypes from 'prop-types';

function normalizeLayout(layout = {}) {
  const houseNodes = layout.house_nodes || layout.houses || [];
  const grahaNodes = layout.graha_nodes || layout.grahas || [];
  const aspectEdges = layout.aspect_edges || layout.aspects || [];

  return {
    viewbox: layout.viewbox || '0 0 320 320',
    houseNodes: houseNodes.map((node, index) => ({
      id: node.id || `house_${node.house_number || index + 1}`,
      house_number: node.house_number || Number(String(node.id || '').replace('house_', '')) || index + 1,
      x: node.x,
      y: node.y,
    })),
    grahaNodes: grahaNodes.map((node) => ({
      id: node.id,
      label: node.label || node.name_english || node.id,
      x: node.x,
      y: node.y,
    })),
    aspectEdges: aspectEdges.map((edge, index) => ({
      id: edge.id || `edge_${index}`,
      source: edge.source || edge.from,
      target: edge.target || edge.to,
    })),
  };
}

export function KundaliGraph({ payload, selectedNode, onSelectNode }) {
  const layout = payload?.layout ? normalizeLayout(payload.layout) : null;

  if (!layout || !layout.houseNodes.length) {
    return (
      <div className="ink-card kundali-graph__empty">
        <p>No kundali graph data is available for this chart.</p>
      </div>
    );
  }

  const selected = selectedNode || null;
  const [minX, minY, viewWidth, viewHeight] = String(layout.viewbox).split(/\s+/).map((value) => Number(value));
  const centerX = (Number.isFinite(minX) ? minX : 0) + ((Number.isFinite(viewWidth) ? viewWidth : 320) / 2);
  const centerY = (Number.isFinite(minY) ? minY : 0) + ((Number.isFinite(viewHeight) ? viewHeight : 320) / 2);
  const houseNodeIds = new Set(layout.houseNodes.map((node) => node.id));
  const grahaNodeIds = new Set(layout.grahaNodes.map((node) => node.id));
  const activateNode = (nodeId) => {
    onSelectNode?.(nodeId);
  };
  const onNodeKeyDown = (event, nodeId) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      activateNode(nodeId);
    }
  };

  const isEdgeActive = (edge) => {
    if (!selected) return true;
    return edge.source === selected || edge.target === selected;
  };

  return (
    <figure className="kundali-graph" aria-label="Interactive kundali graph">
      <svg viewBox={layout.viewbox} role="img">
        <title>Kundali Graph</title>

        <circle cx={centerX} cy={centerY} r={112} className="kundali-graph__stage-ring kundali-graph__stage-ring--outer" />
        <circle cx={centerX} cy={centerY} r={78} className="kundali-graph__stage-ring kundali-graph__stage-ring--inner" />

        {layout.aspectEdges.map((edge) => {
          const source = layout.grahaNodes.find((node) => node.id === edge.source);
          const target = layout.grahaNodes.find((node) => node.id === edge.target);
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

        {layout.houseNodes.map((node) => (
          <g key={node.id}>
            {selected === node.id ? (
              <circle
                cx={node.x}
                cy={node.y}
                r={28}
                className="kundali-graph__selection-halo kundali-graph__selection-halo--house"
              />
            ) : null}
            <circle
              cx={node.x}
              cy={node.y}
              r={selected === node.id ? 20 : 16}
              className={`kundali-graph__house ${selected === node.id ? 'is-selected' : ''}`}
              onClick={() => activateNode(node.id)}
              onKeyDown={(event) => onNodeKeyDown(event, node.id)}
              role="button"
              aria-label={`House ${node.house_number}`}
              tabIndex={0}
            />
            <text x={node.x} y={node.y + 4} textAnchor="middle" className="kundali-graph__house-label">
              {node.house_number}
            </text>
          </g>
        ))}

        {layout.grahaNodes.map((node) => (
          <g key={node.id}>
            {selected === node.id ? (
              <circle
                cx={node.x}
                cy={node.y}
                r={18}
                className="kundali-graph__selection-halo kundali-graph__selection-halo--graha"
              />
            ) : null}
            <circle
              cx={node.x}
              cy={node.y}
              r={selected === node.id ? 10 : 8}
              className={`kundali-graph__graha ${selected === node.id ? 'is-selected' : ''}`}
              onClick={() => activateNode(node.id)}
              onKeyDown={(event) => onNodeKeyDown(event, node.id)}
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
            ? `Selected focus: ${houseNodeIds.has(selected) ? 'House' : grahaNodeIds.has(selected) ? 'Graha' : 'Node'} ${selected}`
            : 'Open the chart tab when you want to inspect house and graha relationships visually, one focus at a time.'}
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
