const SIGN_TRAITS = {
  Aries: 'direct and action-led',
  Taurus: 'steady and materially grounded',
  Gemini: 'curious and adaptive',
  Cancer: 'protective and emotionally tuned',
  Leo: 'expressive and self-directed',
  Virgo: 'careful and detail-sensitive',
  Libra: 'relational and balance-seeking',
  Scorpio: 'intense and private',
  Sagittarius: 'searching and future-facing',
  Capricorn: 'structured and duty-aware',
  Aquarius: 'independent and systems-minded',
  Pisces: 'intuitive and porous',
};

export function defaultDateTime() {
  const now = new Date(Date.now());
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}T06:30`;
}

export function toKnowledge(content, fallback) {
  if (!content?.sections) return fallback;
  return {
    title: content.title || fallback.title,
    intro: content.intro || fallback.intro,
    sections: (content.sections || []).map((section) => ({
      id: section.id,
      title: section.title,
      description: section.description,
      terms: (section.terms || []).map((term) => ({
        name: term.name,
        meaning: term.meaning,
        whyItMatters: term.why_it_matters || term.whyItMatters,
      })),
    })),
  };
}

function strongestGraha(payload) {
  return Object.values(payload?.grahas || {}).find((graha) => graha?.dignity?.state && graha.dignity.state !== 'neutral')
    || Object.values(payload?.grahas || {})[0]
    || null;
}

export function buildThesis(payload, graphPayload) {
  const lagnaSign = payload?.lagna?.rashi_english || 'Unknown';
  const moonSign = payload?.grahas?.moon?.rashi_english || 'Unknown';
  const lagnaTrait = SIGN_TRAITS[lagnaSign] || 'complex';
  const moonTrait = SIGN_TRAITS[moonSign] || 'layered';
  const firstInsight = (graphPayload?.insight_blocks || payload?.insight_blocks || [])[0];

  return `This chart opens with ${lagnaSign} rising, so it meets the world in a ${lagnaTrait} way. The Moon in ${moonSign} adds an inner tone that feels ${moonTrait}${firstInsight ? `, while ${firstInsight.title.toLowerCase()} becomes one of the clearest storylines in the chart.` : '.'}`;
}

export function buildThemeCards(payload, graphPayload) {
  const lagnaSign = payload?.lagna?.rashi_english || 'Unknown';
  const moon = payload?.grahas?.moon;
  const yogas = payload?.yogas || [];
  const doshas = payload?.doshas || [];
  const aspects = payload?.aspects || [];
  const dignified = Object.values(payload?.grahas || {}).find((graha) => graha?.dignity?.state && graha.dignity.state !== 'neutral');
  const firstInsight = (graphPayload?.insight_blocks || payload?.insight_blocks || [])[0];

  const cards = [
    {
      title: 'How you meet the world',
      body: `${lagnaSign} rising frames the chart through a ${SIGN_TRAITS[lagnaSign] || 'distinct'} lens, so first impressions tend to follow that rhythm.`,
    },
    {
      title: 'What steadies the inner life',
      body: moon
        ? `Moon in ${moon.rashi_english} points to an emotional baseline that feels ${SIGN_TRAITS[moon.rashi_english] || 'multi-layered'}.`
        : 'Moon placement details are not available for this chart yet.',
    },
    {
      title: 'Where the chart presses hardest',
      body: yogas.length || doshas.length
        ? `${yogas.length} yoga${yogas.length === 1 ? '' : 's'} and ${doshas.length} dosha${doshas.length === 1 ? '' : 's'} create the strongest pattern pressure in this reading.`
        : aspects.length
          ? `${aspects.length} aspect link${aspects.length === 1 ? '' : 's'} provide the clearest structural clue in this chart.`
          : 'No dominant pattern markers were provided in this response.',
    },
  ];

  if (dignified) {
    cards[2] = {
      title: 'Strongest graha',
      body: `${dignified.name_english || 'A graha'} stands out with ${dignified.dignity.state} dignity in ${dignified.rashi_english}, so that graha colors the chart more strongly than the rest.`,
    };
  } else if (firstInsight) {
    cards[2] = {
      title: firstInsight.title,
      body: firstInsight.summary,
    };
  }

  return cards;
}

export function buildSignalList(payload) {
  return [
    {
      label: 'Yogas',
      value: payload?.yogas?.length ? `${payload.yogas.length} pattern marker${payload.yogas.length === 1 ? '' : 's'}` : 'No yoga markers surfaced',
    },
    {
      label: 'Doshas',
      value: payload?.doshas?.length ? `${payload.doshas.length} caution marker${payload.doshas.length === 1 ? '' : 's'}` : 'No strong dosha markers surfaced',
    },
    {
      label: 'Aspects',
      value: payload?.aspects?.length ? `${payload.aspects.length} major relationship${payload.aspects.length === 1 ? '' : 's'}` : 'Aspect detail is limited',
    },
  ];
}

export function buildSignature(payload) {
  const lagna = payload?.lagna?.rashi_english;
  const moon = payload?.grahas?.moon?.rashi_english;
  const graha = strongestGraha(payload);

  return [
    {
      label: 'Outer style',
      value: lagna ? `${lagna} rising` : 'Lagna pending',
    },
    {
      label: 'Inner weather',
      value: moon ? `Moon in ${moon}` : 'Moon placement pending',
    },
    {
      label: 'Strongest pull',
      value: graha ? `${graha.name_english || 'Graha'} in ${graha.rashi_english || 'sign'}` : 'Strength signal pending',
    },
  ];
}

export function buildInsightHighlights(payload, graphPayload) {
  const highlights = graphPayload?.insight_blocks || payload?.insight_blocks || [];
  return highlights.slice(0, 3).map((item, index) => ({
    id: item.id || `insight_${index}`,
    title: item.title || `Insight ${index + 1}`,
    summary: item.summary || 'Interpretive detail will appear here when available.',
  }));
}

export function buildChartStats(graphPayload) {
  const layout = graphPayload?.layout || {};
  const houses = layout.house_nodes || layout.houses || [];
  const grahas = layout.graha_nodes || layout.grahas || [];
  const aspects = layout.aspect_edges || layout.aspects || [];
  return [
    { label: 'Houses', value: houses.length || 0 },
    { label: 'Grahas', value: grahas.length || 0 },
    { label: 'Aspects', value: aspects.length || 0 },
  ];
}

export function buildChartFocus(selectedNode, payload) {
  if (!selectedNode) {
    return {
      eyebrow: 'Selected focus',
      title: 'Choose a house or graha',
      body: 'The chart and detail panel will narrow to one house or graha at a time, so you never have to read everything at once.',
      note: 'Start with the most visually central node or the graha you already care about.',
    };
  }

  if (selectedNode.startsWith('house_')) {
    const houseNo = Number(selectedNode.split('_')[1]);
    const house = (payload?.houses || []).find((item) => item.house_number === houseNo);
    return {
      eyebrow: `House ${houseNo}`,
      title: house?.rashi_english || `House ${houseNo}`,
      body: `This selection centers the part of the chart tied to house ${houseNo}. Use it when you want the reading to narrow around one life area instead of the whole map.`,
      note: house?.occupants?.length
        ? `${house.occupants.length} graha${house.occupants.length === 1 ? '' : 's'} occupy this house in the current payload.`
        : 'This house is shown without listed occupants in the current payload.',
    };
  }

  const graha = (payload?.grahas || {})[selectedNode];
  return {
    eyebrow: graha?.name_english || 'Graha focus',
    title: graha?.rashi_english || 'Sign placement',
    body: graha
      ? `${graha.name_english} is placed in ${graha.rashi_english} with ${graha.dignity?.state || 'neutral'} dignity, so the chart can now be read from that placement outward instead of all at once.`
      : 'This selection is highlighted in the current graph payload.',
    note: graha?.is_retrograde ? 'Retrograde status is active for this graha.' : 'Select another node to compare the chart geometry.',
  };
}
