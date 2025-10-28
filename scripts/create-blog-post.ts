#!/usr/bin/env tsx
/**
 * ブログ記事自動生成スクリプト
 *
 * 使い方:
 * tsx scripts/create-blog-post.ts --text ~/Desktop/テキストファイル.txt --image ~/Desktop/画像.jpg --slug region3
 *
 * オプション:
 * --text: テキストファイルのパス（必須）
 * --image: 画像ファイルのパス（必須）
 * --slug: 記事のスラッグ（ディレクトリ名とファイル名に使用）（必須）
 * --category: カテゴリー（デフォルト: region）
 */

import * as fs from 'fs/promises';
import * as path from 'path';

interface Args {
  text?: string;
  image?: string;
  slug?: string;
  category?: string;
}

function parseArgs(): Args {
  const args: Args = { category: 'region' };
  for (let i = 2; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg === '--text') args.text = process.argv[++i];
    else if (arg === '--image') args.image = process.argv[++i];
    else if (arg === '--slug') args.slug = process.argv[++i];
    else if (arg === '--category') args.category = process.argv[++i];
  }
  return args;
}

async function main() {
  const { text: textPath, image: imagePath, slug, category } = parseArgs();

  if (!textPath || !imagePath || !slug) {
    console.error('エラー: --text, --image, --slug は必須です');
    process.exit(1);
  }

  const projectRoot = path.join(process.cwd());
  const blogDir = path.join(projectRoot, 'blog/2025', slug);
  const imageExt = path.extname(imagePath);
  const imageName = `${slug}-image${imageExt}`;

  // 1. ディレクトリを作成
  await fs.mkdir(blogDir, { recursive: true });
  console.log(`✓ ディレクトリを作成: ${blogDir}`);

  // 2. 画像をコピー
  await fs.copyFile(imagePath, path.join(blogDir, imageName));
  console.log(`✓ 画像をコピー: ${imageName}`);

  // 3. テキストファイルを読み込む
  const textContent = await fs.readFile(textPath, 'utf-8');

  // 4. タイトルとdescriptionを抽出（# で始まる最初の行をタイトルとする）
  const lines = textContent.split('\n');
  const titleLine = lines.find(l => l.startsWith('# '));
  const title = titleLine ? titleLine.replace(/^#\s*/, '') : slug;

  // 最初の段落をdescriptionとする（空行までの連続した行）
  let description = '';
  let foundTitle = false;
  for (const line of lines) {
    if (line.startsWith('# ')) {
      foundTitle = true;
      continue;
    }
    if (foundTitle && line.trim() && !line.startsWith('#') && !line.startsWith('<')) {
      description += line.trim() + ' ';
      if (description.length > 150) break;
    }
  }
  description = description.slice(0, 200);

  // 5. HTMLファイルを生成
  const html = generateHTML(title, description, textContent, slug, imageName, category);
  await fs.writeFile(path.join(blogDir, `${slug}.html`), html);
  console.log(`✓ HTMLファイルを生成: ${slug}.html`);

  // 6. category-region.htmlを更新
  await updateCategoryPage(projectRoot, slug, title, description, category);
  console.log(`✓ category-${category}.htmlを更新`);

  // 7. blog/index.htmlを更新
  await updateBlogIndex(projectRoot, slug, title, description, imageName, category);
  console.log(`✓ blog/index.htmlを更新`);

  // 8. sitemap.xmlを更新
  await updateSitemap(projectRoot, slug, imageName, title, category);
  console.log(`✓ sitemap.xmlを更新`);

  console.log('\n🎉 ブログ記事の作成が完了しました！');
}

function generateHTML(title: string, description: string, content: string, slug: string, imageName: string, category: string): string {
  const today = new Date().toISOString().split('T')[0];
  const todayJP = today.replace(/-/g, '.');

  // Markdownから本文HTMLを生成（簡易的な変換）
  let bodyHTML = content
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/^## (.+)$/gm, '<h2>$2</h2>')
    .replace(/^### (.+)$/gm, '<h3>$3</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .split('\n')
    .filter(line => !line.startsWith('#'))
    .map(line => line.trim() ? (line.startsWith('<') ? line : `<p>${line}</p>`) : '')
    .join('\n');

  const categoryLabel = category === 'region' ? '地域別資産運用' : category === 'nisa' ? '新NISA' : '投資信託';

  return `<!DOCTYPE html>
<html lang="ja">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-K4EG9Q6FL6"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-K4EG9Q6FL6');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} | 未来投資navi</title>
    <meta name="description" content="${description}">
    <link rel="canonical" href="https://eva-solution.netlify.app/blog/2025/${slug}/${slug}.html">

    <!-- OGP -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://eva-solution.netlify.app/blog/2025/${slug}/${slug}.html">
    <meta property="og:title" content="${title} | 未来投資navi">
    <meta property="og:description" content="${description}">
    <meta property="og:image" content="https://eva-solution.netlify.app/blog/2025/${slug}/${imageName}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="${title}">
    <meta property="og:site_name" content="未来投資navi">
    <meta property="article:published_time" content="${today}T00:00:00+09:00">
    <meta property="article:author" content="りょう">
    <meta property="article:section" content="${categoryLabel}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@investment_navi">
    <meta name="twitter:creator" content="@investment_navi">
    <meta name="twitter:title" content="${title}">
    <meta name="twitter:description" content="${description}">
    <meta name="twitter:image" content="https://eva-solution.netlify.app/blog/2025/${slug}/${imageName}">
    <meta name="twitter:image:alt" content="${title}">

    <!-- 構造化データ (JSON-LD) -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "${title}",
      "description": "${description}",
      "image": "https://eva-solution.netlify.app/blog/2025/${slug}/${imageName}",
      "author": {
        "@type": "Person",
        "name": "りょう"
      },
      "publisher": {
        "@type": "Organization",
        "name": "未来投資navi",
        "logo": {
          "@type": "ImageObject",
          "url": "https://eva-solution.netlify.app/images/logo.png"
        }
      },
      "datePublished": "${today}",
      "dateModified": "${today}",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://eva-solution.netlify.app/blog/2025/${slug}/${slug}.html"
      }
    }
    </script>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f8f9fa;
        }

        .header {
            background: white;
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        }

        .back-btn {
            background: #667eea;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 14px;
            transition: all 0.3s;
        }

        .back-btn:hover {
            background: #5569d0;
            transform: translateY(-2px);
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            margin-top: 20px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.05);
        }

        .article-meta {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }

        .category {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .date {
            color: #999;
            font-size: 14px;
        }

        h1 {
            font-size: 28px;
            color: #2c3e50;
            margin-bottom: 20px;
            line-height: 1.4;
        }

        h2 {
            font-size: 22px;
            color: #667eea;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }

        h3 {
            font-size: 18px;
            color: #764ba2;
            margin: 30px 0 15px 0;
        }

        p {
            margin-bottom: 20px;
            line-height: 1.8;
        }

        ul, ol {
            margin: 20px 0;
            padding-left: 30px;
        }

        li {
            margin-bottom: 10px;
            line-height: 1.7;
        }

        .highlight {
            background: linear-gradient(transparent 70%, #fff59d 70%);
            font-weight: bold;
            padding: 2px 4px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }

            h1 {
                font-size: 24px;
            }

            h2 {
                font-size: 20px;
            }

            .header-content {
                flex-direction: column;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">eva solution</div>
            <a href="../../../index.html" class="back-btn">トップページへ戻る</a>
        </div>
    </header>

    <div class="container">
        <!-- ヘッダー画像 -->
        <div class="article-header-image" style="
                margin: -40px -40px 30px -40px;
                border-radius: 12px 12px 0 0;
                overflow: hidden;
        ">
            <img src="${imageName}"
            alt="${title}"
            style="width: 100%; height: auto; display: block;"
            width="1200" height="630" loading="eager" decoding="async">
        </div>

        <div class="article-meta">
            <span class="category">${categoryLabel}</span>
            <div class="date">${todayJP}</div>
        </div>

        ${bodyHTML}
    </div>
</body>
</html>
`;
}

async function updateCategoryPage(projectRoot: string, slug: string, title: string, description: string, category: string) {
  const categoryFile = path.join(projectRoot, `blog/category-${category}.html`);
  let content = await fs.readFile(categoryFile, 'utf-8');

  const newCard = `            <!-- 記事: ${slug} -->
            <article class="article-card" onclick="location.href='2025/${slug}/${slug}.html'">
                <div class="article-meta">
                    <span class="article-date">${new Date().toISOString().split('T')[0].replace(/-/g, '.')}<span class="new-badge">NEW</span></span>
                    <span class="article-level level-beginner">初心者向け</span>
                </div>
                <h2 class="article-title">${title}</h2>
                <p class="article-description">
                    ${description}
                </p>
                <div class="article-tags">
                    <span class="tag">${category}</span>
                </div>
                <div class="read-more">続きを読む →</div>
            </article>

`;

  // 最初の記事の前に挿入
  content = content.replace(/(<!-- 記事1:)/g, newCard + '$1');

  await fs.writeFile(categoryFile, content);
}

async function updateBlogIndex(projectRoot: string, slug: string, title: string, description: string, imageName: string, category: string) {
  const indexFile = path.join(projectRoot, 'blog/index.html');
  let content = await fs.readFile(indexFile, 'utf-8');

  const categoryLabel = category === 'region' ? '地域別資産運用' : category === 'nisa' ? '新NISA' : '投資信託';
  const categoryComment = category === 'region' ? '<!-- 地域別資産運用 系 -->' : category === 'nisa' ? '<!-- NISA 系（日付降順） -->' : '<!-- 投資信託 系 -->';

  const newCard = `      <a class="card" href="2025/${slug}/${slug}.html">
        <img class="thumb" src="2025/${slug}/${imageName}" alt="${title}" loading="lazy" decoding="async">
        <div class="card-body">
          <h3 class="card-title">${title}</h3>
          <p class="card-desc">${description}</p>
        </div>
      </a>

`;

  // カテゴリーコメントの直後に挿入
  content = content.replace(new RegExp(`(${categoryComment}\\n)`), `$1${newCard}`);

  await fs.writeFile(indexFile, content);
}

async function updateSitemap(projectRoot: string, slug: string, imageName: string, title: string, category: string) {
  const sitemapFile = path.join(projectRoot, 'sitemap.xml');
  let content = await fs.readFile(sitemapFile, 'utf-8');

  const today = new Date().toISOString().split('T')[0];

  const newEntry = `  <url>
    <loc>https://eva-solution.netlify.app/blog/2025/${slug}/${slug}.html</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <image:image>
      <image:loc>https://eva-solution.netlify.app/blog/2025/${slug}/${imageName}</image:loc>
      <image:title>${title}</image:title>
    </image:image>
  </url>
`;

  // </urlset>の直前に挿入
  content = content.replace('</urlset>', newEntry + '</urlset>');

  await fs.writeFile(sitemapFile, content);
}

main().catch((err) => {
  console.error('エラー:', err);
  process.exit(1);
});
