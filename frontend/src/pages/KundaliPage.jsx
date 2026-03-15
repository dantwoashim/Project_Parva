import { useEffect, useMemo, useState } from 'react';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { KundaliGraph } from '../components/KundaliGraph/KundaliGraph';
import { KUNDALI_GLOSSARY } from '../data/temporalGlossary';
import { glossaryAPI, kundaliAPI } from '../services/api';
import { useTemporalContext } from '../context/useTemporalContext';
import { useMemberContext } from '../context/useMemberContext';
import { findPresetByLocation } from '../data/locationPresets';
import './KundaliPage.css';

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

function defaultDateTime() {
  const now = new Date(Date.now());
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}T06:30`;
}

function toKnowledge(content, fallback) {
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

function buildThesis(payload, graphPayload) {
  const lagnaSign = payload?.lagna?.rashi_english || 'Unknown';
  const moonSign = payload?.grahas?.moon?.rashi_english || 'Unknown';
  const lagnaTrait = SIGN_TRAITS[lagnaSign] || 'complex';
  const moonTrait = SIGN_TRAITS[moonSign] || 'layered';
  const firstInsight = (graphPayload?.insight_blocks || payload?.insight_blocks || [])[0];

  return `This chart opens with ${lagnaSign} rising, so it meets the world in a ${lagnaTrait} way. The Moon in ${moonSign} adds an inner tone that feels ${moonTrait}${firstInsight ? `, while ${firstInsight.title.toLowerCase()} becomes one of the clearest storylines in the chart.` : '.'}`;
}

function buildThemeCards(payload, graphPayload) {
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

function buildSignalList(payload) {
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

function strongestGraha(payload) {
  return Object.values(payload?.grahas || {}).find((graha) => graha?.dignity?.state && graha.dignity.state !== 'neutral')
    || Object.values(payload?.grahas || {})[0]
    || null;
}

function buildSignature(payload) {
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

function buildInsightHighlights(payload, graphPayload) {
  const highlights = graphPayload?.insight_blocks || payload?.insight_blocks || [];
  return highlights.slice(0, 3).map((item, index) => ({
    id: item.id || `insight_${index}`,
    title: item.title || `Insight ${index + 1}`,
    summary: item.summary || 'Interpretive detail will appear here when available.',
  }));
}

function buildChartStats(graphPayload) {
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

function buildChartFocus(selectedNode, payload) {
  if (!selectedNode) {
    return {
      eyebrow: 'Selected focus',
      title: 'Choose a house or graha',
      body: 'The chart will highlight relationships around the focus you select, so you never have to read everything at once.',
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
      ? `${graha.name_english} is placed in ${graha.rashi_english} with ${graha.dignity?.state || 'neutral'} dignity, so the diagram now emphasizes the links that radiate outward from that graha.`
      : 'This selection is highlighted in the current graph payload.',
    note: graha?.is_retrograde ? 'Retrograde status is active for this graha.' : 'Select another node to compare the chart geometry.',
  };
}

export function KundaliPage() {
  const { state } = useTemporalContext();
  const { saveReading } = useMemberContext();
  const [datetimeLocal, setDatetimeLocal] = useState(defaultDateTime());
  const [lat, setLat] = useState(String(state.location?.latitude ?? 27.7172));
  const [lon, setLon] = useState(String(state.location?.longitude ?? 85.324));
  const [tz, setTz] = useState(state.timezone || 'Asia/Kathmandu');
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [graphPayload, setGraphPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [graphMeta, setGraphMeta] = useState(null);
  const [knowledge, setKnowledge] = useState(KUNDALI_GLOSSARY);

  const datetimeIso = useMemo(() => `${datetimeLocal}:00`, [datetimeLocal]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [kundali, graphEnvelope, glossary] = await Promise.all([
        kundaliAPI.getKundali({ datetime: datetimeIso, lat, lon, tz }),
        kundaliAPI.getGraphEnvelope({ datetime: datetimeIso, lat, lon, tz }),
        glossaryAPI.get({ domain: 'kundali', lang: state.language }).catch(() => null),
      ]);
      setPayload(kundali);
      setGraphPayload(graphEnvelope.data);
      setMeta(kundali);
      setGraphMeta(graphEnvelope.meta);
      setKnowledge(toKnowledge(glossary?.content, KUNDALI_GLOSSARY));
      setSelectedNode(null);
      setActiveTab('summary');
    } catch (err) {
      setPayload(null);
      setGraphPayload(null);
      setMeta(null);
      setGraphMeta(null);
      setError(err.message || 'Failed to load kundali');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const thesis = useMemo(() => buildThesis(payload, graphPayload), [payload, graphPayload]);
  const themeCards = useMemo(() => buildThemeCards(payload, graphPayload), [payload, graphPayload]);
  const signalList = useMemo(() => buildSignalList(payload), [payload]);
  const signature = useMemo(() => buildSignature(payload), [payload]);
  const insightHighlights = useMemo(() => buildInsightHighlights(payload, graphPayload), [payload, graphPayload]);
  const chartStats = useMemo(() => buildChartStats(graphPayload), [graphPayload]);
  const chartFocus = useMemo(() => buildChartFocus(selectedNode, payload), [selectedNode, payload]);
  const preset = useMemo(() => findPresetByLocation(state.location), [state.location]);

  const activeInsight = useMemo(() => {
    if (!selectedNode || !graphPayload?.layout) return graphPayload?.insight_blocks || payload?.insight_blocks || [];
    const isHouse = selectedNode.startsWith('house_');
    if (isHouse) {
      const houseNo = Number(selectedNode.split('_')[1]);
      return [
        {
          id: selectedNode,
          title: `House ${houseNo}`,
          summary: (payload?.houses || []).find((house) => house.house_number === houseNo)?.rashi_english || 'House focus',
        },
        ...(graphPayload?.insight_blocks || []),
      ];
    }
    const graha = (payload?.grahas || {})[selectedNode];
    if (graha) {
      return [
        {
          id: selectedNode,
          title: graha.name_english || selectedNode,
          summary: `${graha.rashi_english || 'Unknown sign'} | ${graha.dignity?.state || 'neutral'} dignity`,
        },
        ...(graphPayload?.insight_blocks || []),
      ];
    }
    return graphPayload?.insight_blocks || [];
  }, [selectedNode, graphPayload, payload]);

  return (
    <section className="kundali-page animate-fade-in-up">
      <header className="kundali-page__hero ink-card">
        <div className="kundali-page__hero-copy">
          <p className="today-page__eyebrow">Birth Reading</p>
          <h1 className="text-hero">Start with the reading, not the wiring.</h1>
          <p className="kundali-page__intro">
            Start with the reading and strongest patterns. The full graph and detailed tables stay one step lower.
          </p>
        </div>
        <div className="kundali-page__hero-side">
          <article className="kundali-page__thesis-card">
            <span>Chart thesis</span>
            <p>{thesis}</p>
          </article>
          <div className="kundali-page__signature">
            {signature.map((item) => (
              <div key={item.label} className="kundali-page__signature-chip">
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>

          <details className="kundali-page__birth-panel">
            <summary>Birth details</summary>
            <form className="kundali-controls" onSubmit={(event) => { event.preventDefault(); load(); }}>
              <label className="ink-input">
                <span>Birth date and time</span>
                <input type="datetime-local" value={datetimeLocal} onChange={(event) => setDatetimeLocal(event.target.value)} required />
              </label>
              <label className="ink-input">
                <span>Latitude</span>
                <input value={lat} onChange={(event) => setLat(event.target.value)} />
              </label>
              <label className="ink-input">
                <span>Longitude</span>
                <input value={lon} onChange={(event) => setLon(event.target.value)} />
              </label>
              <label className="ink-input">
                <span>Timezone</span>
                <input value={tz} onChange={(event) => setTz(event.target.value)} />
              </label>
              <button className="btn btn-primary" type="submit">Refresh reading</button>
            </form>
          </details>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => saveReading({
              id: datetimeIso,
              title: `${payload?.lagna?.rashi_english || 'Birth'} Reading`,
              summary: thesis,
            })}
          >
            Save reading
          </button>
        </div>
      </header>

      {loading ? <div className="skeleton" style={{ minHeight: '320px', borderRadius: '1.4rem' }} /> : null}

      {!loading && error ? (
        <div className="ink-card kundali-error" role="alert">
          <h2>Birth Reading is unavailable right now</h2>
          <p>{error}</p>
        </div>
      ) : null}

      {!loading && !error && payload ? (
        <>
          <div className="kundali-tabs" role="tablist" aria-label="Kundali views">
            {['summary', 'reading', 'chart', 'details'].map((tab) => (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={activeTab === tab}
                className={`kundali-tab ${activeTab === tab ? 'is-active' : ''}`.trim()}
                onClick={() => setActiveTab(tab)}
              >
                {tab === 'summary' ? 'Summary' : tab === 'reading' ? 'Reading' : tab === 'chart' ? 'Chart' : 'Details'}
              </button>
            ))}
          </div>

          {activeTab === 'summary' ? (
            <section className="kundali-summary">
              <div className="kundali-summary__section-header">
                <div>
                  <p className="today-page__eyebrow">Reading</p>
                  <h2>The strongest themes in the chart</h2>
                </div>
                <div className="kundali-summary__actions">
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => setActiveTab('reading')}>
                    Open reading
                  </button>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => setActiveTab('chart')}>
                    Open chart
                  </button>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => setActiveTab('details')}>
                    Open details
                  </button>
                </div>
              </div>

              <div className="kundali-summary__themes kundali-summary__themes--compact">
                {themeCards.slice(0, 2).map((card) => (
                  <article key={card.title} className="ink-card kundali-summary__theme">
                    <h3>{card.title}</h3>
                    <p>{card.body}</p>
                  </article>
                ))}
              </div>

              <div className="kundali-summary__lower">
                <article className="ink-card kundali-summary__insights">
                  <div className="kundali-summary__section-header">
                    <div>
                      <p className="today-page__eyebrow">Themes</p>
                      <h2>Where the reading concentrates</h2>
                    </div>
                  </div>
                  <div className="kundali-summary__insight-list">
                    {insightHighlights.map((item) => (
                      <article key={item.id} className="kundali-summary__insight-card">
                        <h3>{item.title}</h3>
                        <p>{item.summary}</p>
                      </article>
                    ))}
                    {!insightHighlights.length ? (
                      <p className="muted">Interpretive highlights will appear here when the graph payload includes them.</p>
                    ) : null}
                  </div>
                </article>

                <article className="ink-card kundali-summary__signals">
                  <div className="kundali-summary__section-header">
                    <div>
                      <p className="today-page__eyebrow">Signals</p>
                      <h2>What is shaping the reading</h2>
                    </div>
                  </div>
                  <div className="kundali-summary__signal-list">
                    {signalList.map((item) => (
                      <div key={item.label}>
                        <span>{item.label}</span>
                        <strong>{item.value}</strong>
                      </div>
                    ))}
                  </div>
                </article>
              </div>
            </section>
          ) : null}

          {activeTab === 'reading' ? (
            <section className="kundali-summary">
              <article className="ink-card kundali-summary__insights">
                <div className="kundali-summary__section-header">
                  <div>
                    <p className="today-page__eyebrow">Reading</p>
                    <h2>The chart in plain language</h2>
                  </div>
                </div>
                <p className="kundali-summary__reading-copy">{thesis}</p>
                <div className="kundali-summary__themes">
                  {themeCards.map((card) => (
                    <article key={card.title} className="ink-card kundali-summary__theme">
                      <h3>{card.title}</h3>
                      <p>{card.body}</p>
                    </article>
                  ))}
                </div>
              </article>
            </section>
          ) : null}

          {activeTab === 'chart' ? (
            <section className="kundali-graph-layout">
              <div className="ink-card kundali-graph-shell">
                <div className="kundali-graph-shell__header">
                  <div>
                    <p className="today-page__eyebrow">Chart</p>
                    <h2>Inspect the visual structure when you want the full map.</h2>
                  </div>
                  <p className="kundali-graph-shell__note">
                    Select a house or graha to focus the relationships instead of reading the whole diagram at once.
                  </p>
                </div>
                <div className="kundali-graph-shell__stage">
                  <div className="kundali-graph-shell__legend">
                    {chartStats.map((item) => (
                      <div key={item.label} className="kundali-graph-shell__legend-item">
                        <span>{item.label}</span>
                        <strong>{item.value}</strong>
                      </div>
                    ))}
                  </div>
                  <article className="kundali-graph-shell__focus-card">
                    <span>{chartFocus.eyebrow}</span>
                    <h3>{chartFocus.title}</h3>
                    <p>{chartFocus.body}</p>
                    <small>{chartFocus.note}</small>
                  </article>
                </div>
                <KundaliGraph payload={graphPayload} selectedNode={selectedNode} onSelectNode={setSelectedNode} />
              </div>
              <aside className="ink-card kundali-insight-pane">
                <h2>Chart focus</h2>
                <div className="kundali-insight-list">
                  {activeInsight.map((item) => (
                    <article key={item.id} className="kundali-insight-item">
                      <h3>{item.title}</h3>
                      <p>{item.summary}</p>
                    </article>
                  ))}
                  {!activeInsight.length ? <p className="muted">Chart insights will appear here after selection.</p> : null}
                </div>
              </aside>
            </section>
          ) : null}

          {activeTab === 'details' ? (
            <section className="kundali-details">
              <article className="ink-card kundali-table-wrap">
                <h2>Graha details</h2>
                <table className="ink-table">
                  <thead>
                    <tr>
                      <th>Graha</th>
                      <th>Rashi</th>
                      <th>Longitude</th>
                      <th>Dignity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(payload.grahas || {}).map(([id, row]) => (
                      <tr key={id}>
                        <td>{row.name_english}</td>
                        <td>{row.rashi_english}</td>
                        <td>{row.longitude} deg</td>
                        <td>{row.dignity?.state || 'neutral'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </article>

              <article className="ink-card kundali-details__cards">
                <div>
                  <span>Yogas</span>
                  <strong>{payload.yogas?.length || 0}</strong>
                </div>
                <div>
                  <span>Doshas</span>
                  <strong>{payload.doshas?.length || 0}</strong>
                </div>
                <div>
                  <span>Aspects</span>
                  <strong>{payload.aspects?.length || 0}</strong>
                </div>
              </article>
            </section>
          ) : null}

          <KnowledgePanel
            title={knowledge.title}
            intro={knowledge.intro}
            sections={knowledge.sections}
            className="kundali-knowledge"
          />
          <EvidenceDrawer
            title="Birth Reading"
            intro="This drawer keeps the method profile, place, and chart metadata close by without forcing the technical view first."
            methodRef={graphMeta?.method || meta?.method || payload?.method_profile || 'Birth reading profile'}
            confidenceNote={graphMeta?.confidence?.level || graphMeta?.confidence || meta?.confidence?.level || 'Interpretive guidance'}
            placeUsed={preset?.label || state.timezone}
            computedForDate={datetimeLocal}
            availability={[
              { label: 'Summary reading', available: Boolean(thesis), note: 'The thesis is built from the lagna, moon placement, and leading insight blocks.' },
              { label: 'Interactive chart', available: Boolean(graphPayload?.layout), note: 'Graph detail stays in its own tab so the reading can stay calm by default.' },
              { label: 'Technical tables', available: Boolean(Object.keys(payload?.grahas || {}).length), note: 'Graha and aspect tables stay in Details for expert follow-up.' },
            ]}
            meta={graphMeta || meta}
            traceFallbackId={graphPayload?.calculation_trace_id || payload?.calculation_trace_id}
          />
        </>
      ) : null}
    </section>
  );
}

export default KundaliPage;
