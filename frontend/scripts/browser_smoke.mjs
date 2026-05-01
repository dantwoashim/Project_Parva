import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const baseUrl = process.env.PARVA_SMOKE_BASE_URL;
if (!baseUrl) {
  console.error('PARVA_SMOKE_BASE_URL is required.');
  process.exit(2);
}

const outputDir = path.resolve(process.cwd(), '..', 'output', 'playwright');
const baseOrigin = new URL(baseUrl).origin;
const readyTimeout = 20000;
const consumerForbidden = [
  /localhost/i,
  /\/v3\/api/i,
  /Invalid Date/i,
  /\bundefined\b/i,
  /\bNaN\b/,
];

const viewportPresets = {
  desktop: {
    label: 'desktop',
    config: { viewport: { width: 1440, height: 1080 } },
  },
  mobile: {
    label: 'mobile',
    config: {
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
      deviceScaleFactor: 2,
    },
  },
};

const routes = [
  {
    path: '/',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.waitForURL(/\/today$/, { timeout: readyTimeout });
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Nepal calendar, panchanga/i).waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Upcoming Observances|Panchanga for/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: consumerForbidden,
  },
  {
    path: '/about',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/About Parva|Parva/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: consumerForbidden,
  },
  {
    path: '/today',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Nepal calendar, panchanga/i).waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Upcoming Observances|Panchanga for/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Could not build today's view/i],
  },
  {
    path: '/my-place',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Kathmandu|place/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Unable to load/i, /Failed to load personal panchanga/i],
  },
  {
    path: '/best-time',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Recommended Window|Choose a date|Best Time/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Unable to load muhurta heatmap/i],
  },
  {
    path: '/birth-reading',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Birth Reading|Janma Kundali|birth details/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Unable to load kundali/i],
  },
  {
    path: '/festivals',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/festival/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Could not load timeline/i],
  },
  {
    path: '/festivals/dashain',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Dashain/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Festival not found/i, /Could not load trace data/i],
  },
  {
    path: '/integrations',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Integrations|calendar/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /\.ics/i],
  },
  {
    path: '/panchanga',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Date Converter|Bikram Sambat|Selected date/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Panchanga data could not be loaded/i],
  },
  {
    path: '/saved',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Saved festivals|Calendar export|Current place/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: consumerForbidden,
  },
  {
    path: '/trust',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Trust Center|Service state|Usage posture/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Unable to load trust/i],
  },
  {
    path: '/methodology',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Context first|Engine path|Evidence-led/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: consumerForbidden,
  },
  {
    path: '/truth-lab',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/Truth Lab|Endpoint health|Live evidence/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [...consumerForbidden, /Unable to load trust/i],
  },
  {
    path: '/policy',
    viewports: ['desktop', 'mobile'],
    ready: async (page) => {
      await page.locator('main h1').waitFor({ timeout: readyTimeout });
      await page.locator('main').getByText(/API Policy|Policy metadata|Reliability playbooks/i).first().waitFor({ timeout: readyTimeout });
    },
    forbidden: [/Internal Server Error/i, /Invalid Date/i, /\bundefined\b/i, /\bNaN\b/],
  },
  {
    path: '/embed/temporal-compass.html?date=2026-10-21&lat=27.7172&lon=85.3240&tz=Asia%2FKathmandu',
    viewports: ['desktop'],
    ready: async (page) => {
      await page.getByText('Temporal Compass').waitFor({ timeout: readyTimeout });
      await page.locator('body').waitFor({ timeout: readyTimeout });
    },
    forbidden: [/Request failed/i, /Internal Server Error/i],
  },
  {
    path: '/embed/upcoming-festivals.html?days=30&limit=4',
    viewports: ['desktop'],
    ready: async (page) => {
      await page.getByText('Upcoming Festivals').waitFor({ timeout: readyTimeout });
    },
    forbidden: [/Request failed/i, /Internal Server Error/i],
  },
  {
    path: '/developers/index.html',
    viewports: ['desktop'],
    ready: async (page) => {
      await page.getByText('Developer Portal').waitFor({ timeout: readyTimeout });
      await page.getByText('Commercial.read example').waitFor({ timeout: readyTimeout });
    },
    forbidden: [/Internal Server Error/i],
  },
  {
    path: '/institutions/index.html',
    viewports: ['desktop'],
    ready: async (page) => {
      await page.getByText('Institution Portal').waitFor({ timeout: readyTimeout });
      await page.getByText('Release gate command set').waitFor({ timeout: readyTimeout });
    },
    forbidden: [/Internal Server Error/i],
  },
  {
    path: '/access/index.html',
    viewports: ['desktop'],
    ready: async (page) => {
      await page.getByText('Project Parva Access').waitFor({ timeout: readyTimeout });
      await page.getByText('Choose the smallest surface that solves your problem.').waitFor({ timeout: readyTimeout });
    },
    forbidden: [/Internal Server Error/i],
  },
];

