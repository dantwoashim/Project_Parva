import { useParva } from "../api.js";
import { Status } from "../ui.jsx";

export default function Data() {
  const result = useParva("/v1/sources");
  return <>
    <div className="eyebrow">THE EVIDENCE BEHIND THE DATE</div><h1>Sources & coverage</h1>
    <p className="intro">Conversion, holiday notices, and astronomical calculations are separate kinds of evidence. A source label identifies where a value came from; it does not certify completeness.</p>
    <Status {...result} />
    {result.data && <>
      <section className="coverage-summary"><h2>What this release establishes</h2>
        <p>Conversion table: BS {result.data.release.conversion_years.join("–")}. Years from BS {result.data.release.provisional_from} are provisional.</p>
        <p>Holiday notices: BS {result.data.release.holiday_years.join(", ")}. All years have partial coverage.</p>
        <ul>{result.data.release.limits.map((limit) => <li key={limit}>{limit}</li>)}</ul>
        <p className="small muted">Source-page review: {result.data.release.reviewed_on} · Data release {result.data.release.version}</p>
      </section>
      <div className="scroll"><table><thead><tr><th>Source</th><th>Evidence & limitations</th><th>Reference</th></tr></thead><tbody>
        {Object.entries(result.data.sources).map(([id, source]) => <tr key={id}><td className="mono">{id}</td><td>{source.title}<p className="small muted">{source.note}</p></td><td className="small">
          {source.url && <a href={source.url}>Source document</a>}
          {source.archive_path && <a href={`https://github.com/dantwoashim/Project_Parva/blob/main/${source.archive_path}`}>Archived PDF</a>}
          {source.sha256 && <details><summary>SHA-256</summary><code className="hash">{source.sha256}</code></details>}
        </td></tr>)}
      </tbody></table></div>
      <details className="release-details"><summary>Release fingerprint</summary><code className="hash">{result.data.data_sha256}</code><p className="small">{result.version}</p></details>
    </>}
  </>;
}
