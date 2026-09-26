#!/usr/bin/env python3
"""Offline, preview-only editorial build. Never edits or deploys the live site."""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "editorial"
OUT = ROOT / "dist/blog-preview"
SITE = OUT / "site"
BASE = "https://eva-solution.com"
HERE = Path(__file__).resolve().parent
LINE_URL = 'https://lin.ee/FxIOpk1'
YOUTUBE_URL = 'https://www.youtube.com/channel/UCb-u1hcuQyo7qruBhuiOBZg'
LP_PATTERN = re.compile(r'<section class="reveal-on-scroll" aria-labelledby="blog-list-heading">.*?</section>', re.S)
ASSETS = {".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico", ".woff", ".woff2", ".mp4", ".pdf"}

def digest(p):
  return hashlib.sha256(p.read_bytes()).hexdigest()

def save(path, value):
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def read(path):
  return json.loads(path.read_text(encoding="utf-8"))

def text_only(value):
  value = re.sub(r'<(script|style|svg)\b.*?</\1>', '', value, flags=re.S | re.I)
  return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value))).strip()

class Page(HTMLParser):
  def __init__(self, source):
    super().__init__(convert_charrefs=True)
    self.meta, self.links, self.ids, self.images = {}, [], [], []
    self.h1 = 0
    self.feed(source)

  def handle_starttag(self, tag, attrs):
    a = dict(attrs)
    if tag == 'meta':
      self.meta[a.get('property', a.get('name', ''))] = a.get('content', '')
    if 'id' in a:
      self.ids.append(a['id'])
    if tag == 'h1':
      self.h1 += 1
    if tag == 'img':
      self.images.append(a)
    for key in ('href', 'src', 'poster'):
      if a.get(key):
        self.links.append(a[key])

def source_files():
  files = list(ROOT.glob('*.html')) + list((ROOT / 'css').rglob('*'))
  for folder in ('blog', 'images', 'js', 'assets'):
    files += list((ROOT / folder).rglob('*'))
  return sorted(p for p in set(files) if p.is_file() and not p.is_symlink() and p.suffix.lower() in ASSETS and 'drafts' not in p.parts)

def inventory():
  rows = []
  for p in sorted((ROOT / 'blog').rglob('*.html')):
    if 'drafts' in p.parts or 'archive' in p.parts or p.name.startswith('category-') or p == ROOT / 'blog/index.html':
      continue
    raw = p.read_text(encoding='utf-8')
    page = Page(raw)
    if page.h1 == 0:
      continue
    title = re.search(r'<h1\b[^>]*>(.*?)</h1>', raw, re.S | re.I)
    rel = p.relative_to(ROOT).as_posix()
    rows.append({
      'id': 'existing-' + hashlib.sha256(rel.encode()).hexdigest()[:12],
      'path': rel, 'title': text_only(title.group(1)),
      'description': page.meta.get('description', ''),
      'date': page.meta.get('article:published_time', '')[:10],
      'category': 'SBI証券' if '/sbi-securities/' in rel else page.meta.get('article:section', '投資コラム'),
      'status': 'existing_local', 'public_url': BASE + '/' + rel,
      'publication_verified': False, 'sha256': digest(p),
      'headings': [text_only(s) for s in re.findall(r'<h[23]\b[^>]*>(.*?)</h[23]>', raw, re.S | re.I)],
      'search_text': text_only(raw),
    })
  return rows

def initialize():
  DATA.mkdir(exist_ok=True)
  baseline = DATA / 'source-lock.json'
  if baseline.exists():
    raise ValueError('Baseline already exists; never silently rebaseline.')
  save(baseline, {p.relative_to(ROOT).as_posix(): digest(p) for p in source_files() + [ROOT / 'sitemap.xml']})
  save(DATA / 'existing-articles.json', inventory())
  print('Initialized read-only source inventory and design lock.')

