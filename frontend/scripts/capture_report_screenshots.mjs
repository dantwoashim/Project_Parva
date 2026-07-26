import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const output = resolve(here, '..', '..', 'reports', 'tu-submission', 'figures');
await mkdir(output, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 1024 },
  deviceScaleFactor: 1.5,
  colorScheme: 'light',
});

async function capture(name, url, options = {}) {
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForTimeout(options.wait ?? 2500);
  await page.screenshot({
    path: resolve(output, name),
    fullPage: options.fullPage ?? false,
  });
  await page.close();
}

await capture('ui_today.png', 'https://prabinghimire1.com.np/today', { wait: 5000 });
await capture('ui_festivals.png', 'https://prabinghimire1.com.np/festivals', { wait: 5000 });
await capture('api_docs.png', 'https://api.prabinghimire1.com.np/docs', { wait: 4000 });

const panchangaPage = await context.newPage();
await panchangaPage.goto('https://prabinghimire1.com.np/panchanga', {
  waitUntil: 'networkidle',
  timeout: 90000,
});
const dateInput = panchangaPage.locator('input[type="date"]').first();
await dateInput.fill('2025-08-16');
await dateInput.dispatchEvent('change');
await panchangaPage.waitForFunction(
  () => document.body.innerText.includes('2082 Shrawan 31'),
  { timeout: 60000 },
);
await panchangaPage.screenshot({ path: resolve(output, 'ui_panchanga_boundary.png') });
await panchangaPage.close();

const apiPage = await context.newPage();
const apiResponse = await apiPage.goto(
  'https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2025-07-16',
  { waitUntil: 'networkidle', timeout: 90000 },
);
const rawJson = await apiPage.locator('body').innerText();
const parsedJson = JSON.parse(rawJson);
const reportView = {
  gregorian: parsedJson.gregorian,
  bikram_sambat: {
    year: parsedJson.bikram_sambat?.year,
    month: parsedJson.bikram_sambat?.month,
    day: parsedJson.bikram_sambat?.day,
    month_name: parsedJson.bikram_sambat?.month_name,
    confidence: parsedJson.bikram_sambat?.confidence,
    source_range: parsedJson.bikram_sambat?.source_range,
  },
  tithi: {
    tithi_name: parsedJson.tithi?.tithi_name,
    paksha: parsedJson.tithi?.paksha,
    reference_time: parsedJson.tithi?.reference_time,
    sunrise_used: parsedJson.tithi?.sunrise_used,
  },
  engine_path: parsedJson.engine_path,
  meta: {
    confidence: parsedJson.meta?.confidence,
    result_class: parsedJson.meta?.result_class,
  },
};
const formattedJson = JSON.stringify(reportView, null, 2);
await apiPage.goto('about:blank');
await apiPage.setContent(`<!doctype html>
  <html><head><meta charset="utf-8"><style>
    body { margin: 0; background: #f7f8fa; color: #17202a; font-family: Arial, sans-serif; }
    header { background: #123b5d; color: white; padding: 28px 42px 24px; }
    h1 { margin: 0 0 12px; font-size: 30px; }
    .request { font: 18px Consolas, monospace; overflow-wrap: anywhere; }
    .status { display: inline-block; margin-top: 14px; padding: 7px 12px; background: #dff3e5; color: #174c2c; font-weight: 700; }
    pre { margin: 26px 42px; padding: 28px; background: white; border: 1px solid #c9d2dc;
      font: 19px/1.45 Consolas, monospace; white-space: pre-wrap; overflow-wrap: anywhere; }
  </style></head><body>
  <header><h1>Project Parva calendar API</h1>
  <div class="request">GET /v3/api/calendar/convert?date=2025-07-16</div>
  <div class="status">HTTP ${apiResponse?.status() ?? 200}</div></header>
  <pre></pre></body></html>`);
await apiPage.locator('pre').evaluate((node, text) => { node.textContent = text; }, formattedJson);
await apiPage.screenshot({ path: resolve(output, 'api_boundary_response.png') });
await apiPage.close();

await browser.close();
