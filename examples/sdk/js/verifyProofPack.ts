import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyProofPack } from '../../../packages/parva-local-kernel/src/index';

const path = process.argv[2] ?? 'examples/external/proofpacks/civil-conversion.proofpack.json';
const artifact = JSON.parse(readFileSync(resolve(path), 'utf8'));
const result = await verifyProofPack(artifact, []);

console.log(JSON.stringify({ ...result, boundary: artifact.boundary ?? artifact.membrane?.boundary }, null, 2));
process.exit(result.verified ? 0 : 1);
