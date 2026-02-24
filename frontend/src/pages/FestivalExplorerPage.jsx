import { useEffect, useMemo, useState } from 'react';
import { festivalAPI } from '../services/api';
import { useTemporalContext } from '../context/TemporalContext';
import { TimelineRibbon } from '../components/TimelineRibbon/TimelineRibbon';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import './FestivalExplorerPage.css';

function addDays(base, days) {
  const d = new Date(`${base}T00:00:00`);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export function FestivalExplorerPage() {
  const { state } = useTemporalContext();
  const [fromDate, setFromDate] = useState(state.date);
  const [windowDays, setWindowDays] = useState(180);
  const [category, setCategory] = useState('');
  const [region, setRegion] = useState('');

  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const toDate = useMemo(() => addDays(fromDate, windowDays), [fromDate, windowDays]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const envelope = await festivalAPI.getTimelineEnvelope({
          from: fromDate,
          to: toDate,
          qualityBand: state.qualityBand,
          category: category || undefined,
          region: region || undefined,
          lang: state.language,
        });

        if (!cancelled) {
          setPayload(envelope.data);
          setMeta(envelope.meta);
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setMeta(null);
          setError(err.message || 'Failed to load festival timeline');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [fromDate, toDate, category, region, state.qualityBand, state.language]);

  return (
    <section className="explorer-page animate-fade-in-up">
      <header className="explorer-hero">
        <h1 className="text-hero">Festival Explorer Ribbon</h1>
        <p className="explorer-hero__sub">Browse observances continuously across months with quality-aware filters.</p>
      </header>

      <div className="explorer-filters">
        <label className="ink-input explorer-control">
          <span>From</span>
          <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
        </label>

        <label className="ink-input explorer-control">
          <span>Window</span>
          <select value={windowDays} onChange={(e) => setWindowDays(Number(e.target.value))}>
            <option value={90}>90 days</option>
            <option value={180}>180 days</option>
            <option value={365}>365 days</option>
          </select>
        </label>

        <label className="ink-input explorer-control">
          <span>Category</span>
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All</option>
            <option value="national">National</option>
            <option value="newari">Newari</option>
            <option value="hindu">Hindu</option>
            <option value="buddhist">Buddhist</option>
            <option value="regional">Regional</option>
          </select>
        </label>

        <label className="ink-input explorer-control explorer-control--wide">
          <span>Region</span>
          <input
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            placeholder="kathmandu_valley"
          />
        </label>
      </div>

      {loading && (
        <div className="explorer-grid">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton explorer-skeleton" />
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="ink-card explorer-error" role="alert">
          <h3>Could not load timeline</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <TimelineRibbon groups={payload?.groups || []} />
      )}

      {state.mode === 'authority' && !loading && !error && (
        <AuthorityInspector
          title="Explorer Authority"
          meta={meta}
          traceFallbackId={payload?.calculation_trace_id}
        />
      )}
    </section>
  );
}

export default FestivalExplorerPage;
