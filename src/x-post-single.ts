#!/usr/bin/env -S node --enable-source-maps
/**
 * X 1本長文投稿スクリプト（未来投資navi 標準）
 *
 * 使い方:
 *   npx tsx src/x-post-single.ts --draft <path.md> [--image <path.jpg>] [--dry]
 *
 * Markdown フォーマット:
 *   - frontmatter (--- ... ---) はスキップ
 *   - ## 本文 セクション全体が1ツイート（`---` 区切りは使わない）
 *   - ## リプライ セクションは自己リプライとして投稿
 *   - 本文ツイートのみ画像を添付（--image で指定）
 *
 * 標準: 1本長文（1,200〜1,800字）+ リプライ1本
 * スレッド型（複数分割）は廃止（2026-05-22 ユーザーFB）
 */

import 'dotenv/config';
import { TwitterApi } from 'twitter-api-v2';
import * as fs from 'fs/promises';

type Args = {
  draft?: string;
  image?: string;
  imageOn?: 'main' | 'reply';
  dry?: boolean;
};

function parseArgs(): Args {
  const args: Args = { imageOn: 'main' };
  for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (a === '--draft') args.draft = process.argv[++i];
    else if (a === '--image') args.image = process.argv[++i];
    else if (a === '--image-on') {
      const v = process.argv[++i];
      if (v !== 'main' && v !== 'reply') {
        throw new Error(`--image-on は main または reply のみ指定可能（指定値: ${v}）`);
      }
      args.imageOn = v;
    }
    else if (a === '--image-reply') args.imageOn = 'reply';
    else if (a === '--dry' || a === '--dry-run') args.dry = true;
  }
  return args;
}

/**
 * Markdown から本文とリプライを抽出する
 * ## 本文 セクション全体を1ブロックとして返す（`---` 区切りは分割しない）
 */
