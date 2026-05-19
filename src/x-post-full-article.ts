#!/usr/bin/env -S node --enable-source-maps
import 'dotenv/config';
import { TwitterApi } from 'twitter-api-v2';
import * as fs from 'fs/promises';
import * as path from 'path';

type Args = {
  file?: string;
  dry?: boolean;
};

function parseArgs(): Args {
  const args: Args = {};
  for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (a === '--file') args.file = process.argv[++i];
    else if (a === '--dry-run' || a === '--dry') args.dry = true;
  }
  return args;
}

async function main() {
  const { file: fileArg, dry } = parseArgs();

  if (!fileArg) {
    throw new Error('Please specify a file with --file <path>');
  }

  const html = await fs.readFile(fileArg, 'utf-8');

  // Extract Header Image
  let imagePath = '';
  const imgMatch = html.match(/<img[^>]+src="([^"]+)"[^>]*>/);
  if (imgMatch) {
    const src = imgMatch[1];
    imagePath = path.resolve(path.dirname(fileArg), src);
  }

  // Extract Article Body
  // Find the content between <h1> and the end of the article (before footer-cta)
  const h1Match = html.match(/<h1>(.*?)<\/h1>/);
  const title = h1Match ? h1Match[1] : '';

  let bodyHtml = html;
  const startIdx = html.indexOf('<h1>');
  const endIdx = html.indexOf('<div class="youtube-cta">'); // Skip CTAs for the post
  
  if (startIdx !== -1) {
    let contentStr = html.substring(startIdx, html.indexOf('</body>'));
    
    // Remove CTA blocks
    contentStr = contentStr.replace(/<div class="youtube-cta">[\s\S]*?<\/div>/g, '');
    contentStr = contentStr.replace(/<div class="line-cta">[\s\S]*?<\/div>/g, '');
    contentStr = contentStr.replace(/<div class="footer-cta">[\s\S]*?<\/div>/g, '');
    contentStr = contentStr.replace(/<div class="article-sub-image">[\s\S]*?<\/div>/g, '');
    
    // Replace <br> with newline
    contentStr = contentStr.replace(/<br\s*\/?>/gi, '\n');
    // Replace block tags with double newlines
    contentStr = contentStr.replace(/<\/p>/gi, '\n\n');
    contentStr = contentStr.replace(/<\/h[1-6]>/gi, '\n\n');
    
    // Remove all remaining HTML tags
    contentStr = contentStr.replace(/<[^>]+>/g, '');
    
    // Decode HTML entities
    contentStr = contentStr.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
    
    // Clean up whitespace (remove more than 3 consecutive newlines)
    contentStr = contentStr.replace(/\n{3,}/g, '\n\n');
    contentStr = contentStr.trim();
    
    bodyHtml = contentStr;
  }

  const text = bodyHtml;
  
  if (dry) {
    console.log('--- dry-run (x-post-full-article) ---');
    console.log(`file: ${fileArg}`);
    console.log(`image: ${imagePath}`);
    console.log(`length: ${text.length}`);
    console.log('\n' + text);
    return;
  }

  // OAuth 1.0a User Context
  const client = new TwitterApi({
    appKey: env('X_API_KEY'),
    appSecret: env('X_API_SECRET'),
    accessToken: env('X_ACCESS_TOKEN'),
    accessSecret: env('X_ACCESS_TOKEN_SECRET'),
  });
  const rw = client.readWrite;

  let mediaId: string | undefined;
  if (imagePath) {
    try {
      const imageBuffer = await fs.readFile(imagePath);
      mediaId = await rw.v1.uploadMedia(imageBuffer, {
        mimeType: getMediaType(imagePath)
      });
      console.log(`✓ 画像をアップロード: ${imagePath} (mediaId: ${mediaId})`);
    } catch (err) {
      console.error('画像のアップロードに失敗:', err);
      throw err;
    }
  }

  // ツイート投稿
  const tweetParams: any = { text };
  if (mediaId) {
    tweetParams.media = { media_ids: [mediaId] };
  }

  console.log('投稿中...');
  const res = await rw.v2.tweet(tweetParams);
  console.log(`OK posted: https://x.com/i/web/status/${res.data?.id}`);
}

function getMediaType(filename: string): string {
  const ext = filename.toLowerCase().split('.').pop();
  switch (ext) {
    case 'jpg':
    case 'jpeg': return 'image/jpeg';
    case 'png': return 'image/png';
    case 'gif': return 'image/gif';
    case 'webp': return 'image/webp';
    default: return 'image/jpeg';
  }
}

function env(key: string): string {
  const v = process.env[key];
  if (!v) throw new Error(`Missing env: ${key}. .envファイルを確認してください。`);
  return v;
}

main().catch((err: any) => {
  const code = err?.code || err?.status || 'ERR';
  const body = err?.data || err?.errors || err?.response?.data;
  const bodyStr = body ? (typeof body === 'string' ? body : JSON.stringify(body)) : '';
  const msg = err?.message || String(err);
  process.stderr.write(`ERROR ${code}: ${msg}${bodyStr ? ' | ' + bodyStr : ''}\n`);
  process.exit(1);
});
