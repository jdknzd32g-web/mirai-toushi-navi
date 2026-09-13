const fs = require('fs');
const path = require('path');
const { createRequire } = require('module');
const runtime = createRequire('/Users/satoshioka/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json');
const { chromium } = runtime('playwright');
const root = path.resolve(__dirname, '../..');
const out = path.join(root, process.env.RELEASE_BATCH === 'additional' ? 'dist/blog-release-additional' : 'dist/blog-release');
const read = n => JSON.parse(fs.readFileSync(path.join(out, n)));
(async () => {
  const deploy = read('deploy.json'), manifest = read('package.json');
  const base = process.argv.includes('--production') ? 'https://eva-solution.com' : deploy.url;
  const report = { status: 'blocked', deploy: deploy.id, base, checks: [], errors: [] };
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    for (const width of [1440, 390, 320]) {
      const context = await browser.newContext({ viewport: { width, height: 960 } });
      await context.route('**/*', route => route.request().url().startsWith(base + '/') ? route.continue() : route.abort());
      const page = await context.newPage();
      for (const name of [...manifest.articles, 'index.html', 'blog/index.html']) {
        const response = await page.goto(base + '/' + name, { waitUntil: 'load' });
        if (!response.ok()) report.errors.push('HTTP:' + name);
        if (base === 'https://eva-solution.com' && /noindex/i.test(response.headers()['x-robots-tag'] || '')) report.errors.push('HTTP noindex:' + name);
        const result = await page.evaluate(({ name, articles }) => {
          const errors = [];
          if (document.documentElement.scrollWidth > innerWidth + 1) errors.push('overflow');
          if (document.body.textContent.includes('ローカル確認用・未公開') || document.querySelector('meta[name="robots"]')?.content.includes('noindex')) errors.push('preview-marker');
          if (articles.includes(name)) {
            if (document.querySelector('link[rel="canonical"]')?.href !== 'https://eva-solution.com/' + name) errors.push('canonical');
            if (!document.querySelector('meta[property="og:image"]')?.content) errors.push('og-image');
            const schema = JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent);
            if (schema['@type'] !== 'Article' || !schema.datePublished) errors.push('schema');
            if (document.querySelectorAll('.bp-highlight').length !== 3 || document.querySelectorAll('.bp-emphasis').length !== 4) errors.push('emphasis');
          } else {
            // Netlify Pretty URLs rewrites hrefs to extensionless equivalents.
            const normalize = value => value.replace(/\.html$/, '').replace(/\/$/, '');
            for (const article of articles) if (![...document.links].some(a => normalize(new URL(a.href).pathname) === normalize('/' + article))) errors.push('missing-discovery:' + article);
            if (name === 'index.html' && document.querySelectorAll('.bp-latest-card').length !== 3) errors.push('lp-count');
          }
          return errors;
        }, { name, articles: manifest.articles });
        report.errors.push(...result.map(error => `${width}:${name}:${error}`));
        report.checks.push({ width, page: name, status: result.length ? 'blocked' : 'pass' });
        if (width === 390) await page.screenshot({ path: path.join(out, 'release-' + name.replaceAll('/', '-') + '.png'), fullPage: false });
      }
      await context.close();
    }
    const sitemap = await fetch(base + '/sitemap.xml').then(r => { if (!r.ok) throw Error('Sitemap missing'); return r.text(); });
    for (const name of manifest.articles) if (!sitemap.includes('https://eva-solution.com/' + name)) report.errors.push('sitemap:' + name);
    for (const name of manifest.articles) {
      const html = fs.readFileSync(path.join(out, 'site', name), 'utf8');
      const paths = [...html.matchAll(/(?:href|src)="(\/[^"#]*)"/g)].map(m => m[1]);
      for (const route of new Set(paths)) {
        const response = await fetch(base + route, { method: 'HEAD' });
        if (!response.ok) report.errors.push('Dependency HTTP:' + route);
      }
    }
    report.status = report.errors.length ? 'blocked' : 'pass';
  } catch (e) { report.errors.push(e.message); }
  finally { await browser.close(); }
  fs.writeFileSync(path.join(out, base === deploy.url ? 'verified.json' : 'production-verified.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
  process.exitCode = report.status === 'pass' ? 0 : 1;
  if (report.status === 'pass' && process.argv.includes('--production')) {
    const result = require('child_process').spawnSync(process.execPath, [path.join(__dirname, 'post-published-x.cjs'), '--send'], {cwd:root, stdio:'inherit'});
    if (result.error || result.status !== 0) {
      console.error('Production verification passed, but X posting needs attention. Inspect posting logs before retrying.');
      process.exitCode = 1;
    }
  }
})();
