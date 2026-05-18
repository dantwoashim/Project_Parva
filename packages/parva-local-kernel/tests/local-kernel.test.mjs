import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import test from 'node:test';
import {
  replayMembrane,
  replayPanchangaMembrane,
  verifyCivilOperation,
  verifyMembrane,
  verifyPanchangaMembrane,
  verifyProofPack,
  verifyTimepack,
} from '../dist/index.js';

const root = resolve('../..');

function loadFixtures(dir) {
  const fixtureDir = join(root, 'tests/fixtures/proof', dir);
  return readdirSync(fixtureDir)
    .filter((name) => name.endsWith('.json'))
    .sort()
    .map((name) => join(fixtureDir, name))
    .map((path) => {
    return JSON.parse(readFileSync(path, 'utf8'));
    });
}

const civilFixtures = loadFixtures('civil');
const panchangaFixtures = loadFixtures('panchanga');

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

test('civil fixtures verify and replay locally', async () => {
  assert.equal(civilFixtures.length >= 12, true);
  for (const fixture of civilFixtures) {
    const result = await verifyCivilOperation(fixture.membrane, []);
    assert.deepEqual(result, { verified: true, reason: 'verified' });
  }
});

test('local replay rejects wrong but self-consistent civil result', async () => {
  const fixture = civilFixtures.find((item) => item.operation === 'ad_to_bs');
  const membrane = clone(fixture.membrane);
  membrane.result.bs_date = '2082-01-03';
  const replay = await replayMembrane(membrane, []);
  assert.deepEqual(replay, { verified: false, reason: 'replayed_result_mismatch' });
});

test('local formula replay covers all civil operations without fixture lookup', async () => {
  const byName = new Map(civilFixtures.map((fixture) => [fixture.name, fixture.membrane]));
  const cases = [
    'bs_to_ad_valid',
    'ad_to_bs_valid',
    'validate_bs_date_valid',
    'validate_bs_date_invalid',
    'holiday_membership',
    'holiday_non_membership',
    'working_day_true',
    'working_day_false',
    'fiscal_year_boundary',
    'bs_months_canonical',
    'bs_months_static_lookup',
    'bs_months_compare',
  ];
  for (const name of cases) {
    assert.deepEqual(await replayMembrane(byName.get(name), []), { verified: true, reason: 'replayed' }, name);
  }
});

test('local verifier rejects missing field provenance and witness tampering', async () => {
  const fixture = civilFixtures.find((item) => item.operation === 'working_day');
  const missingProvenance = clone(fixture.membrane);
  delete missingProvenance.field_provenance.is_working_day;
  assert.equal((await verifyMembrane(missingProvenance, { fixtures: civilFixtures })).reason, 'field_provenance_missing');

  const tamperedWitness = clone(fixture.membrane);
  tamperedWitness.witness_hash = 'parva:wit:v1:sha256:bad';
  assert.equal((await verifyMembrane(tamperedWitness, { fixtures: civilFixtures })).reason, 'witness_hash_mismatch');
});

test('local verifier catches BS month total tampering', async () => {
  const fixture = civilFixtures.find((item) => item.name === 'bs_months_canonical');
  const membrane = clone(fixture.membrane);
  membrane.result.total_days = 1;
  assert.equal((await replayMembrane(membrane, [])).reason, 'bs_month_total_mismatch');
});

test('local verifier rejects high authority from sample source dockets', async () => {
  const fixture = civilFixtures.find((item) => item.name === 'bs_to_ad_valid');
  const membrane = clone(fixture.membrane);
  membrane.boundary.authority = 'structured_official';
  membrane.field_provenance.ad_date.authority = 'structured_official';
  assert.equal((await verifyMembrane(membrane, { fixtures: [] })).reason, 'authority_overclaim');
});

test('panchanga fixture verifies with ephemeris metadata', async () => {
  const fixture = panchangaFixtures[0];
  const result = await verifyPanchangaMembrane(fixture.membrane, panchangaFixtures);
  assert.deepEqual(result, { verified: true, reason: 'verified' });
  assert.equal(fixture.membrane.boundary.not_panchanga_authority, true);
  assert.equal(fixture.membrane.ephemeris_metadata.provider_kind, 'pinned_fixture');
});

