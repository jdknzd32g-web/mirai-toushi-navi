"""Prepare only explicitly approved articles and narrowly scoped discovery edits."""
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import pipeline as p
import quality

ADDITIONAL = os.environ.get('RELEASE_BATCH') == 'additional'
DAILY = os.environ.get('RELEASE_DATE')
ADDON_ID = os.environ.get('RELEASE_ARTICLE_ID')
if DAILY and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', DAILY):
  raise ValueError('Invalid RELEASE_DATE')
if ADDON_ID and not re.fullmatch(r'[a-z0-9-]+', ADDON_ID):
  raise ValueError('Invalid RELEASE_ARTICLE_ID')
if sum(bool(value) for value in [DAILY, ADDITIONAL, ADDON_ID]) > 1:
  raise ValueError('Choose only one release mode')
OUT = p.ROOT / ('dist/blog-release-' + DAILY if DAILY else 'dist/blog-release-addon-' + ADDON_ID if ADDON_ID else 'dist/blog-release-additional' if ADDITIONAL else 'dist/blog-release')
SITE = OUT / 'site'
TARGETS = ({'2026-09-13-sbi-contact-details-check', '2026-09-13-family-account-map'} if ADDITIONAL else {'2026-09-13-sbi-first-order-checklist', '2026-09-13-cash-reserve-worksheet'})

