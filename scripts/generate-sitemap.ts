#!/usr/bin/env tsx
/**
 * サイトマップ自動生成スクリプト
 *
 * blog/2025/ ディレクトリ内の全てのブログ記事を走査して、
 * sitemap.xml を完全に再生成します。
 */

import * as fs from 'fs/promises';
import * as path from 'path';

interface BlogPost {
  slug: string;
  htmlPath: string;
  imagePath?: string;
  title: string;
  lastmod: string;
}

async function getAllBlogPosts(projectRoot: string): Promise<BlogPost[]> {
  const blogDir = path.join(projectRoot, 'blog/2025');
  const posts: BlogPost[] = [];

  try {
    const entries = await fs.readdir(blogDir, { withFileTypes: true });

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;

      const slug = entry.name;
      const postDir = path.join(blogDir, slug);

      // HTMLファイルを探す
      const files = await fs.readdir(postDir);
      const htmlFile = files.find(f => f.endsWith('.html'));
      if (!htmlFile) continue;

      const htmlPath = path.join(postDir, htmlFile);

      // 画像ファイルを探す
      const imageFile = files.find(f => /\.(jpg|jpeg|png|webp)$/i.test(f));
      const imagePath = imageFile ? path.join(postDir, imageFile) : undefined;

      // HTMLファイルからタイトルを抽出
      const htmlContent = await fs.readFile(htmlPath, 'utf-8');
      const titleMatch = htmlContent.match(/<title>(.*?)<\/title>/);
      const title = titleMatch ? titleMatch[1].replace(' | 未来投資navi', '') : slug;

      // ファイルの最終更新日時を取得
      const stats = await fs.stat(htmlPath);
      const lastmod = stats.mtime.toISOString().split('T')[0];

      posts.push({
        slug,
        htmlPath,
        imagePath,
        title,
        lastmod
      });
    }
  } catch (err) {
    console.error('Error reading blog directory:', err);
  }

  // スラグ名でソート
  posts.sort((a, b) => a.slug.localeCompare(b.slug));

  return posts;
}

function generateSitemapXML(posts: BlogPost[]): string {
  const baseUrl = 'https://eva-solution.netlify.app';

  let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">

  <!-- Main Pages -->
  <url>
    <loc>${baseUrl}/</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>

  <url>
    <loc>${baseUrl}/blog/</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>

  <url>
    <loc>${baseUrl}/blog/category-nisa.html</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <url>
    <loc>${baseUrl}/blog/category-mutual-fund.html</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <url>
    <loc>${baseUrl}/blog/category-region.html</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Blog Posts -->
`;

  for (const post of posts) {
    const imageFileName = post.imagePath ? path.basename(post.imagePath) : '';

    xml += `  <url>
    <loc>${baseUrl}/blog/2025/${post.slug}/${post.slug}.html</loc>
    <lastmod>${post.lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>`;

    if (imageFileName) {
      xml += `
    <image:image>
      <image:loc>${baseUrl}/blog/2025/${post.slug}/${imageFileName}</image:loc>
      <image:title>${post.title}</image:title>
    </image:image>`;
    }

    xml += `
  </url>
`;
  }

  xml += `</urlset>
`;

  return xml;
}

async function main() {
  const projectRoot = path.join(process.cwd());

  console.log('🔍 ブログ記事を走査中...');
  const posts = await getAllBlogPosts(projectRoot);
  console.log(`✓ ${posts.length}件の記事を発見`);

  console.log('📝 sitemap.xmlを生成中...');
  const sitemapContent = generateSitemapXML(posts);

  const sitemapPath = path.join(projectRoot, 'sitemap.xml');
  await fs.writeFile(sitemapPath, sitemapContent, 'utf-8');

  console.log(`✓ sitemap.xmlを更新しました (${posts.length}件の記事)`);
  console.log(`   保存先: ${sitemapPath}`);
}

main().catch((err) => {
  console.error('エラー:', err);
  process.exit(1);
});
