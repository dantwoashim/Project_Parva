import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { verifyTimepack } from '../../../packages/parva-local-kernel/src/index';

const artifact = JSON.parse(readFileSync(resolve('examples/external/timepacks/payroll-date-risk.timepack.json'), 'utf8'));
const result = await verifyTimepack(artifact, []);

console.log(JSON.stringify({ ...result, boundary: artifact.boundary_summary }, null, 2));
process.exit(result.verified ? 0 : 1);
