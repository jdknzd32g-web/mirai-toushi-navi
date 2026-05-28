import 'dotenv/config';
import { TwitterApi } from 'twitter-api-v2';

function env(k: string): string {
  const v = process.env[k];
  if (!v) throw new Error(`Missing env: ${k}`);
  return v;
}

async function main() {
  const client = new TwitterApi({
    appKey: env('X_API_KEY'),
    appSecret: env('X_API_SECRET'),
    accessToken: env('X_ACCESS_TOKEN'),
    accessSecret: env('X_ACCESS_TOKEN_SECRET'),
  });
  const me = await client.v2.me();
  console.log(`認証アカウント: @${me.data.username} (${me.data.name})`);
  const timeline = await client.v2.userTimeline(me.data.id, {
    max_results: 15,
    'tweet.fields': ['created_at', 'text'],
  });
  console.log('--- 直近ツイート ---');
  for (const t of timeline.data.data ?? []) {
    const first = t.text.split('\n')[0].slice(0, 50);
    console.log(`[${t.created_at}] ${first}`);
  }
}

main().catch((e) => {
  console.error('ERROR:', e?.data || e?.message || e);
  process.exit(1);
});
