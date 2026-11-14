import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fmt, todayISO, useParva } from "../api.js";
import { Source, Status } from "../ui.jsx";

const thisYear = Number(todayISO().slice(0, 4));
const NAMES = ["Baishakh", "Jestha", "Ashadh", "Shrawan", "Bhadra", "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"];
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

/** A festival rule as one English sentence: "Kartik krishna 15 (amavasya), evening anchor". */
function ruleText(rule) {
  if (!rule) return "committee-decided; gazette only";
  if (rule.bs) return `${NAMES[rule.bs[0] - 1]} ${rule.bs[1]} (fixed BS date)`;
  if (rule.after) return `${rule.offset} day${rule.offset === 1 ? "" : "s"} after ${rule.after}`;
  if (rule.same_as) return `same day as ${rule.same_as}`;
  if (!rule.tithi) return "committee-decided; gazette only";
  const moon = rule.tithi === 15 ? (rule.paksha === "krishna" ? " (amavasya)" : " (purnima)") : rule.tithi === 30 ? " (amavasya)" : "";
  return `${cap(rule.month)} ${rule.paksha} ${rule.tithi}${moon}${rule.at ? `, ${rule.at} anchor` : ""}`;
}

export function FestivalList() {
  const [year, setYear] = useState(thisYear);
  const list = useParva("/v1/festivals", { year });
  return (
    <>
      <h1>Festivals <span className="muted">{year}</span></h1>
      <p className="row">
        <button className="quiet" aria-label="Previous year" disabled={year <= 1944} onClick={() => setYear(year - 1)}>← {year - 1}</button>
        <button className="quiet" aria-label="Next year" disabled={year >= 2038} onClick={() => setYear(year + 1)}>{year + 1} →</button>
        <span className="small muted">Source labels distinguish recorded notice dates from computed estimates. Festival duration does not imply an office closure.</span>
      </p>
      <Status {...list} />
      {list.data && (
        <div className="scroll"><table>
          <thead><tr><th>Date</th><th>Festival</th><th>Source</th><th>Engine says</th></tr></thead>
          <tbody>{list.data.filter((f) => f.start).map((f) => (
            <tr key={f.id}>
              <td className="mono">{f.start}{f.end !== f.start ? ` → ${f.end}` : ""}</td>
              <td><Link to={`/festivals/${f.id}`}>{f.name}</Link> <span className="ne muted">{f.name_ne}</span></td>
              <td><Source id={f.source} /></td>
              <td className="mono muted">{!f.engine ? "no rule" : !f.gazette ? "no gazette" : f.engine === f.gazette ? "agrees" : `${f.engine} (differs)`}</td>
            </tr>
          ))}</tbody>
        </table></div>
      )}
    </>
  );
}

export function FestivalDetail() {
  const { id } = useParams();
  const [year, setYear] = useState(thisYear);
  const f = useParva(`/v1/festivals/${id}`, { year });
  const d = f.data;
  return (
    <>
      <Status {...f} />
      {d && (
        <article className="prose">
          <img className="hero" src={`/festivals/${id}.webp`} alt="" onError={(e) => { e.currentTarget.style.display = "none"; }} />
          <h1>{d.name} <span className="ne muted">{d.name_nepali}</span></h1>
          <p className="muted"><em>{d.tagline}</em></p>
          <section className="card">
            <p className="row">
              <button className="quiet" aria-label="Previous year" disabled={year <= 1944} onClick={() => setYear(year - 1)}>←</button>
              <strong>{year}:</strong>
              {d.start ? <span>{fmt(d.start)}{d.end !== d.start ? ` – ${fmt(d.end)}` : ""}</span> : <span className="muted">not determined</span>}
              <button className="quiet" aria-label="Next year" disabled={year >= 2038} onClick={() => setYear(year + 1)}>→</button>
              <Source id={f.source} />
            </p>
            <p className="small muted">
              Gazette: {d.gazette ?? "—"} · Engine: {d.engine ?? "no rule"} ·
              Rule: {ruleText(d.rule)}
            </p>
          </section>
          <p>{d.description}</p>
          {d.mythology?.summary && <><h3>Mythology</h3><p>{d.mythology.summary}</p></>}
          {d.mythology?.origin_story && d.mythology.origin_story.split("\n\n").map((p, i) => <p key={i}>{p}</p>)}
          {d.simple_rituals?.length > 0 && <><h3>Rituals</h3><ul>{d.simple_rituals.map((r, i) => <li key={i}>{typeof r === "string" ? r : r.name ?? r.title ?? JSON.stringify(r)}</li>)}</ul></>}
          <p className="small muted">Celebrated by {d.who_celebrates}. Regions: {(d.regional_focus ?? []).join(", ")}. Deities: {(d.connected_deities ?? []).join(", ")}.</p>
        </article>
      )}
    </>
  );
}
