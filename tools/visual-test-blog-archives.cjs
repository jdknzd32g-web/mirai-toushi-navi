const fs = require('fs');
const path = require('path');
const {createRequire} = require('module');
const fallback = '/Users/satoshioka/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json';
let playwright;
try { playwright = require('playwright'); }
catch { playwright = createRequire(process.env.PLAYWRIGHT_PACKAGE || fallback)('playwright'); }

const root = path.resolve(__dirname, '..');
const base = process.env.ARCHIVE_PREVIEW_URL || 'http://127.0.0.1:8877';
const output = path.join(root, 'dist/blog-archive-check');
fs.mkdirSync(output, {recursive: true});

(async () => {
  const errors = [];
  const checks = [];
  const browser = await playwright.chromium.launch({headless: true, channel: 'chrome'});
  try {
    for (const width of [1440, 768, 390, 320]) {
      const context = await browser.newContext({viewport: {width, height: 960}, reducedMotion: 'reduce'});
      await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
      for (const url of ['/blog/index.html', '/blog/archive/2025/09/index.html']) {
        const page = await context.newPage();
        const pageErrors = [];
        page.on('pageerror', error => pageErrors.push(`JS: ${error.message}`));
        page.on('response', response => { if (response.url().startsWith(base) && response.status() >= 400) pageErrors.push(`HTTP ${response.status()}: ${response.url()}`); });
        await page.goto(base + url, {waitUntil: 'networkidle'});
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
        if (overflow) pageErrors.push('horizontal overflow');
        const smallText = await page.locator('.card h3,.month-nav a').evaluateAll(elements => elements.filter(element => parseFloat(getComputedStyle(element).fontSize) < 13).length);
        if (smallText) pageErrors.push(`small text: ${smallText}`);
        const cards = await page.locator('.card').count();
        if (!cards) pageErrors.push('no article cards');
        if (url === '/blog/index.html' && cards !== 113) pageErrors.push(`all-article card count: ${cards}`);
        await page.screenshot({path: path.join(output, `${url.includes('archive') ? 'archive' : 'index'}-${width}.png`), fullPage: false});
        checks.push({width, url, cards, errors: pageErrors});
        errors.push(...pageErrors.map(error => `${width} ${url}: ${error}`));
        await page.close();
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }
  const report = {status: errors.length ? 'blocked' : 'pass', widths: [1440, 768, 390, 320], checks, errors};
  fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  if (errors.length) process.exit(1);
})().catch(error => { console.error(error); process.exit(1); });
