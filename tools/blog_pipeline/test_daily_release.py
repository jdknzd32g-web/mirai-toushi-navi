import copy
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
      with patch.object(r, 'DAILY', '2026-09-13'), patch.object(r, 'OUT', out), patch.object(r, 'SITE', out / 'site'), patch.object(r.quality, 'check', return_value=True), patch.object(r.p, 'articles', return_value=articles):
        r.main()
      result = json.loads((out / 'package.json').read_text())
      self.assertEqual(len(result['article_ids']), 2)
      self.assertEqual(len(result['files']), 5)
      lp = (out / 'site/index.html').read_text()
      self.assertEqual(lp.count('class="bp-latest-card"'), 3)
      self.assertEqual(lp.count('href="/assets/editorial/lp-slot.css"'), 1)


if __name__ == '__main__':
  unittest.main()
