// Local-only Playwright checks. Uses the bundled runtime; no API keys.
const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const crypto = require('crypto');
const fallback = '/Users/satoshioka/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json';
const bundled = createRequire(process.env.PLAYWRIGHT_PACKAGE || fallback);
const { PNG } = bundled('pngjs');
let playwright;
try { playwright = require('playwright'); }
catch { playwright = createRequire(process.env.PLAYWRIGHT_PACKAGE || fallback)('playwright'); }
const root = path.resolve(__dirname, '../..');
const out = path.join(root, 'dist/blog-preview');
const base = process.env.PREVIEW_URL || 'http://127.0.0.1:8765';
const freeze = '*{animation:none!important;transition:none!important;scroll-behavior:auto!important}.reveal-on-scroll{opacity:1!important;transform:none!important}';

async function prepare(page, url) {
  await page.goto(base + url, { waitUntil: 'load' });
  await page.addStyleTag({ content: freeze });
  await page.evaluate(async () => {
    document.querySelectorAll('video').forEach(v => { v.pause(); v.currentTime = 0; });
    for (const img of document.images) { img.loading = 'eager'; }
    await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
    await document.fonts.ready;
    window.scrollTo(0, 0);
  });
}

(async () => {
  const report = { status: 'running', externalResources: 'blocked for deterministic local checks', viewports: [], errors: [] };
  const browser = await playwright.chromium.launch({ headless: true, channel: 'chrome' });
  const build = JSON.parse(fs.readFileSync(path.join(out, 'build-report.json')));
  report.build_fingerprint = build.build_fingerprint;
  const pages = build.managed_pages;
  try {
    for (const width of [1440, 768, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 960 }, reducedMotion: 'reduce', deviceScaleFactor: 1, bypassCSP: true });
      await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
      const before = await context.newPage();
      const after = await context.newPage();
      const errors = [];
      after.on('pageerror', e => errors.push('JS: ' + e.message));
      after.on('response', r => { if (r.url().startsWith(base) && r.status() >= 400) errors.push('HTTP ' + r.status() + ': ' + r.url()); });
      await prepare(before, '/baseline.html');
      await prepare(after, '/index.html');
      const slot = '[aria-labelledby="blog-list-heading"]';
      const cards = await after.locator(slot + ' .bp-latest-card').count();
      if (cards !== 3) errors.push('LP must have exactly three cards');
      await after.locator(slot).screenshot({ path: path.join(out, `lp-slot-${width}.png`) });
      await after.evaluate(() => window.scrollTo(0, 0));
      await after.screenshot({ path: path.join(out, `lp-${width}.png`), fullPage: false });
      // The existing body gradient depends on total document height. Normalize
      // only the approved slot's content for pixel comparison, keeping the new
      // stylesheet active so a leaking selector will still fail this test.
      const originalSlot = await before.locator(slot).evaluate(e => e.innerHTML);
      await after.locator(slot).evaluate((e, markup) => { e.innerHTML = markup; }, originalSlot);
      // Fixed overlays are scroll-triggered. Compare the protected page regions
      // without overlays; actual overlay appearance is retained in LP captures.
      for (const page of [before, after]) {
        await page.mouse.move(0, 0);
        await page.addStyleTag({ content: '.fixed-cta{display:none!important}body>.header{position:relative!important;top:auto!important}' });
      }
      // Compare matching visible top-level regions outside the one allowed slot.
      const selector = 'body > header, body > section, body > footer';
      const beforeRegions = before.locator(selector);
      const afterRegions = after.locator(selector);
      for (const page of [before, after]) {
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      }
      // Warm up full-page capture: Chromium may settle image/layout geometry on
      // the first beyond-viewport capture. Use the subsequent stable capture.
      for (const page of [before, after]) {
        await page.screenshot({ fullPage: true, animations: 'disabled' });
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      }
      const beforeFull = PNG.sync.read(await before.screenshot({ fullPage: true, animations: 'disabled' }));
      const afterFull = PNG.sync.read(await after.screenshot({ fullPage: true, animations: 'disabled' }));
      const crop = (full, box) => {
        const x = Math.max(0, Math.round(box.x)), y = Math.max(0, Math.round(box.y));
        const target = new PNG({ width: Math.min(Math.round(box.width), full.width - x), height: Math.min(Math.round(box.height), full.height - y) });
        if (target.width <= 0 || target.height <= 0) throw Error('Invalid crop: ' + JSON.stringify({box, fullWidth: full.width, fullHeight: full.height}));
        PNG.bitblt(full, target, x, y, target.width, target.height, 0, 0);
        return target;
      };
      const diffs = [];
      if (await beforeRegions.count() !== await afterRegions.count()) errors.push('LP region count changed');
      for (let i = 0; i < await beforeRegions.count(); i++) {
        const a = beforeRegions.nth(i), b = afterRegions.nth(i);
        if (await a.getAttribute('aria-labelledby') === 'blog-list-heading' || !(await a.isVisible())) continue;
        const aBox = await a.boundingBox(), bBox = await b.boundingBox();
        aBox.y += await before.evaluate(() => scrollY);
        bBox.y += await after.evaluate(() => scrollY);
        if (Math.abs(aBox.width - bBox.width) > 1 || Math.abs(aBox.height - bBox.height) > 1) diffs.push({ region: i, reason: 'dimensions' });
        const ap = crop(beforeFull, aBox), bp = crop(afterFull, bBox);
        const aImage = PNG.sync.write(ap), bImage = PNG.sync.write(bp);
        let changedPixels = 0;
        if (ap.width !== bp.width || ap.height !== bp.height) changedPixels = ap.width * ap.height;
        else for (let j = 0; j < ap.data.length; j += 4) {
          if ([0, 1, 2, 3].some(c => Math.abs(ap.data[j + c] - bp.data[j + c]) > 1)) changedPixels++;
        }
        const pixelBudget = Math.floor(ap.width * ap.height * 0.00005);
        if (changedPixels > pixelBudget) {
          diffs.push({ region: i, reason: 'pixels', changedPixels });
          fs.writeFileSync(path.join(out, `diff-before-${width}-${i}.png`), aImage);
          fs.writeFileSync(path.join(out, `diff-after-${width}-${i}.png`), bImage);
        }
      }
      if (diffs.length) errors.push('Protected LP region visual differences: ' + JSON.stringify(diffs));
      const checked = [];
      for (const rel of pages) {
        await prepare(after, '/' + rel);
        const metrics = await after.evaluate(() => ({
          width: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          brokenImages: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src')),
          paragraphsBelow16: [...document.querySelectorAll('.bp-container p, .bp-container td, .bp-container li')].filter(e => parseFloat(getComputedStyle(e).fontSize) < 16).length
        }));
        if (metrics.scrollWidth > width + 1) errors.push(rel + ': horizontal overflow ' + metrics.scrollWidth);
        if (metrics.brokenImages.length) errors.push(rel + ': broken images ' + metrics.brokenImages.join(', '));
        if (metrics.paragraphsBelow16) errors.push(rel + ': text smaller than 16px');
        if (rel.includes('first-order-checklist') || rel.includes('cash-reserve-worksheet')) {
          await after.screenshot({ path: path.join(out, `${path.basename(rel, '.html')}-${width}.png`), fullPage: true });
          await after.screenshot({ path: path.join(out, `${path.basename(rel, '.html')}-top-${width}.png`) });
          await after.locator('.bp-table-scroll').screenshot({ path: path.join(out, `${path.basename(rel, '.html')}-table-${width}.png`) });
        }
        checked.push({ page: rel, ...metrics });
      }
      report.viewports.push({ width, protectedRegions: await beforeRegions.count() - 1, cards, diffs, checked });
      report.errors.push(...errors.map(e => `${width}px: ${e}`));
      await context.close();
    }
    for (const [name, expected] of Object.entries(build.output_hashes || {})) {
      const actual = crypto.createHash('sha256').update(fs.readFileSync(path.join(out, 'site', name))).digest('hex');
      if (actual !== expected) report.errors.push('Build changed during visual test: ' + name);
    }
    report.status = report.errors.length ? 'blocked' : 'pass';
  } catch (e) {
    report.status = 'blocked';
    report.errors.push(e.stack);
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(out, 'visual-report.json'), JSON.stringify(report, null, 2));
  }
  console.log(JSON.stringify({ status: report.status, errors: report.errors, widths: report.viewports.map(v => v.width) }, null, 2));
  process.exitCode = report.status === 'pass' ? 0 : 1;
})();
