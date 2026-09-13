// Read-only browser gate against the approved copper article, never rebaselines.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { createRequire } = require('module');
const runtime = createRequire(process.env.PLAYWRIGHT_PACKAGE || '/Users/satoshioka/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json');
const { chromium } = runtime('playwright');
const root = path.resolve(__dirname, '../..');
const out = path.join(root, 'dist/blog-preview');
const base = process.env.PREVIEW_URL || 'http://127.0.0.1:8765';
const reference = 'blog/2026/copper-price-2026/copper-price-2026.html';
const sha = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const widths = [1440, 768, 390, 320];
const pairs = [
  ['body', '.bp-page', ['backgroundColor', 'color', 'fontFamily', 'fontSize', 'lineHeight']],
  ['.container', '.bp-container', ['maxWidth']],
  ['.hero-image', '.bp-hero', ['aspectRatio', 'borderRadius', 'marginBottom']],
  ['.article-title', '.bp-container h1', ['fontSize', 'lineHeight', 'color']],
  ['.article-category', '.bp-category', ['backgroundColor', 'color', 'borderRadius']],
  ['.lead', '.bp-lead', ['backgroundColor', 'borderLeftWidth', 'borderLeftColor', 'borderRadius']],
  ['.toc', '.bp-toc', ['backgroundColor', 'borderTopColor', 'borderRadius']],
  ['article h2', '.bp-container article h2', ['fontSize', 'color', 'borderBottomColor', 'borderBottomWidth']],
  ['.youtube-channel-banner', '.bp-youtube', ['backgroundImage', 'borderRadius', 'borderTopColor']],
  ['.yt-icon', '.bp-yt-icon', ['backgroundColor', 'borderRadius', 'width', 'height']],
  ['.yt-cta-btn', '.bp-yt-button', ['backgroundColor', 'borderRadius']],
  ['.cta-box', '.bp-cta', ['backgroundImage', 'borderRadius', 'textAlign']],
  ['.cta-button', '.bp-cta a', ['backgroundColor', 'color', 'borderRadius']],
  ['.summary-box', '.bp-summary', ['backgroundColor', 'borderTopWidth', 'borderTopColor', 'borderRadius']],
  ['.author-photo', '.bp-author img', ['width', 'height', 'borderRadius', 'objectFit']]
];

async function styles(page, referenceMode) {
  return page.evaluate(({ pairs, referenceMode }) => pairs.map(pair => {
    const selector = pair[referenceMode ? 0 : 1], element = document.querySelector(selector);
    if (!element) return { selector, missing: true };
    const css = getComputedStyle(element);
    return { selector, values: Object.fromEntries(pair[2].map(key => [key, css[key]])) };
  }), { pairs, referenceMode });
}

