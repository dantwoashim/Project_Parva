import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { temporalAPI } from '../services/api';
import { useTemporalContext } from '../context/TemporalContext';
import { OrbitalRing } from '../components/Compass/OrbitalRing';
import { HorizonStrip } from '../components/Compass/HorizonStrip';
import { AuthorityInspector } from '../components/UI/AuthorityInspector';
import './TemporalCompassPage.css';

function toNumber(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function TemporalCompassPage() {
  const navigate = useNavigate();
  const { state, setDate } = useTemporalContext();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [meta, setMeta] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const envelope = await temporalAPI.getCompassEnvelope({
          date: state.date,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          qualityBand: state.qualityBand,
        });
        if (!cancelled) {
          setData(envelope.data);
          setMeta(envelope.meta);
        }
      } catch (err) {
        if (!cancelled) {
          setData(null);
          setMeta(null);
          setError(err.message || 'Failed to load Temporal Compass');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone, state.qualityBand]);

  const festivalsToday = data?.today?.festivals || [];
  const bsLabel = useMemo(() => {
    const bs = data?.bikram_sambat;
    if (!bs) return '—';
    return `${bs.year} ${bs.month_name} ${bs.day}`;
  }, [data]);

  return (
    <section className="compass-page animate-fade-in-up">
      <header className="compass-hero ink-card">
        <div>
          <p className="compass-eyebrow">Temporal Compass</p>
          <h1>{bsLabel}</h1>
          <p className="compass-subtitle">
            {data?.primary_readout?.tithi_name || '—'} · {data?.primary_readout?.paksha || '—'}
          </p>
          <label className="ink-input compass-date-input">
            <span>Date</span>
            <input type="date" value={state.date} onChange={(e) => setDate(e.target.value)} />
          </label>
        </div>

        <OrbitalRing
          ratio={toNumber(data?.orbital?.phase_ratio, 0)}
          number={data?.orbital?.tithi}
          label="Lunar progression"
        />
      </header>

      {loading && (
        <div className="compass-loading">
          <div className="skeleton" style={{ height: '120px', borderRadius: '18px' }} />
          <div className="skeleton" style={{ height: '280px', borderRadius: '18px' }} />
        </div>
      )}

      {!loading && error && (
        <div className="ink-card compass-error" role="alert">
          <h3>Could not load temporal compass</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <HorizonStrip
            sunrise={data?.horizon?.sunrise}
            sunset={data?.horizon?.sunset}
            currentMuhurta={data?.horizon?.current_muhurta}
          />

          <section className="compass-signals">
            <article className="ink-card">
              <h3>Nakshatra</h3>
              <p>{data?.signals?.nakshatra?.name || '—'}</p>
            </article>
            <article className="ink-card">
              <h3>Yoga</h3>
              <p>{data?.signals?.yoga?.name || '—'}</p>
            </article>
            <article className="ink-card">
              <h3>Karana</h3>
              <p>{data?.signals?.karana?.name || '—'}</p>
            </article>
            <article className="ink-card">
              <h3>Vaara</h3>
              <p>{data?.signals?.vaara?.name_english || '—'}</p>
            </article>
          </section>

          <section className="compass-festivals ink-card">
            <header>
              <h2>Today&apos;s Festivals</h2>
              <p>{festivalsToday.length} active</p>
            </header>
            {!festivalsToday.length && <p className="muted">No observances in current quality filter.</p>}
            <div className="compass-festivals__list">
              {festivalsToday.map((festival) => (
                <button
                  key={`${festival.id}-${festival.start_date}`}
                  type="button"
                  className="compass-festival-card"
                  onClick={() => navigate(`/festivals/${festival.id}`)}
                >
                  <span>{festival.name}</span>
                  <small>{festival.start_date}</small>
                </button>
              ))}
            </div>
          </section>

          {state.mode === 'authority' && (
            <AuthorityInspector
              title="Temporal Compass Authority"
              meta={meta}
              traceFallbackId={data?.calculation_trace_id}
            />
          )}
        </>
      )}
    </section>
  );
}

export default TemporalCompassPage;
