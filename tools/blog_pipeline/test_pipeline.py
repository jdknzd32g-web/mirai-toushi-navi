import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('pipeline', Path(__file__).with_name('pipeline.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class SafetyTests(unittest.TestCase):
  def test_emphasis_is_scoped_and_escaped(self):
    result = p.emphasized('前<script>後', {'kind': 'highlight', 'text': '<script>'})
    self.assertIn('<strong class="bp-highlight">&lt;script&gt;</strong>', result)
    self.assertNotIn('<script>', result)

  def test_ambiguous_stale_long_emphasis_rejected(self):
    for value, phrase in [('同じ同じ', '同じ'), ('原稿', '変更済み'), ('長' * 41, '長' * 41)]:
      with self.assertRaises(ValueError):
        p.emphasized(value, {'kind': 'bold', 'text': phrase})

  def test_trials_have_three_highlights_and_four_bold_spans(self):
    for article in p.articles():
      result = p.render_article(article)
      self.assertEqual(result.count('class="bp-highlight"'), 3)
      self.assertEqual(result.count('class="bp-emphasis"'), 4)
      self.assertEqual(result.count('class="bp-related-link"'), len(article['related']))

  def test_design_requires_summary_and_diagrams(self):
    with self.assertRaises(ValueError):
      p.design_content({'id': 'unknown-draft', 'sections': []})

  def test_design_rejects_out_of_range_section(self):
    with self.assertRaises(ValueError):
      p.design_content({'id': 'test', 'sections': [], 'design': {'summary': ['要約'], 'diagrams': {'1': {'title': '図', 'cards': [['a', 'b'], ['c', 'd']]}}}})

  def test_diagram_text_is_escaped(self):
    result = p.render_diagram({'title': '<script>alert(1)</script>', 'cards': [['<img src=x>', '説明'], ['確認', '内容']]})
    self.assertNotIn('<script>', result)
    self.assertNotIn('<img', result)
    self.assertIn('&lt;script&gt;', result)

  def test_trial_articles_have_common_components_in_order(self):
    for a in p.articles():
      result = p.render_article(a)
      markers = ['class="bp-hero"', 'class="bp-article-header"', 'class="bp-lead"', 'class="bp-youtube"', 'class="bp-toc"', '<article>', 'class="bp-summary"', 'class="bp-cta"', 'class="bp-author"', 'class="bp-sources"']
      positions = [result.index(marker) for marker in markers]
      self.assertEqual(positions, sorted(positions))
      self.assertIn(p.LINE_URL, result)
      self.assertIn(p.YOUTUBE_URL, result)
      self.assertGreaterEqual(result.count('class="bp-diagram"'), 1)

  def test_path_traversal_rejected(self):
    for value in ('../index.html', '/tmp/a.html', 'blog/../index.html', 'blog/a.js'):
      with self.assertRaises(ValueError):
        p.safe_path(value)

  def test_text_cannot_inject_markup(self):
    self.assertNotIn('<script>', p.inline('<script>alert(1)</script>'))
    self.assertIn('href="#source-1"', p.inline('fact [S1]'))

  def test_missing_or_duplicate_slot_blocks(self):
    with self.assertRaises(ValueError):
      p.inject_lp('<html></html>', [])
    slot = '<section class="reveal-on-scroll" aria-labelledby="blog-list-heading"></section>'
    with self.assertRaises(ValueError):
      p.inject_lp(slot + slot, [])

  def test_latest_never_exceeds_three(self):
    raw = (p.ROOT / 'index.html').read_text()
    row = {'path': 'blog/example.html', 'category': 'テスト', 'title': '記事', 'date': '2026-09-13'}
    rendered = p.inject_lp(raw, [row] * 20)
    self.assertEqual(rendered.count('class="bp-latest-card"'), 3)
    self.assertEqual(p.LP_PATTERN.sub('', raw), p.LP_PATTERN.sub('', rendered.replace('<link rel="stylesheet" href="/assets/editorial/lp-slot.css">\n', '')))

  def test_existing_sbi_index_is_an_article(self):
    records = p.inventory()
    paths = [a['path'] for a in records]
    self.assertIn('blog/sbi-securities/index.html', paths)
    self.assertNotIn('blog/index.html', paths)
    self.assertEqual(len(paths), len(set(paths)))

  def test_source_lock_unchanged(self):
    p.verify_lock()

  def test_lock_detects_modified_source(self):
    old_data, old_root = p.DATA, p.ROOT
    with tempfile.TemporaryDirectory() as folder:
      try:
        p.DATA = p.ROOT = Path(folder)
        f = p.ROOT / 'index.html'
        f.write_text('before')
        p.save(p.DATA / 'source-lock.json', {'index.html': p.digest(f)})
        f.write_text('after')
        with self.assertRaises(ValueError):
          p.verify_lock()
      finally:
        p.DATA, p.ROOT = old_data, old_root

  def test_preview_internal_links(self):
    report = p.read(p.OUT / 'build-report.json')
    self.assertEqual(p.link_errors(report['managed_pages']), [])

  def test_missing_link_is_detected(self):
    with tempfile.TemporaryDirectory() as folder:
      old_site = p.SITE
      try:
        p.SITE = Path(folder)
        (p.SITE / 'test.html').write_text('<a href="missing.html">missing</a>')
        self.assertEqual(len(p.link_errors(['test.html'])), 1)
      finally:
        p.SITE = old_site

  def test_source_files_exclude_private_material(self):
    for f in p.source_files():
      self.assertNotIn('editorial', f.parts)
      self.assertNotIn('.env', f.name)
      self.assertNotIn('drafts', f.parts)

  def test_rebuild_is_repeatable_and_keeps_sources(self):
    p.build()
    report = p.read(p.OUT / 'build-report.json')
    before = {name: p.digest(p.SITE / name) for name in report['managed_pages']}
    p.build()
    self.assertEqual(before, {name: p.digest(p.SITE / name) for name in report['managed_pages']})
    p.verify_lock()

if __name__ == '__main__':
  unittest.main()
