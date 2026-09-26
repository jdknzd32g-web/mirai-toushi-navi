const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const outputArg = process.argv.indexOf('--output-root');
const outputRoot = outputArg >= 0 ? path.resolve(process.argv[outputArg + 1]) : root;
if (outputArg >= 0 && !process.argv[outputArg + 1]) throw new Error('--output-root requires a path');
const ledger = JSON.parse(fs.readFileSync(path.join(root, 'editorial/article-ledger.json'), 'utf8'));

// Older pages did not store a publication date. These archive months are based on
// the first repository registration date and should be replaced if a confirmed
// publication month is found later.
const legacyMonths = {
  'blog/2025/mutual-fund1/mutual-fund1.html': '2025-09',
  'blog/2025/mutual-fund2/mutual-fund2.html': '2025-09',
  'blog/2025/mutual-fund3/mutual-fund3.html': '2025-09',
  'blog/2025/mutual-fund4/mutual-fund4.html': '2025-10',
  'blog/2025/mutual-fund5/mutual-fund5.html': '2025-10',
  'blog/2025/mutual-fund6/mutual-fund6.html': '2025-10',
  'blog/2025/mutual-fund7/mutual-fund7.html': '2025-10',
  'blog/2025/nisa-start-guide4/nisa-start-guide4.html': '2025-09',
  'blog/2025/nisa-start-guide5/nisa-start-guide5.html': '2025-09',
  'blog/2025/nisa-start-guide6/nisa-start-guide6.html': '2025-10',
  'blog/2025/nisa-start-guide7/nisa-start-guide7.html': '2025-10',
  'blog/2025/nisa-start-guide8/nisa-start-guide8.html': '2025-10',
  'blog/2025/nisa-start-guide9/nisa-start-guide9.html': '2025-10',
  'blog/2025/region1/region1.html': '2025-10',
  'blog/2025/region3/region3.html': '2025-10',
  'blog/2025/region6/region6.html': '2025-11',
  'blog/2025/region7/region7.html': '2025-11',
  'blog/2025/region8/region8.html': '2025-11'
};

const esc = value => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

const articles = ledger.articles.map(article => {
  article = {...article, date: article.publication_date || article.date};
  const month = article.date ? article.date.slice(0, 7) : legacyMonths[article.path];
  if (!month) throw new Error(`Archive month missing: ${article.path}`);
  return {...article, month};
}).sort((a, b) => {
  const ad = a.date || `${a.month}-01`;
  const bd = b.date || `${b.month}-01`;
  return bd.localeCompare(ad) || a.title.localeCompare(b.title, 'ja');
});

