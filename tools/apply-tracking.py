#!/usr/bin/env python3
"""Apply tools/tracking.py to the hand-written pages in public/.

The generated pages get their tags from the builders. These six are edited by
hand, so the tags are injected here instead. The paid landing pages are
refreshed here too, in place, so a tracking change reaches them without a
rebuild (which would clobber the hand-edited /ga-plumbing-services).

Every other page in public/ (the generated pages, the per-LP thank-you pages,
/thank-you, /lp-door-hangers ...) gets the "Call from Ads" call-click block
(tracking.call_click) in place, without touching the rest of its tags.

Safe to re-run: every existing tracking script/noscript/comment is stripped
first — matched on the tag IDs and the gtag/fbq/dataLayer globals, so the site's
own scripts are left alone — then exactly one fresh block is inserted. Running
it twice leaves the file byte-for-byte identical.

Run:  python3 tools/apply-tracking.py
"""
import glob, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracking

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, 'public')
HAND_WRITTEN = ['index.html', 'services.html', 'gallery.html',
                'about.html', 'contact.html', '404.html']
LANDING_PAGES = [f'{slug}.html' for slug in sorted(tracking.LP_GTM_PAGES)
                 if os.path.exists(os.path.join(PUBLIC, f'{slug}.html'))]

# what marks a chunk of markup as belonging to a tracking tag
FINGERPRINTS = (tracking.GTM_ID, tracking.LP_GTM_ID, tracking.GA4_ID, tracking.ADS_ID, tracking.META_PIXEL_ID,
                'dataLayer', 'gtag(', 'fbq(', 'googletagmanager.com', 'connect.facebook.net',
                'facebook.com/tr', 'gtag_report_conversion')
COMMENTS = re.compile(
    r'\s*<!--\s*(?:/?tracking:(?:head|body|call-click)|Event snippet for [^>]*?|(?:End )?Google (?:tag|Tag Manager|Ads)'
    r'[^>]*?|(?:End )?Meta Pixel Code)\s*-->', re.I)


def strip(s):
    def drop(m):
        return '' if any(fp in m.group(0) for fp in FINGERPRINTS) else m.group(0)
    s = re.sub(r'\s*<script\b[^>]*>.*?</script>', drop, s, flags=re.S)
    s = re.sub(r'\s*<script\b[^>]*/>', drop, s)
    s = re.sub(r'\s*<noscript\b[^>]*>.*?</noscript>', drop, s, flags=re.S)
    return COMMENTS.sub('', s)


changed = []
for name in HAND_WRITTEN + LANDING_PAGES:
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

# the call-click block on every page: replaced where it is, else added at the
# end of <head>, after the page's Google tags
CALL_CLICK = re.compile(re.escape(tracking.CALL_CLICK_START) + '.*?' + re.escape(tracking.CALL_CLICK_END), re.S)
for path in sorted(glob.glob(os.path.join(PUBLIC, '**', '*.html'), recursive=True)):
    name = os.path.relpath(path, PUBLIC)
    original = open(path).read()
    m = CALL_CLICK.search(original)
    if m:
        rest = original[:m.start()] + original[m.end():]
        s = original[:m.start()] + tracking.call_click(rest) + original[m.end():]
    elif '</head>' in original:
        s = original.replace('</head>', tracking.call_click(original) + '\n</head>', 1)
    else:
        print(f'  SKIPPED {name}: no </head> for the call-click block')
        continue
    if s != original:
        open(path, 'w').write(s)
        if name not in changed:
            changed.append(name)

print(f'tracking applied; {len(changed)} file(s) rewritten: ' + (', '.join(changed) or 'none'))
