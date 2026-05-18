import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyTimepack } from '../../../packages/parva-local-kernel/src/index';

const path = process.argv[2] ?? 'examples/external/timepacks/civil-conversion.timepack.json';
const artifact = JSON.parse(readFileSync(resolve(path), 'utf8'));
const result = await verifyTimepack(artifact, []);

console.log(JSON.stringify({ ...result, boundary: artifact.boundary_summary }, null, 2));
process.exit(result.verified ? 0 : 1);
