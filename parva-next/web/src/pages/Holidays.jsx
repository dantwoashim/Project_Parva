import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { fmt, useParva } from "../api.js";
import { Coverage, Source, Status } from "../ui.jsx";

export default function Holidays() {
  const today = useParva("/v1/today");
  const params = useParams();
  const navigate = useNavigate();
  const year = Number(params.year ?? today.data?.bs.year);
  const page = useParva(year ? `/v1/holidays/${year}` : null, { scope: "all" });
  const coverage = useParva(year ? `/v1/coverage/${year}` : null);
  const days = year && Array.isArray(page.data) ? page.data : [];
  const [scope, setScope] = useState("all");
  const scopes = [...new Set(days.flatMap((h) => h.scopes ?? [h.scope]))].sort();
  const rows = days.filter((h) => scope === "all" || h.scope === "national" || (h.scopes ?? [h.scope]).includes(scope));

  return (
    <>
      <h1>Holidays {year ? <span className="muted">BS {year}</span> : ""}</h1>
      <Status loading={today.loading || page.loading} error={page.error || today.error} />
      {year > 0 && (
        <>
          <p className="row">
            <button className="quiet" disabled={year <= 2000} onClick={() => navigate(`/holidays/${year - 1}`)}>← {year - 1}</button>
            <button className="quiet" disabled={year >= 2095} onClick={() => navigate(`/holidays/${year + 1}`)}>{year + 1} →</button>
            <select aria-label="Holiday scope" value={scope} onChange={(e) => setScope(e.target.value)}>
              <option value="all">all scopes</option>
              <option value="national">national</option>
              {scopes.filter((s) => s !== "national").map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <Source id={page.source} />
            <a className="small" href={`/v1/holidays/${year}.ics?scope=${scope}`}>Reviewed closures (.ics)</a>
          </p>
          <Coverage value={coverage.data?.coverage} />
          {!days.length && (
            <p className="muted">No gazette on file for BS {year}. <Link to="/data">Which years are covered?</Link></p>
          )}
          {rows.length > 0 && (
            <div className="scroll"><table>
              <thead><tr><th>AD</th><th>BS</th><th>Name</th><th>Scope</th><th>Gazette line</th></tr></thead>
              <tbody>{rows.map((h) => (
                <tr key={h.id + h.ad}>
                  <td>{fmt(h.ad)}</td>
                  <td className="mono">{h.bs}</td>
                  <td title={h.span === "assumed" ? "end date not in the gazette text; span assumed" : undefined}>
                    {h.name}{h.days > 1 ? ` (${h.days} days)` : ""}
                    {h.span === "assumed" && <span className="muted small"> (assumed)</span>}
                  </td>
                  <td>{(h.scopes ?? [h.scope]).join(", ")}<br /><span className="small muted">{h.closure === false ? "Observance; no closure in this notice" : "Closure"}</span></td>
                  <td className="ne small">{h.text}<p className="muted">{h.review === "source_checked" ? `Source reviewed · PDF p. ${h.source_page}` : "Needs source review"}</p></td>
                </tr>
              ))}</tbody>
            </table></div>
          )}
        </>
      )}
    </>
  );
}
