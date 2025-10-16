#!/usr/bin/env -S node --enable-source-maps
import 'dotenv/config';
import { findCandidateFiles, listContentRoots, readText } from './lib/fs.js';
import { extract, clampLen } from './lib/text.js';
import { buildPost } from './lib/style.js';
import { readPosted } from './lib/queue.js';
import { tooSimilar } from './lib/dedupe.js';

type Args = { slot?: string; root?: string; file?: string };
function parseArgs(): Args {
  const args: Args = {};
  for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (a === '--slot') args.slot = process.argv[++i];
    else if (a === '--root') args.root = process.argv[++i];
    else if (a === '--file') args.file = process.argv[++i];
  }
  return args;
}

async function main() {
  const { slot, root, file: fileArg } = parseArgs();
  let file: string;
  if (fileArg) {
    file = fileArg;
  } else {
    const roots = await listContentRoots(root);
    if (!roots.length) {
      console.error('No content roots found');
      process.exit(1);
    }
    // Pick first root with files
    let files: string[] = [];
    for (const r of roots) {
      const cand = await findCandidateFiles(r);
      if (cand.length) { files = cand.map(c => c.file); break; }
    }
    if (!files.length) {
      console.error('No candidate files (.md|.mdx|.txt)');
      process.exit(1);
    }
    // Take newest
    file = files[0];
  }
  const raw = await readText(file);
  const { topic, point } = extract(raw);
  const hashtags = suggestTags(raw);
  const { text, len } = buildPost(topic, point, { hashtags });

  const posted = await readPosted();
  const similar = tooSimilar(text, posted.posted, 0.85);

  const { ok } = clampLen(text);
  if (!ok) {
    console.error(`[INVALID] text length out of 130-140: ${len}`);
    process.exit(1);
  }

  // Output draft
  console.log('--- dry-run ---');
  if (slot) console.log(`slot: ${slot}`);
  console.log(`file: ${file}`);
  console.log(`length: ${len}`);
  console.log(`similar(>=0.85 within history): ${similar}`);
  console.log('\n' + text);
}

function suggestTags(src: string): string[] {
  const tags: string[] = [];
  const s = src.toLowerCase();
  if (/(nisa|新nisa)/i.test(s)) tags.push('新NISA');
  if (/(資産|積立|投資)/.test(s)) tags.push('資産運用');
  return tags.slice(0, 2);
}

main().catch(err => {
  console.error(`ERR: ${err?.message || String(err)}`);
  process.exit(1);
});
