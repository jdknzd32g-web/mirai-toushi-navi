"""Prepare only explicitly approved articles and narrowly scoped discovery edits."""
import hashlib
import html
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pipeline as p
import quality

ADDITIONAL = os.environ.get('RELEASE_BATCH') == 'additional'
OUT = p.ROOT / ('dist/blog-release-additional' if ADDITIONAL else 'dist/blog-release')
SITE = OUT / 'site'
TARGETS = ({'2026-09-13-sbi-contact-details-check', '2026-09-13-family-account-map'} if ADDITIONAL else {'2026-09-13-sbi-first-order-checklist', '2026-09-13-cash-reserve-worksheet'})

def main():
  if not quality.check():
    raise ValueError('Preview gates did not pass')
  articles = [a for a in p.articles() if a['id'] in TARGETS]
  if {a['id'] for a in articles} != TARGETS:
    raise ValueError('Two approved articles required')
  remote = {f['path'].lstrip('/'): f['sha'] for f in p.read(OUT / 'remote-files.json')}
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
    rendered = rendered.replace('原稿作成・情報確認 ' + a['date'], '公開 ' + a['date'] + ' ・ 情報確認 ' + a['date'])
    schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['description'], 'image': p.BASE + '/' + a['hero'], 'datePublished': a['date'], 'dateModified': a['date'], 'author': {'@type': 'Person', 'name': 'りょう'}, 'publisher': {'@type': 'Organization', 'name': '未来投資navi'}, 'mainEntityOfPage': p.BASE + '/' + a['path']}
    metas = {'og:type': 'article', 'og:title': a['title'], 'og:description': a['description'], 'og:url': p.BASE + '/' + a['path'], 'og:image': p.BASE + '/' + a['hero'], 'og:site_name': '未来投資navi', 'article:published_time': a['date']}
    extra = '\n'.join(f'<meta property="{key}" content="{html.escape(value, quote=True)}">' for key, value in metas.items())
    extra += '\n<meta name="twitter:card" content="summary_large_image">\n<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>\n'
    rendered = rendered.replace('</head>', extra + '</head>')
    if 'noindex' in rendered or 'ローカル確認用' in rendered:
      raise ValueError('Preview marker in release')
    add(a['path'], rendered)
  for name in ['assets/editorial/article.css', 'assets/editorial/lp-slot.css']:
    if name in remote:
      if hashlib.sha1((p.SITE / name).read_bytes()).hexdigest() != remote[name]:
        raise ValueError('Shared asset changed; review existing consumers')
      continue
    add(name, (p.SITE / name).read_bytes())
  # Existing LP was tested with exactly this single-slot change.
  original = (OUT / 'baseline/index.html').read_text()
  previous = p.ROOT / 'dist/blog-release/site/index.html' if ADDITIONAL else p.ROOT / 'index.html'
  if original != previous.read_text():
    raise ValueError('LP baseline differs from reviewed source')
  if ADDITIONAL:
    # Preserve the live page, changing only the existing latest-three slot.
    third = next(a for a in p.articles() if a['id'] == '2026-09-13-sbi-first-order-checklist')
    candidate = p.inject_lp(original, articles + [third])
    css = '<link rel="stylesheet" href="/assets/editorial/lp-slot.css">'
    if candidate.count(css) == 2:
      candidate = candidate.replace(css + '\n', '', 1)
    add('index.html', candidate)
  else:
    add('index.html', (p.SITE / 'index.html').read_bytes())
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
    ET.SubElement(url, '{' + ns + '}lastmod').text = a['date']
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
  manifest = {'files': list(package), 'hashes': {name: hashlib.sha1(data).hexdigest() for name, data in package.items()}, 'articles': [a['path'] for a in articles], 'build_fingerprint': p.read(p.OUT / 'build-report.json')['build_fingerprint']}
  p.save(OUT / 'package.json', manifest)
  print(json.dumps({'files': list(package), 'source_files_unchanged': True}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
  main()