def verify_lock():
  locks = read(DATA / 'source-lock.json')
  changed = [p for p, h in locks.items() if not (ROOT / p).is_file() or digest(ROOT / p) != h]
  if changed:
    raise ValueError('Protected source changed: ' + ', '.join(changed))
  current = {p.relative_to(ROOT).as_posix() for p in source_files() + [ROOT / 'sitemap.xml']}
  if current != set(locks):
    raise ValueError('Source file set changed; explicitly review and refresh the inventory.')
  design = DATA / 'design-lock.json'
  if design.exists():
    for name, expected in read(design).items():
      if digest(HERE / name) != expected:
        raise ValueError('Frozen template changed: ' + name)

def safe_path(value):
  p = Path(value)
  if p.is_absolute() or '..' in p.parts or not value.startswith('blog/') or p.suffix != '.html':
    raise ValueError('Unsafe article path: ' + value)
  return value

def grams(value):
  s = re.sub(r'\s+', '', value.lower())
  return {s[i:i + 3] for i in range(max(0, len(s) - 2))}

def similarity(a, b):
  aa, bb = grams(a), grams(b)
  return len(aa & bb) / max(1, len(aa | bb))

def article_text(a):
  parts = [a.get(k, '') for k in ('title', 'description', 'category', 'intent', 'angle')]
  parts += a.get('lead', [])
  for s in a.get('sections', []):
    parts.append(s.get('heading', ''))
    parts += s.get('paragraphs', [])
    parts += s.get('items', [])
    if s.get('note'):
      parts.append(s['note'])
    if s.get('table'):
      t = s['table']
      parts.append(t.get('caption', ''))
      parts += t.get('columns', [])
      for row in t.get('rows', []):
        parts += row
  for f in a.get('faq', []):
    parts += [f.get('q', ''), f.get('a', '')]
  return '\n'.join(str(p) for p in parts if p)

def comparison_text(a):
  return a.get('search_text') or article_text(a)

def duplicate_candidates(article, rows):
  candidates = []
  article_body = article_text(article)
  for other in rows:
    if other['path'] == article['path']:
      continue
    title_score = similarity(article['title'], other['title'])
    body_score = similarity(article_body, comparison_text(other))
    candidates.append({
      'path': other['path'],
      'title': other['title'],
      'category': other.get('category', ''),
      'title_score': round(title_score, 3),
      'body_score': round(body_score, 3),
    })
  return sorted(candidates, key=lambda item: (item['body_score'], item['title_score']), reverse=True)

def validate_duplicate_gate(current, rows):
  report = []
  for a in current:
    candidates = duplicate_candidates(a, rows)[:8]
    blocking = [c for c in candidates if c['title_score'] >= 0.85 or c['body_score'] >= 0.30]
    if blocking:
      top = blocking[0]
      raise ValueError(
        'Potential duplicate article: '
        + a['id'] + ' resembles ' + top['path']
        + f' (title={top["title_score"]}, body={top["body_score"]})'
      )
    report.append({
      'id': a['id'],
      'candidates': candidates,
      'editorial_review': a['duplicate_review'],
      'gate': 'pass',
      'thresholds': {'title_score': 0.85, 'body_score': 0.30},
      'limitation': 'Character similarity is a hard pre-publication gate; editorial_review must still explain intent, angle, and audience difference.',
    })
  return report

def articles():
  result = [read(p) for p in sorted((DATA / 'articles').glob('*.json'))]
  seen = set()
  for a in result:
    safe_path(a['path'])
    if a['path'] in seen or (ROOT / a['path']).exists():
      raise ValueError('Duplicate or existing article path: ' + a['path'])
    seen.add(a['path'])
    for field in ('id', 'title', 'description', 'category', 'date', 'hero', 'hero_alt', 'intent', 'angle', 'lead', 'sections', 'faq', 'sources', 'related', 'duplicate_review'):
      if not a.get(field):
        raise ValueError('Missing ' + field)
    if not (ROOT / a['hero']).resolve().is_relative_to(ROOT) or not (ROOT / a['hero']).is_file():
      raise ValueError('Missing or unsafe hero image')
    for s in a['sources']:
      if urlsplit(s['url']).scheme != 'https' or not s.get('checked'):
        raise ValueError('Unverified source metadata')
  return result

