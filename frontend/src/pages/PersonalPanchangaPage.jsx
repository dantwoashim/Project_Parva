import { useEffect, useState } from 'react';
import { personalAPI } from '../services/api';
import './PersonalPanchangaPage.css';

function todayIso() {
  return new Date(Date.now()).toISOString().slice(0, 10);
}

export function PersonalPanchangaPage() {
  const [date, setDate] = useState(todayIso());
  const [lat, setLat] = useState('27.7172');
  const [lon, setLon] = useState('85.3240');
  const [tz, setTz] = useState('Asia/Kathmandu');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await personalAPI.getPanchanga({ date, lat, lon, tz });
      setPayload(data);
    } catch (err) {
      setPayload(null);
      setError(err.message || 'Failed to load personal panchanga');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="personal-page">
      <header className="glass-card personal-page__header">
        <div>
          <h2 className="text-display">Personal Panchanga</h2>
          <p>Location-aware daily panchanga with traceable metadata.</p>
        </div>

        <form
          className="personal-page__controls"
          onSubmit={(e) => {
            e.preventDefault();
            load();
          }}
        >
          <label>
            <span>Date</span>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
          </label>
          <label>
            <span>Lat</span>
            <input value={lat} onChange={(e) => setLat(e.target.value)} placeholder="27.7172" />
          </label>
          <label>
            <span>Lon</span>
            <input value={lon} onChange={(e) => setLon(e.target.value)} placeholder="85.3240" />
          </label>
          <label>
            <span>Timezone</span>
            <input value={tz} onChange={(e) => setTz(e.target.value)} placeholder="Asia/Kathmandu" />
          </label>
          <button type="submit" className="btn btn-primary">Refresh</button>
        </form>
      </header>

      {loading && (
        <div className="glass-card personal-page__state">
          <h3>Calculating personal panchanga...</h3>
          <div className="skeleton" style={{ height: '180px', marginTop: '1rem' }} />
        </div>
      )}

      {!loading && error && (
        <div className="glass-card personal-page__state" role="alert">
          <h3>Unable to load personal panchanga</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && payload && (
        <>
          <section className="personal-page__grid">
            <article className="glass-card personal-card">
              <h3>Tithi</h3>
              <p className="value">{payload.tithi?.name || '—'}</p>
              <p className="meta">#{payload.tithi?.number || '—'} · {payload.tithi?.paksha || '—'}</p>
            </article>
            <article className="glass-card personal-card">
              <h3>Nakshatra</h3>
              <p className="value">{payload.nakshatra?.name || '—'}</p>
              <p className="meta">#{payload.nakshatra?.number || '—'}</p>
            </article>
            <article className="glass-card personal-card">
              <h3>Yoga</h3>
              <p className="value">{payload.yoga?.name || '—'}</p>
              <p className="meta">#{payload.yoga?.number || '—'}</p>
            </article>
            <article className="glass-card personal-card">
              <h3>Karana</h3>
              <p className="value">{payload.karana?.name || '—'}</p>
              <p className="meta">#{payload.karana?.number || '—'}</p>
            </article>
            <article className="glass-card personal-card">
              <h3>Vaara</h3>
              <p className="value">{payload.vaara?.name_english || '—'}</p>
              <p className="meta">{payload.vaara?.name_sanskrit || '—'}</p>
            </article>
          </section>

          <section className="glass-card personal-page__meta">
            <h3>Computation Context</h3>
            <div className="personal-page__meta-grid">
              <p><strong>Date:</strong> {payload.date}</p>
              <p><strong>BS:</strong> {payload.bikram_sambat?.year} {payload.bikram_sambat?.month_name} {payload.bikram_sambat?.day}</p>
              <p><strong>Location:</strong> {payload.location?.latitude}, {payload.location?.longitude}</p>
              <p><strong>Timezone:</strong> {payload.location?.timezone}</p>
              <p><strong>Confidence:</strong> {payload.confidence || 'unknown'}</p>
              <p><strong>Quality Band:</strong> {payload.quality_band || 'validated'}</p>
              <p><strong>Method Profile:</strong> {payload.method_profile || payload.method || 'unknown'}</p>
              <p><strong>Advisory Scope:</strong> {payload.advisory_scope || 'informational'}</p>
              <p><strong>Trace ID:</strong> {payload.calculation_trace_id || 'N/A'}</p>
            </div>
            {Array.isArray(payload.warnings) && payload.warnings.length > 0 && (
              <ul className="personal-page__warnings">
                {payload.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </section>
  );
}

export default PersonalPanchangaPage;
