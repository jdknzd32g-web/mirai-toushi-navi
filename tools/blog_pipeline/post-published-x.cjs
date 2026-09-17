// Post only verified production releases. No deploy authority is granted here.
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '../..');
const origin = 'https://eva-solution.com';
const norm = value => value.replace(/\.html$/, '').replace(/\/$/, '');
const eligible = a => !/sbi|ＳＢＩ/i.test([a.path, a.title, a.category].join(' '));
function compose(a) {
  const budget = 275;
  let summary = '', count = 0;
  for (const c of a.description || a.title) {
    const size = c.codePointAt(0) > 127 ? 2 : 1;
    if (count + size > budget) { summary += '…'; break; }
    summary += c; count += size;
  }
  return summary;
}
function composeReply(a) { return origin + '/' + a.path; }
async function run() {
  require('dotenv').config({path:path.join(root, '.env')});
  const {TwitterApi} = require('twitter-api-v2');
  const send = process.argv.includes('--send');
  const ledger = path.join(root, 'editorial/x-published-results.json');
  const lock = path.join(root, 'editorial/x-published.lock');
  const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
  const records = fs.existsSync(ledger) ? read(ledger) : [];
  const oldLog = path.join(root, 'editorial/x-post-results-2026-09-13.json');
  const prior = fs.existsSync(oldLog) ? read(oldLog) : [];
  const releases = read(path.join(root, 'editorial/published-releases.json')).releases;
  // An exclusive persistent lock prevents overlapping scheduled/manual senders.
  // A crashed process leaves the lock for explicit reconciliation, never blind retry.
  let locked = false;
  try {
    if (send) { fs.writeFileSync(lock, String(process.pid), {flag:'wx'}); locked = true; }
    const jobs = [];
    for (const release of releases) {
      if (release.status !== 'published') continue;
      const dir = path.dirname(path.resolve(root, release.package));
      if (!dir.startsWith(path.join(root, 'dist') + path.sep)) throw Error('Invalid release directory');
      const reportPath = path.join(dir, 'production-verified.json');
      if (!fs.existsSync(reportPath)) continue;
      const report = read(reportPath);
      if (report.status !== 'pass' || report.base !== origin || report.deploy !== release.deploy_id || report.errors.length) continue;
      for (const id of release.articles) {
        if (!/^[a-z0-9-]+$/.test(id)) throw Error('Invalid article id');
        const a = read(path.join(root, 'editorial/articles', id + '.json'));
        if (!eligible(a)) continue;
        if (!/^blog\/[a-z0-9_/-]+\.html$/.test(a.path) || a.path.includes('..')) throw Error('Invalid article path');
        const url = origin + '/' + a.path;
        if (!release.urls.includes(url)) throw Error('Article is not in published release');
        if (!report.checks.some(c=>c.page === a.path && c.status === 'pass')) throw Error('Article was not verified');
        const previous = [...prior, ...records].find(r=>r.article === id || norm(r.url) === norm(url));
        if (previous) {
          if (!['verified','skipped_existing'].includes(previous.status)) throw Error('Uncertain previous posting: ' + id);
          continue;
        }
        if (!jobs.some(j=>j.article === id)) jobs.push({article:id, url, text:compose(a), reply_text:composeReply(a)});
      }
    }
    if (!jobs.length) { console.log(JSON.stringify({status:'no_pending_posts'})); return; }
    const client = new TwitterApi({appKey:process.env.X_API_KEY,appSecret:process.env.X_API_SECRET,accessToken:process.env.X_ACCESS_TOKEN,accessSecret:process.env.X_ACCESS_TOKEN_SECRET});
    const me = (await client.v2.me()).data;
    if (me.id !== '1703121550982234112' || me.username !== 'ryo20230917') throw Error('Unexpected X account');
    const timeline = await client.v2.userTimeline(me.id, {max_results:100,'tweet.fields':['entities']});
    const save = () => fs.writeFileSync(ledger, JSON.stringify(records, null, 2));
    for (const job of jobs) {
      const found = (timeline.data.data || []).find(t=>t.entities?.urls?.some(u=>norm(u.expanded_url) === norm(job.url)));
      if (found) {
        if (send) { records.push({...job,status:'skipped_existing',id:found.id}); save(); }
        continue;
      }
      const page = await fetch(job.url, {signal:AbortSignal.timeout(30000)});
      const html = await page.text();
      if (!page.ok || new URL(page.url).origin !== origin || /noindex/i.test(page.headers.get('x-robots-tag') || '') || /ローカル確認用・未公開|noindex/i.test(html)) throw Error('Article is not publicly ready');
      if (!send) { console.log(JSON.stringify({status:'dry_run',...job})); continue; }
      const record = {...job,status:'sending',at:new Date().toISOString()};
      records.push(record); save();
      const posted = await client.v2.tweet(job.text);
      record.id = posted.data.id; record.post_url = 'https://x.com/' + me.username + '/status/' + record.id;
      record.status = 'main_posted'; save();
      const replied = await client.v2.tweet({text:job.reply_text,reply:{in_reply_to_tweet_id:record.id}});
      record.reply_id = replied.data.id;
      record.reply_url = 'https://x.com/' + me.username + '/status/' + record.reply_id;
      record.status = 'posted'; save();
      const verifiedMain = (await client.v2.singleTweet(record.id, {'tweet.fields':['author_id','entities']})).data;
      const verifiedReply = (await client.v2.singleTweet(record.reply_id, {'tweet.fields':['author_id','entities','referenced_tweets']})).data;
      if (verifiedMain.author_id !== me.id || verifiedMain.entities?.urls?.some(u=>norm(u.expanded_url) === norm(job.url))) throw Error('Main post readback mismatch');
      if (verifiedReply.author_id !== me.id || !verifiedReply.entities?.urls?.some(u=>norm(u.expanded_url) === norm(job.url)) || !verifiedReply.referenced_tweets?.some(t=>t.type === 'replied_to' && t.id === record.id)) throw Error('Reply readback mismatch');
      record.status = 'verified'; save();
      console.log(JSON.stringify(record));
    }
  } finally { if (locked) fs.unlinkSync(lock); }
}
module.exports = {eligible, compose, composeReply, norm};
if (require.main === module) run().catch(e=>{console.error(JSON.stringify({error:e.message}));process.exitCode=1;});
