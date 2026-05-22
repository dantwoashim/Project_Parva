import { loadParvaClient, resolveApiBase } from './_preflight.mjs';

const { ParvaClient } = await loadParvaClient();

const parva = new ParvaClient({
  baseUrl: resolveApiBase(),
});

const payload = await parva.getProtocolVersion();

console.log(JSON.stringify(payload, null, 2));
