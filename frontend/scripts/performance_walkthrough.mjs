import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright';
import { preview } from 'vite';

let baseUrl = process.env.PARVA_PERF_BASE_URL;
const reportPath = process.env.PARVA_PERF_REPORT_PATH;

async function startPreviewServer() {
  const server = await preview({
    root: process.cwd(),
    logLevel: 'silent',
    preview: {
      host: '127.0.0.1',
      port: 4174,
      strictPort: false,
    },
  });
  const address = server.httpServer.address();
  const port = typeof address === 'object' && address ? address.port : 4174;
  baseUrl = `http://127.0.0.1:${port}`;
  return server;
}

const routes = [
  { path: '/', label: 'Home', ready: /^Project Parva$/i, viewports: ['desktop', 'mobile'] },
  { path: '/today', label: 'Today', ready: /Today in/i, viewports: ['desktop'] },
  { path: '/festivals', label: 'Festivals', ready: /^Festivals$/i, viewports: ['desktop', 'mobile'] },
  { path: '/developers', label: 'Developers', ready: /Build with Nepal's calendar/i, viewports: ['desktop'] },
  { path: '/pricing', label: 'Pricing', ready: /API access that grows/i, viewports: ['desktop'] },
  { path: '/proof', label: 'Proof Viewer', ready: /Inspect Parva proof packs/i, viewports: ['desktop'] },
];

const viewports = {
  desktop: { viewport: { width: 1440, height: 1000 } },
  mobile: {
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 2,
  },
};

const thresholds = {
  first_contentful_paint_ms: 2500,
  largest_contentful_paint_ms: 3500,
  cumulative_layout_shift: 0.1,
  startup_long_task_total_ms: 1800,
  startup_long_task_worst_ms: 950,
  interaction_long_task_total_ms: 180,
  interaction_frame_p95_ms: 40,
  interaction_frames_over_50_ms_per_probe: 1,
  transfer_kb: 1600,
};
const interactionProbeCount = 3;
const measurementSampleCount = 3;

function percentile(values, ratio) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * ratio))];
}

async function installObservers(page) {
  await page.addInitScript(() => {
    window.__parvaPerf = {
      cls: 0,
      layoutShifts: [],
      lcp: 0,
      longTasks: [],
      frameProbe: null,
    };

    try {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            window.__parvaPerf.cls += entry.value;
            window.__parvaPerf.layoutShifts.push({
              start: entry.startTime,
              value: entry.value,
              sources: (entry.sources || []).map((source) => {
                const node = source.node;
                if (!node) return 'unknown';
                const id = node.id ? `#${node.id}` : '';
                const classes = typeof node.className === 'string'
                  ? node.className.trim().split(/\s+/).filter(Boolean).slice(0, 3).map((name) => `.${name}`).join('')
                  : '';
                return `${node.tagName?.toLowerCase() || 'node'}${id}${classes}`;
              }),
            });
          }
        }
      }).observe({ type: 'layout-shift', buffered: true });
    } catch {
      // Unsupported metrics stay at their neutral value.
    }

    try {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const last = entries[entries.length - 1];
        if (last) window.__parvaPerf.lcp = last.startTime;
      }).observe({ type: 'largest-contentful-paint', buffered: true });
    } catch {
      // Unsupported metrics stay at their neutral value.
    }

    try {
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          window.__parvaPerf.longTasks.push({
            start: entry.startTime,
            duration: entry.duration,
          });
        }
      }).observe({ type: 'longtask', buffered: true });
    } catch {
      // Unsupported metrics stay at their neutral value.
    }
  });
}

async function probeMenuFrames(page) {
  await page.evaluate(() => {
    window.__parvaPerf.startupLongTasks = [...window.__parvaPerf.longTasks];
    window.__parvaPerf.longTasks = [];
    window.__parvaPerf.frameProbes = [];
  });

  for (let index = 0; index < interactionProbeCount; index += 1) {
    await page.evaluate(() => {
      const probe = { frames: [], done: false };
      window.__parvaPerf.frameProbe = probe;
      window.__parvaPerf.frameProbes.push(probe);
      const started = performance.now();
      const tick = (timestamp) => {
        probe.frames.push(timestamp);
        if (timestamp - started < 900) {
          requestAnimationFrame(tick);
        } else {
          probe.done = true;
        }
      };
      requestAnimationFrame(tick);
    });

    const trigger = page.getByRole('button', { name: /Open navigation/i });
    if (await trigger.count()) {
      await trigger.click();
      await page.waitForTimeout(220);
      const close = page
        .getByRole('dialog', { name: /Project Parva navigation/i })
        .getByRole('button', { name: /Close navigation/i });
      if (await close.count()) await close.click();
    }

    await page.waitForFunction(() => window.__parvaPerf?.frameProbe?.done === true);
  }
}

