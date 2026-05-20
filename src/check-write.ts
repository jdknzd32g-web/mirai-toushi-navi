import 'dotenv/config';
import { TwitterApi } from 'twitter-api-v2';

async function main() {
  const client = new TwitterApi({
    appKey: process.env.X_API_KEY!,
    appSecret: process.env.X_API_SECRET!,
    accessToken: process.env.X_ACCESS_TOKEN!,
    accessSecret: process.env.X_ACCESS_TOKEN_SECRET!,
  });

  console.log('Testing text tweet posting...');
  try {
    const res = await client.readWrite.v2.tweet('Hello World! Testing API write permissions.');
    console.log('✓ Success! Tweet posted:', res.data.id);
  } catch (err: any) {
    console.error('✗ Failed to tweet:', err.message, err.data);
  }
}

main();
