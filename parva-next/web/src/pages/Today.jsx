import { Link } from "react-router-dom";
import { fmt, todayISO, useParva, workingLabel } from "../api.js";
import { Source, Status } from "../ui.jsx";

export default function Today() {
  const iso = todayISO();
  const today = useParva("/v1/convert", { ad: iso });
  const work = useParva("/v1/working-day", { ad: iso });
  const next = useParva("/v1/upcoming", { ad: iso, count: 5 });
  const panchanga = useParva("/v1/panchanga", { ad: iso });
  return <>
    <div className="eyebrow">NEPAL STANDARD TIME · UTC +05:45</div>
    <section className="today-layout">
      <div className="date-panel">
        <h1>Your day, in Nepal.</h1><Status {...today} />
        {today.data && <>
          <div className="date-number">{today.data.bs.day}<span>{today.data.bs.month_name}<br /><span className="muted">{today.data.bs.year} BS</span></span></div>
          <p className="ne native-date">{today.data.bs.nepali}</p>
          <p className="muted">{fmt(today.data.ad)}</p>
          <div className="row"><Link className="button" to="/calendar">Open calendar</Link><Link className="text-link" to="/convert">Convert a date →</Link></div>
        </>}
      </div>
      <aside className="day-status">
        <div className="eyebrow">NATIONAL SCOPE · SATURDAY WEEKEND</div>
        <Status {...work} />
        {work.data && <>
          <h2>{workingLabel(work.data.working)}</h2>
          {work.data.weekend && <p>Saturday weekend under the selected policy.</p>}
          {work.data.holidays.map((holiday) => <p key={holiday.id}>{holiday.name}</p>)}
          {work.data.working === null && <p>The included notices cannot establish whether today is a working day.</p>}
          <p className="small muted">Holiday coverage: {work.data.coverage}. Check applicable notices and your employer’s policy.</p>
          <Source id={work.source} /><p><Link to="/holidays">Explore holiday evidence →</Link></p>
        </>}
      </aside>
    </section>
    <div className="dashboard-lower">
      <section><div className="section-heading"><h2>Coming up</h2><Link to="/festivals">All festivals →</Link></div>
        <Status {...next} />
        <div className="event-list">{next.data?.map((festival) => <Link className="event" key={festival.id} to={`/festivals/${festival.id}`}>
          <span className="event-date">{fmt(festival.start)}</span><span>{festival.name}<small className="ne muted">{festival.name_ne}</small></span><Source id={festival.source} />
        </Link>)}</div>
        {next.data?.length === 0 && <p className="muted">No upcoming dates within the supported range.</p>}
      </section>
      <section><div className="section-heading"><h2>At sunrise</h2><span className="small muted">Kathmandu · computed</span></div><Status {...panchanga} />
        {panchanga.data && <dl className="facts">{[
          ["Tithi", `${panchanga.data.tithi_name} · ${panchanga.data.paksha}`],
          ["Lunar month", panchanga.data.lunar_month + (panchanga.data.adhik_month ? " (adhik)" : "")],
          ["Nakshatra", panchanga.data.nakshatra],
          ["Sunrise / sunset", `${panchanga.data.sunrise.slice(11,16)} / ${panchanga.data.sunset.slice(11,16)}`],
        ].map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>}
      </section>
    </div>
  </>;
}