def inline(value):
  # Text only plus explicit source tokens. Raw HTML cannot escape the template.
  return re.sub(r'\[S(\d+)\]', r'<a class="bp-cite" href="#source-\1">［\1］</a>', html.escape(value))

def doc(title, description, body, path):
  return f'''<!DOCTYPE html>
<html lang="ja"><head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>{html.escape(title)} | 未来投資navi</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <link rel="canonical" href="{BASE}/{path}">
  <link rel="stylesheet" href="/assets/editorial/article.css">
</head><body class="bp-page">
  <div class="bp-preview">ローカル確認用・未公開</div>
  <header class="bp-nav"><a href="/index.html">未来投資navi</a><a href="/blog/index.html">記事一覧</a></header>
  <main class="bp-container">{body}</main>
  <footer class="bp-footer">未来投資navi / eva solution<br>投資には元本割れのリスクがあります。</footer>
</body></html>'''

def design_content(a):
  # New drafts keep these fields in their structured manuscript. The two
  # original trials use a versioned local supplement; never overwrite Drive.
  content = a.get('design') or read(HERE / 'design-content.json').get(a['id'])
  if not content or not content.get('summary') or not content.get('diagrams'):
    raise ValueError('Missing summary/diagram design content: ' + a['id'])
  if not isinstance(content['summary'], list) or any(not isinstance(s, str) or not s.strip() for s in content['summary']):
    raise ValueError('Invalid summary')
  if not isinstance(content['diagrams'], dict):
    raise ValueError('Invalid diagrams')
  for section, figure in content['diagrams'].items():
    if not str(section).isdigit() or not 1 <= int(section) <= len(a['sections']):
      raise ValueError('Invalid diagram section')
    if not isinstance(figure.get('title'), str) or not figure['title'].strip() or not 2 <= len(figure.get('cards', [])) <= 3:
      raise ValueError('Invalid diagram content')
    if figure.get('layout', 'cards') not in ('cards', 'flow', 'record'):
      raise ValueError('Invalid diagram layout')
    if any(not isinstance(card, list) or len(card) != 2 or any(not isinstance(t, str) or not t.strip() for t in card) for card in figure['cards']):
      raise ValueError('Invalid diagram cards')
  return content

def render_diagram(figure):
  e = html.escape
  layout = figure.get('layout', 'cards')
  klass = 'bp-diagram bp-diagram--' + layout
  number = (lambda i: f'STEP {i}') if layout == 'flow' else (lambda i: f'{i:02}')
  return '<figure class="' + klass + '" aria-label="' + e(figure['title'], quote=True) + '"><figcaption>' + e(figure['title']) + '</figcaption><div class="bp-diagram-grid">' + ''.join(
    f'<div class="bp-diagram-card"><span class="bp-diagram-number" aria-hidden="true">{number(i)}</span><strong>{e(card[0])}</strong><span>{e(card[1])}</span></div>'
    for i, card in enumerate(figure['cards'], 1)) + '</div></figure>'

def emphasized(value, rule=None):
  if rule is None:
    return inline(value)
  phrase = rule.get('text', '')
  if rule.get('kind') not in ('bold', 'highlight') or not 1 <= len(phrase) <= 40 or value.count(phrase) != 1 or re.search(r'\[S\d+\]', phrase):
    raise ValueError('Invalid, ambiguous or stale emphasis rule')
  before, after = value.split(phrase)
  klass = 'bp-highlight' if rule['kind'] == 'highlight' else 'bp-emphasis'
  return inline(before) + f'<strong class="{klass}">' + html.escape(phrase) + '</strong>' + inline(after)

