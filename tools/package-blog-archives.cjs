const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'dist/blog-archive-release');
const remotePath = path.join(out, 'remote-files.json');
const baselinePath = path.join(out, 'baseline.json');
if (!fs.existsSync(remotePath) || !fs.existsSync(baselinePath)) throw new Error('Run RELEASE_ARCHIVE=1 release.cjs inspect first');

const sourceFiles = [
  'blog/index.html',
  'blog/archive/2026/09/index.html',
  'blog/archive/2026/07/index.html',
  'blog/archive/2026/06/index.html',
  'blog/archive/2026/05/index.html',
  'blog/archive/2026/01/index.html',
  'blog/archive/2025/11/index.html',
  'blog/archive/2025/10/index.html',
  'blog/archive/2025/09/index.html',
  'blog/archive/2025/01/index.html'
];
const remote = JSON.parse(fs.readFileSync(remotePath, 'utf8'));
const site = path.join(out, 'site');
fs.mkdirSync(site, {recursive: true});
const hashes = {};
for (const name of sourceFiles) {
  const source = path.join(root, name);
  const target = path.join(site, name);
  if (!fs.existsSync(source)) throw new Error(`Missing source: ${name}`);
  fs.mkdirSync(path.dirname(target), {recursive: true});
  fs.copyFileSync(source, target);
  hashes[name] = crypto.createHash('sha1').update(fs.readFileSync(target)).digest('hex');
}
const index = fs.readFileSync(path.join(site, 'blog/index.html'), 'utf8');
if ((index.match(/class="card"/g) || []).length !== 113) throw new Error('All-article count must be 113');
if ((index.match(/href="archive\/\d{4}\/\d{2}\/index\.html"/g) || []).length < 9) throw new Error('Nine archive links required');

const changedExisting = sourceFiles.filter(name => remote.some(item => item.path === '/' + name));
const newFiles = sourceFiles.filter(name => !remote.some(item => item.path === '/' + name));
if (JSON.stringify(changedExisting) !== JSON.stringify(['blog/index.html'])) throw new Error(`Unexpected existing targets: ${changedExisting.join(', ')}`);
if (newFiles.length !== 9) throw new Error(`Expected nine new archive pages, got ${newFiles.length}`);

const manifest = {
  release_type: 'blog_archive',
  release_date: new Date().toISOString(),
  files: sourceFiles,
  changed_existing_files: changedExisting,
  new_files: newFiles,
  hashes
};
fs.writeFileSync(path.join(out, 'package.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify({status: 'pass', files: sourceFiles.length, changedExisting, newFiles}, null, 2));
