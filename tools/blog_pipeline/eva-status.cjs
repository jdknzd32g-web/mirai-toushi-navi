// Read-only cross-project inventory. Never recurse into the home directory.
const fs = require('fs');
const path = require('path');
const base = '/Users/satoshioka';
const read = p => fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : null;
const repo = path.join(base, 'mirai-toushi-navi');
const governance = require('./eva-governance.cjs');
const folders = fs.readdirSync(base, {withFileTypes:true})
  .filter(e=>e.isDirectory() && !e.name.startsWith('.') && e.name !== 'Library')
  .map(e=>({name:e.name, inspected:false}));
const projects = ['eva-solution-ops','mirai-toushi-navi','youtube-project-share','youtube-project-share/channels/WAIZU'].map(name=>({name,path:path.join(base,name),...governance.classify(path.join(base,name)),exists:fs.existsSync(path.join(base,name)),git:fs.existsSync(path.join(base,name,'.git'))}));
const released = read(path.join(repo,'editorial/published-releases.json'));
const posts = [...(read(path.join(repo,'editorial/x-post-results-2026-09-13.json')) || []),...(read(path.join(repo,'editorial/x-published-results.json')) || [])];
console.log(JSON.stringify({at:new Date().toISOString(),scope:'Top-level folder names and allowlisted publication metadata only; not a full content audit',folders,projects,blog:{building:fs.existsSync(path.join(repo,'editorial/BUILD_IN_PROGRESS')),releases:released?.releases.map(r=>({date:r.date,status:r.status,deploy:r.deploy_id,urls:r.urls,drive_sync:r.drive_sync,source_sync:r.source_sync})),x:posts.map(p=>({article:p.article,status:p.status,url:p.post_url}))},excluded:['hidden directories','Library','credentials','customer data','financial records','private documents','media file contents']},null,2));
