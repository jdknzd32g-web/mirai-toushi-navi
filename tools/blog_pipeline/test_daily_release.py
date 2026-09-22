import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import package_release as r


class DailyReleaseTests(unittest.TestCase):
  def test_requires_one_sbi_and_one_other(self):
    with patch.object(r, 'DAILY', '2026-09-13'), patch.object(r.quality, 'check', return_value=True):
      with self.assertRaisesRegex(ValueError, 'exactly one SBI'):
        r.main()  # Four articles on the special first day must not be republished.

  def test_packages_two_articles_without_changing_live_source(self):
    articles = copy.deepcopy(r.p.articles())
    for a in articles:
      if a['id'] not in {'2026-09-13-sbi-contact-details-check', '2026-09-13-family-account-map'}:
        a['date'] = '2026-09-12'
    source = r.p.ROOT / 'dist/blog-release-additional'
    with tempfile.TemporaryDirectory() as tmp:
      out = Path(tmp)
      shutil.copytree(source / 'baseline', out / 'baseline')
      shutil.copyfile(source / 'remote-files.json', out / 'remote-files.json')
      remote = json.loads((out / 'remote-files.json').read_text())
      for item in remote:
        name = item['path'].lstrip('/')
        if name in {'assets/editorial/article.css', 'assets/editorial/lp-slot.css'}:
          item['sha'] = hashlib.sha1((r.p.SITE / name).read_bytes()).hexdigest()
      (out / 'remote-files.json').write_text(json.dumps(remote))
      with patch.object(r, 'DAILY', '2026-09-13'), patch.object(r, 'OUT', out), patch.object(r, 'SITE', out / 'site'), patch.object(r.quality, 'check', return_value=True), patch.object(r.p, 'articles', return_value=articles):
        r.main()
      result = json.loads((out / 'package.json').read_text())
      self.assertEqual(len(result['article_ids']), 2)
      self.assertEqual(len(result['files']), 5)
      lp = (out / 'site/index.html').read_text()
      self.assertEqual(lp.count('class="bp-latest-card"'), 3)
      self.assertEqual(lp.count('href="/assets/editorial/lp-slot.css"'), 1)

  def test_packages_one_explicit_addon_with_reviewed_shared_css(self):
    article_id = '2026-09-18-new-nisa-monthly-amount'
    source = r.p.ROOT / 'dist/blog-release-2026-09-18'
    with tempfile.TemporaryDirectory() as tmp:
      out = Path(tmp)
      shutil.copytree(source / 'baseline', out / 'baseline')
      shutil.copyfile(source / 'remote-files.json', out / 'remote-files.json')
      with patch.object(r, 'DAILY', None), patch.object(r, 'ADDON_ID', article_id), patch.object(r, 'OUT', out), patch.object(r, 'SITE', out / 'site'), patch.object(r.quality, 'check', return_value=True), patch.dict(r.os.environ, {'ALLOW_REVIEWED_SHARED_ASSET':'1'}):
        r.main()
      result = json.loads((out / 'package.json').read_text())
      self.assertEqual(result['article_ids'], [article_id])
      self.assertEqual(result['release_mode'], 'addon')
      self.assertIn('assets/editorial/article.css', result['files'])
      self.assertEqual((out / 'site/index.html').read_text().count('class="bp-latest-card"'), 3)


if __name__ == '__main__':
  unittest.main()
