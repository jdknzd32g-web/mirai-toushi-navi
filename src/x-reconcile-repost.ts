import 'dotenv/config';
import { TwitterApi } from 'twitter-api-v2';

function env(key: string): string {
  const value = process.env[key];
  if (!value) throw new Error(`Missing env: ${key}`);
  return value;
}

function arg(name: string): string {
  const index = process.argv.indexOf(name);
  const value = index >= 0 ? process.argv[index + 1] : undefined;
  if (!value) throw new Error(`Missing argument: ${name}`);
  return value;
}

function normalized(value: string): string {
  return value.replace(/\.html$/, '').replace(/\/$/, '');
}

async function main() {
  const oldId = arg('--old');
  const mainId = arg('--main');
  const replyId = arg('--reply');
  const expectedUrl = arg('--url');
  for (const id of [oldId, mainId, replyId]) {
    if (!/^\d+$/.test(id)) throw new Error(`Invalid X post ID: ${id}`);
  }

  const client = new TwitterApi({
    appKey: env('X_API_KEY'),
    appSecret: env('X_API_SECRET'),
    accessToken: env('X_ACCESS_TOKEN'),
    accessSecret: env('X_ACCESS_TOKEN_SECRET'),
  }).readWrite;

  const me = (await client.v2.me()).data;
  if (me.id !== '1703121550982234112' || me.username !== 'ryo20230917') {
    throw new Error('Unexpected X account');
  }

  const fields = { 'tweet.fields': ['author_id', 'entities', 'referenced_tweets'] as const };
  const [oldPost, mainPost, replyPost] = await Promise.all([
    client.v2.singleTweet(oldId, fields),
    client.v2.singleTweet(mainId, fields),
    client.v2.singleTweet(replyId, fields),
  ]);
  if (!mainPost.data) throw new Error(`New main post not readable: ${JSON.stringify(mainPost)}`);
  if (!replyPost.data) throw new Error(`New reply not readable: ${JSON.stringify(replyPost)}`);
  const hasUrl = (tweet: typeof oldPost.data) => tweet.entities?.urls?.some(
    item => normalized(item.expanded_url) === normalized(expectedUrl),
  );
  const oldAlreadyDeleted = !oldPost.data && oldPost.errors?.some(error => error.title === 'Not Found Error');
  if (!oldAlreadyDeleted && (!oldPost.data || oldPost.data.author_id !== me.id || !hasUrl(oldPost.data))) {
    throw new Error(`Old post verification failed: ${JSON.stringify(oldPost)}`);
  }
  if (mainPost.data.author_id !== me.id || hasUrl(mainPost.data)) throw new Error('New main post verification failed');
  if (replyPost.data.author_id !== me.id || !hasUrl(replyPost.data)) throw new Error('New reply URL verification failed');
  if (!replyPost.data.referenced_tweets?.some(item => item.type === 'replied_to' && item.id === mainId)) {
    throw new Error('New reply relationship verification failed');
  }

  if (!oldAlreadyDeleted) {
    const deleted = await client.v2.deleteTweet(oldId);
    if (!deleted.data.deleted) throw new Error('Old post deletion was not confirmed');
  }
  console.log(JSON.stringify({
    status: 'reconciled',
    deleted: `https://x.com/${me.username}/status/${oldId}`,
    old_already_deleted: oldAlreadyDeleted,
    main: `https://x.com/${me.username}/status/${mainId}`,
    reply: `https://x.com/${me.username}/status/${replyId}`,
  }));
}

main().catch(error => {
  console.error(error?.data || error?.message || error);
  process.exit(1);
});
