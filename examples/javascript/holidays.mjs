import { ParvaClient } from "../../packages/parva-js/dist/index.js";

const parva = new ParvaClient({
  baseUrl: process.env.PARVA_API_BASE || "https://api.prabinghimire1.com.np/v3/api",
});

const payload = await parva.evaluateDate({
  profile_id: "nepal_private_company_default",
  bs_date: "2082-01-01",
  decision_intent: "public_holiday_lookup",
});

console.log(JSON.stringify(payload, null, 2));