def render_article(a):
  e = html.escape
  design = design_content(a)
  rules = design.get('emphasis', {})
  used = set()
  def rich(value, key):
    if key in rules:
      used.add(key)
    return emphasized(value, rules.get(key))
  body = f'<img class="bp-hero" src="/{e(a["hero"])}" alt="{e(a["hero_alt"])}" width="1200" height="675">'
  body += f'<header class="bp-article-header"><p class="bp-category">{e(a["category"])}</p><h1>{e(a["title"])}</h1><p class="bp-meta">りょう｜未来投資navi ・ 原稿作成・情報確認 {a["date"]}</p></header>'
  body += '<div class="bp-lead">' + ''.join(f'<p>{rich(p, "lead." + str(j))}</p>' for j, p in enumerate(a['lead'])) + '</div>'
  body += f'<a class="bp-youtube" href="{YOUTUBE_URL}" target="_blank" rel="noopener noreferrer"><div class="bp-yt-inner"><span class="bp-yt-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span><div><span class="bp-yt-label">YOUTUBE CHANNEL</span><strong class="bp-yt-name">未来投資navi</strong></div></div><p>50代・60代からの資産づくりを、動画でもわかりやすくお伝えします。</p><span class="bp-yt-button">YouTubeチャンネルを見る</span></a>'
  body += '<nav class="bp-toc" aria-label="目次"><h2>この記事で確認すること</h2><ol>'
  body += ''.join(f'<li><a href="#section-{i}">{e(s["heading"])}</a></li>' for i, s in enumerate(a['sections'], 1)) + '</ol></nav>'
  body += '<article>'
  for i, s in enumerate(a['sections'], 1):
    body += f'<section id="section-{i}"><h2>{e(s["heading"])}</h2>'
    if str(i) in design['diagrams']:
      body += render_diagram(design['diagrams'][str(i)])
    for j, p in enumerate(s.get('paragraphs', [])):
      body += '<p>' + rich(p, f'sections.{i}.paragraphs.{j}') + '</p>'
    if s.get('items'):
      body += '<ul class="bp-checklist">' + ''.join(f'<li>{inline(p)}</li>' for p in s['items']) + '</ul>'
    if s.get('table'):
      t = s['table']
      body += '<div class="bp-table-scroll" tabindex="0" role="region" aria-label="' + e(t['caption']) + '"><table><caption>' + e(t['caption']) + '</caption><thead><tr>'
      body += ''.join(f'<th scope="col">{e(c)}</th>' for c in t['columns']) + '</tr></thead><tbody>'
      body += ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>' for row in t['rows']) + '</tbody></table></div>'
    if s.get('note'):
      body += f'<aside class="bp-note">{inline(s["note"])}</aside>'
    body += '</section>'
  body += '<section><h2>よくある質問</h2>' + ''.join(f'<div class="bp-faq"><h3>{e(f["q"])}</h3><p>{inline(f["a"])}</p></div>' for f in a['faq']) + '</section></article>'
  body += '<section class="bp-summary"><h2>まとめ｜今日のポイント</h2><ul>' + ''.join('<li>' + rich(s, f'summary.{j}') + '</li>' for j, s in enumerate(design['summary'])) + '</ul></section>'
  body += f'<aside class="bp-cta"><h2>自分の家計に当てはめて考えたい方へ</h2><p>生活費・年金・今後の予定によって、無理のない投資額は変わります。迷ったら、整理したいことを公式LINEからお知らせください。</p><a href="{LINE_URL}" target="_blank" rel="noopener noreferrer">公式LINEで相談する</a></aside>'
  body += '<aside class="bp-author" aria-label="著者紹介"><img src="/blog/2026/copper-price-2026/blog_profile_ryo.jpg" width="72" height="72" alt="りょう｜未来投資navi"><div><h2>りょう｜未来投資navi</h2><p>50代・60代の投資初心者に向けて、家計と資産づくりについて発信しています。YouTubeチャンネル「未来投資navi」も運営。</p></div></aside>'
  body += '<section class="bp-related"><h2>あわせて読みたい</h2><p>気になるテーマから、次の確認へ進めます。</p><ul>' + ''.join(f'<li><a class="bp-related-link" href="/{e(r["path"])}"><span class="bp-link-label">関連記事</span><span class="bp-link-title">{e(r["title"])}</span><span class="bp-link-action">記事を読む <span aria-hidden="true">→</span></span></a></li>' for r in a['related']) + '</ul></section>'
  body += '<section class="bp-sources"><h2>出典・確認日</h2><p>本文の出典番号から、根拠となる公式資料を確認できます。</p><ol>' + ''.join(f'<li id="source-{i}"><a class="bp-source-link" href="{e(s["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{e(s["title"])}</a><span class="bp-source-meta">{s["checked"]}確認 ・ 外部サイト／新しいタブ</span></li>' for i, s in enumerate(a['sources'], 1)) + '</ol><p>制度・画面・サービス条件は変更される場合があります。取引前に公式情報をご確認ください。本記事は一般的な情報提供であり、特定商品の購入や利益を保証するものではありません。</p></section>'
  if used != set(rules):
    raise ValueError('Unresolved emphasis locations: ' + ', '.join(set(rules) - used))
  return doc(a['title'], a['description'], body, a['path'])

