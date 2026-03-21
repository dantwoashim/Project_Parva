import { useMemo, useState } from 'react';
import './KundaliGraph.css';

const GRAHA_ABBREVIATIONS = {
  sun: 'Su',
  moon: 'Mo',
  mars: 'Ma',
  mercury: 'Me',
  jupiter: 'Ju',
  venus: 'Ve',
  saturn: 'Sa',
  rahu: 'Ra',
  ketu: 'Ke',
};

const SIGN_ABBREVIATIONS = {
  Aries: 'Ari',
  Taurus: 'Tau',
  Gemini: 'Gem',
  Cancer: 'Can',
  Leo: 'Leo',
  Virgo: 'Vir',
  Libra: 'Lib',
  Scorpio: 'Sco',
  Sagittarius: 'Sag',
  Capricorn: 'Cap',
  Aquarius: 'Aqu',
  Pisces: 'Pis',
};

const HOUSE_POSITIONS = {
  1: { top: '11%', left: '50%' },
  2: { top: '19%', left: '76%' },
  3: { top: '34%', left: '86%' },
  4: { top: '50%', left: '79%' },
  5: { top: '66%', left: '86%' },
  6: { top: '81%', left: '76%' },
  7: { top: '89%', left: '50%' },
  8: { top: '81%', left: '24%' },
  9: { top: '66%', left: '14%' },
  10: { top: '50%', left: '21%' },
  11: { top: '34%', left: '14%' },
  12: { top: '19%', left: '24%' },
};

function humanizeId(value) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function grahaShortLabel(id, graha) {
  return GRAHA_ABBREVIATIONS[id]
    || graha?.short_label
    || graha?.label?.slice(0, 2)
    || humanizeId(id).slice(0, 2);
}

function grahaTitle(graha) {
  const parts = [graha?.label || graha?.name_english, graha?.rashi || graha?.rashi_english];
  if (graha?.is_retrograde) {
    parts.push('Retrograde');
  }
  if (graha?.dignity?.state && graha.dignity.state !== 'neutral') {
    parts.push(graha.dignity.state);
  }
  return parts.filter(Boolean).join(' • ');
}

function buildGrahaMap(payload) {
  const map = new Map();

  for (const node of payload?.layout?.graha_nodes || []) {
    map.set(node.id, {
      ...node,
      id: node.id,
      label: node.label || node.name_english || humanizeId(node.id),
    });
  }

  for (const [id, row] of Object.entries(payload?.grahas || {})) {
    const existing = map.get(id) || {};
    map.set(id, {
      ...existing,
      ...row,
      id,
      label: existing.label || row?.name_english || humanizeId(id),
    });
  }

  return map;
}

function buildHouses(payload, grahaMap) {
  const graphHouses = payload?.layout?.house_nodes || [];
  const fallbackHouses = payload?.houses || [];

  return Array.from({ length: 12 }, (_, index) => {
    const houseNumber = index + 1;
    const source = graphHouses.find((house) => Number(house.house_number) === houseNumber)
      || fallbackHouses.find((house) => Number(house.house_number) === houseNumber)
      || {};
    const occupantIds = Array.isArray(source.occupants) ? source.occupants : [];
    const occupants = occupantIds.map((id) => {
      const graha = grahaMap.get(id) || {};
      return {
        ...graha,
        id,
        label: graha.label || graha.name_english || humanizeId(id),
        shortLabel: grahaShortLabel(id, graha),
      };
    });

    return {
      ...source,
      house_number: houseNumber,
      rashi_english: source.rashi_english || source.label || `House ${houseNumber}`,
      rashi_sanskrit: source.rashi_sanskrit || '',
      occupants,
    };
  });
}

function buildLegendItems(houses, grahaMap) {
  const ids = new Set();
  houses.forEach((house) => {
    house.occupants.forEach((occupant) => ids.add(occupant.id));
  });

  if (!ids.size) {
    grahaMap.forEach((_, id) => ids.add(id));
  }

  return Array.from(ids).map((id) => {
    const graha = grahaMap.get(id) || { id };
    return {
      id,
      shortLabel: grahaShortLabel(id, graha),
      label: graha.label || graha.name_english || humanizeId(id),
    };
  });
}

