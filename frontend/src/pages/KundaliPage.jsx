import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { KundaliGraph } from '../components/KundaliGraph/KundaliGraph';
import { KUNDALI_GLOSSARY } from '../data/temporalGlossary';
import { findPresetByLocation } from '../data/locationPresets';
import { useMemberContext } from '../context/useMemberContext';
import { useTemporalContext } from '../context/useTemporalContext';
import { glossaryAPI, kundaliAPI, muhurtaAPI, personalAPI } from '../services/api';
import { describeSupportError } from '../services/errorFormatting';
import { formatProductTime, formatProductTimeRange } from '../utils/productDateTime';
import {
  buildChartFocus,
  buildChartStats,
  buildInsightHighlights,
  buildSignalList,
  buildSignature,
  buildThemeCards,
  buildThesis,
  defaultDateTime,
  toKnowledge,
} from './kundali/kundaliPresentation';
import './KundaliPage.css';

function strongestGraha(payload) {
  return Object.values(payload?.grahas || {}).find((graha) => graha?.dignity?.state && graha.dignity.state !== 'neutral')
    || Object.values(payload?.grahas || {})[0]
    || null;
}

function formatBsDate(bsDate) {
  if (!bsDate?.month_name || !bsDate?.day || !bsDate?.year) {
    return 'Bikram Sambat date pending';
  }
  return `${bsDate.month_name} ${bsDate.day}`;
}

function formatBsMeta(bsDate, panchanga) {
  const lunarNote = [panchanga?.tithi?.paksha, panchanga?.tithi?.name].filter(Boolean).join(' | ');
  if (!lunarNote) return `Bikram Sambat ${bsDate?.year || ''}`.trim();
  return lunarNote;
}

function formatPlanetSpeed(graha) {
  return graha?.is_retrograde ? 'Retro' : 'Direct';
}

function formatPlanetDegree(graha) {
  const value = Number(graha?.longitude);
  if (!Number.isFinite(value)) return 'Pending';
  return `${value.toFixed(1)} deg`;
}

function buildPanchangaCards(personalPayload) {
  return [
    {
      label: 'Tithi',
      sanskrit: 'तिथि',
      value: personalPayload?.tithi?.name || 'Pending',
      note: personalPayload?.tithi?.paksha ? `Until ${personalPayload.tithi.paksha}` : 'Lunar day guidance appears when available.',
    },
    {
      label: 'Vara',
      sanskrit: 'वार',
      value: personalPayload?.vaara?.name_english || 'Pending',
      note: personalPayload?.vaara?.name_sanskrit || 'Weekday rhythm appears when available.',
    },
    {
      label: 'Nakshatra',
      sanskrit: 'नक्षत्र',
      value: personalPayload?.nakshatra?.name || 'Pending',
      note: personalPayload?.nakshatra?.lord || personalPayload?.nakshatra?.deity || 'Star field detail appears when available.',
    },
    {
      label: 'Yoga',
      sanskrit: 'योग',
      value: personalPayload?.yoga?.name || 'Pending',
      note: personalPayload?.yoga?.quality || 'Auspiciousness appears when available.',
    },
    {
      label: 'Karana',
      sanskrit: 'करण',
      value: personalPayload?.karana?.name || 'Pending',
      note: personalPayload?.karana?.quality || 'Action quality appears when available.',
    },
  ];
}

function buildContextCards({ personalPayload, muhurtaPayload, selectedFocus, state }) {
  return [
    {
      icon: 'bedtime',
      title: 'Moon Phase',
      body: personalPayload?.tithi?.paksha
        ? `${personalPayload.tithi.paksha} fortnight | ${personalPayload.tithi.name || 'Current tithi'}`
        : 'Moon phase detail appears when the personal panchanga payload is available.',
    },
    {
      icon: 'timer',
      title: 'Rahu Kaal',
      body: muhurtaPayload?.rahu_kalam
        ? formatProductTimeRange(muhurtaPayload.rahu_kalam.start, muhurtaPayload.rahu_kalam.end, state)
        : 'Rahu Kaal appears when the daily muhurta context is available.',
    },
    {
      icon: 'network_node',
      title: selectedFocus.eyebrow,
      body: selectedFocus.note,
    },
  ];
}

