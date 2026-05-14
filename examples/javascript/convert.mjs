import { ParvaClient } from "../../packages/parva-js/dist/index.js";

const parva = new ParvaClient({
  baseUrl: process.env.PARVA_API_BASE || "https://api.prabinghimire1.com.np/v3/api",
});

const payload = {
  adToBs: await parva.adToBs("2026-04-14"),
  bsToAd: await parva.bsToAd({ year: 2083, month: 1, day: 1 }),
};

console.log(JSON.stringify(payload, null, 2));
