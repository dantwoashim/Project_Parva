import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const baseUrl = process.env.PARVA_GOLDEN_BASE_URL || process.env.PARVA_SMOKE_BASE_URL;
const reportPath = process.env.PARVA_GOLDEN_REPORT_PATH;

if (!baseUrl) {
  console.error('PARVA_GOLDEN_BASE_URL is required.');
  process.exit(2);
}

const outputDir = path.resolve(process.cwd(), '..', 'output', 'playwright');
const readyTimeout = 20000;
const baseOrigin = new URL(baseUrl).origin;

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

function relevantResponse(response) {
  try {
    const url = new URL(response.url());
    if (url.origin !== baseOrigin) return false;
    if (url.pathname.endsWith('/favicon.ico')) return false;
    return response.status() >= 400;
  } catch {
    return false;
  }
}

function safeSlug(value) {
  return String(value).replaceAll(/[^a-zA-Z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'journey';
}

function escapeRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

async function openEvidenceDrawer(page, { summaryLabel = null, title = null } = {}) {
  if (summaryLabel) {
    await page.locator('summary').filter({ hasText: summaryLabel }).click();
  }
  await page.getByRole('button', { name: /How this was calculated/i }).last().click();
  const dialog = page.getByRole('dialog');
  await dialog.waitFor({ timeout: readyTimeout });
  await dialog.getByText(/Method available/i).waitFor({ timeout: readyTimeout });
  if (title) {
    await dialog.getByRole('heading', { name: new RegExp(`^${escapeRegex(title)}$`, 'i') }).waitFor({ timeout: readyTimeout });
  }
  await dialog.getByRole('button', { name: /Close/i }).click();
  await dialog.waitFor({ state: 'hidden', timeout: readyTimeout });
}

async function writeReport(payload) {
  if (!reportPath) {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  await fs.mkdir(path.dirname(reportPath), { recursive: true });
  await fs.writeFile(reportPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
}

async function runJourney(browser, definition) {
  const viewport = viewportPresets[definition.viewport];
  const context = await browser.newContext(viewport.config);
  const page = await context.newPage();
  const responseErrors = [];
  const consoleErrors = [];
  const pageErrors = [];
  const steps = [];
  const slug = `${safeSlug(definition.id)}-${viewport.label}`;

  page.on('response', (response) => {
    if (relevantResponse(response)) {
      responseErrors.push(`${response.status()} ${response.url()}`);
    }
  });
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });
  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });

  async function step(label, action) {
    const entry = { label, status: 'running' };
    steps.push(entry);
    try {
      await action();
      entry.status = 'passed';
    } catch (error) {
      entry.status = 'failed';
      entry.error = error.message;
      throw error;
    }
  }

  try {
    await definition.run(page, step);

    if (responseErrors.length || consoleErrors.length || pageErrors.length) {
      const diagnostics = [
        ...responseErrors.map((entry) => `response:${entry}`),
        ...consoleErrors.map((entry) => `console:${entry}`),
        ...pageErrors.map((entry) => `page:${entry}`),
      ];
      throw new Error(diagnostics.join(' | '));
    }

    const screenshotPath = path.join(outputDir, `golden-journey-${slug}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    return {
      id: definition.id,
      title: definition.title,
      viewport: viewport.label,
      status: 'passed',
      final_url: page.url(),
      screenshot: screenshotPath,
      steps,
    };
  } catch (error) {
    const failurePath = path.join(outputDir, `golden-journey-${slug}-failure.png`);
    await page.screenshot({ path: failurePath, fullPage: true }).catch(() => undefined);
    return {
      id: definition.id,
      title: definition.title,
      viewport: viewport.label,
      status: 'failed',
      final_url: page.url(),
      screenshot: failurePath,
      error: error.message,
      diagnostics: {
        responses: responseErrors,
        console: consoleErrors,
        page: pageErrors,
      },
      steps,
    };
  } finally {
    await context.close();
  }
}

const journeys = [
  {
    id: 'home-to-today',
    title: 'Navigate from home to the Today reading and open evidence',
    viewport: 'desktop',
    run: async (page, step) => {
      await step('Open home', async () => {
        await page.goto(new URL('/', baseUrl).toString(), { waitUntil: 'domcontentloaded' });
        await page.locator('.almanac-home__alignment h1').waitFor({ timeout: readyTimeout });
        await page.getByRole('heading', { name: /Upcoming Festivals/i }).waitFor({ timeout: readyTimeout });
      });

      await step('Navigate to Today', async () => {
        await page.getByLabel('Primary').getByRole('link', { name: /^Today$/i }).click();
        await page.waitForURL(/\/today$/, { timeout: readyTimeout });
        await page.getByRole('heading', { name: /The rest of today in one compact pass/i }).waitFor({ timeout: readyTimeout });
      });

      await step('Open evidence drawer', async () => {
        await openEvidenceDrawer(page, { summaryLabel: 'How this was calculated' });
      });
    },
  },
  {
    id: 'my-place-controls',
    title: 'Change the saved place context and inspect method evidence',
    viewport: 'desktop',
    run: async (page, step) => {
      await step('Open My Place', async () => {
        await page.goto(new URL('/my-place', baseUrl).toString(), { waitUntil: 'domcontentloaded' });
        await page.getByRole('heading', { name: /Keep the place that changes your day in view/i }).waitFor({ timeout: readyTimeout });
      });

      await step('Switch to Pokhara preset', async () => {
        await page.locator('.personal-page__controls select').selectOption('pokhara');
        await page.locator('.consumer-home__place-copy h3').filter({ hasText: 'Pokhara' }).waitFor({ timeout: readyTimeout });
      });

      await step('Inspect place evidence', async () => {
        await openEvidenceDrawer(page, { summaryLabel: 'Place signals and method' });
      });
    },
  },
  {
    id: 'festival-detail-story',
    title: 'Open a featured observance and persist it locally',
    viewport: 'desktop',
    run: async (page, step) => {
      await step('Open Festivals', async () => {
        await page.goto(new URL('/festivals', baseUrl).toString(), { waitUntil: 'domcontentloaded' });
        await page.locator('.explorer-hero h1').waitFor({ timeout: readyTimeout });
        await page.locator('.explorer-card').first().waitFor({ timeout: readyTimeout });
      });

      await step('Open featured observance', async () => {
        await page.locator('.explorer-card').first().click();
        await page.waitForURL(/\/festivals\/[^/]+$/, { timeout: readyTimeout });
        await page.locator('.festival-detail__hero-copy h1').waitFor({ timeout: readyTimeout });
      });

      await step('Save observance locally', async () => {
        await page.getByRole('button', { name: /Save observance/i }).click();
        await page.getByRole('button', { name: /^Saved$/i }).waitFor({ timeout: readyTimeout });
      });

      await step('Inspect festival evidence', async () => {
        await openEvidenceDrawer(page);
      });
    },
  },
  {
    id: 'best-time-activity',
    title: 'Switch activities on Best Time and verify the evidence path',
    viewport: 'desktop',
    run: async (page, step) => {
      await step('Open Best Time', async () => {
        await page.goto(new URL('/best-time', baseUrl).toString(), { waitUntil: 'domcontentloaded' });
        await page.getByRole('heading', { name: /Choose a date first/i }).waitFor({ timeout: readyTimeout });
        await page.locator('.muhurta-page__activity-pill').first().waitFor({ timeout: readyTimeout });
      });

      await step('Switch activity', async () => {
        const activityPill = page.locator('.muhurta-page__activity-pill').nth(1);
        const label = (await activityPill.textContent())?.trim() || '';
        await activityPill.click();
        await page.locator('.muhurta-page__activity-pill.is-active', { hasText: label }).waitFor({ timeout: readyTimeout });
      });

      await step('Select a timing block', async () => {
        await page.locator('.muhurta-page__summary-item, .muhurta-page__day-card').first().click();
        await page.locator('.muhurta-page__timeline-item').first().waitFor({ timeout: readyTimeout });
      });

      await step('Inspect muhurta evidence', async () => {
        await openEvidenceDrawer(page);
      });
    },
  },
  {
    id: 'birth-reading',
    title: 'Open Birth Reading controls and save a local reading',
    viewport: 'desktop',
    run: async (page, step) => {
      await step('Open Birth Reading', async () => {
        await page.goto(new URL('/birth-reading', baseUrl).toString(), { waitUntil: 'domcontentloaded' });
        await page.getByRole('heading', { name: /Enter the birth details first/i }).waitFor({ timeout: readyTimeout });
      });

      await step('Enter birth details', async () => {
        const form = page.locator('.kundali-reset__form-card');
        await form.getByLabel(/^Day$/i, { exact: true }).fill('15');
        await form.getByLabel(/^Month$/i, { exact: true }).fill('2');
        await form.getByLabel(/^Year$/i, { exact: true }).fill('1994');
        await form.getByLabel(/^Birth time$/i, { exact: true }).fill('06:30');
        await form.getByLabel(/^Place$/i, { exact: true }).fill('Kathmandu, Nepal');
        await form.getByRole('button', { name: /Show manual coordinates/i }).click();
        await form.getByLabel(/^Latitude$/i, { exact: true }).fill('27.7172');
        await form.getByLabel(/^Longitude$/i, { exact: true }).fill('85.3240');
        await form.getByLabel(/^Timezone$/i, { exact: true }).fill('Asia/Kathmandu');
        await form.getByRole('button', { name: /Generate chart/i }).click();
        await page.getByRole('heading', { name: /Kathmandu, Nepal/i }).waitFor({ timeout: readyTimeout });
        await page.getByRole('tab', { name: /Chart/i }).waitFor({ timeout: readyTimeout });
      });

      await step('Save reading', async () => {
        await page.getByRole('button', { name: /Save Reading/i }).click();
        await page.locator('.member-notice').waitFor({ timeout: readyTimeout });
      });

      await step('Inspect kundali evidence', async () => {
        await openEvidenceDrawer(page, { title: 'Birth Reading' });
      });
    },
  },
  {
    id: 'mobile-menu-navigation',
    title: 'Use the mobile menu to reach a launch-critical page',
    viewport: 'mobile',
    run: async (page, step) => {
      await step('Open home on mobile', async () => {
        await page.goto(new URL('/', baseUrl).toString(), { waitUntil: 'domcontentloaded' });
        await page.locator('.almanac-home__alignment h1').waitFor({ timeout: readyTimeout });
      });

      await step('Open mobile menu', async () => {
        await page.getByRole('button', { name: /Menu/i }).click();
        await page.getByRole('dialog').waitFor({ timeout: readyTimeout });
      });

      await step('Navigate to Festivals', async () => {
        await page.getByRole('dialog').getByRole('link', { name: /^Festivals$/i }).click();
        await page.waitForURL(/\/festivals$/, { timeout: readyTimeout });
        await page.locator('.explorer-hero h1').waitFor({ timeout: readyTimeout });
      });
    },
  },
];

async function main() {
  await fs.mkdir(outputDir, { recursive: true });
  const existingArtifacts = await fs.readdir(outputDir);
  await Promise.all(
    existingArtifacts
      .filter((name) => name.startsWith('golden-journey-'))
      .map((name) => fs.rm(path.join(outputDir, name), { force: true })),
  );

  const browser = await chromium.launch({ headless: true });

  try {
    const results = [];
    for (const journey of journeys) {
      results.push(await runJourney(browser, journey));
    }

    const hasFailures = results.some((result) => result.status !== 'passed');
    const payload = {
      generated_at: new Date().toISOString(),
      status: hasFailures ? 'failed' : 'passed',
      base_url: baseUrl,
      runner: 'playwright-chromium',
      journeys: results,
      artifacts_dir: outputDir,
    };
    await writeReport(payload);

    if (hasFailures) {
      const failures = results.filter((result) => result.status !== 'passed');
      throw new Error(
        failures
          .map((failure) => `${failure.id}: ${failure.error || 'Unknown error'}`)
          .join(' | '),
      );
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