function buildDashaCards(payload) {
  return (payload?.dasha?.timeline || []).slice(0, 3).map((period, index) => ({
    id: `${period.lord || 'period'}_${index}`,
    label: index === 0 ? 'Major period' : index === 1 ? 'Following period' : 'Long arc',
    value: period.lord || 'Pending',
    note: period.duration_years ? `${period.duration_years} year cycle` : 'Timeline detail appears when available.',
  }));
}

export function KundaliPage() {
  const { state } = useTemporalContext();
  const { saveReading } = useMemberContext();
  const [datetimeLocal, setDatetimeLocal] = useState(defaultDateTime());
  const [lat, setLat] = useState(String(state.location?.latitude ?? 27.7172));
  const [lon, setLon] = useState(String(state.location?.longitude ?? 85.324));
  const [tz, setTz] = useState(state.timezone || 'Asia/Kathmandu');
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);
  const [graphPayload, setGraphPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [graphMeta, setGraphMeta] = useState(null);
  const [personalPayload, setPersonalPayload] = useState(null);
  const [muhurtaPayload, setMuhurtaPayload] = useState(null);
  const [knowledge, setKnowledge] = useState(KUNDALI_GLOSSARY);

  const datetimeIso = useMemo(() => `${datetimeLocal}:00`, [datetimeLocal]);
  const readingDate = useMemo(() => datetimeLocal.slice(0, 10), [datetimeLocal]);
  const preset = useMemo(() => findPresetByLocation(state.location), [state.location]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [kundali, graphEnvelope, glossary, personalEnvelope, muhurtaEnvelope] = await Promise.all([
          kundaliAPI.getKundali({ datetime: datetimeIso, lat, lon, tz }),
          kundaliAPI.getGraphEnvelope({ datetime: datetimeIso, lat, lon, tz }),
          glossaryAPI.get({ domain: 'kundali', lang: state.language }).catch(() => null),
          personalAPI.getPanchangaEnvelope({ date: readingDate, lat, lon, tz }).catch(() => null),
          muhurtaAPI.getHeatmapEnvelope({ date: readingDate, lat, lon, tz, type: 'general' }).catch(() => null),
        ]);

        if (cancelled) return;

        setPayload(kundali);
        setGraphPayload(graphEnvelope.data || null);
        setMeta(kundali);
        setGraphMeta(graphEnvelope.meta || null);
        setPersonalPayload(personalEnvelope?.data || null);
        setMuhurtaPayload(muhurtaEnvelope?.data || null);
        setKnowledge(toKnowledge(glossary?.content, KUNDALI_GLOSSARY));
        setSelectedNode(null);
      } catch (err) {
        if (cancelled) return;
        setPayload(null);
        setGraphPayload(null);
        setMeta(null);
        setGraphMeta(null);
        setPersonalPayload(null);
        setMuhurtaPayload(null);
        setError(describeSupportError(err, 'Failed to load kundali'));
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [datetimeIso, lat, lon, readingDate, state.language, tz]);

  const thesis = useMemo(() => buildThesis(payload, graphPayload), [payload, graphPayload]);
  const themeCards = useMemo(() => buildThemeCards(payload, graphPayload), [payload, graphPayload]);
  const signalList = useMemo(() => buildSignalList(payload), [payload]);
  const signature = useMemo(() => buildSignature(payload), [payload]);
  const insightHighlights = useMemo(() => buildInsightHighlights(payload, graphPayload), [payload, graphPayload]);
  const chartStats = useMemo(() => buildChartStats(graphPayload), [graphPayload]);
  const graphDisplayPayload = useMemo(
    () => ({
      ...(graphPayload || {}),
      lagna: graphPayload?.lagna || payload?.lagna || null,
      houses: payload?.houses || [],
    }),
    [graphPayload, payload],
  );
  const focusPayload = useMemo(
    () => ({
      ...payload,
      houses: graphPayload?.layout?.house_nodes || payload?.houses || [],
      grahas: payload?.grahas || {},
    }),
    [graphPayload, payload],
  );
  const chartFocus = useMemo(() => buildChartFocus(selectedNode, focusPayload), [focusPayload, selectedNode]);
  const planetOfDay = useMemo(() => strongestGraha(payload), [payload]);
  const panchangaCards = useMemo(() => buildPanchangaCards(personalPayload), [personalPayload]);
  const dashaCards = useMemo(() => buildDashaCards(payload), [payload]);
  const grahaRows = useMemo(() => Object.entries(payload?.grahas || {}), [payload]);

  const selectedFocus = useMemo(() => {
    if (selectedNode) {
      return chartFocus;
    }

    if (planetOfDay) {
      return {
        eyebrow: 'Planet of the day',
        title: `${planetOfDay.name_english || 'Graha'} in ${planetOfDay.rashi_english || 'its sign'}`,
        body: planetOfDay.dignity?.state && planetOfDay.dignity.state !== 'neutral'
          ? `${planetOfDay.name_english} carries ${planetOfDay.dignity.state} dignity today, which makes it the clearest place to start reading the chart.`
          : `${planetOfDay.name_english} is the easiest anchor into the chart when you want one planet to orient the whole reading.`,
        note: planetOfDay.is_retrograde ? 'Retrograde motion is active in this placement.' : 'Open the chart and select another graha or house to compare the structure.',
      };
    }

    return chartFocus;
  }, [chartFocus, planetOfDay, selectedNode]);

  const contextCards = useMemo(
    () => buildContextCards({ personalPayload, muhurtaPayload, selectedFocus, state }),
    [muhurtaPayload, personalPayload, selectedFocus, state],
  );

  const sunriseValue = personalPayload?.local_sunrise || personalPayload?.sunrise;
  const sunsetValue = personalPayload?.sunset;
  const placeLabel = preset?.label || personalPayload?.location?.title || payload?.location?.title || 'Kathmandu, NP';

  if (loading) {
    return (
      <section className="kundali-editorial animate-fade-in-up consumer-route consumer-route--analysis">
        <div className="skeleton kundali-editorial__hero-skeleton" />
        <div className="skeleton kundali-editorial__band-skeleton" />
        <div className="skeleton kundali-editorial__band-skeleton" />
      </section>
    );
  }

  if (error || !payload) {
    return (
      <section className="kundali-editorial animate-fade-in-up consumer-route consumer-route--analysis">
        <article className="kundali-editorial__error editorial-card" role="alert">
          <p className="kundali-editorial__eyebrow">Personal Path</p>
          <h1>Birth Reading is unavailable right now.</h1>
          <p>{error || 'The kundali profile could not be assembled from the live payloads.'}</p>
        </article>
      </section>
    );
  }

  return (
    <section className="kundali-editorial animate-fade-in-up consumer-route consumer-route--analysis">
      <header className="kundali-editorial__masthead">
        <div className="kundali-editorial__masthead-copy">
          <div className="kundali-editorial__kicker-row">
            <span className="kundali-editorial__eyebrow">Personal Path</span>
            <span className="kundali-editorial__rule" />
          </div>
          <h1>Janma Kundali</h1>
          <p>
            The celestial map of your soul&apos;s descent, etched in the alignment of the stars at the moment of your first breath.
          </p>
        </div>

        <div className="kundali-editorial__masthead-meta">
          <div className="kundali-editorial__place-row">
            <span className="material-symbols-outlined">location_on</span>
            <span>{placeLabel}</span>
          </div>
          <div className="kundali-editorial__calendar-readout">
            <strong>{formatBsDate(personalPayload?.bikram_sambat)}</strong>
            <span>{formatBsMeta(personalPayload?.bikram_sambat, personalPayload)}</span>
          </div>
        </div>
      </header>

      <section className="kundali-editorial__hero-grid">
        <article className="kundali-editorial__chart-panel editorial-card">
          <div className="kundali-editorial__panel-label">Birth chart / राशिचक्र</div>
          <div className="kundali-editorial__chart-stage">
            <KundaliGraph payload={graphDisplayPayload} selectedNode={selectedNode} onSelectNode={setSelectedNode} />
          </div>

          <div className="kundali-editorial__signature-row">
            <div>
              <span>Ascendant</span>
              <strong>{payload?.lagna?.rashi_english || 'Pending'}</strong>
            </div>
            <div>
              <span>Nakshatra</span>
              <strong>{personalPayload?.nakshatra?.name || 'Pending'}</strong>
            </div>
            <div>
              <span>Strongest pull</span>
              <strong>{signature[2]?.value || 'Pending'}</strong>
            </div>
          </div>
        </article>

        <div className="kundali-editorial__side-stack">
          <article className="kundali-editorial__insight-card glass-panel">
            <div className="kundali-editorial__insight-head">
              <span className="material-symbols-outlined">flare</span>
              <div>
                <span>{selectedFocus.eyebrow}</span>
                <strong>{selectedFocus.title}</strong>
              </div>
            </div>
            <div className="kundali-editorial__insight-copy">
              <h2>{selectedFocus.body}</h2>
              <p>{thesis}</p>
            </div>
            <div className="kundali-editorial__insight-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => saveReading({
                  id: datetimeIso,
                  title: `${payload?.lagna?.rashi_english || 'Birth'} Reading`,
                  summary: thesis,
                })}
              >
                Save Reading
              </button>
              <EvidenceDrawer
                title="Birth Reading"
                intro="This keeps the place, method profile, and trace metadata nearby without forcing the technical reading first."
                methodRef={graphMeta?.method || meta?.method || payload?.method_profile || 'Birth reading profile'}
                confidenceNote={graphMeta?.confidence?.level || graphMeta?.confidence || meta?.confidence?.level || payload?.quality_band || 'Interpretive guidance'}
                placeUsed={placeLabel}
                computedForDate={datetimeLocal}
                availability={[
                  { label: 'Summary reading', available: Boolean(thesis), note: 'The main reading is built from lagna, moon placement, and available insight blocks.' },
                  { label: 'Interactive chart', available: Boolean(graphPayload?.layout), note: 'Chart relationships stay visible without overwhelming the opening read.' },
                  { label: 'Personal panchanga', available: Boolean(personalPayload), note: 'Daily rhythm appears when the place-aware panchanga payload is available.' },
                ]}
                meta={graphMeta || meta}
                traceFallbackId={graphPayload?.calculation_trace_id || payload?.calculation_trace_id}
              />
            </div>
          </article>

          <article className="kundali-editorial__positions-card editorial-card">
            <h2>Planetary Positions</h2>
            <div className="kundali-editorial__positions-table">
              <table>
                <thead>
                  <tr>
                    <th>Graha</th>
                    <th>Rashi</th>
                    <th>Degree</th>
                    <th>Speed</th>
                  </tr>
                </thead>
                <tbody>
                  {grahaRows.map(([id, row]) => (
                    <tr key={id}>
                      <td>{row.name_english}</td>
                      <td>{row.rashi_english || 'Pending'}</td>
                      <td>{formatPlanetDegree(row)}</td>
                      <td>{formatPlanetSpeed(row)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        </div>
      </section>

      <section className="kundali-editorial__panchanga-block">
        <div className="kundali-editorial__section-head">
          <div>
            <h2>Personal Panchanga</h2>
            <p>Your daily rhythms recalculated for the same place and time as the chart.</p>
          </div>
          <Link className="kundali-editorial__spark-link" to="/my-place">
            <span className="material-symbols-outlined">auto_awesome</span>
          </Link>
        </div>

        <div className="kundali-editorial__panchanga-grid">
          {panchangaCards.map((item) => (
            <article key={item.label} className="kundali-editorial__panchanga-card">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <small>{item.note}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="kundali-editorial__context-grid">
        <article className="kundali-editorial__context-card kundali-editorial__context-card--map editorial-card">
          <span className="material-symbols-outlined">map</span>
          <h2>Almanac Context</h2>
          <p>Celestial timings adjusted for your current terrestrial coordinates and saved timezone.</p>
          <div className="kundali-editorial__sun-marks">
            <div>
              <span>Sunrise</span>
              <strong>{sunriseValue ? formatProductTime(sunriseValue, state) : 'Pending'}</strong>
            </div>
            <div>
              <span>Sunset</span>
              <strong>{sunsetValue ? formatProductTime(sunsetValue, state) : 'Pending'}</strong>
            </div>
          </div>
        </article>

        <div className="kundali-editorial__context-stack">
          {contextCards.map((item) => (
            <article key={item.title} className="kundali-editorial__context-card">
              <div className="kundali-editorial__context-icon">
                <span className="material-symbols-outlined">{item.icon}</span>
              </div>
              <div>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="kundali-editorial__reading-grid">
        <article className="kundali-editorial__reading-card editorial-card">
          <div className="kundali-editorial__section-tag">Chart themes</div>
          <h2>The reading in plain language</h2>
          <p className="kundali-editorial__reading-copy">{thesis}</p>
          <div className="kundali-editorial__theme-grid">
            {themeCards.map((card) => (
              <article key={card.title} className="kundali-editorial__theme-card">
                <h3>{card.title}</h3>
                <p>{card.body}</p>
              </article>
            ))}
          </div>
        </article>

        <div className="kundali-editorial__reading-rail">
          <article className="kundali-editorial__signals-card">
            <div className="kundali-editorial__section-tag">What shapes it</div>
            <div className="kundali-editorial__signal-list">
              {signalList.map((item) => (
                <div key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </article>

          <article className="kundali-editorial__signals-card">
            <div className="kundali-editorial__section-tag">Chart geometry</div>
            <div className="kundali-editorial__signal-list">
              {chartStats.map((item) => (
                <div key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </article>
        </div>
      </section>

      <section className="kundali-editorial__bottom-grid">
        <article className="kundali-editorial__insight-list-card editorial-card">
          <div className="kundali-editorial__section-tag">Interpretive highlights</div>
          <h2>Where the chart concentrates</h2>
          <div className="kundali-editorial__highlight-list">
            {insightHighlights.length ? insightHighlights.map((item) => (
              <article key={item.id} className="kundali-editorial__highlight-item">
                <h3>{item.title}</h3>
                <p>{item.summary}</p>
              </article>
            )) : (
              <p className="muted">Interpretive highlights will appear here when the graph payload includes them.</p>
            )}
          </div>
        </article>

        <article className="kundali-editorial__dasha-card editorial-card">
          <div className="kundali-editorial__section-tag">Dasha rhythm</div>
          <h2>Long-cycle emphasis</h2>
          <div className="kundali-editorial__highlight-list">
            {dashaCards.length ? dashaCards.map((item) => (
              <article key={item.id} className="kundali-editorial__highlight-item">
                <h3>{item.value}</h3>
                <p>{item.note}</p>
              </article>
            )) : (
              <p className="muted">Major period highlights appear here when the dasha timeline is available.</p>
            )}
          </div>
        </article>
      </section>

      <details className="kundali-editorial__drawer editorial-card">
        <summary>Birth details and coordinates</summary>
        <form className="kundali-editorial__controls" onSubmit={(event) => event.preventDefault()}>
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
        </form>
      </details>

      <details className="kundali-editorial__drawer editorial-card">
        <summary>Technical details</summary>
        <div className="kundali-editorial__technical-grid">
          <article className="kundali-editorial__technical-card">
            <h3>Graha detail</h3>
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
                    <td>{formatPlanetDegree(row)}</td>
                    <td>{row.dignity?.state || 'neutral'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <article className="kundali-editorial__technical-card">
            <h3>Pattern counts</h3>
            <div className="kundali-editorial__signal-list">
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
            </div>
          </article>
        </div>
      </details>

      <KnowledgePanel
        title={knowledge.title}
        intro={knowledge.intro}
        sections={knowledge.sections}
        className="kundali-editorial__knowledge"
      />
    </section>
  );
}

export default KundaliPage;
