import { loadParvaClient, resolveApiBase } from './_preflight.mjs';

const { ParvaClient } = await loadParvaClient();

const parva = new ParvaClient({
  baseUrl: resolveApiBase(),
});

const payload = await parva.evaluateDate({
  profile_id: "nepal_private_company_default",
  bs_date: "2082-01-01",
  decision_intent: "public_holiday_lookup",
});

console.log(JSON.stringify(payload, null, 2));
