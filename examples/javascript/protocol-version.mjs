import { ParvaClient } from "../../packages/parva-js/dist/index.js";

const parva = new ParvaClient({
  baseUrl: process.env.PARVA_API_BASE || "https://api.prabinghimire1.com.np/v3/api",
});

const payload = await parva.getProtocolVersion();

console.log(JSON.stringify(payload, null, 2));