async function collectMetrics(page) {
  return page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0];
    const paint = performance.getEntriesByType('paint');
    const resources = performance.getEntriesByType('resource');
    const frameProbes = window.__parvaPerf?.frameProbes || [];
    const frameIntervals = frameProbes.flatMap((probe) => (
      probe.frames.slice(1).map((value, index) => value - probe.frames[index])
    ));
    const transferBytes = resources.reduce((total, entry) => total + (entry.transferSize || 0), 0);
    const resourceGroups = resources.reduce((groups, entry) => {
      const type = entry.initiatorType || 'other';
      groups[type] = (groups[type] || 0) + (entry.transferSize || 0);
      return groups;
    }, {});
    const startupLongTasks = window.__parvaPerf?.startupLongTasks || [];
    const interactionLongTasks = window.__parvaPerf?.longTasks || [];
    const largestResources = resources
      .map((entry) => ({
        name: entry.name,
        type: entry.initiatorType || 'other',
        transfer_bytes: entry.transferSize || 0,
      }))
      .sort((left, right) => right.transfer_bytes - left.transfer_bytes)
      .slice(0, 12);

    return {
      navigation: {
        dom_content_loaded_ms: navigation?.domContentLoadedEventEnd || 0,
        load_event_ms: navigation?.loadEventEnd || 0,
        response_end_ms: navigation?.responseEnd || 0,
      },
      first_contentful_paint_ms: paint.find((entry) => entry.name === 'first-contentful-paint')?.startTime || 0,
      largest_contentful_paint_ms: window.__parvaPerf?.lcp || 0,
      cumulative_layout_shift: window.__parvaPerf?.cls || 0,
      layout_shifts: window.__parvaPerf?.layoutShifts || [],
      startup_long_tasks: {
        count: startupLongTasks.length,
        total_ms: startupLongTasks.reduce((total, entry) => total + entry.duration, 0),
        worst_ms: Math.max(0, ...startupLongTasks.map((entry) => entry.duration)),
        entries: startupLongTasks,
      },
      interaction_long_tasks: {
        count: interactionLongTasks.length,
        total_ms: interactionLongTasks.reduce((total, entry) => total + entry.duration, 0),
        worst_ms: Math.max(0, ...interactionLongTasks.map((entry) => entry.duration)),
        entries: interactionLongTasks,
      },
      interaction_frames: {
        count: frameIntervals.length,
        probe_count: frameProbes.length,
        intervals_ms: frameIntervals,
      },
      transfer_bytes: transferBytes,
      transfer_by_type: resourceGroups,
      largest_resources: largestResources,
      horizontal_overflow_px: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
    };
  });
}

function thresholdChecks(metrics, p95, framesOver50) {
  const probeCount = Math.max(1, metrics.interaction_frames.probe_count);
  return {
    first_contentful_paint: metrics.first_contentful_paint_ms <= thresholds.first_contentful_paint_ms,
    largest_contentful_paint: !metrics.largest_contentful_paint_ms
      || metrics.largest_contentful_paint_ms <= thresholds.largest_contentful_paint_ms,
    cumulative_layout_shift: metrics.cumulative_layout_shift <= thresholds.cumulative_layout_shift,
    startup_long_task_total: metrics.startup_long_tasks.total_ms <= thresholds.startup_long_task_total_ms,
    startup_long_task_worst: metrics.startup_long_tasks.worst_ms <= thresholds.startup_long_task_worst_ms,
    interaction_long_task_total:
      metrics.interaction_long_tasks.total_ms <= thresholds.interaction_long_task_total_ms * probeCount,
    interaction_frame_p95: p95 <= thresholds.interaction_frame_p95_ms,
    interaction_frames_over_50:
      framesOver50 <= thresholds.interaction_frames_over_50_ms_per_probe * probeCount,
    transfer_size: (metrics.transfer_bytes / 1024) <= thresholds.transfer_kb,
    horizontal_overflow: metrics.horizontal_overflow_px === 0,
  };
}

