#!/usr/bin/env python3
"""Apply tools/tracking.py to the hand-written pages in public/.

The generated pages get their tags from the builders. These six are edited by
hand, so the tags are injected here instead.

Safe to re-run: every existing tracking script/noscript/comment is stripped
first — matched on the tag IDs and the gtag/fbq/dataLayer globals, so the site's
own scripts are left alone — then exactly one fresh block is inserted. Running
it twice leaves the file byte-for-byte identical.

Run:  python3 tools/apply-tracking.py
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracking

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, 'public')
HAND_WRITTEN = ['index.html', 'services.html', 'gallery.html',
                'about.html', 'contact.html', '404.html']

# what marks a chunk of markup as belonging to a tracking tag
FINGERPRINTS = (tracking.GTM_ID, tracking.GA4_ID, tracking.ADS_ID, tracking.META_PIXEL_ID,
                'dataLayer', 'gtag(', 'fbq(', 'googletagmanager.com', 'connect.facebook.net',
                'facebook.com/tr')
COMMENTS = re.compile(
    r'\s*<!--\s*(?:tracking:(?:head|body)|(?:End )?Google (?:tag|Tag Manager|Ads)'
    r'[^>]*?|(?:End )?Meta Pixel Code)\s*-->', re.I)


def strip(s):
    def drop(m):
        return '' if any(fp in m.group(0) for fp in FINGERPRINTS) else m.group(0)
    s = re.sub(r'\s*<script\b[^>]*>.*?</script>', drop, s, flags=re.S)
    s = re.sub(r'\s*<script\b[^>]*/>', drop, s)
    s = re.sub(r'\s*<noscript\b[^>]*>.*?</noscript>', drop, s, flags=re.S)
    return COMMENTS.sub('', s)


changed = []
for name in HAND_WRITTEN:
    path = os.path.join(PUBLIC, name)
    original = open(path).read()

    # the site's own <script src> tags live at the end of the body; strip only
    # touches tracking markup, so they survive
    s = strip(original)

    body_open = re.search(r'<body[^>]*>', s)
    if '</head>' not in s or not body_open:
        print(f'  SKIPPED {name}: no </head>/<body ...> to anchor to')
        continue

    slug = None if name == 'index.html' else name[:-5]
    s = s.replace('</head>', tracking.head(slug) + '\n</head>', 1)
    body_open = re.search(r'<body[^>]*>', s)
    s = s[:body_open.end()] + '\n' + tracking.body(slug) + s[body_open.end():]

    if s != original:
        open(path, 'w').write(s)
        changed.append(name)

print(f'tracking applied; {len(changed)} file(s) rewritten: ' + (', '.join(changed) or 'none'))
