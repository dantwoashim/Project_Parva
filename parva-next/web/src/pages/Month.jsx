import { Link, useNavigate, useParams } from "react-router-dom";
import { todayISO, useParva } from "../api.js";
import { Coverage, Source, Status } from "../ui.jsx";

const NAMES = ["Baishakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"];
const DOW = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];

const addDays = (iso, n) => { const d = new Date(`${iso}T00:00:00Z`); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };

export default function Month() {
  const today = useParva("/v1/today");
  const params = useParams();
  const navigate = useNavigate();
  const year = Number(params.year ?? today.data?.bs.year);
  const month = Number(params.month ?? today.data?.bs.month);
  const page = useParva(year ? `/v1/month/${year}/${month}` : null);
  const m = year && page.data?.days ? page.data : null;
  const todayAD = todayISO();
  const holidayOn = (ad) => (m.holidays ?? []).filter((h) => { const gap = (new Date(ad) - new Date(h.ad)) / 864e5; return h.closure !== false && gap >= 0 && gap < h.days; });
  const goYear = (e) => { const y = Number(e.target.value); if (y >= 2000 && y <= 2095 && y !== year) navigate(`/calendar/${y}/${month}`); };
  const step = (delta) => { const idx = (month - 1 + delta + 12) % 12; navigate(`/calendar/${year + Math.floor((month - 1 + delta) / 12)}/${idx + 1}`); };

  return (
    <>
      <h1>{m ? `${NAMES[month - 1]} ${year}` : "Calendar"}</h1>
      <Status loading={today.loading || page.loading} error={page.error || today.error} />
      {m && (
        <>
          <p className="row">
            <button className="quiet" disabled={year === 2000 && month === 1} onClick={() => step(-1)}>← previous</button>
            <select aria-label="BS month" value={month} onChange={(e) => navigate(`/calendar/${year}/${e.target.value}`)}>
              {NAMES.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}
            </select>
            <input aria-label="BS year" type="number" min="2000" max="2095" key={year} defaultValue={year} style={{ width: "6rem" }}
              onBlur={goYear} onKeyDown={(e) => e.key === "Enter" && goYear(e)} />
            <button className="quiet" onClick={() => navigate(`/calendar/${today.data?.bs.year}/${today.data?.bs.month}`)}>today</button>
            <button className="quiet" disabled={year === 2095 && month === 12} onClick={() => step(1)}>next →</button>
            <Source id={page.source} />
          </p>
          <p className="muted small">{m.days} days · {m.start_ad} to {m.end_ad}</p>
          <Coverage value={m.coverage} />
          <div className="month">
            {DOW.map((d) => <div key={d} className="dow">{d}</div>)}
            {Array.from({ length: (m.start_weekday + 1) % 7 }, (_, i) => <div key={`pad${i}`} />)}
            {Array.from({ length: m.days }, (_, i) => {
              const ad = addDays(m.start_ad, i);
              const dow = (m.start_weekday + 1 + i) % 7;
              const hs = holidayOn(ad);
              const cls = ["day", dow === 6 ? "sat" : "", hs.some((h) => h.scope === "national") ? "holiday" : "", ad === todayAD ? "today" : ""].join(" ");
              return (
                <div key={ad} className={cls} title={hs.map((h) => h.name).join(", ")}>
                  <span className="bs">{i + 1}</span><span className="ad">{Number(ad.slice(8))}</span>
                  {hs.slice(0, 2).map((h) => <span key={h.id} className="tag">{h.name}</span>)}
                </div>
              );
            })}
          </div>
          {m.holidays.length > 0 && (
            <div className="scroll"><table style={{ marginTop: "1.5rem" }}>
              <thead><tr><th>Recorded this month</th><th>BS</th><th>AD</th><th>For</th><th>Gazette line</th></tr></thead>
              <tbody>{m.holidays.map((h) => (
                <tr key={h.id + h.ad}><td>{h.name}{h.days > 1 ? ` (${h.days} days)` : ""}</td><td className="mono">{h.bs}</td><td className="mono">{h.ad}</td><td>{h.scope}</td><td className="ne small">{h.text}<p className="muted">{h.closure === false ? "Observance · " : ""}{h.review === "source_checked" ? `PDF p. ${h.source_page}` : "Needs source review"}</p></td></tr>
              ))}</tbody>
            </table></div>
          )}
          {!m.holidays.length && <p className="muted small">No recorded holidays in this month. <Link to="/data">Which years are covered?</Link></p>}
        </>
      )}
    </>
  );
}
