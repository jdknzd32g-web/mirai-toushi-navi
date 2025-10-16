#!/usr/bin/env -S node --enable-source-maps
import 'dotenv/config';
import { TwitterApi } from 'twitter-api-v2';

async function main() {
  const client = new TwitterApi({
    appKey: env('X_API_KEY'),
    appSecret: env('X_API_SECRET'),
    accessToken: env('X_ACCESS_TOKEN'),
    accessSecret: env('X_ACCESS_TOKEN_SECRET'),
  });
  const rw = client.readWrite;

  // Verify user context
  const me = await rw.v2.me();
  console.log('Authenticated as:', me.data);

  console.log('Ready to tweet via OAuth 1.0a user context.');
}

function env(key: string): string {
  const v = process.env[key];
  if (!v) throw new Error(`Missing env: ${key}`);
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

