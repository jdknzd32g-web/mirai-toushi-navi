#!/usr/bin/env -S node --enable-source-maps
import 'dotenv/config';
import { TwitterApi } from 'twitter-api-v2';
import { findCandidateFiles, listContentRoots, readText } from './lib/fs.js';
import { extract } from './lib/text.js';
import { buildPost } from './lib/style.js';
import { appendPosted, readPosted } from './lib/queue.js';
import { signature, tooSimilar } from './lib/dedupe.js';

type Args = { slot?: string; root?: string; dry?: boolean; file?: string; force?: boolean };
function parseArgs(): Args {
  const args: Args = {};
  for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (a === '--slot') args.slot = process.argv[++i];
    else if (a === '--root') args.root = process.argv[++i];
    else if (a === '--dry-run' || a === '--dry') args.dry = true;
    else if (a === '--file') args.file = process.argv[++i];
    else if (a === '--force') args.force = true;
  }
  return args;
}

async function main() {
  const { slot, root, dry, file: fileArg, force } = parseArgs();

  let file: string;
  if (fileArg) {
    file = fileArg;
  } else {
    const roots = await listContentRoots(root);
    if (!roots.length) throw new Error('No content roots found');
    let files: string[] = [];
    for (const r of roots) {
      const cand = await findCandidateFiles(r);
      if (cand.length) { files = cand.map(c => c.file); break; }
    }
    if (!files.length) throw new Error('No candidate files (.md|.mdx|.txt)');
    file = files[0];
  }
  const raw = await readText(file);
  const { topic, point } = extract(raw);
  const hashtags = suggestTags(raw);
  const { text, len } = buildPost(topic, point, { hashtags });

  const posted = await readPosted();
  const isSimilar = tooSimilar(text, posted.posted, 0.85);
  if (isSimilar && !force) throw new Error('Too similar to a recent post (<=60 days)');

  if (dry) {
    console.log('--- dry-run (x-post) ---');
    if (slot) console.log(`slot: ${slot}`);
    console.log(`file: ${file}`);
    console.log(`length: ${len}`);
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
  const res = await rw.v2.tweet(text);

  const sig = signature(text);
  await appendPosted({ date: new Date().toISOString(), file, text, sig });

  console.log(`OK posted: https://x.com/i/web/status/${res.data?.id}`);
}

function suggestTags(src: string): string[] {
  const tags: string[] = [];
  const s = src.toLowerCase();
  if (/(nisa|新nisa)/i.test(s)) tags.push('新NISA');
  if (/(資産|積立|投資)/.test(s)) tags.push('資産運用');
  return tags.slice(0, 2);
}

function env(key: string): string {
  const v = process.env[key];
  if (!v) throw new Error(`Missing env: ${key}`);
  return v;
}

main().catch((err: any) => {
  // Enhanced diagnostics on failure
  const code = err?.code || err?.status || 'ERR';
  const body = err?.data || err?.errors || err?.response?.data;
  const bodyStr = body ? (typeof body === 'string' ? body : JSON.stringify(body)) : '';
  const msg = err?.message || String(err);
  process.stderr.write(`ERROR ${code}: ${msg}${bodyStr ? ' | ' + bodyStr : ''}\n`);
  process.exit(1);
});