function evaluateThresholds(metrics) {
  const intervals = metrics.interaction_frames.intervals_ms;
  const p95 = percentile(intervals, 0.95);
  const framesOver50 = intervals.filter((value) => value > 50).length;
  const checks = thresholdChecks(metrics, p95, framesOver50);

  return {
    status: Object.values(checks).every(Boolean) ? 'passed' : 'failed',
    checks,
    interaction_frame_p95_ms: p95,
    interaction_frames_over_50_ms: framesOver50,
  };
}

function median(values) {
  return percentile(values.filter(Number.isFinite), 0.5);
}

function mergeDiagnostics(samples) {
  return {
    responses: [...new Set(samples.flatMap((sample) => sample.diagnostics.responses))],
    console: [...new Set(samples.flatMap((sample) => sample.diagnostics.console))],
    page: [...new Set(samples.flatMap((sample) => sample.diagnostics.page))],
  };
}

function aggregateCaseSamples(samples) {
  const startupTotal = median(samples.map((sample) => sample.metrics.startup_long_tasks.total_ms));
  const reference = [...samples].sort((left, right) => (
    Math.abs(left.metrics.startup_long_tasks.total_ms - startupTotal)
    - Math.abs(right.metrics.startup_long_tasks.total_ms - startupTotal)
  ))[0];
  const numericMedian = (select) => median(samples.map(select));
  const metrics = {
    ...reference.metrics,
    navigation: {
      dom_content_loaded_ms: numericMedian((sample) => sample.metrics.navigation.dom_content_loaded_ms),
      load_event_ms: numericMedian((sample) => sample.metrics.navigation.load_event_ms),
      response_end_ms: numericMedian((sample) => sample.metrics.navigation.response_end_ms),
    },
    first_contentful_paint_ms: numericMedian((sample) => sample.metrics.first_contentful_paint_ms),
    largest_contentful_paint_ms: numericMedian((sample) => sample.metrics.largest_contentful_paint_ms),
    cumulative_layout_shift: numericMedian((sample) => sample.metrics.cumulative_layout_shift),
    startup_long_tasks: {
      ...reference.metrics.startup_long_tasks,
      count: Math.round(numericMedian((sample) => sample.metrics.startup_long_tasks.count)),
      total_ms: startupTotal,
      worst_ms: numericMedian((sample) => sample.metrics.startup_long_tasks.worst_ms),
    },
    interaction_long_tasks: {
      ...reference.metrics.interaction_long_tasks,
      count: Math.round(numericMedian((sample) => sample.metrics.interaction_long_tasks.count)),
      total_ms: numericMedian((sample) => sample.metrics.interaction_long_tasks.total_ms),
      worst_ms: numericMedian((sample) => sample.metrics.interaction_long_tasks.worst_ms),
    },
    interaction_frames: {
      count: Math.round(numericMedian((sample) => sample.metrics.interaction_frames.count)),
      probe_count: Math.round(numericMedian((sample) => sample.metrics.interaction_frames.probe_count)),
      p95_ms: numericMedian((sample) => sample.metrics.interaction_frames.p95_ms),
      frames_over_50_ms: Math.round(
        numericMedian((sample) => sample.metrics.interaction_frames.frames_over_50_ms),
      ),
    },
    transfer_bytes: numericMedian((sample) => sample.metrics.transfer_bytes),
    transfer_kb: Number(
      (numericMedian((sample) => sample.metrics.transfer_bytes) / 1024).toFixed(2),
    ),
    horizontal_overflow_px: Math.max(
      ...samples.map((sample) => sample.metrics.horizontal_overflow_px),
    ),
  };
  const checks = thresholdChecks(
    metrics,
    metrics.interaction_frames.p95_ms,
    metrics.interaction_frames.frames_over_50_ms,
  );
  const diagnostics = mergeDiagnostics(samples);
  const cleanDiagnostics = !diagnostics.responses.length
    && !diagnostics.console.length
    && !diagnostics.page.length;

  return {
    path: reference.path,
    label: reference.label,
    viewport: reference.viewport,
    status: Object.values(checks).every(Boolean) && cleanDiagnostics ? 'passed' : 'failed',
    sample_count: samples.length,
    metrics,
    checks,
    diagnostics,
    sample_summaries: samples.map((sample, index) => ({
      sample: index + 1,
      status: sample.status,
      first_contentful_paint_ms: sample.metrics.first_contentful_paint_ms,
      largest_contentful_paint_ms: sample.metrics.largest_contentful_paint_ms,
      cumulative_layout_shift: sample.metrics.cumulative_layout_shift,
      startup_long_task_total_ms: sample.metrics.startup_long_tasks.total_ms,
      startup_long_task_worst_ms: sample.metrics.startup_long_tasks.worst_ms,
      interaction_long_task_total_ms: sample.metrics.interaction_long_tasks.total_ms,
      interaction_frame_p95_ms: sample.metrics.interaction_frames.p95_ms,
      interaction_frames_over_50_ms: sample.metrics.interaction_frames.frames_over_50_ms,
      transfer_kb: sample.metrics.transfer_kb,
    })),
  };
}

