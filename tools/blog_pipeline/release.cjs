// Explicit, one-off Netlify release. Reuses existing remote files by digest.
// Never uploads the repository, credentials, editorial data or preview tools.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../..');
const additional = process.env.RELEASE_BATCH === 'additional';
const daily = process.env.RELEASE_DATE;
const addonId = process.env.RELEASE_ARTICLE_ID;
const archive = process.env.RELEASE_ARCHIVE === '1';
if (daily && !/^\d{4}-\d{2}-\d{2}$/.test(daily)) throw Error('Invalid RELEASE_DATE');
if (addonId && !/^[a-z0-9-]+$/.test(addonId)) throw Error('Invalid RELEASE_ARTICLE_ID');
if ([daily, additional, addonId, archive].filter(Boolean).length > 1) throw Error('Choose only one release mode');
const out = path.join(root, archive ? 'dist/blog-archive-release' : daily ? 'dist/blog-release-' + daily : addonId ? 'dist/blog-release-addon-' + addonId : additional ? 'dist/blog-release-additional' : 'dist/blog-release');
const preview = path.join(root, 'dist/blog-preview/site');
const siteId = '2674e228-ed72-43a3-be06-05e8441e0823';
const origin = 'https://eva-solution.com';
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const hash = (data, algorithm = 'sha1') => crypto.createHash(algorithm).update(data).digest('hex');
const save = (name, data) => { fs.mkdirSync(path.dirname(path.join(out, name)), { recursive: true }); fs.writeFileSync(path.join(out, name), typeof data === 'string' || Buffer.isBuffer(data) ? data : JSON.stringify(data, null, 2)); };
async function api(endpoint, method = 'GET', body) {
  const config = read('/Users/satoshioka/Library/Preferences/netlify/config.json');
  const token = config.users[config.userId].auth.token;
  const binary = Buffer.isBuffer(body);
  const response = await fetch('https://api.netlify.com/api/v1' + endpoint, { method, redirect: 'error', signal: AbortSignal.timeout(60000), headers: { Authorization: 'Bearer ' + token, ...(body ? { 'Content-Type': binary ? 'application/octet-stream' : 'application/json' } : {}) }, body: body ? binary ? body : JSON.stringify(body) : undefined });
  if (!response.ok) throw Error(`Netlify ${method} ${endpoint}: HTTP ${response.status}`);
  return response.json();
}
async function current() {
  const site = await api('/sites/' + siteId);
  if (site.custom_domain !== 'eva-solution.com' || site.build_settings.repo_url !== 'https://github.com/jdknzd32g-web/mirai-toushi-navi') throw Error('Wrong destination');
  return site;
}
const targets = ['index.html', 'blog/index.html', 'sitemap.xml'];
async function inspect() {
  const site = await current();
  const published = await api('/deploys/' + site.published_deploy.id);
  const files = await api('/sites/' + siteId + '/files');
  if (!Array.isArray(files) || !files.length || files.some(f => f.deploy_id !== site.published_deploy.id)) throw Error('Mixed/empty remote inventory');
  save('remote-files.json', files);
  save('baseline.json', { siteId, origin, published: site.published_deploy.id });
  const report = [];
  for (const name of targets) {
    const response = await fetch(`https://${site.published_deploy.id}--eva-solution.netlify.app/${name}`);
    if (!response.ok) throw Error('Cannot read live ' + name);
    let bytes = Buffer.from(await response.arrayBuffer());
    const remote = files.find(f => f.path === '/' + name);
    // Netlify postprocessing may transform served HTML. Prefer the exact local
    // source only when its SHA1 is independently confirmed by the remote API.
    if (remote && fs.existsSync(path.join(root, name)) && hash(fs.readFileSync(path.join(root, name))) === remote.sha) bytes = fs.readFileSync(path.join(root, name));
    const prior = path.join(root, 'dist/blog-release/site', name);
    if (additional && remote && fs.existsSync(prior) && hash(fs.readFileSync(prior)) === remote.sha) bytes = fs.readFileSync(prior);
    if (daily || addonId || archive) {
      for (const release of read(path.join(root, 'editorial/published-releases.json')).releases) {
        const source = path.resolve(root, path.dirname(release.package), 'site', name);
        if (!source.startsWith(path.join(root, 'dist') + path.sep)) throw Error('Unsafe release source');
        if (remote && fs.existsSync(source) && hash(fs.readFileSync(source)) === remote.sha) bytes = fs.readFileSync(source);
      }
    }
    // A normal GitHub production deploy can supersede an API-published daily
    // release. Accept its exact source bytes only when Netlify identifies the
    // configured repository's main branch and the commit-pinned GitHub file
    // independently matches the remote inventory SHA1.
    if (remote && hash(bytes) !== remote.sha &&
        published.context === 'production' &&
        published.branch === 'main' &&
        /^[0-9a-f]{40}$/.test(published.commit_ref || '')) {
      const sourceUrl = `https://raw.githubusercontent.com/jdknzd32g-web/mirai-toushi-navi/${published.commit_ref}/${name}`;
      const sourceResponse = await fetch(sourceUrl, { redirect: 'error', signal: AbortSignal.timeout(60000) });
      if (sourceResponse.ok) {
        const sourceBytes = Buffer.from(await sourceResponse.arrayBuffer());
        if (hash(sourceBytes) === remote.sha) bytes = sourceBytes;
      }
    }
    if (!remote || hash(bytes) !== remote.sha) throw Error('Remote content hash mismatch: ' + name);
    save('baseline/' + name, bytes);
    report.push({ name, localMatches: fs.existsSync(path.join(root, name)) && hash(fs.readFileSync(path.join(root, name))) === remote.sha });
  }
  let releaseFiles = files;
  let recovery = null;
  if (published.context === 'production' &&
      published.branch === 'main' &&
      /^[0-9a-f]{40}$/.test(published.commit_ref || '')) {
    const ledger = read(path.join(root, 'editorial/published-releases.json'));
    const previous = ledger.releases.find(r => r.deploy_id !== published.id);
    const previousInventory = previous &&
      path.resolve(root, path.dirname(previous.package), 'remote-files.json');
    if (previousInventory &&
        previousInventory.startsWith(path.join(root, 'dist') + path.sep) &&
        fs.existsSync(previousInventory)) {
      const commitResponse = await fetch(
        `https://api.github.com/repos/jdknzd32g-web/mirai-toushi-navi/commits/${published.commit_ref}`,
        { redirect: 'error', signal: AbortSignal.timeout(60000), headers: { Accept: 'application/vnd.github+json' } }
      );
      if (!commitResponse.ok) throw Error('Cannot verify GitHub production commit');
      const commit = await commitResponse.json();
      if (commit.sha !== published.commit_ref || !Array.isArray(commit.files)) throw Error('Invalid GitHub commit metadata');
      const removed = new Set(commit.files.filter(f => f.status === 'removed').map(f => '/' + f.filename));
      const currentPaths = new Set(files.map(f => f.path));
      const previousFiles = read(previousInventory);
      if (!Array.isArray(previousFiles) || previousFiles.some(f => !f.path || !/^[0-9a-f]{40}$/.test(f.sha || ''))) {
        throw Error('Invalid previous verified inventory');
      }
      const recovered = previousFiles.filter(f => !currentPaths.has(f.path) && !removed.has(f.path));
      if (recovered.length) {
        releaseFiles = [...files, ...recovered];
        recovery = {
          current_deploy: published.id,
          current_commit: published.commit_ref,
          previous_verified_deploy: previous.deploy_id,
          current_files: files.length,
          recovered_files: recovered.length,
          explicit_commit_deletions_preserved: [...removed].sort(),
          release_files: releaseFiles.length
        };
      }
    }
  }
  save('release-files.json', releaseFiles);
  if (recovery) save('recovery.json', recovery);
  console.log(JSON.stringify({ baseline: site.published_deploy.id, files: files.length, releaseFiles: releaseFiles.length, recovery, targets: report }, null, 2));
}
async function draft() {
  const baseline = read(path.join(out, 'baseline.json'));
  if ((await current()).published_deploy.id !== baseline.published) throw Error('Live site changed');
  const releaseInventory = fs.existsSync(path.join(out, 'release-files.json')) ? 'release-files.json' : 'remote-files.json';
  const files = Object.fromEntries(read(path.join(out, releaseInventory)).map(f => [f.path, f.sha]));
  const manifest = read(path.join(out, 'package.json'));
  const local = {};
  for (const name of manifest.files) {
    const bytes = fs.readFileSync(path.join(out, 'site', name));
    if (hash(bytes) !== manifest.hashes[name]) throw Error('Package changed: ' + name);
    files['/' + name] = hash(bytes);
    local[hash(bytes)] = { name, bytes };
  }
  if (fs.existsSync(path.join(out, 'deploy.json'))) throw Error('Deploy already created; inspect it, do not duplicate');
  const deploy = await api('/sites/' + siteId + '/deploys', 'POST', { files, draft: true, title: archive ? 'Complete monthly blog archive' : daily ? 'Daily verified articles ' + daily : addonId ? 'Verified add-on article ' + addonId : additional ? 'Publish approved contact details and family account map articles' : 'Publish two approved articles: SBI checklist and cash reserve worksheet' });
  save('deploy.json', { id: deploy.id, url: deploy.deploy_ssl_url, previous: baseline.published });
  for (const sha of deploy.required || []) {
    if (!local[sha]) throw Error('Netlify requested an unchanged remote asset; refusing incomplete deploy');
    const item = local[sha];
    await api('/deploys/' + deploy.id + '/files/' + item.name.split('/').map(encodeURIComponent).join('/'), 'PUT', item.bytes);
  }
  console.log(JSON.stringify({ id: deploy.id, url: deploy.deploy_ssl_url, uploaded: deploy.required.length }));
}
async function status() {
  const saved = read(path.join(out, 'deploy.json'));
  const deploy = await api('/deploys/' + saved.id);
  console.log(JSON.stringify({ id: deploy.id, state: deploy.state, url: deploy.deploy_ssl_url, error: deploy.error_message }));
}
async function publish() {
  const saved = read(path.join(out, 'deploy.json'));
  const verified = read(path.join(out, 'verified.json'));
  if (verified.deploy !== saved.id || verified.status !== 'pass') throw Error('Release not verified');
  const site = await current();
  if (![saved.previous, saved.id].includes(site.published_deploy.id)) throw Error('Concurrent live change; do not overwrite');
  if ((await api('/deploys/' + saved.id)).state !== 'ready') throw Error('Deploy not ready');
  if (site.published_deploy.id !== saved.id) await api('/sites/' + siteId + '/deploys/' + saved.id + '/restore', 'POST');
  if ((await current()).published_deploy.id !== saved.id) throw Error('Publication not confirmed');
  if (daily || addonId) {
    const manifest = read(path.join(out, 'package.json'));
    const expected = addonId ? 1 : 2;
    if (!Array.isArray(manifest.article_ids) || manifest.article_ids.length !== expected || (addonId && manifest.article_ids[0] !== addonId)) throw Error('Missing article IDs');
    const ledgerPath = path.join(root, 'editorial/published-releases.json');
    const ledger = read(ledgerPath);
    if (!ledger.releases.some(r=>r.deploy_id === saved.id)) {
      ledger.releases.unshift({date:manifest.release_date || daily,status:'published',release_type:addonId?'addon':'daily',deploy_id:saved.id,previous_deploy_id:saved.previous,origin,articles:manifest.article_ids,urls:manifest.articles.map(n=>origin+'/'+n),package:path.relative(root,path.join(out,'package.json')),source_sync:'not_promoted_to_git_checkout',drive_sync:'prepublication_verified',...(process.env.RELEASE_NO_SNS === '1' ? {no_sns:true} : {})});
      fs.writeFileSync(ledgerPath, JSON.stringify(ledger, null, 2));
    }
  }
  console.log(JSON.stringify({ published: saved.id, expected: saved.id, origin }));
}
({ inspect, draft, status, publish }[process.argv[2]] || (() => { throw Error('Choose inspect, draft, status or publish'); }))().catch(e => { console.error(e.message); process.exitCode = 1; });