function houseSummary(house) {
  const sign = house?.rashi_english || `House ${house?.house_number || ''}`.trim();
  const sanskrit = house?.rashi_sanskrit ? `(${house.rashi_sanskrit})` : '';
  return [sign, sanskrit].filter(Boolean).join(' ');
}

export function KundaliGraph({ payload, selectedNode, onSelectNode }) {
  const [viewMode, setViewMode] = useState('chart');
  const grahaMap = useMemo(() => buildGrahaMap(payload), [payload]);
  const houses = useMemo(() => buildHouses(payload, grahaMap), [grahaMap, payload]);
  const legendItems = useMemo(() => buildLegendItems(houses, grahaMap), [grahaMap, houses]);
  const selectedHouseNumber = selectedNode?.startsWith('house_')
    ? Number(selectedNode.slice('house_'.length))
    : null;
  const selectedGrahaId = selectedHouseNumber ? null : selectedNode;
  const lagnaSign = payload?.lagna?.rashi_english || houses[0]?.rashi_english || 'Unknown';
  const selectedGrahaHouseNumber = selectedGrahaId
    ? houses.find((house) => house.occupants.some((occupant) => occupant.id === selectedGrahaId))?.house_number
    : null;

  const focusSummary = useMemo(() => {
    if (selectedHouseNumber) {
      const house = houses.find((item) => item.house_number === selectedHouseNumber);
      return {
        eyebrow: `House ${selectedHouseNumber}`,
        title: houseSummary(house),
        note: 'Tap again to clear focus',
      };
    }

    if (selectedGrahaId) {
      const graha = grahaMap.get(selectedGrahaId);
      return {
        eyebrow: graha?.shortLabel || grahaShortLabel(selectedGrahaId, graha),
        title: graha?.label || humanizeId(selectedGrahaId),
        note: graha?.rashi || graha?.rashi_english || 'Tap again to clear focus',
      };
    }

    return {
      eyebrow: 'North Indian',
      title: `${lagnaSign} Lagna`,
      note: 'Select a house or graha',
    };
  }, [grahaMap, houses, lagnaSign, selectedGrahaId, selectedHouseNumber]);

  if (!houses.length) {
    return (
      <div className="kundali-graph__empty">
        <strong>Birth chart unavailable</strong>
        <p>The kundali graph payload did not include house placements.</p>
      </div>
    );
  }

  const toggleSelection = (value) => {
    onSelectNode?.(selectedNode === value ? null : value);
  };

  return (
    <figure className="kundali-graph">
      <div className="kundali-graph__toolbar">
        <div className="kundali-graph__mode-switch" role="tablist" aria-label="Birth chart display mode">
          <button
            type="button"
            className={`kundali-graph__mode-toggle${viewMode === 'chart' ? ' is-active' : ''}`}
            aria-selected={viewMode === 'chart'}
            onClick={() => setViewMode('chart')}
          >
            North Indian chart
          </button>
          <button
            type="button"
            className={`kundali-graph__mode-toggle${viewMode === 'list' ? ' is-active' : ''}`}
            aria-selected={viewMode === 'list'}
            onClick={() => setViewMode('list')}
          >
            House list
          </button>
        </div>
        <p className="kundali-graph__orientation">Lagna at top • houses fixed • signs move</p>
      </div>

      {viewMode === 'chart' ? (
        <div className="kundali-graph__canvas" role="group" aria-label={`North Indian kundali chart with ${lagnaSign} lagna`}>
          <svg className="kundali-graph__frame" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
            <rect x="8" y="8" width="84" height="84" rx="4" />
            <path d="M50 8 L92 50 L50 92 L8 50 Z" />
            <path d="M8 8 L50 50 L92 92" />
            <path d="M92 8 L50 50 L8 92" />
            <path d="M50 8 L50 92" />
            <path d="M8 50 L92 50" />
          </svg>

          {houses.map((house) => {
            const isSelectedHouse = selectedHouseNumber === house.house_number;
            const hasSelectedGraha = selectedGrahaHouseNumber === house.house_number;
            const position = HOUSE_POSITIONS[house.house_number];

            return (
              <article
                key={house.house_number}
                className={`kundali-graph__house${isSelectedHouse || hasSelectedGraha ? ' is-active' : ''}${house.house_number === 1 ? ' is-lagna' : ''}`}
                style={{ '--house-top': position.top, '--house-left': position.left }}
              >
                <button
                  type="button"
                  className="kundali-graph__house-anchor"
                  aria-pressed={isSelectedHouse}
                  aria-label={`House ${house.house_number}: ${houseSummary(house)}`}
                  onClick={() => toggleSelection(`house_${house.house_number}`)}
                >
                  <span className="kundali-graph__house-number">{house.house_number}</span>
                  <span className="kundali-graph__house-sign">{SIGN_ABBREVIATIONS[house.rashi_english] || house.rashi_english}</span>
                  {house.house_number === 1 ? <span className="kundali-graph__house-tag">Asc</span> : null}
                </button>

                {house.occupants.length ? (
                  <div className="kundali-graph__occupants">
                    {house.occupants.map((occupant) => {
                      const isSelectedGraha = selectedGrahaId === occupant.id;
                      const isDignified = occupant?.dignity?.state && occupant.dignity.state !== 'neutral';

                      return (
                        <button
                          key={occupant.id}
                          type="button"
                          className={`kundali-graph__chip${isSelectedGraha ? ' is-selected' : ''}${isDignified ? ' is-dignified' : ''}`}
                          aria-pressed={isSelectedGraha}
                          title={grahaTitle(occupant)}
                          onClick={() => toggleSelection(occupant.id)}
                        >
                          <span>{occupant.shortLabel}</span>
                          {occupant.is_retrograde ? <small>R</small> : null}
                        </button>
                      );
                    })}
                  </div>
                ) : null}
              </article>
            );
          })}

          <button type="button" className="kundali-graph__center-note" onClick={() => onSelectNode?.(null)}>
            <span>{focusSummary.eyebrow}</span>
            <strong>{focusSummary.title}</strong>
            <small>{focusSummary.note}</small>
          </button>
        </div>
      ) : (
        <div className="kundali-graph__list" role="list" aria-label="Birth chart houses">
          {houses.map((house) => {
            const isSelectedHouse = selectedHouseNumber === house.house_number;
            const hasSelectedGraha = selectedGrahaHouseNumber === house.house_number;

            return (
              <article
                key={house.house_number}
                className={`kundali-graph__list-row${isSelectedHouse || hasSelectedGraha ? ' is-active' : ''}`}
                role="listitem"
              >
                <button
                  type="button"
                  className="kundali-graph__list-house"
                  aria-pressed={isSelectedHouse}
                  onClick={() => toggleSelection(`house_${house.house_number}`)}
                >
                  <span className="kundali-graph__list-number">{house.house_number}</span>
                  <span className="kundali-graph__list-copy">
                    <strong>{house.rashi_english}</strong>
                    <small>{house.rashi_sanskrit || (house.house_number === 1 ? 'Ascendant house' : 'Fixed house position')}</small>
                  </span>
                </button>

                <div className="kundali-graph__list-occupants">
                  {house.occupants.length ? house.occupants.map((occupant) => (
                    <button
                      key={occupant.id}
                      type="button"
                      className={`kundali-graph__chip${selectedGrahaId === occupant.id ? ' is-selected' : ''}${occupant?.dignity?.state && occupant.dignity.state !== 'neutral' ? ' is-dignified' : ''}`}
                      aria-pressed={selectedGrahaId === occupant.id}
                      title={grahaTitle(occupant)}
                      onClick={() => toggleSelection(occupant.id)}
                    >
                      <span>{occupant.shortLabel}</span>
                      {occupant.is_retrograde ? <small>R</small> : null}
                    </button>
                  )) : (
                    <span className="kundali-graph__list-empty">No grahas in this house</span>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}

      <div className="kundali-graph__legend">
        <p className="kundali-graph__caption">
          Read the chart house by house, then use the planetary table beside it for full names, signs, and degrees.
        </p>
        <div className="kundali-graph__legend-items" aria-label="Graha abbreviations">
          {legendItems.map((item) => (
            <span key={item.id} className="kundali-graph__legend-chip">
              <strong>{item.shortLabel}</strong>
              <span>{item.label}</span>
            </span>
          ))}
        </div>
      </div>
    </figure>
  );
}

export default KundaliGraph;
