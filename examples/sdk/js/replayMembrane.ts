import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { replayMembrane } from '../../../packages/parva-local-kernel/src/index';

const path = process.argv[2] ?? 'examples/external/proofpacks/civil-conversion.proofpack.json';
const artifact = JSON.parse(readFileSync(resolve(path), 'utf8'));
const membrane = artifact.membrane ?? artifact;
const result = await replayMembrane(membrane, []);

console.log(JSON.stringify({ ...result, operation: membrane.canonical_query?.operation }, null, 2));
process.exit(result.verified ? 0 : 1);