async function inspect(page, benchmark) {
  const actual = await styles(page, false), errors = [];
  actual.forEach((item, index) => {
    if (item.missing) errors.push('missing:' + item.selector);
    else for (const key of pairs[index][2]) {
      if (item.values[key] !== benchmark[index].values[key]) errors.push(`style:${item.selector}:${key}`);
    }
  });
  const structure = await page.evaluate(() => {
    const errors = [], $ = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
    const visible = el => el && el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden' && Number(getComputedStyle(el).opacity) > 0;
    const order = ['.bp-hero', '.bp-container h1', '.bp-lead', '.bp-youtube', '.bp-toc', '.bp-container article', '.bp-summary', '.bp-cta', '.bp-author', '.bp-sources'];
    for (const selector of order) {
      if (all(selector).length !== 1 || !visible($(selector))) errors.push('component:' + selector);
    }
    for (let i = 1; i < order.length; i++) {
      const a = $(order[i - 1]), b = $(order[i]);
      if (a && b && !(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING)) errors.push('order:' + order[i]);
      if (a && b && a.getBoundingClientRect().bottom > b.getBoundingClientRect().top + 1) errors.push('visual-order:' + order[i]);
    }
    if (all('h1').length !== 1) errors.push('h1-count');
    for (const [selector, url, label] of [
      ['.bp-youtube', 'https://www.youtube.com/channel/UCb-u1hcuQyo7qruBhuiOBZg', 'YouTube'],
      ['.bp-cta a', 'https://lin.ee/FxIOpk1', 'LINE']
    ]) {
      const link = $(selector);
      if (!link || link.href !== url || !link.relList.contains('noopener') || !link.relList.contains('noreferrer') || link.target !== '_blank') errors.push('official-link:' + label);
      if (link && link.getBoundingClientRect().height < 44) errors.push('touch-target:' + label);
    }
    if ($('.bp-cta a')?.textContent !== '公式LINEで相談する') errors.push('line-label');
    if (!all('.bp-toc a').length || all('.bp-toc a').some(a => !document.getElementById(a.hash.slice(1)))) errors.push('toc-links');
    if (all('img').some(img => !img.complete || !img.naturalWidth || !img.alt.trim())) errors.push('images');
    if (document.documentElement.scrollWidth > innerWidth + 1) errors.push('page-overflow');
    const hero = $('.bp-hero');
    if (hero && Math.abs(hero.clientWidth / hero.clientHeight - 16 / 9) > .02) errors.push('hero-ratio');
    const small = all('.bp-container p:not(.bp-meta):not(.bp-category), .bp-container td, .bp-container th, .bp-container li, .bp-diagram span, .bp-diagram strong, .bp-cta a').filter(el => visible(el) && parseFloat(getComputedStyle(el).fontSize) < 16);
    if (small.length) errors.push('text-below-16');
    const emphasis = all('.bp-emphasis, .bp-highlight');
    if (all('.bp-highlight').length > 5) errors.push('highlight-count');
    for (const el of emphasis) {
      const css = getComputedStyle(el);
      if (el.tagName !== 'STRONG' || parseInt(css.fontWeight) < 700 || el.textContent.length > 40 || !el.textContent.trim()) errors.push('emphasis-format');
      if (css.color !== 'rgb(51, 51, 51)') errors.push('emphasis-color');
      if (el.closest('a, h1, h2, h3, .bp-diagram, .bp-toc, .bp-cta, .bp-author, .bp-sources, .bp-related')) errors.push('emphasis-location');
      if (el.matches('.bp-highlight') && (!css.backgroundImage.includes('rgb(255, 229, 138)') || css.display !== 'inline' || css.whiteSpace === 'nowrap')) errors.push('highlight-style');
    }
    for (const group of all('.bp-lead, article > section, .bp-summary')) {
      if (group.querySelectorAll('.bp-highlight').length > 1 || group.querySelectorAll('.bp-emphasis').length > 2) errors.push('emphasis-section-limit');
    }
    const reading = all('.bp-lead p, article p, article li, article td, .bp-summary li').filter(el => !el.closest('.bp-diagram'));
    for (const el of reading) if (el.querySelectorAll('.bp-emphasis, .bp-highlight').length > 1) errors.push('emphasis-paragraph-limit');
    const total = reading.reduce((sum, el) => sum + el.textContent.length, 0);
    if (emphasis.reduce((sum, el) => sum + el.textContent.length, 0) > total * .15) errors.push('emphasis-density');
    if (!all('.bp-related-link').length || !all('.bp-source-link').length) errors.push('link-components-missing');
    for (const link of all('.bp-related-link')) {
      const css = getComputedStyle(link);
      if (css.display !== 'block' || css.backgroundColor !== 'rgb(243, 246, 250)' || css.borderLeftWidth !== '4px' || link.getBoundingClientRect().height < 44 || !link.querySelector('.bp-link-action')) errors.push('related-link-style');
    }
    for (const link of all('.bp-source-link, .bp-cite, .bp-toc a')) {
      if (!getComputedStyle(link).textDecorationLine.includes('underline')) errors.push('text-link-style');
    }
    const diagrams = all('.bp-diagram');
    if (!diagrams.length) errors.push('diagrams-missing');
    for (const diagram of diagrams) {
      if (getComputedStyle(diagram).backgroundColor !== 'rgb(23, 50, 74)' || getComputedStyle(diagram).color !== 'rgb(255, 255, 255)') errors.push('diagram-colors');
      if ([...diagram.querySelectorAll('.bp-diagram-card')].some(card => getComputedStyle(card).borderTopColor !== 'rgb(245, 200, 66)')) errors.push('diagram-accent');
      if (!visible(diagram) || diagram.previousElementSibling?.tagName !== 'H2' || !diagram.getAttribute('aria-label')) errors.push('diagram-structure');
      if (diagram.scrollWidth > diagram.clientWidth + 1 || diagram.scrollHeight > diagram.clientHeight + 1) errors.push('diagram-overflow');
      if (diagram.querySelectorAll('.bp-diagram-card').length < 2) errors.push('diagram-content');
      if (innerWidth <= 600 && getComputedStyle(diagram.querySelector('.bp-diagram-grid')).gridTemplateColumns.split(' ').length !== 1) errors.push('diagram-mobile-stack');
    }
    return errors;
  });
  return [...errors, ...structure];
}

async function prepare(page, rel) {
  const response = await page.goto(base + '/' + rel, { waitUntil: 'load' });
  if (!response.ok()) throw Error('HTTP ' + response.status() + ': ' + rel);
  await page.addStyleTag({ content: '*{animation:none!important;transition:none!important;scroll-behavior:auto!important}' });
  await page.evaluate(async () => {
    for (const img of document.images) img.loading = 'eager';
    await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
    await document.fonts.ready;
  });
}

