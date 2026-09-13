#!/usr/bin/env python3
"""Serve only the generated preview, bound to localhost, with no tracking."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path

SITE = Path(__file__).resolve().parents[2] / 'dist/blog-preview/site'

class PreviewHandler(SimpleHTTPRequestHandler):
  def end_headers(self):
    self.send_header('X-Robots-Tag', 'noindex, nofollow')
    self.send_header('Cache-Control', 'no-store')
    self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'none'; frame-src 'none'; form-action 'none'")
    super().end_headers()

if __name__ == '__main__':
  server = ThreadingHTTPServer(('127.0.0.1', 8765), partial(PreviewHandler, directory=str(SITE)))
  print('Local preview: http://127.0.0.1:8765/review.html', flush=True)
  server.serve_forever()
