import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';

const baseUrl = process.env.PARVA_A11Y_BASE_URL || process.env.PARVA_SMOKE_BASE_URL;
const reportPath = process.env.PARVA_A11Y_REPORT_PATH;

if (!baseUrl) {
  console.error('PARVA_A11Y_BASE_URL is required.');
  process.exit(2);
}

const outputDir = path.resolve(process.cwd(), '..', 'output', 'playwright');
const baseOrigin = new URL(baseUrl).origin;
const readyTimeout = 20000;

const viewports = {
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
  { path: '/', label: 'Home', viewports: ['desktop', 'mobile'], readyText: /Project Parva/i },
  { path: '/today', label: 'Today', viewports: ['desktop', 'mobile'], readyText: /Today in|Upcoming Observances/i },
  { path: '/best-time', label: 'Best Time', viewports: ['desktop', 'mobile'], readyText: /Best Time|Muhurta/i },
  {
    path: '/festivals',
    label: 'Festivals',
    viewports: ['desktop', 'mobile'],
    readySelector: '.festival-list-card',
  },
  {
    path: '/festivals/dashain',
    label: 'Festival Detail',
    viewports: ['desktop', 'mobile'],
    readyText: /Ghata Sthapana|Kalash Sthapana/i,
  },
  { path: '/my-place', label: 'My Place', viewports: ['desktop', 'mobile'], readyText: /Place|Kathmandu/i },
  { path: '/birth-reading', label: 'Birth Reading', viewports: ['desktop', 'mobile'], readyText: /Birth Reading|Janma Kundali/i },
  { path: '/integrations', label: 'Integrations', viewports: ['desktop', 'mobile'], readyText: /Integrations/i },
  { path: '/panchanga', label: 'Panchanga', viewports: ['desktop', 'mobile'], readyText: /Panchanga|Date Converter/i },
  { path: '/trust', label: 'Trust', viewports: ['desktop', 'mobile'], readyText: /Trust|Reliability/i },
  { path: '/methodology', label: 'Methodology', viewports: ['desktop', 'mobile'], readyText: /Methodology|Calculation|Evidence-led/i },
  { path: '/truth-lab', label: 'Truth Lab', viewports: ['desktop', 'mobile'], readyText: /Truth Lab|Live evidence/i },
  { path: '/policy', label: 'API Policy', viewports: ['desktop', 'mobile'], readyText: /API Policy|contract/i },
  { path: '/about', label: 'About', viewports: ['desktop', 'mobile'], readyText: /About Parva|source-aware time layer/i },
  { path: '/saved', label: 'Saved', viewports: ['desktop', 'mobile'], readyText: /Profile|Saved/i },
  { path: '/benchmark', label: 'Benchmark', viewports: ['desktop', 'mobile'], readyText: /Nepali Time Reliability Benchmark/i },
  { path: '/proof', label: 'Proof Viewer', viewports: ['desktop', 'mobile'], readyText: /Inspect Parva proof packs/i },
  { path: '/developers', label: 'Developers', viewports: ['desktop', 'mobile'], readyText: /Build with Nepal's calendar/i },
  { path: '/future-bs', label: 'Future BS', viewports: ['desktop', 'mobile'], readyText: /Future dates need a risk label/i },
  { path: '/enterprise', label: 'Enterprise', viewports: ['desktop', 'mobile'], readyText: /Catch date errors before/i },
  { path: '/pricing', label: 'Pricing', viewports: ['desktop', 'mobile'], readyText: /API access that grows/i },
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

function safeSlug(value) {
  return String(value).replaceAll(/[^a-zA-Z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'route';
}

async function visibleIssues(page) {
  return page.evaluate(() => {
    const issues = [];
    const viewportWidth = document.documentElement.clientWidth;
    const scrollWidth = document.documentElement.scrollWidth;
    if (scrollWidth > viewportWidth + 1) {
      issues.push(`horizontal-overflow:${scrollWidth - viewportWidth}px`);
    }

    const main = document.querySelector('main');
    if (!main) issues.push('missing-main-landmark');

    const h1s = [...document.querySelectorAll('h1')].filter((node) => node.textContent.trim());
    if (h1s.length !== 1) issues.push(`expected-one-h1:${h1s.length}`);

    const navs = [...document.querySelectorAll('nav')];
    const unnamedNav = navs.find((node) => !node.getAttribute('aria-label') && !node.getAttribute('aria-labelledby'));
    if (unnamedNav) issues.push('unnamed-navigation-landmark');

    const unlabeledControls = [...document.querySelectorAll('button, a[href], input, select, textarea')]
      .filter((node) => {
        const rect = node.getBoundingClientRect();
        const visible = rect.width > 0 && rect.height > 0 && getComputedStyle(node).visibility !== 'hidden';
        if (!visible) return false;
        const tagName = node.tagName.toLowerCase();
        const type = node.getAttribute('type');
        if (type === 'hidden') return false;
        const name = [
          node.getAttribute('aria-label'),
          node.getAttribute('title'),
          node.textContent,
          node.getAttribute('placeholder'),
          node.getAttribute('value'),
        ].filter(Boolean).join(' ').trim();
        if (name) return false;
        if (node.id && document.querySelector(`label[for="${CSS.escape(node.id)}"]`)) return false;
        if (tagName === 'input' && node.closest('label')) return false;
        return true;
      })
      .slice(0, 8)
      .map((node) => node.outerHTML.slice(0, 120));
    if (unlabeledControls.length) issues.push(`unlabeled-controls:${unlabeledControls.join('|')}`);

    const unlabeledImages = [...document.querySelectorAll('img')]
      .filter((node) => !node.hasAttribute('alt') && node.getAttribute('role') !== 'presentation')
      .slice(0, 8)
      .map((node) => node.src || node.outerHTML.slice(0, 80));
    if (unlabeledImages.length) issues.push(`missing-image-alt:${unlabeledImages.join('|')}`);

    const shortTargets = [...document.querySelectorAll('button, a[href], input, select, textarea')]
      .filter((node) => {
        const rect = node.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;
        if (getComputedStyle(node).visibility === 'hidden') return false;
        return rect.width < 36 || rect.height < 34;
      })
      .slice(0, 8)
      .map((node) => `${node.tagName.toLowerCase()}:${Math.round(node.getBoundingClientRect().width)}x${Math.round(node.getBoundingClientRect().height)}:${node.textContent.trim().slice(0, 30)}`);
    if (shortTargets.length) issues.push(`short-touch-targets:${shortTargets.join('|')}`);

    return issues;
  });
}

async function keyboardIssues(page) {
  const issues = [];
  const seen = new Set();
  const seenVisibleControl = new Set();
  for (let index = 0; index < 18; index += 1) {
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => {
      const node = document.activeElement;
      if (!node || node === document.body) return null;
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return {
        tag: node.tagName.toLowerCase(),
        text: (node.getAttribute('aria-label') || node.textContent || node.getAttribute('placeholder') || '').trim().slice(0, 60),
        type: node.getAttribute('type') || '',
        width: rect.width,
        height: rect.height,
        visible: rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden',
        focusVisible: node.matches(':focus-visible'),
        outline: style.outlineStyle,
        boxShadow: style.boxShadow,
      };
    });
    if (!focused) continue;
    const signature = `${focused.tag}:${focused.type}:${focused.text}`;
    seen.add(signature);
    if (!focused.visible) issues.push(`hidden-focus:${focused.tag}:${focused.text}`);
    if (focused.focusVisible) seenVisibleControl.add(signature);
    if (!focused.focusVisible && focused.tag === 'input' && ['date', 'time'].includes(focused.type) && seenVisibleControl.has(signature)) {
      continue;
    }
    if (focused.outline === 'none' && focused.boxShadow === 'none') {
      issues.push(`weak-focus-ring:${focused.tag}:${focused.text}`);
    }
  }
  if (seen.size < 3) issues.push(`keyboard-reached-too-few-controls:${seen.size}`);
  return [...new Set(issues)].slice(0, 12);
}

async function runRoute(browser, route, viewportName) {
  const viewport = viewports[viewportName];
  const context = await browser.newContext(viewport.config);
  const page = await context.newPage();
  const responseErrors = [];
  const consoleErrors = [];
  const pageErrors = [];
  const routeUrl = new URL(route.path, baseUrl).toString();
  const slug = `${safeSlug(route.path)}-${viewport.label}`;

  page.on('response', (response) => {
    if (relevantResponse(response)) responseErrors.push(`${response.status()} ${response.url()}`);
  });
  page.on('console', (message) => {
    if (message.type() === 'error' && !/429|Too Many Requests/i.test(message.text())) consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  try {
    await page.goto(routeUrl, { waitUntil: 'domcontentloaded' });
    if (route.readySelector) {
      await page.locator(route.readySelector).first().waitFor({ timeout: readyTimeout });
    } else {
      await page.locator('main').getByText(route.readyText).first().waitFor({ timeout: readyTimeout });
    }

    const issues = [
      ...(await visibleIssues(page)),
      ...(await keyboardIssues(page)),
    ];

    await page.getByText(/^Opening Parva$/i).waitFor({ state: 'hidden', timeout: readyTimeout });
    await page.evaluate(() => {
      if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
      window.scrollTo(0, 0);
    });
    await page.waitForTimeout(250);

    const screenshotPath = path.join(outputDir, `a11y-${slug}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });

    return {
      path: route.path,
      label: route.label,
      viewport: viewport.label,
      status: responseErrors.length || consoleErrors.length || pageErrors.length || issues.length ? 'failed' : 'passed',
      issues,
      diagnostics: {
        responses: responseErrors,
        console: consoleErrors,
        page: pageErrors,
      },
      screenshot: screenshotPath,
    };
  } finally {
    await context.close();
  }
}

async function writeReport(payload) {
  if (!reportPath) {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }
  await fs.mkdir(path.dirname(reportPath), { recursive: true });
  await fs.writeFile(reportPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });
  const existingArtifacts = await fs.readdir(outputDir);
  await Promise.all(
    existingArtifacts
      .filter((name) => name.startsWith('a11y-'))
      .map((name) => fs.rm(path.join(outputDir, name), { force: true })),
  );

  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const route of routes) {
      for (const viewportName of route.viewports) {
        results.push(await runRoute(browser, route, viewportName));
      }
    }
  } finally {
    await browser.close();
  }

  const failures = results.filter((result) => result.status !== 'passed');
  const payload = {
    generated_at: new Date().toISOString(),
    status: failures.length ? 'failed' : 'passed',
    base_url: baseUrl,
    runner: 'playwright-chromium',
    routes: results,
    artifacts_dir: outputDir,
  };
  await writeReport(payload);

  if (failures.length) {
    throw new Error(
      failures
        .map((failure) => `${failure.path} ${failure.viewport}: ${[...failure.issues, ...failure.diagnostics.responses, ...failure.diagnostics.console, ...failure.diagnostics.page].join(' | ')}`)
        .join('\n'),
    );
  }
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
