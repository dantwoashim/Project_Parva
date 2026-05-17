export function PanchangaProofDrawer({ proof }) {
  if (!proof?.capsule) {
    return null;
  }

  const capsule = proof.capsule;
  const boundary = capsule.boundary || {};
  const ephemeris = capsule.ephemeris_metadata || {};
  const result = capsule.result || {};
  const provenance = capsule.field_provenance || {};

  return (
    <section aria-label="Panchanga proof drawer">
      <h2>Panchanga proof</h2>
      <p role="note">
        Computed ephemeris result, not official Panchanga authority and not ritual final authority.
      </p>
      <dl>
        <dt>Identity hash</dt>
        <dd>{capsule.identity_hash}</dd>
        <dt>Witness hash</dt>
        <dd>{capsule.witness_hash}</dd>
        <dt>Boundary</dt>
        <dd>{boundary.claim_boundary}</dd>
        <dt>Ephemeris provider</dt>
        <dd>{ephemeris.provider_id} / {ephemeris.provider_kind}</dd>
        <dt>Ephemeris version</dt>
        <dd>{ephemeris.ephemeris_version || 'not specified'}</dd>
        <dt>Location</dt>
        <dd>
          {capsule.canonical_query?.context?.latitude}, {capsule.canonical_query?.context?.longitude}{' '}
          {capsule.canonical_query?.context?.timezone}
        </dd>
        <dt>Ayanamsa</dt>
        <dd>{capsule.canonical_query?.context?.ayanamsa}</dd>
        <dt>Tithi</dt>
        <dd>{result.tithi?.name || result.tithi?.number}</dd>
        <dt>Nakshatra</dt>
        <dd>{result.nakshatra?.name || result.nakshatra?.number}</dd>
      </dl>
      <table>
        <caption>Field provenance</caption>
        <thead>
          <tr>
            <th>Field</th>
            <th>Authority</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(provenance).map(([field, value]) => (
            <tr key={field}>
              <td>{field}</td>
              <td>{value.authority}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