def main():
  if not quality.check():
    raise ValueError('Preview gates did not pass')
  articles = [a for a in p.articles() if a['id'] in TARGETS]
  if ADDON_ID:
    articles = [a for a in p.articles() if a['id'] == ADDON_ID]
    if len(articles) != 1:
      raise ValueError('Add-on release requires exactly one explicit article')
  elif DAILY:
    articles = [a for a in p.articles() if a['date'] == DAILY]
    if len(articles) != 2 or sum(bool(re.search(r'sbi|ＳＢＩ', a['path'] + a['title'] + a['category'], re.I)) for a in articles) != 1:
      raise ValueError('Daily release requires exactly one SBI and one non-SBI article')
  elif {a['id'] for a in articles} != TARGETS:
    raise ValueError('Two approved articles required')
  inventory = OUT / 'release-files.json'
  if not inventory.exists():
    inventory = OUT / 'remote-files.json'
  remote = {f['path'].lstrip('/'): f['sha'] for f in p.read(inventory)}
  package = {}
  def add(name, content):
    if name.startswith(('/', '.')) or '..' in Path(name).parts:
      raise ValueError('Unsafe output path')
    package[name] = content.encode() if isinstance(content, str) else content
  for a in articles:
    if a['path'] in remote:
      raise ValueError('Target already published; review before replacing')
    rendered = (p.SITE / a['path']).read_text()
    rendered = rendered.replace('<meta name="robots" content="noindex,nofollow">', '<meta name="robots" content="index,follow">')
    rendered = rendered.replace('  <div class="bp-preview">ローカル確認用・未公開</div>\n', '')
    publication_date = a.get('publication_date', a['date'])
    checked_date = a.get('checked_date', a['date'])
    for value in (publication_date, checked_date):
      if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Invalid article publication or checked date')
    rendered = rendered.replace('原稿作成・情報確認 ' + a['date'], '公開 ' + publication_date + ' ・ 情報確認 ' + checked_date)
    schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['description'], 'image': p.BASE + '/' + a['hero'], 'datePublished': a['date'], 'dateModified': a['date'], 'author': {'@type': 'Person', 'name': 'りょう'}, 'publisher': {'@type': 'Organization', 'name': '未来投資navi'}, 'mainEntityOfPage': p.BASE + '/' + a['path']}
    schema.update(datePublished=publication_date, dateModified=checked_date)
    metas = {'og:type': 'article', 'og:title': a['title'], 'og:description': a['description'], 'og:url': p.BASE + '/' + a['path'], 'og:image': p.BASE + '/' + a['hero'], 'og:site_name': '未来投資navi', 'article:published_time': publication_date}
    extra = '\n'.join(f'<meta property="{key}" content="{html.escape(value, quote=True)}">' for key, value in metas.items())
    extra += '\n<meta name="twitter:card" content="summary_large_image">\n<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>\n'
    rendered = rendered.replace('</head>', extra + '</head>')
    if 'noindex' in rendered or 'ローカル確認用' in rendered:
      raise ValueError('Preview marker in release')
    add(a['path'], rendered)
  for name in ['assets/editorial/article.css', 'assets/editorial/lp-slot.css']:
    if name in remote:
      if hashlib.sha1((p.SITE / name).read_bytes()).hexdigest() != remote[name]:
        if not ADDON_ID or os.environ.get('ALLOW_REVIEWED_SHARED_ASSET') != '1':
          raise ValueError('Shared asset changed; review existing consumers')
        build = p.read(p.OUT / 'build-report.json')
        design = p.read(p.OUT / 'design-report.json')
        visual = p.read(p.OUT / 'visual-report.json')
        fingerprint = build['build_fingerprint']
        if design.get('status') != 'pass' or visual.get('status') != 'pass' or design.get('build_fingerprint') != fingerprint or visual.get('build_fingerprint') != fingerprint:
          raise ValueError('Shared asset review is missing or stale')
        add(name, (p.SITE / name).read_bytes())
      continue
    add(name, (p.SITE / name).read_bytes())
  # Existing LP was tested with exactly this single-slot change.
  original = (OUT / 'baseline/index.html').read_text()
  previous = p.ROOT / 'dist/blog-release/site/index.html' if ADDITIONAL else p.ROOT / 'index.html'
  if not (DAILY or ADDON_ID) and original != previous.read_text():
    raise ValueError('LP baseline differs from reviewed source')
  if DAILY or ADDITIONAL or ADDON_ID:
    # Preserve the live page, changing only the existing latest-three slot.
    if DAILY or ADDON_ID:
      published_ids = {id for r in p.read(p.DATA / 'published-releases.json')['releases'] if r['status'] == 'published' for id in r['articles']}
      older = sorted([a for a in p.articles() if a['id'] in published_ids and a['path'] in remote], key=lambda a: (a['date'], a['id']), reverse=True)
      needed = 3 - len(articles)
      if len(older) < needed:
        raise ValueError('Previous published articles required for three-card LP')
      discovery_articles = articles + older[:needed]
    else:
      discovery_articles = articles + [next(a for a in p.articles() if a['id'] == '2026-09-13-sbi-first-order-checklist')]
    candidate = p.inject_lp(original, [dict(a, date=a.get('publication_date', a['date'])) for a in discovery_articles])
    css = '<link rel="stylesheet" href="/assets/editorial/lp-slot.css">'
    if candidate.count(css) == 2:
      candidate = candidate.replace(css + '\n', '', 1)
    add('index.html', candidate)
  else:
    add('index.html', (p.SITE / 'index.html').read_bytes())
  # The all-article index and current monthly archive are generated together so
  # their counts and links cannot drift when the daily pair is published.
  if DAILY:
    generated = OUT / 'archive-generated'
    subprocess.run(['node', str(p.ROOT / 'tools/build-blog-archives.cjs'), '--output-root', str(generated)], cwd=p.ROOT, check=True, capture_output=True, text=True)
    add('blog/index.html', (generated / 'blog/index.html').read_bytes())
    months = {a['date'][:7] for a in articles}
    for month in months:
      year, number = month.split('-')
      archive = f'blog/archive/{year}/{number}/index.html'
      add(archive, (generated / archive).read_bytes())
  else:
    # Preserve the existing blog index design and all existing cards.
    blog = (OUT / 'baseline/blog/index.html').read_text()
    marker = '<div class="grid">'
    if blog.count(marker) != 1:
      raise ValueError('Ambiguous blog index insertion point')
    cards = ''.join(f'<a class="card" href="/{html.escape(a["path"])}"><span class="tag">{html.escape(a["category"])}</span><h3>{html.escape(a["title"])}</h3><div class="meta"><time datetime="{a["date"]}">{a["date"].replace("-", ".")}</time><span class="read">記事を読む →</span></div></a>\n' for a in articles)
    add('blog/index.html', blog.replace(marker, marker + '\n' + cards, 1))
  # Repair unescaped ampersands only; preserve existing sitemap entries.
  raw = (OUT / 'baseline/sitemap.xml').read_text()
  raw = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', raw)
  tree = ET.fromstring(raw)
  ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
  ET.register_namespace('', ns)
  ET.register_namespace('image', 'http://www.google.com/schemas/sitemap-image/1.1')
  for a in articles:
    url = ET.SubElement(tree, '{' + ns + '}url')
    ET.SubElement(url, '{' + ns + '}loc').text = p.BASE + '/' + a['path']
    ET.SubElement(url, '{' + ns + '}lastmod').text = a.get('checked_date', a['date'])
  add('sitemap.xml', ET.tostring(tree, encoding='utf-8', xml_declaration=True))
  # Only add missing dependencies used by the approved article pages.
  for a in articles:
    for asset in [a['hero'], 'blog/2026/copper-price-2026/blog_profile_ryo.jpg']:
      if asset not in remote:
        add(asset, (p.ROOT / asset).read_bytes())
  errors = []
  for name, content in list(package.items()):
    if not name.endswith('.html'):
      continue
    page = p.Page(content.decode())
    for url in page.links:
      target = p.local_target(name, url)
      if target is None:
        continue
      dest, fragment = target
      relative = dest.relative_to(p.SITE).as_posix()
      if relative not in package and relative not in remote:
        errors.append(name + ' -> ' + relative)
      if fragment and relative in package and relative.endswith('.html') and fragment not in p.Page(package[relative].decode()).ids:
        errors.append(name + ' missing anchor ' + fragment)
  # Only new article dependencies are blocking; preserve pre-existing LP links.
  errors = [error for error in errors if any(error.startswith(a['path'] + ' ') for a in articles)]
  if errors:
    raise ValueError('Release links missing: ' + str(errors))
  SITE.mkdir(parents=True, exist_ok=True)
  for name, content in package.items():
    dest = SITE / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
  manifest = {'files': list(package), 'hashes': {name: hashlib.sha1(data).hexdigest() for name, data in package.items()}, 'articles': [a['path'] for a in articles], 'article_ids': [a['id'] for a in articles], 'release_date': articles[0]['date'], 'release_mode': 'addon' if ADDON_ID else 'daily' if DAILY else 'additional' if ADDITIONAL else 'initial', 'build_fingerprint': p.read(p.OUT / 'build-report.json')['build_fingerprint']}
  p.save(OUT / 'package.json', manifest)
  print(json.dumps({'files': list(package), 'source_files_unchanged': True}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
  main()