(async () => {
  const report = { status: 'blocked', benchmark: reference, widths, checks: [], errors: [], negative_tests: [], published: false };
  let browser;
  try {
    const build = read(path.join(out, 'build-report.json'));
    report.build_fingerprint = build.build_fingerprint;
    report.checker_sha256 = sha(__filename);
    const pinned = read(path.join(root, 'editorial/source-lock.json'))[reference];
    if (!pinned || sha(path.join(root, reference)) !== pinned || sha(path.join(out, 'site', reference)) !== pinned) throw Error('Approved reference changed; refusing to rebaseline');
    report.reference_sha256 = pinned;
    const articles = fs.readdirSync(path.join(root, 'editorial/articles')).filter(f => f.endsWith('.json')).map(f => read(path.join(root, 'editorial/articles', f)).path);
    if (!articles.length || new Set(articles).size !== articles.length || articles.some(a => !build.managed_pages.includes(a))) throw Error('Article coverage mismatch');
    browser = await chromium.launch({ channel: 'chrome', headless: true });
    for (const width of widths) {
      const context = await browser.newContext({ viewport: { width, height: 960 }, deviceScaleFactor: 1, bypassCSP: true, reducedMotion: 'reduce' });
      await context.route('**/*', route => route.request().url().startsWith(base + '/') ? route.continue() : route.abort());
      const page = await context.newPage();
      page.on('pageerror', e => report.errors.push('JS:' + e.message));
      page.on('response', r => { if (r.url().startsWith(base + '/') && r.status() >= 400) report.errors.push('HTTP:' + r.url()); });
      await prepare(page, reference);
      const benchmark = await styles(page, true);
      if (benchmark.some(b => b.missing)) throw Error('Reference selectors missing');
      for (const rel of articles) {
        await prepare(page, rel);
        const errors = await inspect(page, benchmark);
        report.checks.push({ width, page: rel, errors });
        report.errors.push(...errors.map(e => `${width}px ${rel}: ${e}`));
        if (!errors.length) {
          await page.screenshot({ path: path.join(out, `design-${path.basename(rel, '.html')}-${width}.png`), fullPage: true });
          if (width === 390 || width === 1440) {
            for (const component of ['diagram', 'youtube', 'cta', 'author', 'related', 'sources', 'lead']) {
              await page.locator('.bp-' + component).first().screenshot({ path: path.join(out, `design-${path.basename(rel, '.html')}-${width}-${component}.png`) });
            }
          }
        }
      }
      // Deliberately break a passing page in memory, then prove it is rejected.
      // No files, original articles or served pages are modified by these tests.
      if (width === 390 && !report.checks.filter(c => c.width === width).some(c => c.errors.length)) {
        const mutations = [
          ['missing-youtube', '.bp-youtube', 'remove'],
          ['wrong-line', '.bp-cta a', 'href'],
          ['wrong-color', '.bp-cta a', 'color'],
          ['wrong-width', '.bp-container', 'width'],
          ['hero-order', '.bp-hero', 'order'],
          ['missing-diagrams', '.bp-diagram', 'remove-all'],
          ['tiny-diagram', '.bp-diagram span', 'tiny'],
          ['hidden-author', '.bp-author', 'hide'],
          ['overflow', '.bp-diagram', 'overflow'],
          ['red-emphasis', '.bp-highlight', 'red'],
          ['long-emphasis', '.bp-highlight', 'long'],
          ['unstyled-related', '.bp-related-link', 'unstyled']
        ];
        for (const [name, selector, operation] of mutations) {
          await prepare(page, articles[0]);
          await page.evaluate(({ selector, operation }) => {
            const el = document.querySelector(selector);
            if (operation === 'remove') el.remove();
            if (operation === 'remove-all') document.querySelectorAll(selector).forEach(e => e.remove());
            if (operation === 'href') el.href = 'https://example.invalid/';
            if (operation === 'color') el.style.backgroundColor = 'green';
            if (operation === 'width') el.style.maxWidth = '808px';
            if (operation === 'order') document.querySelector('.bp-lead').after(el);
            if (operation === 'tiny') el.style.fontSize = '9px';
            if (operation === 'hide') el.style.display = 'none';
            if (operation === 'overflow') el.style.width = '1000px';
            if (operation === 'red') el.style.color = 'red';
            if (operation === 'long') el.textContent = '強調'.repeat(30);
            if (operation === 'unstyled') el.style.backgroundColor = 'transparent';
          }, { selector, operation });
          const detected = await inspect(page, benchmark);
          report.negative_tests.push({ name, detected: detected.length > 0, errors: detected });
          if (!detected.length) report.errors.push('Checker failed negative test: ' + name);
        }
      }
      await context.close();
    }
    if (report.negative_tests.length !== 12) report.errors.push('Negative tests incomplete');
    for (const [rel, expected] of Object.entries(build.output_hashes)) {
      if (sha(path.join(out, 'site', rel)) !== expected) report.errors.push('Build changed: ' + rel);
    }
    report.status = report.errors.length ? 'blocked' : 'pass';
  } catch (error) { report.errors.push(error.stack); }
  finally {
    if (browser) await browser.close();
    fs.writeFileSync(path.join(out, 'design-report.json'), JSON.stringify(report, null, 2));
  }
  console.log(JSON.stringify(report, null, 2));
  process.exitCode = report.status === 'pass' ? 0 : 1;
})();