def markdown(a):
  parts = ['# ' + a['title'], '状態：未公開・確認待ち', '記事ID：' + a['id'], '予定パス：' + a['path'], 'メタ説明：' + a['description'], *a['lead']]
  for s in a['sections']:
    parts += ['## ' + s['heading'], *s.get('paragraphs', [])]
    parts += ['- ' + p for p in s.get('items', [])]
    if s.get('table'):
      t = s['table']
      table_lines = [' | '.join(t['columns']), ' | '.join(['---'] * len(t['columns']))] + [' | '.join(r) for r in t['rows']]
      parts += ['\n'.join(table_lines)]
    if s.get('note'):
      parts += ['補足：' + s['note']]
  parts += ['## よくある質問']
  for f in a['faq']:
    parts += ['### ' + f['q'], f['a']]
  parts += ['## ご相談', '自分の家計に当てはめて考えたい方は、[公式LINE](https://lin.ee/FxIOpk1)から整理したいことをお知らせください。', '## あわせて読みたい']
  parts += [f'[{r["title"]}]({BASE}/{r["path"]})' for r in a['related']]
  parts += ['## 出典'] + [f'[S{i}] [{s["title"]}]({s["url"]}) / {s["checked"]}確認' for i, s in enumerate(a['sources'], 1)]
  parts += ['## 重複確認', a['duplicate_review']]
  return '\n\n'.join(parts) + '\n'

def render_list(rows, title='投資コラムの記事一覧', path='blog/index.html'):
  groups = {}
  for a in sorted(rows, key=lambda a: a['date'], reverse=True):
    groups.setdefault(a['category'] or '投資コラム', []).append(a)
  body = f'<h1>{title}</h1><p>50代・60代のための投資と暮らしの読みもの。全{len(rows)}記事（未公開の試作を含む）。</p>'
  for category, group in groups.items():
    body += '<section><h2>' + html.escape(category) + '</h2><ul class="bp-index">'
    body += ''.join(f'<li><a href="/{html.escape(a["path"])}">{html.escape(a["title"])}</a><span>{a["date"]} {"確認待ち" if a["status"] != "existing_local" else ""}</span></li>' for a in group) + '</ul></section>'
  return doc(title, title, body, path)

def inject_lp(raw, rows):
  if len(LP_PATTERN.findall(raw)) != 1:
    raise ValueError('LP slot is missing or ambiguous. Stop instead of appending.')
  cards = ''
  for a in rows[:3]:
    cards += f'<a class="bp-latest-card" href="/{html.escape(a["path"])}"><span>{html.escape(a["category"])}</span><h3>{html.escape(a["title"])}</h3><small>{a["date"]}</small></a>'
  slot = '<section class="reveal-on-scroll" aria-labelledby="blog-list-heading"><div class="container"><h2 id="blog-list-heading">投資コラム</h2><div class="bp-latest">' + cards + '</div><div style="text-align:center"><a href="blog/index.html" class="cta-button">投資コラムの記事一覧を見る</a></div></div></section>'
  result = LP_PATTERN.sub(lambda _: slot, raw)
  return result.replace('</head>', '<link rel="stylesheet" href="/assets/editorial/lp-slot.css">\n</head>', 1)

