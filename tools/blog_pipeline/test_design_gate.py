"""Final gate must refuse missing, stale and failed benchmark reports."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import quality


class DesignGateTests(unittest.TestCase):
  def run_gate(self, design, present=True):
    records = {
      'build-report.json': {'status': 'static_pass', 'build_fingerprint': 'build-1', 'output_hashes': {}},
      'visual-report.json': {'status': 'pass', 'build_fingerprint': 'build-1'},
      'design-report.json': design,
      'drive-map.json': {'files': {}}
    }
    with tempfile.TemporaryDirectory() as directory:
      if present:
        (Path(directory) / 'design-report.json').touch()
      with patch.object(quality.p, 'OUT', Path(directory)), \
           patch.object(quality.p, 'verify_lock'), \
           patch.object(quality.p, 'read', side_effect=lambda path: records[path.name]), \
           patch.object(quality.p, 'digest', return_value='checker-1'), \
           patch.object(quality.p, 'save'), contextlib.redirect_stdout(io.StringIO()):
        return quality.check()

  def good(self):
    return {'status': 'pass', 'build_fingerprint': 'build-1', 'checker_sha256': 'checker-1',
            'widths': [1440, 768, 390, 320], 'negative_tests': [{'detected': True}] * 12}

  def test_current_report_passes(self):
    self.assertTrue(self.run_gate(self.good()))

  def test_missing_report_blocks(self):
    self.assertFalse(self.run_gate({}, present=False))

  def test_stale_build_blocks(self):
    self.assertFalse(self.run_gate({**self.good(), 'build_fingerprint': 'old-build'}))

  def test_changed_checker_blocks(self):
    self.assertFalse(self.run_gate({**self.good(), 'checker_sha256': 'old-checker'}))

  def test_failed_design_blocks(self):
    self.assertFalse(self.run_gate({**self.good(), 'status': 'blocked'}))

  def test_missing_viewport_blocks(self):
    self.assertFalse(self.run_gate({**self.good(), 'widths': [1440]}))

  def test_undetected_mutation_blocks(self):
    self.assertFalse(self.run_gate({**self.good(), 'negative_tests': [{'detected': False}] * 12}))