const monthKeys = [...new Set(articles.map(article => article.month))].sort().reverse();
const byMonth = new Map(monthKeys.map(month => [month, articles.filter(article => article.month === month)]));
const label = month => {
  const [year, number] = month.split('-');
  return `${year}年${Number(number)}月`;
};
const displayDate = article => article.date ? article.date.replaceAll('-', '.') : label(article.month);
const isoDate = article => article.date || `${article.month}-01`;
const relativeArticle = (article, archive = false) => {
  const withinBlog = article.path.replace(/^blog\//, '');
  return archive ? `../../../${withinBlog}` : withinBlog;
};

const styles = `
    :root{--navy:#102b3f;--blue:#176b87;--teal:#2c8b82;--ink:#1f2a30;--muted:#68777d;--cream:#f4f1e9;--paper:#fffdf8;--line:#dce3e1;--orange:#d96c3c;--gold:#f0c86b}
    *,*::before,*::after{box-sizing:border-box}
    html{scroll-behavior:smooth}
    body{margin:0;font-family:"Hiragino Mincho ProN","Yu Mincho",YuMincho,serif;color:var(--ink);background:var(--cream);line-height:1.8}
    a{color:inherit}
    .hero{position:relative;overflow:hidden;background:var(--navy);color:#fff;padding:24px 24px 68px}
    .hero::after{content:"";position:absolute;right:-120px;bottom:-180px;width:430px;height:430px;border:1px solid rgba(255,255,255,.16);border-radius:50%;box-shadow:0 0 0 55px rgba(255,255,255,.035),0 0 0 110px rgba(255,255,255,.025)}
    .nav,.hero-inner,.main{width:min(1080px,100%);margin:0 auto}
    .nav{position:relative;z-index:1;display:flex;justify-content:space-between;align-items:center;gap:20px}
    .brand{font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-weight:700;letter-spacing:.08em;text-decoration:none}
    .home{font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:13px;color:#d7e5e7;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.35)}
    .hero-inner{position:relative;z-index:1;padding-top:70px}
    .eyebrow{display:flex;align-items:center;gap:12px;margin:0 0 12px;font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:12px;font-weight:700;letter-spacing:.18em;color:#8dd0c7}
    .eyebrow::before{content:"";width:34px;height:2px;background:#8dd0c7}
    h1{margin:0;font-size:clamp(36px,6vw,60px);font-weight:600;line-height:1.35;letter-spacing:.04em}
    .lead{max-width:690px;margin:20px 0 0;color:#d1dde0;font-size:16px}
    .main{padding:56px 24px 96px}
    .section-head{display:flex;justify-content:space-between;align-items:end;gap:24px;margin-bottom:24px}
    .section-head h2{margin:0;color:var(--navy);font-size:27px;font-weight:600;letter-spacing:.05em}
    .section-head p{margin:0;font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:12px;color:var(--muted)}
    .month-nav{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 54px;padding:0;list-style:none}
    .month-nav a{display:block;padding:10px 16px;border:1px solid rgba(23,107,135,.22);border-radius:999px;background:var(--paper);color:var(--blue);font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:14px;font-weight:700;text-decoration:none}
    .month-nav a:hover,.month-nav a:focus-visible{background:#dfeae6;border-color:var(--teal)}
    .archive-section{scroll-margin-top:24px;margin-top:52px}
    .archive-section:first-of-type{margin-top:0}
    .archive-title{display:flex;align-items:center;justify-content:space-between;gap:20px;margin:0 0 20px;padding-bottom:12px;border-bottom:2px solid rgba(44,139,130,.28)}
    .archive-title h2{margin:0;color:var(--navy);font-size:26px}
    .archive-title a{font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:13px;color:var(--blue);font-weight:700;text-decoration:none}
    .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
    .card{display:flex;flex-direction:column;min-height:210px;padding:28px;background:linear-gradient(180deg,rgba(255,253,248,.94),rgba(255,251,244,.98));border:1px solid rgba(16,43,63,.09);border-radius:20px;text-decoration:none;box-shadow:0 10px 24px rgba(16,43,63,.05);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
    .card:hover,.card:focus-visible{border-color:#9dbbb8;transform:translateY(-3px);box-shadow:0 18px 34px rgba(16,43,63,.08)}
    .tag{display:inline-block;margin-bottom:14px;font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:11px;font-weight:700;letter-spacing:.08em;color:var(--teal)}
    .card h3{margin:0 0 24px;font-size:18px;line-height:1.7;font-weight:600}
    .meta{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:auto;font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:12px;color:var(--muted)}
    .read{color:var(--orange);font-weight:700}
    .back{display:inline-flex;margin:0 0 34px;color:var(--blue);font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-weight:700;text-decoration:none}
    .cta{display:flex;justify-content:space-between;align-items:center;gap:28px;margin-top:58px;padding:34px 38px;background:#dfeae6;border-left:5px solid var(--teal)}
    .cta h2{margin:0 0 4px;font-size:20px;color:var(--navy)}
    .cta p{margin:0;font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:13px;color:#4c6267}
    .cta a{flex-shrink:0;padding:12px 24px;background:var(--navy);color:#fff;text-decoration:none;font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans",sans-serif;font-size:13px;font-weight:700}
    @media(max-width:720px){.hero{padding-bottom:50px}.hero-inner{padding-top:48px}.lead{font-size:15px}.main{padding:40px 18px 72px}.section-head{align-items:start;flex-direction:column;gap:4px}.month-nav{gap:8px;margin-bottom:42px}.month-nav a{padding:9px 13px;font-size:13px}.archive-title{align-items:flex-start;flex-direction:column;gap:4px}.grid{grid-template-columns:1fr}.card{min-height:0;padding:24px}.cta{align-items:stretch;flex-direction:column;padding:28px}.cta a{text-align:center}}
`;

const card = (article, archive = false) => `      <a class="card" href="${esc(relativeArticle(article, archive))}"><span class="tag">${esc(article.category || '資産形成')}</span><h3>${esc(article.title)}</h3><div class="meta"><time datetime="${esc(isoDate(article))}">${esc(displayDate(article))}</time><span class="read">読む →</span></div></a>`;
const monthNav = archive => monthKeys.map(month => `      <li><a href="${archive ? `../../${month.slice(0, 4)}/${month.slice(5)}/index.html` : `archive/${month.slice(0, 4)}/${month.slice(5)}/index.html`}">${label(month)} <span aria-label="記事数">（${byMonth.get(month).length}）</span></a></li>`).join('\n');

const shell = ({title, description, canonical, eyebrow, heading, lead, navHome, content}) => `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${esc(title)}</title>
  <meta name="description" content="${esc(description)}">
  <link rel="canonical" href="${esc(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="${esc(canonical)}">
  <meta property="og:title" content="${esc(title)}">
  <meta property="og:description" content="${esc(description)}">
  <meta property="og:site_name" content="未来投資navi">
  <script type="application/ld+json">${JSON.stringify({'@context':'https://schema.org','@type':'CollectionPage',name:title,url:canonical}).replaceAll('<', '\\u003c')}</script>
  <style>${styles}  </style>
</head>
<body>
  <header class="hero">
    <nav class="nav"><a class="brand" href="${navHome}">未来投資navi</a><a class="home" href="${navHome}">トップページへ</a></nav>
    <div class="hero-inner"><p class="eyebrow">${esc(eyebrow)}</p><h1>${heading}</h1><p class="lead">${esc(lead)}</p></div>
  </header>
  <main class="main">
${content}
    <aside class="cta"><div><h2>お金の悩みを、ひとりで抱えないために。</h2><p>未来投資naviでは、50代・60代の資産運用をわかりやすくサポートしています。</p></div><a href="${navHome}#contact">相談について見る</a></aside>
  </main>
</body>
</html>
`;

const indexSections = monthKeys.map(month => `    <section class="archive-section" id="month-${month}">
      <div class="archive-title"><h2>${label(month)}</h2><a href="archive/${month.slice(0, 4)}/${month.slice(5)}/index.html">この月の記事一覧 →</a></div>
      <div class="grid">
${byMonth.get(month).map(article => card(article)).join('\n')}
      </div>
    </section>`).join('\n\n');

const indexContent = `    <div class="section-head"><h2>年月から記事を探す</h2><p>全${articles.length}記事を掲載しています</p></div>
    <ul class="month-nav">
${monthNav(false)}
    </ul>
${indexSections}`;

fs.mkdirSync(path.join(outputRoot, 'blog'), {recursive: true});
fs.writeFileSync(path.join(outputRoot, 'blog/index.html'), shell({
  title: '記事一覧 | 未来投資navi',
  description: `未来投資naviの全${articles.length}記事を年月別に掲載。新NISA、退職金、資産形成、家計改善の記事を探せます。`,
  canonical: 'https://eva-solution.com/blog/',
  eyebrow: 'MIRAI INVESTMENT JOURNAL',
  heading: '知りたい記事を、<br>年月から探す。',
  lead: '新NISA、退職金、家計改善、資産形成の記事を、公開年月ごとにまとめました。',
  navHome: '../index.html',
  content: indexContent
}));

for (const month of monthKeys) {
  const [year, number] = month.split('-');
  const monthly = byMonth.get(month);
  const dir = path.join(outputRoot, 'blog/archive', year, number);
  fs.mkdirSync(dir, {recursive: true});
  const content = `    <a class="back" href="../../../index.html">← 全記事一覧へ戻る</a>
    <div class="section-head"><h2>${label(month)}の記事</h2><p>${monthly.length}件</p></div>
    <ul class="month-nav">
${monthNav(true)}
    </ul>
    <div class="grid">
${monthly.map(article => card(article, true)).join('\n')}
    </div>`;
  fs.writeFileSync(path.join(dir, 'index.html'), shell({
    title: `${label(month)}の記事一覧 | 未来投資navi`,
    description: `未来投資naviで${label(month)}に公開した${monthly.length}記事の一覧です。`,
    canonical: `https://eva-solution.com/blog/archive/${year}/${number}/`,
    eyebrow: 'MONTHLY ARCHIVE',
    heading: `${year}年${Number(number)}月<br>記事一覧`,
    lead: `${label(month)}に公開した記事をまとめています。`,
    navHome: '../../../../index.html',
    content
  }));
}

console.log(JSON.stringify({articles: articles.length, outputRoot, months: monthKeys.map(month => ({month, count: byMonth.get(month).length}))}, null, 2));
