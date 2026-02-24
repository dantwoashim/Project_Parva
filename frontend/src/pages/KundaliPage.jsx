import { useEffect, useMemo, useState } from 'react';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import { KnowledgePanel } from '../components/UI/KnowledgePanel';
import { KundaliGraph } from '../components/KundaliGraph/KundaliGraph';
import { KUNDALI_GLOSSARY } from '../data/temporalGlossary';
import { glossaryAPI, kundaliAPI } from '../services/api';
import { useTemporalContext } from '../context/TemporalContext';
import './KundaliPage.css';

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

export function KundaliPage() {
  const { state } = useTemporalContext();

  const [datetimeLocal, setDatetimeLocal] = useState(defaultDateTime());
  const [lat, setLat] = useState(String(state.location?.latitude ?? 27.7172));
  const [lon, setLon] = useState(String(state.location?.longitude ?? 85.3240));
  const [tz, setTz] = useState(state.timezone || 'Asia/Kathmandu');
  const [selectedNode, setSelectedNode] = useState(null);

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

  const activeInsight = useMemo(() => {
    if (!selectedNode || !graphPayload?.layout) return graphPayload?.insight_blocks || payload?.insight_blocks || [];
    const isHouse = selectedNode.startsWith('house_');
    if (isHouse) {
      const houseNo = Number(selectedNode.split('_')[1]);
      return [
        {
          id: selectedNode,
          title: `House ${houseNo}`,
          summary: (payload?.houses || []).find((h) => h.house_number === houseNo)?.rashi_english || 'House focus',
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
          summary: `${graha.rashi_english || 'Unknown sign'} · ${graha.longitude}° · ${graha.is_retrograde ? 'Retrograde' : 'Direct'}`,
        },
        ...(graphPayload?.insight_blocks || []),
      ];
    }
    return graphPayload?.insight_blocks || [];
  }, [selectedNode, graphPayload, payload]);

  return (
    <section className="kundali-page animate-fade-in-up">
      <form className="kundali-controls ink-card" onSubmit={(e) => { e.preventDefault(); load(); }}>
        <label className="ink-input">
          <span>Birth Date & Time</span>
          <input type="datetime-local" value={datetimeLocal} onChange={(e) => setDatetimeLocal(e.target.value)} required />
        </label>
        <label className="ink-input">
          <span>Latitude</span>
          <input value={lat} onChange={(e) => setLat(e.target.value)} />
        </label>
        <label className="ink-input">
          <span>Longitude</span>
          <input value={lon} onChange={(e) => setLon(e.target.value)} />
        </label>
        <label className="ink-input">
          <span>Timezone</span>
          <input value={tz} onChange={(e) => setTz(e.target.value)} />
        </label>
        <button className="btn btn-primary" type="submit">Generate</button>
      </form>

      {loading && <div className="skeleton" style={{ height: '320px', borderRadius: '16px' }} />}

      {!loading && error && (
        <div className="ink-card kundali-error" role="alert">
          <h3>Unable to load kundali</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && payload && (
        <>
          <section className="kundali-hero-row">
            <article className="ink-card ink-card--saffron kundali-rashi-card">
              <h3>Moon Rashi</h3>
              <p>{payload.grahas?.moon?.rashi_sanskrit || '—'}</p>
              <small>{payload.grahas?.moon?.rashi_english || '—'}</small>
            </article>
            <article className="ink-card ink-card--gold kundali-rashi-card">
              <h3>Lagna</h3>
              <p>{payload.lagna?.rashi_sanskrit || '—'}</p>
              <small>{payload.lagna?.rashi_english || '—'}</small>
            </article>
            <article className="ink-card kundali-rashi-card">
              <h3>Signals</h3>
              <p>{payload.yogas?.length || 0} yoga · {payload.doshas?.length || 0} dosha</p>
              <small>{payload.aspects?.length || 0} aspects</small>
            </article>
          </section>

          <section className="kundali-graph-layout">
            <div className="ink-card kundali-graph-shell">
              <KundaliGraph payload={graphPayload} selectedNode={selectedNode} onSelectNode={setSelectedNode} />
            </div>

            <aside className="ink-card kundali-insight-pane">
              <h3>Interpretation Sidebar</h3>
              <div className="kundali-insight-list">
                {activeInsight.map((item) => (
                  <article key={item.id} className="kundali-insight-item">
                    <h4>{item.title}</h4>
                    <p>{item.summary}</p>
                  </article>
                ))}
              </div>
            </aside>
          </section>

          <section className="ink-card kundali-table-wrap">
            <h3>Graha Table</h3>
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
                    <td>{row.longitude}°</td>
                    <td>{row.dignity?.state || 'neutral'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <KnowledgePanel
            title={knowledge.title}
            intro={knowledge.intro}
            sections={knowledge.sections}
            className="kundali-knowledge"
          />

          {state.mode === 'authority' && (
            <AuthorityInspector
              title="Kundali Authority"
              meta={graphMeta || meta}
              traceFallbackId={graphPayload?.calculation_trace_id || payload?.calculation_trace_id}
            />
          )}
        </>
      )}
    </section>
  );
}

export default KundaliPage;
