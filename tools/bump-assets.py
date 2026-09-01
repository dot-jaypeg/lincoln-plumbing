#!/usr/bin/env python3
"""Stamp every page's asset URLs with a hash of the asset contents.

Why this exists: the version token used to be a hand-maintained string
(`?v=static-4`). Edit style.css without remembering to bump it and returning
visitors keep a stale stylesheet under the same URL — which, with the old
7-day cache header on assets, meant new markup rendering against old CSS for a
week. A content hash can't drift: change the file, the URL changes.

Run this AFTER the builders, since it rewrites the emitted HTML:

    python3 tools/build-legacy-lps.py
    python3 tools/build-legacy-all.py
    python3 tools/bump-assets.py

The hash is also written to content/asset-version.txt so the builders emit the
current value directly and this pass is a no-op when nothing changed.
"""
import glob, hashlib, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, 'public')
VERSION_FILE = os.path.join(ROOT, 'content', 'asset-version.txt')

# assets whose URLs carry ?v=... in the markup
HASHED = ['css/style.css', 'js/main.js', 'fonts/Inter-Variable.ttf']


def compute():
    h = hashlib.md5()
    for rel in HASHED:
        p = os.path.join(PUBLIC, rel)
        if os.path.exists(p):
            h.update(open(p, 'rb').read())
    return h.hexdigest()[:10]


def current():
    if os.path.exists(VERSION_FILE):
        return open(VERSION_FILE).read().strip()
    return ''


if __name__ == '__main__':
    version = compute()
    previous = current()

    files = glob.glob(os.path.join(PUBLIC, '**', '*.html'), recursive=True)
    changed = 0
    for f in files:
        s = original = open(f).read()
        s = re.sub(r'(\?v=)[A-Za-z0-9._-]+', r'\g<1>' + version, s)
        if s != original:
            open(f, 'w').write(s)
            changed += 1

    os.makedirs(os.path.dirname(VERSION_FILE), exist_ok=True)
    open(VERSION_FILE, 'w').write(version + '\n')

    moved = ' (unchanged)' if version == previous else f' (was {previous or "none"})'
    print(f'asset version {version}{moved} — stamped into {changed} of {len(files)} pages')