test('panchanga replay validates pinned components, metadata, and non-authority boundaries', async () => {
  const fixture = panchangaFixtures[0];
  assert.deepEqual(await replayPanchangaMembrane(fixture.membrane, panchangaFixtures), {
    verified: true,
    reason: 'panchanga_replayed',
  });

  const wrongTithi = clone(fixture.membrane);
  wrongTithi.result.tithi.number = 17;
  assert.equal((await replayPanchangaMembrane(wrongTithi, panchangaFixtures)).reason, 'panchanga_component_mismatch:tithi.number');

  const wrongNakshatra = clone(fixture.membrane);
  wrongNakshatra.result.nakshatra.name = 'Bharani';
  assert.equal(
    (await replayPanchangaMembrane(wrongNakshatra, panchangaFixtures)).reason,
    'panchanga_component_mismatch:nakshatra.name',
  );

  const wrongSunrise = clone(fixture.membrane);
  wrongSunrise.result.sunrise.local_time = '05:41:30';
  assert.equal(
    (await replayPanchangaMembrane(wrongSunrise, panchangaFixtures)).reason,
    'panchanga_component_mismatch:sunrise.local_time',
  );

  const changedLocation = clone(fixture.membrane);
  changedLocation.canonical_query.context.latitude = 28.0;
  assert.equal((await verifyPanchangaMembrane(changedLocation, panchangaFixtures)).reason, 'identity_hash_mismatch');

  const changedTimezone = clone(fixture.membrane);
  changedTimezone.canonical_query.context.timezone = 'asia/tokyo';
  assert.equal((await verifyPanchangaMembrane(changedTimezone, panchangaFixtures)).reason, 'identity_hash_mismatch');

  const changedAyanamsa = clone(fixture.membrane);
  changedAyanamsa.canonical_query.context.ayanamsa = 'raman';
  assert.equal((await verifyPanchangaMembrane(changedAyanamsa, panchangaFixtures)).reason, 'identity_hash_mismatch');

  const changedProvider = clone(fixture.membrane);
  changedProvider.ephemeris_metadata.provider_id = 'other_provider';
  assert.equal(
    (await verifyPanchangaMembrane(changedProvider, panchangaFixtures)).reason,
    'ephemeris_metadata_proof_mismatch',
  );

  const missingMethodDocket = clone(fixture.membrane);
  missingMethodDocket.method_docket_refs = [];
  assert.equal((await verifyPanchangaMembrane(missingMethodDocket, panchangaFixtures)).reason, 'method_dockets_missing');

  const missingBoundary = clone(fixture.membrane);
  missingBoundary.boundary.not_ritual_final_authority = false;
  assert.equal(
    (await verifyPanchangaMembrane(missingBoundary, panchangaFixtures)).reason,
    'panchanga_not_ritual_final_authority_missing',
  );

  const fallbackClaimsJpl = clone(fixture.membrane);
  fallbackClaimsJpl.ephemeris_metadata.provider_kind = 'fallback_approx';
  fallbackClaimsJpl.ephemeris_metadata.fallback_used = true;
  fallbackClaimsJpl.ephemeris_metadata.jpl_backed = true;
  fallbackClaimsJpl.proof_pack.source_artifacts.ephemeris_metadata = clone(fallbackClaimsJpl.ephemeris_metadata);
  assert.equal((await verifyPanchangaMembrane(fallbackClaimsJpl, panchangaFixtures)).reason, 'fallback_provider_claims_jpl');
});

test('proofpack and timepack verification use child replay', async () => {
  const fixture = civilFixtures[0];
  assert.deepEqual(await verifyProofPack({ level: 'audit', membrane: fixture.membrane }, civilFixtures), {
    verified: true,
    reason: 'verified',
  });
  const timepack = {
    kind: 'parva_timepack',
    timepack_version: 'v1',
    proof_packs: [{ level: 'audit', membrane: fixture.membrane }],
    boundary_summary: { not_authority: true, review_required: true },
  };
  assert.deepEqual(await verifyTimepack(timepack, civilFixtures), { verified: true, reason: 'verified' });
});