function relevantResponse(response) {
  try {
    const url = new URL(response.url());
    if (url.origin !== baseOrigin) return false;
    if (url.pathname.endsWith('/favicon.ico')) return false;
    if (response.status() === 429 && url.pathname.includes('/v3/api/temporal/compass')) return false;
    return response.status() >= 400;
  } catch {
    return false;
  }
}

function slugifyRoute(routePath) {
  return routePath
    .replaceAll(/https?:\/\//g, '')
    .replaceAll(/[^a-zA-Z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    || 'home';
}

async function ensureNoForbiddenText(page, patterns) {
  const text = await page.locator('body').innerText();
  for (const pattern of patterns) {
    if (pattern.test(text)) {
      throw new Error(`Forbidden text matched ${pattern}`);
    }
  }
}

async function runViewportSmoke(browser, route, viewportPreset) {
  const page = await browser.newPage(viewportPreset.config);
  const routeUrl = new URL(route.path, baseUrl).toString();
  const routeSlug = slugifyRoute(route.path);
  const outputSlug = `${routeSlug}-${viewportPreset.label}`;
  const responseErrors = [];
  const consoleErrors = [];
  const pageErrors = [];

  page.on('response', (response) => {
    if (relevantResponse(response)) {
      responseErrors.push(`${response.status()} ${response.url()}`);
    }
  });
  page.on('console', (msg) => {
    if (msg.type() === 'error' && !/429|Too Many Requests/i.test(msg.text())) {
      consoleErrors.push(msg.text());
    }
  });
  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });

  try {
    await page.goto(routeUrl, { waitUntil: 'domcontentloaded' });
    try {
      await route.ready(page);
      await ensureNoForbiddenText(page, route.forbidden);
    } catch (error) {
      await page.screenshot({
        path: path.join(outputDir, `smoke-${outputSlug}-ready-failure.png`),
        fullPage: true,
      });
      const bodyText = await page.locator('body').innerText();
      const diagnostics = [
        ...responseErrors.map((entry) => `response:${entry}`),
        ...consoleErrors.map((entry) => `console:${entry}`),
        ...pageErrors.map((entry) => `page:${entry}`),
      ].join('\n');
      await fs.writeFile(
        path.join(outputDir, `smoke-${outputSlug}-body.txt`),
        `${bodyText}\n\n${diagnostics}`,
        'utf8',
      );
      throw error;
    }

    await page.screenshot({
      path: path.join(outputDir, `smoke-${outputSlug}.png`),
      fullPage: true,
    });

    if (responseErrors.length || consoleErrors.length || pageErrors.length) {
      const details = [
        ...responseErrors.map((entry) => `response:${entry}`),
        ...consoleErrors.map((entry) => `console:${entry}`),
        ...pageErrors.map((entry) => `page:${entry}`),
      ].join(' | ');
      throw new Error(`Smoke failure on ${route.path} (${viewportPreset.label}): ${details}`);
    }
  } finally {
    await page.close();
  }
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });
  const existingArtifacts = await fs.readdir(outputDir);
  await Promise.all(
    existingArtifacts
      .filter((name) => name.startsWith('smoke-'))
      .map((name) => fs.rm(path.join(outputDir, name), { force: true })),
  );

  const browser = await chromium.launch({ headless: true });

  try {
    for (const route of routes) {
      for (const viewportName of route.viewports || ['desktop']) {
        const viewportPreset = viewportPresets[viewportName];
        if (!viewportPreset) {
          throw new Error(`Unknown viewport preset: ${viewportName}`);
        }
        await runViewportSmoke(browser, route, viewportPreset);
      }
    }

    console.log('Browser smoke passed.');
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
