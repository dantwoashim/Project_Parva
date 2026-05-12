import assert from "node:assert/strict";
import test from "node:test";
import {
  DEFAULT_API_BASE,
  DEFAULT_FUTURE_BS_CAPABILITIES_URL,
  ParvaClient,
} from "../dist/index.js";

function jsonResponse(payload, init = {}) {
  return {
    ok: init.ok ?? true,
    status: init.status ?? 200,
    statusText: init.statusText ?? "OK",
    text: async () => JSON.stringify(payload),
  };
}

test("uses the public v3 base for conversion calls", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      return jsonResponse({ gregorian: "2026-04-14" });
    },
  });

  const payload = await client.bsToAd({ year: 2083, month: 1, day: 1 });

  assert.equal(payload.gregorian, "2026-04-14");
  assert.equal(calls[0].url, `${DEFAULT_API_BASE}/calendar/bs-to-gregorian`);
  assert.equal(calls[0].init.method, "POST");
});

test("uses the public v4 capabilities endpoint for future-BS capabilities", async () => {
  const calls = [];
  const client = new ParvaClient({
    fetchImpl: async (url) => {
      calls.push(url);
      return jsonResponse({
        surface: "future_bs_risk_research",
        publication_status: "computed_prediction_not_official",
      });
    },
  });

  const payload = await client.getFutureBsCapabilities();

  assert.equal(payload.publication_status, "computed_prediction_not_official");
  assert.equal(calls[0], DEFAULT_FUTURE_BS_CAPABILITIES_URL);
});

test("validateBsDate converts public 400 responses into a validation result", async () => {
  const client = new ParvaClient({
    fetchImpl: async () => jsonResponse({ detail: "Invalid BS date" }, {
      ok: false,
      status: 400,
      statusText: "Bad Request",
    }),
  });

  const result = await client.validateBsDate({ year: 2083, month: 1, day: 32 });

  assert.equal(result.valid, false);
  assert.equal(result.publication_status, "computed_prediction_not_official");
  assert.match(result.error, /Invalid BS date/);
});