function parseDraft(raw: string): { mainText: string; replyText: string | null } {
  // frontmatter 除去
  let body = raw;
  if (body.startsWith('---')) {
    const end = body.indexOf('\n---', 3);
    if (end !== -1) {
      body = body.slice(end + 4);
    }
  }

  const lines = body.split('\n');
  const sections: Record<string, string[]> = {};
  let currentSection = '__top__';
  for (const line of lines) {
    const hMatch = line.match(/^##\s+(.+)/);
    if (hMatch) {
      currentSection = hMatch[1].trim();
      sections[currentSection] = [];
    } else {
      if (!sections[currentSection]) sections[currentSection] = [];
      sections[currentSection].push(line);
    }
  }

  const mainLines = sections['本文'] ?? sections['__top__'] ?? [];
  const replyLines = sections['リプライ'] ?? null;

  const mainText = mainLines.join('\n').trim();
  const replyText = replyLines ? replyLines.join('\n').trim() : null;

  return {
    mainText,
    replyText: replyText && replyText.length > 0 ? replyText : null,
  };
}

/**
 * X の文字数カウント（URL は 23字固定換算）
 */
function countChars(text: string): number {
  const urlRegex = /https?:\/\/[^\s]+/g;
  let count = 0;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  while ((match = urlRegex.exec(text)) !== null) {
    count += match.index - lastIndex;
    count += 23;
    lastIndex = match.index + match[0].length;
  }
  count += text.length - lastIndex;
  return count;
}

function getMediaType(filename: string): string {
  const ext = filename.toLowerCase().split('.').pop();
  switch (ext) {
    case 'jpg':
    case 'jpeg':
      return 'image/jpeg';
    case 'png':
      return 'image/png';
    case 'gif':
      return 'image/gif';
    case 'webp':
      return 'image/webp';
    default:
      return 'image/jpeg';
  }
}

function env(key: string): string {
  const v = process.env[key];
  if (!v) throw new Error(`Missing env: ${key}`);
  return v;
}

async function main() {
  const parsed = parseArgs();
  const { draft, image: imageArg, dry } = parsed;
  // 【安全装置 / 恒久対策 2026-05-26】
  // 標準仕様: 画像は本文ツイートのみ。リプライには絶対に添付しない。
  // 過去に「リプにヘッダー画像が付く」との指摘が再発したため、ここで強制的に main 固定。
  // （※実測ではAPIレベルでリプに画像は付いていない＝スレッド表示UIの挙動。ただし将来の
  //   --image-reply 誤用による実添付を防ぐため、リプ画像の経路自体を無効化する。）
  let imageOn: 'main' | 'reply' = parsed.imageOn ?? 'main';
  if (imageOn === 'reply') {
    console.warn('⚠ リプライへの画像添付は標準仕様で禁止されています。本文ツイートに添付します（--image-reply / --image-on reply は無視されました）。');
    imageOn = 'main';
  }

  if (!draft) {
    console.error('Usage: npx tsx src/x-post-single.ts --draft <path.md> [--image <path.jpg>] [--dry]');
    process.exit(1);
  }

  const raw = await fs.readFile(draft, 'utf8');
  const { mainText, replyText } = parseDraft(raw);

  if (!mainText) {
    throw new Error('ドラフトから本文を抽出できませんでした。## 本文 セクションを確認してください。');
  }

  const mainLen = countChars(mainText);
  const replyLen = replyText ? countChars(replyText) : 0;

  // --- プレビュー出力 ---
  console.log('');
  console.log('='.repeat(60));
  console.log('  X 1本長文投稿プレビュー');
  console.log('='.repeat(60));
  console.log(`  ドラフト  : ${draft}`);
  console.log(`  画像添付  : ${imageArg ? `${imageArg} (→ ${imageOn === 'reply' ? 'リプライ' : '本文'})` : '(なし)'}`);
  console.log(`  モード    : ${dry ? 'DRY-RUN（投稿しません）' : '本投稿'}`);
  console.log('='.repeat(60));
  console.log('');
  // X Premium: 上限 25,000字。非Premiumは 280字。Premium前提で運用
  const lenNote = mainLen > 25000 ? ' ⚠ 25,000字超（X上限）' : mainLen > 280 ? ' ✓（Premiumで投稿可）' : ' ✓';
  const mainImgTag = imageArg && imageOn === 'main' ? '  [画像添付]' : '';
  console.log(`[本文]  ${mainLen}字${lenNote}${mainImgTag}`);
  console.log('-'.repeat(60));
  console.log(mainText);
  console.log('');

  if (replyText) {
    // リプライは標準仕様で常に画像なし（恒久対策）
    console.log(`[リプライ]  ${replyLen}字 ✓  （画像なし・標準仕様で固定）`);
    console.log('-'.repeat(60));
    console.log(replyText);
    console.log('');
  }

  if (dry) {
    console.log('--- dry-run 完了。本投稿は --dry フラグなしで実行してください。 ---');
    return;
  }

  // --- 本投稿 ---
  const client = new TwitterApi({
    appKey: env('X_API_KEY'),
    appSecret: env('X_API_SECRET'),
    accessToken: env('X_ACCESS_TOKEN'),
    accessSecret: env('X_ACCESS_TOKEN_SECRET'),
  });
  const rw = client.readWrite;

  // 画像アップロード（--image-on で本文 or リプライを選択）
  let mediaId: string | undefined;
  if (imageArg) {
    try {
      const imageBuffer = await fs.readFile(imageArg);
      mediaId = await rw.v1.uploadMedia(imageBuffer, {
        mimeType: getMediaType(imageArg),
      });
      console.log(`✓ 画像アップロード完了 (mediaId: ${mediaId}, 添付先: ${imageOn === 'reply' ? 'リプライ' : '本文'})`);
    } catch (err) {
      console.error('画像アップロード失敗:', err);
      throw err;
    }
  }

  // 本文ツイート投稿
  const mainParams: any = { text: mainText };
  if (mediaId && imageOn === 'main') {
    mainParams.media = { media_ids: [mediaId] };
  }
  const mainRes = await rw.v2.tweet(mainParams);
  const mainId = mainRes.data?.id;
  console.log(`✓ 本文投稿完了: https://x.com/i/web/status/${mainId}`);

  // リプライ投稿（あれば）
  // 【安全装置 / 恒久対策 2026-05-26】リプライには media を絶対に積まない。
  // media は本文ツイート(mainParams)のみ。ここで media を付けるコードは置かないこと。
  if (replyText && mainId) {
    const replyParams: any = {
      text: replyText,
      reply: { in_reply_to_tweet_id: mainId },
    };
    // ↑ replyParams に .media は付けない（リプ画像の経路を恒久的に廃止）
    const replyRes = await rw.v2.tweet(replyParams);
    const replyId = replyRes.data?.id;
    console.log(`✓ リプライ投稿完了（画像なし）: https://x.com/i/web/status/${replyId}`);
  }

  console.log('');
  console.log('投稿が完了しました。');
}

main().catch((err: any) => {
  const code = err?.code || err?.status || 'ERR';
  const body = err?.data || err?.errors || err?.response?.data;
  const bodyStr = body ? (typeof body === 'string' ? body : JSON.stringify(body)) : '';
  const msg = err?.message || String(err);
  process.stderr.write(`ERROR ${code}: ${msg}${bodyStr ? ' | ' + bodyStr : ''}\n`);
  process.exit(1);
});
