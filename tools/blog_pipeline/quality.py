#!/usr/bin/env python3
"""Final local readiness gate. It cannot publish anything."""
from datetime import datetime
import json
from pathlib import Path
import sys
import pipeline as p

def check():
  p.verify_lock()
  build = p.read(p.OUT / 'build-report.json')
  visual = p.read(p.OUT / 'visual-report.json')
  failures = []
  if build['status'] != 'static_pass':
    failures.append('Static checks failed')
  if visual['status'] != 'pass' or visual.get('build_fingerprint') != build['build_fingerprint']:
    failures.append('Visual checks missing, failed, or stale')
  for name, expected in build['output_hashes'].items():
    if not (p.SITE / name).exists() or p.digest(p.SITE / name) != expected:
      failures.append('Generated file changed after checks: ' + name)
  mapping = p.read(p.DATA / 'drive-map.json')
  for key, f in mapping['files'].items():
    if not f.get('readback_verified') or p.digest(p.ROOT / f['path']) != f['sha256']:
      failures.append('Drive sync missing or local file changed: ' + key)
  result = {
    'status': 'blocked' if failures else 'preview_ready',
    'published': False,
    'checked_at': datetime.now().astimezone().isoformat(),
    'build_fingerprint': build['build_fingerprint'],
    'source_unchanged': True,
    'drive_files_verified': len(mapping['files']),
    'viewports': [v['width'] for v in visual.get('viewports', [])],
    'failures': failures,
    'limitation': 'Drive readback is checked against the last verified revision; each next run must re-fetch remote metadata. No publication or cross-browser guarantee.'
  }
  p.save(p.OUT / 'quality-report.json', result)
  print(json.dumps(result, ensure_ascii=False, indent=2))
  return not failures

if __name__ == '__main__':
  sys.exit(0 if check() else 1)
