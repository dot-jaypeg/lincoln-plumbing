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
LP = os.path.join(ROOT, 'lp')            # lp. subdomain landing pages (served by server.js)
VERSION_FILE = os.path.join(ROOT, 'content', 'asset-version.txt')

# assets whose URLs carry ?v=... in the markup
HASHED = ['css/style.css', 'js/main.js', 'fonts/Inter-Variable.ttf']
# lp/ pages load style.css from public/ plus their own two files. They get a
# separate hash so an LP tweak doesn't bust the cache on every organic page.
LP_HASHED = [os.path.join(PUBLIC, rel) for rel in HASHED] + [
    os.path.join(LP, 'css', 'lp.css'), os.path.join(LP, 'js', 'lead-form.js')]


def compute(paths=None):
    h = hashlib.md5()
    for p in paths or [os.path.join(PUBLIC, rel) for rel in HASHED]:
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

    def stamp(files, version):
        changed = 0
        for f in files:
            s = original = open(f).read()
            s = re.sub(r'(\?v=)[A-Za-z0-9._-]+', r'\g<1>' + version, s)
            if s != original:
                open(f, 'w').write(s)
                changed += 1
        return changed

    files = glob.glob(os.path.join(PUBLIC, '**', '*.html'), recursive=True)
    changed = stamp(files, version)
    lp_files = glob.glob(os.path.join(LP, '**', '*.html'), recursive=True)
    lp_version = compute(LP_HASHED)
    lp_changed = stamp(lp_files, lp_version)

    os.makedirs(os.path.dirname(VERSION_FILE), exist_ok=True)
    open(VERSION_FILE, 'w').write(version + '\n')

    moved = ' (unchanged)' if version == previous else f' (was {previous or "none"})'
    print(f'asset version {version}{moved} — stamped into {changed} of {len(files)} pages')
    print(f'lp asset version {lp_version} — stamped into {lp_changed} of {len(lp_files)} lp pages')
