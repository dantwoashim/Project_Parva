import { loadParvaClient, resolveApiBase } from './_preflight.mjs';

const { ParvaClient } = await loadParvaClient();

const parva = new ParvaClient({
  baseUrl: resolveApiBase(),
});

const payload = {
  adToBs: await parva.adToBs("2026-04-14"),
  bsToAd: await parva.bsToAd({ year: 2083, month: 1, day: 1 }),
};

console.log(JSON.stringify(payload, null, 2));