async function runCase(browser, route, viewportName) {
  const context = await browser.newContext(viewports[viewportName]);
  const page = await context.newPage();
  const diagnostics = { responses: [], console: [], page: [] };
  const origin = new URL(baseUrl).origin;

  page.on('response', (response) => {
    try {
      const url = new URL(response.url());
      if (url.origin === origin && response.status() >= 400 && response.status() !== 429) {
        diagnostics.responses.push(`${response.status()} ${response.url()}`);
      }
    } catch {
      // Ignore malformed browser URLs.
    }
  });
  page.on('console', (message) => {
    if (message.type() === 'error' && !/429|Too Many Requests/i.test(message.text())) {
      diagnostics.console.push(message.text());
    }
  });
  page.on('pageerror', (error) => diagnostics.page.push(error.message));

  try {
    await installObservers(page);
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.goto(new URL(route.path, baseUrl).toString(), { waitUntil: 'domcontentloaded' });
    await page.getByRole('heading', { name: route.ready, level: 1 }).waitFor({ timeout: 20000 });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(320);
    await probeMenuFrames(page);
    const metrics = await collectMetrics(page);
    const evaluation = evaluateThresholds(metrics);
    const cleanDiagnostics = !diagnostics.responses.length && !diagnostics.console.length && !diagnostics.page.length;

    return {
      path: route.path,
      label: route.label,
      viewport: viewportName,
      status: evaluation.status === 'passed' && cleanDiagnostics ? 'passed' : 'failed',
      metrics: {
        ...metrics,
        interaction_frames: {
          count: metrics.interaction_frames.count,
          probe_count: metrics.interaction_frames.probe_count,
          p95_ms: evaluation.interaction_frame_p95_ms,
          frames_over_50_ms: evaluation.interaction_frames_over_50_ms,
        },
        transfer_kb: Number((metrics.transfer_bytes / 1024).toFixed(2)),
      },
      checks: evaluation.checks,
      diagnostics,
    };
  } finally {
    await context.close();
  }
}

async function main() {
  const previewServer = baseUrl ? null : await startPreviewServer();
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const route of routes) {
      for (const viewportName of route.viewports) {
        const samples = [];
        for (let index = 0; index < measurementSampleCount; index += 1) {
          samples.push(await runCase(browser, route, viewportName));
        }
        results.push(aggregateCaseSamples(samples));
      }
    }
  } finally {
    await browser.close();
    await previewServer?.close();
  }

  const failures = results.filter((result) => result.status !== 'passed');
  const payload = {
    generated_at: new Date().toISOString(),
    status: failures.length ? 'failed' : 'passed',
    base_url: baseUrl,
    runner: 'playwright-chromium',
    measurement_model: {
      cold_context_samples: measurementSampleCount,
      interaction_probes_per_sample: interactionProbeCount,
      aggregation: 'median',
    },
    thresholds,
    results,
  };

  if (reportPath) {
    await fs.mkdir(path.dirname(reportPath), { recursive: true });
    await fs.writeFile(reportPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  } else {
    console.log(JSON.stringify(payload, null, 2));
  }

  if (failures.length) {
    throw new Error(failures.map((item) => `${item.path} ${item.viewport}`).join(', '));
  }
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
