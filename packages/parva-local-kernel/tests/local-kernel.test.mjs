import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import test from 'node:test';
import {
  replayMembrane,
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
    const result = await verifyCivilOperation(fixture.membrane, civilFixtures);
    assert.deepEqual(result, { verified: true, reason: 'verified' });
  }
});

test('local replay rejects wrong but self-consistent civil result', async () => {
  const fixture = civilFixtures.find((item) => item.operation === 'ad_to_bs');
  const membrane = clone(fixture.membrane);
  membrane.result.bs_date = '2082-01-03';
  const replay = await replayMembrane(membrane, civilFixtures);
  assert.deepEqual(replay, { verified: false, reason: 'replayed_result_mismatch' });
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
  assert.equal((await replayMembrane(membrane, civilFixtures)).reason, 'replayed_result_mismatch');
});

test('panchanga fixture verifies with ephemeris metadata', async () => {
  const fixture = panchangaFixtures[0];
  const result = await verifyPanchangaMembrane(fixture.membrane, panchangaFixtures);
  assert.deepEqual(result, { verified: true, reason: 'verified' });
  assert.equal(fixture.membrane.boundary.not_panchanga_authority, true);
  assert.equal(fixture.membrane.ephemeris_metadata.provider_kind, 'pinned_fixture');
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
