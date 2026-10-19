"""Regression checks: retired Git entrypoints must not mutate or send data."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class GitPublishingTests(unittest.TestCase):
  def check_retired_push(self, name):
    with tempfile.TemporaryDirectory() as tmp:
      target = Path(tmp)
      helper = target / 'tools/auto-push'
      helper.mkdir(parents=True)
      for entry in ('autopush.sh', 'auto_push.sh'):
        source = ROOT / 'tools/auto-push' / entry
        if source.is_symlink():
          (helper / entry).symlink_to(os.readlink(source))
        else:
          shutil.copyfile(source, helper / entry)
      binaries = target / 'bin'
      binaries.mkdir()
      for binary in ('git', 'npx', 'netlify'):
        trap = binaries / binary
        trap.write_text('#!/bin/sh\ntouch "$POLICY_TRAP"\nexit 99\n')
        trap.chmod(0o755)
      sitemap = target / 'sitemap.xml'
      sitemap.write_bytes(b'published sitemap sentinel\n')
      marker = target / 'unexpected-command'
      env = dict(os.environ, PATH=str(binaries) + os.pathsep + os.environ['PATH'], POLICY_TRAP=str(marker))
      result = subprocess.run(['bash', str(helper / name)], cwd=target, env=env, capture_output=True)
      self.assertEqual(result.returncode, 1)
      self.assertIn(b'disabled', result.stderr)
      self.assertFalse(marker.exists(), 'Retired entrypoint invoked a mutation or network command')
      self.assertEqual(sitemap.read_bytes(), b'published sitemap sentinel\n')

  def test_old_autopush_stops_before_git_or_sitemap(self):
    self.check_retired_push('autopush.sh')

  def test_old_alias_stops_before_git_or_sitemap(self):
    self.check_retired_push('auto_push.sh')

  def test_legacy_generator_leaves_sitemap_untouched(self):
    with tempfile.TemporaryDirectory() as tmp:
      target = Path(tmp)
      script = target / 'generate-sitemap.ts'
      shutil.copyfile(ROOT / 'scripts/generate-sitemap.ts', script)
      sitemap = target / 'sitemap.xml'
      sitemap.write_bytes(b'published sitemap sentinel\n')
      result = subprocess.run(['node', str(script)], cwd=target, capture_output=True)
      self.assertEqual(result.returncode, 1)
      self.assertIn(b'disabled', result.stderr)
      self.assertEqual(sitemap.read_bytes(), b'published sitemap sentinel\n')

  def test_git_build_skips_and_fails_closed_if_forced(self):
    config = (ROOT / 'netlify.toml').read_text()
    build = re.search(r'^\[build\]\n(.*?)(?=^\[|\Z)', config, re.M | re.S).group(1)
    for key, expected in [('ignore', 0), ('command', 1)]:
      command = re.search(r'^\s*' + key + r' = "(.*)"$', build, re.M).group(1)
      result = subprocess.run(['bash', '-c', command], capture_output=True)
      self.assertEqual(result.returncode, expected)


if __name__ == '__main__':
  unittest.main()