def local_target(source, url):
  u = urlsplit(url)
  if u.scheme in ('mailto', 'tel', 'data', 'javascript') or (u.netloc and u.netloc not in ('eva-solution.com', 'eva-solution.netlify.app')):
    return None
  resolved = urlsplit(urljoin('/' + source, url))
  path = unquote(resolved.path).lstrip('/')
  p = SITE / path
  if not p.resolve().is_relative_to(SITE.resolve()):
    return None
  if p.is_dir():
    p /= 'index.html'
  return p, unquote(resolved.fragment)

def link_errors(paths):
  errors = []
  for rel in paths:
    page = Page((SITE / rel).read_text(encoding='utf-8'))
    for url in page.links:
      target = local_target(rel, url)
      if target is None:
        continue
      p, fragment = target
      if not p.is_file():
        errors.append({'page': rel, 'url': url, 'reason': 'missing file'})
      elif fragment and p.suffix == '.html' and fragment not in Page(p.read_text(encoding='utf-8')).ids:
        errors.append({'page': rel, 'url': url, 'reason': 'missing anchor'})
  return errors

def build_staged():
  verify_lock()
  current = articles()
  existing = read(DATA / 'existing-articles.json')
  rows = existing + [dict(a, status='draft') for a in current]
  duplicate_report = validate_duplicate_gate(current, rows)
  SITE.mkdir(parents=True, exist_ok=True)
  # Only public assets are copied. No .env, Git data, scripts, drafts or credentials.
  for p in source_files():
    dest = SITE / p.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
  assets = SITE / 'assets/editorial'
  assets.mkdir(parents=True, exist_ok=True)
  for name in ('article.css', 'lp-slot.css'):
    shutil.copy2(HERE / name, assets / name)
  raw = (ROOT / 'index.html').read_text(encoding='utf-8')
  (SITE / 'baseline.html').write_text(raw, encoding='utf-8')
  ordered = sorted(rows, key=lambda a: (a['date'], a['path']), reverse=True)
  (SITE / 'index.html').write_text(inject_lp(raw, ordered), encoding='utf-8')
  managed = ['index.html', 'blog/index.html']
  for a in current:
    p = SITE / a['path']
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_article(a), encoding='utf-8')
    (DATA / 'exports').mkdir(exist_ok=True)
    (DATA / 'exports' / (a['id'] + '.md')).write_text(markdown(a), encoding='utf-8')
    managed.append(a['path'])
  (SITE / 'blog/index.html').write_text(render_list(rows), encoding='utf-8')
  for category, name in [('SBI証券', 'sbi'), ('家計・生活設計', 'life-planning')]:
    path = f'blog/category-{name}.html'
    (SITE / path).write_text(render_list([a for a in rows if a['category'] == category], category + 'の記事一覧', path), encoding='utf-8')
    managed.append(path)
  # Preserve legacy sitemap URLs that resolve locally; never list missing files.
  ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
  old_text = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
  # Some legacy image titles contain unescaped '&'. Read only loc fields and
  # serialize valid XML anew in the preview, leaving the original untouched.
  try:
    old = ET.fromstring(old_text)
    old_urls = [loc.text for loc in old.findall('.//s:url/s:loc', ns)]
    legacy_xml_valid = True
  except ET.ParseError:
    old_urls = [html.unescape(s) for s in re.findall(r'<loc>(.*?)</loc>', old_text, re.S)]
    legacy_xml_valid = False
  urls = set(BASE + '/' + r['path'] for r in rows)
  omitted = []
  for loc in old_urls:
    path = urlsplit(loc).path
    target = local_target('index.html', path)
    if target and target[0].is_file():
      urls.add(BASE + path)
    else:
      omitted.append(loc)
  urls.update(BASE + '/' + p for p in managed)
  tree = ET.Element('urlset', xmlns=ns['s'])
  for url in sorted(urls):
    ET.SubElement(ET.SubElement(tree, 'url'), 'loc').text = url
  ET.ElementTree(tree).write(SITE / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
  (SITE / 'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
  # Dashboard is local only and deliberately not in the sitemap.
  dash = '<h1>記事追加の確認室</h1><p>本番のLP・記事・画像は変更していません。この画面はローカル専用です。</p><ul><li><a href="/index.html">LP：最新記事3件の表示</a></li><li><a href="/baseline.html">変更前のLP</a></li><li><a href="/blog/index.html">全記事一覧</a></li>'
  dash += ''.join(f'<li><a href="/{a["path"]}">{html.escape(a["title"])}</a></li>' for a in current) + '</ul><p>表示・リンク検査に合格しても、本番公開には別途承認が必要です。</p>'
  (SITE / 'review.html').write_text(doc('記事追加の確認室', 'ローカル確認', dash, 'review.html'), encoding='utf-8')
  managed.append('review.html')
  errors = link_errors(managed)
  for a in current:
    page = Page((SITE / a['path']).read_text(encoding='utf-8'))
    if page.h1 != 1 or len(page.ids) != len(set(page.ids)):
      errors.append({'page': a['path'], 'reason': 'heading or ID violation'})
  verify_lock()
  report = {'status': 'static_pass' if not errors else 'blocked', 'published': False, 'existing_articles': len(existing), 'trial_articles': len(current), 'managed_pages': managed, 'internal_link_errors': errors, 'legacy_sitemap_xml_valid': legacy_xml_valid, 'omitted_legacy_sitemap_urls': omitted, 'duplicate_review': duplicate_report, 'source_lock_unchanged': True, 'external_links': 'Official sources reviewed separately; no guarantee of future reachability.'}
  report['output_hashes'] = {name: digest(SITE / name) for name in managed + ['assets/editorial/article.css', 'assets/editorial/lp-slot.css', 'sitemap.xml']}
  report['build_fingerprint'] = hashlib.sha256(json.dumps(report['output_hashes'], sort_keys=True).encode()).hexdigest()
  save(OUT / 'build-report.json', report)
  save(OUT / 'visual-report.json', {'status': 'pending', 'build_fingerprint': report['build_fingerprint']})
  save(DATA / 'article-ledger.json', {'version': 1, 'articles': [{k: v for k, v in r.items() if k not in ('search_text', 'sections', 'lead', 'faq')} for r in rows]})
  lines = ['# 未来投資navi 記事台帳', '', '既存記事はローカルに存在することを確認済み。本番公開状態は未照合。試作記事は未公開。', '', '| 状態 | 記事 | 保存先 |', '| --- | --- | --- |']
  lines += [f'| {"既存・公開未照合" if a["status"] == "existing_local" else "未公開・確認待ち"} | {a["title"].replace("|", "／")} | {a["path"]} |' for a in rows]
  (DATA / 'article-ledger.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
  print(json.dumps({k: v for k, v in report.items() if k not in ('duplicate_review', 'managed_pages', 'output_hashes')}, ensure_ascii=False, indent=2))
  if errors:
    raise ValueError('Preview checks failed. No publication allowed.')

def build():
  global SITE
  OUT.mkdir(parents=True, exist_ok=True)
  original = SITE
  stage = Path(tempfile.mkdtemp(prefix='candidate-', dir=OUT))
  SITE = stage
  try:
    build_staged()
    if original.exists():
      # Recoverable previous preview; never recursively delete user files.
      backup = Path(tempfile.mkdtemp(prefix='previous-', dir=OUT)) / 'site'
      original.rename(backup)
    stage.rename(original)
  finally:
    SITE = original

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('command', choices=['init', 'build', 'verify'])
  args = parser.parse_args()
  try:
    {'init': initialize, 'build': build, 'verify': verify_lock}[args.command]()
  except (ValueError, KeyError, OSError) as exc:
    print(str(exc), file=sys.stderr)
    sys.exit(1)
