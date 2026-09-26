const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const ledger = JSON.parse(fs.readFileSync(path.join(root, 'editorial/article-ledger.json'), 'utf8'));
const indexPath = path.join(root, 'blog/index.html');
const index = fs.readFileSync(indexPath, 'utf8');
const errors = [];

const count = (source, needle) => source.split(needle).length - 1;
if (count(index, 'class="card"') !== ledger.articles.length) {
  errors.push(`blog/index.html card count: ${count(index, 'class="card"')} != ${ledger.articles.length}`);
}

for (const article of ledger.articles) {
  const href = article.path.replace(/^blog\//, '');
  if (count(index, `href="${href}"`) !== 1) errors.push(`article link missing or duplicated: ${href}`);
}

const archiveFiles = [...index.matchAll(/href="(archive\/\d{4}\/\d{2}\/index\.html)"/g)].map(match => match[1]);
const uniqueArchives = [...new Set(archiveFiles)];
if (uniqueArchives.length !== 9) errors.push(`archive link count: ${uniqueArchives.length} != 9`);

for (const relative of uniqueArchives) {
  const file = path.join(root, 'blog', relative);
  if (!fs.existsSync(file)) {
    errors.push(`archive file missing: ${relative}`);
    continue;
  }
  const html = fs.readFileSync(file, 'utf8');
  if (!html.includes('← 全記事一覧へ戻る')) errors.push(`back link missing: ${relative}`);
  for (const href of [...html.matchAll(/href="([^"]+)"/g)].map(match => match[1])) {
    if (/^(?:https?:|#|mailto:|tel:)/.test(href)) continue;
    const clean = href.split('#')[0].split('?')[0];
    if (!clean) continue;
    const resolved = path.resolve(path.dirname(file), clean);
    const previewResolved = path.join(root, 'dist/blog-preview/site', path.relative(root, resolved));
    if (!fs.existsSync(resolved) && !fs.existsSync(previewResolved)) errors.push(`broken link: ${relative} -> ${href}`);
  }
}

if (!index.includes(`全${ledger.articles.length}記事を掲載しています`)) errors.push('total article count text missing');
if (index.includes('2026年6月以降の記事を掲載しています')) errors.push('old cutoff message remains');

if (errors.length) {
  console.error(JSON.stringify({status: 'blocked', errors}, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({status: 'pass', articles: ledger.articles.length, archives: uniqueArchives.length}, null, 2));
