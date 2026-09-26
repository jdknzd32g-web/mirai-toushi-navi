const fs = require('fs');
const path = require('path');
const {createRequire} = require('module');
const runtime = createRequire('/Users/satoshioka/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json');
const {chromium} = runtime('playwright');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'dist/blog-archive-release');
const deploy = JSON.parse(fs.readFileSync(path.join(out, 'deploy.json')));
const manifest = JSON.parse(fs.readFileSync(path.join(out, 'package.json')));
const production = process.argv.includes('--production');
const base = production ? 'https://eva-solution.com' : deploy.url;

(async () => {
  const report = {status: 'blocked', deploy: deploy.id, base, checks: [], errors: []};
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  try {
    for (const width of [1440, 390, 320]) {
      const context = await browser.newContext({viewport: {width, height: 960}, reducedMotion: 'reduce'});
      await context.route('**/*', route => route.request().url().startsWith(base + '/') ? route.continue() : route.abort());
      for (const name of manifest.files) {
        const page = await context.newPage();
        const response = await page.goto(`${base}/${name}`, {waitUntil: 'networkidle'});
        const errors = [];
        if (!response || !response.ok()) errors.push(`HTTP ${response?.status() || 'none'}`);
        const pageErrors = await page.evaluate(name => {
          const errors = [];
          if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) errors.push('overflow');
          if (document.querySelectorAll('.card').length === 0) errors.push('no-cards');
          if (name === 'blog/index.html' && document.querySelectorAll('.card').length !== 113) errors.push('all-article-count');
          if (name === 'blog/index.html' && document.querySelectorAll('.month-nav a').length !== 9) errors.push('month-link-count');
          if (!document.querySelector('link[rel="canonical"]')?.href.startsWith('https://eva-solution.com/blog/')) errors.push('canonical');
          return errors;
        }, name);
        errors.push(...pageErrors);
        report.errors.push(...errors.map(error => `${width}:${name}:${error}`));
        report.checks.push({width, page: name, status: errors.length ? 'blocked' : 'pass'});
        if (width === 390 && (name === 'blog/index.html' || name === 'blog/archive/2025/09/index.html')) {
          await page.screenshot({path: path.join(out, `${production ? 'production' : 'draft'}-${name.includes('archive') ? 'archive' : 'index'}-390.png`), fullPage: false});
        }
        await page.close();
      }
      await context.close();
    }
    report.status = report.errors.length ? 'blocked' : 'pass';
  } catch (error) {
    report.errors.push(error.message);
  } finally {
    await browser.close();
  }
  fs.writeFileSync(path.join(out, production ? 'production-verified.json' : 'verified.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'pass') process.exit(1);
})().catch(error => { console.error(error); process.exit(1); });
