import {
  buildContractError,
  ensureApiEnvelope,
  ensureLocation,
  ensureNumber,
  ensureObject,
  ensureObjectArray,
  ensureOptionalObject,
  ensureString,
  withContractRequestId,
} from './apiContractCore';

export function normalizeKundaliGraphEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/kundali/graph', envelope);
  return withContractRequestId(normalized, () => {
    const data = normalized.data;
    ensureString(data.datetime, '/kundali/graph', 'Kundali graph payload must include a datetime string.');
    ensureLocation(data.location, '/kundali/graph');
    ensureOptionalObject(data.lagna, '/kundali/graph', 'Kundali graph lagna must be an object when present.');

    const layout = ensureObject(
      data.layout,
      '/kundali/graph',
      'Kundali graph payload must include a layout object.',
    );
    ensureString(
      layout.viewbox,
      '/kundali/graph',
      'Kundali graph layout.viewbox must be a non-empty string.',
    );

    const houseNodes = ensureObjectArray(
      layout.house_nodes,
      '/kundali/graph',
      'Kundali graph layout.house_nodes must be an array of house nodes.',
    );
    if (!houseNodes.length) {
      throw buildContractError(
        '/kundali/graph',
        'Kundali graph layout.house_nodes must contain at least one house node.',
        layout.house_nodes,
      );
    }
    houseNodes.forEach((node) => {
      ensureString(node.id, '/kundali/graph', 'Kundali graph house node id must be a non-empty string.');
      ensureNumber(node.x, '/kundali/graph', 'Kundali graph house node x must be a finite number.');
      ensureNumber(node.y, '/kundali/graph', 'Kundali graph house node y must be a finite number.');
    });

    const grahaNodes = ensureObjectArray(
      layout.graha_nodes,
      '/kundali/graph',
      'Kundali graph layout.graha_nodes must be an array of graha nodes.',
    );
    grahaNodes.forEach((node) => {
      ensureString(node.id, '/kundali/graph', 'Kundali graph graha node id must be a non-empty string.');
      ensureNumber(node.x, '/kundali/graph', 'Kundali graph graha node x must be a finite number.');
      ensureNumber(node.y, '/kundali/graph', 'Kundali graph graha node y must be a finite number.');
    });

    const aspectEdges = ensureObjectArray(
      layout.aspect_edges,
      '/kundali/graph',
      'Kundali graph layout.aspect_edges must be an array of aspect edges.',
    );
    aspectEdges.forEach((edge) => {
      ensureString(edge.source, '/kundali/graph', 'Kundali graph aspect edge source must be a non-empty string.');
      ensureString(edge.target, '/kundali/graph', 'Kundali graph aspect edge target must be a non-empty string.');
    });

    const insights = ensureObjectArray(
      data.insight_blocks,
      '/kundali/graph',
      'Kundali graph insight_blocks must be an array of insight objects.',
    );
    insights.forEach((item) => {
      ensureString(item.id, '/kundali/graph', 'Kundali graph insight block id must be a non-empty string.');
      ensureString(item.title, '/kundali/graph', 'Kundali graph insight block title must be a non-empty string.');
      ensureString(item.summary, '/kundali/graph', 'Kundali graph insight block summary must be a non-empty string.');
    });
    return normalized;
  });
}
