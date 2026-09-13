// Explicit posting of today's two non-SBI articles only; never scheduled.
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { TwitterApi } = require('twitter-api-v2');
const root = path.resolve(__dirname, '../..');
const client = new TwitterApi({appKey:process.env.X_API_KEY,appSecret:process.env.X_API_SECRET,accessToken:process.env.X_ACCESS_TOKEN,accessSecret:process.env.X_ACCESS_TOKEN_SECRET});
const plan = JSON.parse(fs.readFileSync(path.join(root, 'editorial/x-posts-2026-09-13.json')));
const logFile = path.join(root, 'editorial/x-post-results-2026-09-13.json');
const readLog = () => fs.existsSync(logFile) ? JSON.parse(fs.readFileSync(logFile)) : [];
const save = log => fs.writeFileSync(logFile, JSON.stringify(log, null, 2));
const norm = url => url.replace(/\.html$/, '').replace(/\/$/, '');
(async () => {
  const me = (await client.v2.me()).data;
  if (me.id !== '1703121550982234112' || me.username !== 'ryo20230917') throw Error('Unexpected X account');
  const timeline = await client.v2.userTimeline(me.id, {max_results:100, 'tweet.fields':['entities','created_at']});
  const recent = timeline.data.data || [];
  const log = readLog();
  for (const post of plan) {
    if (!post.url.startsWith('https://eva-solution.com/blog/life-planning/')) throw Error('Out-of-scope article');
    // Conservative bound: count every non-ASCII character as two; t.co URLs use 23.
    const weighted = [...post.text.replace(post.url, '')].reduce((n,c)=>n+(c.codePointAt(0)>127?2:1), 23);
    if (weighted > 280) throw Error('Post exceeds safe length');
    const existing = recent.find(t => t.entities?.urls?.some(u=>norm(u.expanded_url)===norm(post.url)));
    if (existing) { console.log(JSON.stringify({article:post.article,skipped_existing:existing.id})); continue; }
    if (log.some(x=>x.article===post.article)) throw Error('Prior posting attempt exists; inspect it before retrying');
    const page = await fetch(post.url);
    if (!page.ok || (await page.text()).includes('ローカル確認用・未公開')) throw Error('Article not publicly ready');
    if (!process.argv.includes('--send')) { console.log(JSON.stringify({account:me.username,weighted,text:post.text})); continue; }
    const record = {article:post.article,url:post.url,text:post.text,status:'sending',at:new Date().toISOString()};
    log.push(record); save(log);
    const tweet = await client.v2.tweet(post.text);
    record.id = tweet.data.id;
    record.post_url = 'https://x.com/' + me.username + '/status/' + record.id;
    record.status = 'posted'; save(log);
    const verified = await client.v2.singleTweet(record.id, {'tweet.fields':['author_id','entities']});
    if (verified.data.author_id !== me.id) throw Error('Post verification failed');
    record.status = 'verified'; save(log);
    console.log(JSON.stringify(record));
  }
})().catch(e=>{console.error(JSON.stringify({error:e.message,code:e.code,title:e.data?.title}));process.exitCode=1;});
