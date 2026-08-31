#!/usr/bin/env python3
"""Scrape-and-replace the rest of the legacy WordPress site.

`tools/build-legacy-lps.py` handles the 11 hand-coded landing pages. This one
handles everything else in the legacy sitemap — the service hub/child pages, the
service-location pages, the utility pages, and the blog posts — all of which are
ordinary Divi/WordPress pages whose content lives in
<article><div class="entry-content">.

Content is carried over as-is (prose, headings, lists, images, internal links);
the chrome, design system, phone/email and the GHL form come from this site.

Run:  python3 tools/build-legacy-all.py
"""
import html, json, os, re, sys, importlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
lp = importlib.import_module('build-legacy-lps')
import tracking

ROOT = lp.ROOT
RAW = os.path.join(ROOT, 'content', 'legacy-scrape', 'raw-html-full')
PUBLIC = lp.PUBLIC
LEGACY_HOST = 'https://www.lincolnplumbingandrooter.com'
SLUG_FILE = os.path.join(ROOT, 'content', 'legacy-scrape', 'all-slugs.txt')
# Ten of the legacy posts were rewritten for this site before the platform swap
# and lived at /blog/<slug>. Their approved copy is snapshotted in
# content/repo-posts/ and wins over the legacy version — but it is now served at
# the legacy root-level slug, which is where the links and rankings point.
REPO_POSTS = os.path.join(ROOT, 'content', 'repo-posts')
REPO_META = (json.load(open(os.path.join(REPO_POSTS, '_meta.json')))
             if os.path.exists(os.path.join(REPO_POSTS, '_meta.json')) else {})

# pages this site already owns with its own copy, or that the LP builder made
SKIP = {'', 'about', 'contact', 'blog'} | set(lp.PAGES.keys())

# hero photo per top-level area
HERO = {
    'plumbing-services': 'work-prep.jpg',
    'drains-and-sewers': 'work-commercial-drain.jpg',
    'leak-detection': 'work-attic-access.jpg',
    'service-locations': 'van-side.jpg',
    'specials': 'van-warehouse.jpg',
    'testimonials': 'team-two-techs.jpg',
    'sitemap': 'team-meeting.jpg',
    'privacy-policy': 'team-meeting.jpg',
    'lp-job-ad': 'team-training.jpg',
    'meta-thank-you': 'team-meeting.jpg',
}
POST_HEROES = ['work-kitchen-drain.jpg', 'work-commercial-drain.jpg', 'work-prep.jpg',
               'work-bathroom-vanity.jpg', 'work-attic-access.jpg', 'work-kitchen-repair.jpg',
               'gallery-hose-outdoor.jpg', 'van-side.jpg']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']


def txt(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s or ''))).strip()


def img_name(u):
    u = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', u)
    return re.sub(r'[^A-Za-z0-9._-]', '-', os.path.basename(u)).lower()


def normalise_phone(s):
    """Both of the company's numbers turn up in the legacy copy in several
    formats (the job-ad pages already used the main line). Rewrite every one of
    them to whichever number the page being built should show — display format
    first, then the digits inside tel: links, in one pass each so a replacement
    can't be re-matched by the next pattern."""
    digits = lp.tel()[4:]
    # tel: hrefs first, so the display pass can't corrupt one into tel:1909-765-…
    s = re.sub(r'tel:\+?1?[\s.-]?\(?909\)?[\s.-]?7(?:65[\s.-]?0236|80[\s.-]?0887)',
               'tel:' + digits, s)
    # then the human-readable form, skipping anything sitting inside a run of
    # digits (i.e. the tel: numbers just normalised above)
    return re.sub(r'(?<!\d)\(?909\)?[\s.-]?7(?:65[\s.-]?0236|80[\s.-]?0887)(?!\d)',
                  lp.phone(), s)


def clean_body(ec, slug_map):
    """Turn a Divi/WordPress entry-content blob into plain semantic prose."""
    s = re.sub(r'<(script|style|noscript)\b.*?</\1>', '', ec, flags=re.S | re.I)
    s = re.sub(r'<ul[^>]*class="fuse-subpages".*?</ul>', '', s, flags=re.S)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)

    # real image srcs hide in data-lazy-src; point them at our local copies
    def fix_img(m):
        tag = m.group(0)
        src = re.search(r'data-lazy-src="([^"]+)"', tag) or re.search(r'src="(https?://[^"]+)"', tag)
        if not src or 'facebook.com' in src.group(1) or '/wp-content/uploads/' not in src.group(1):
            return ''
        alt = re.search(r'alt="([^"]*)"', tag)
        return (f'<figure><img src="/images/legacy/{img_name(src.group(1))}" '
                f'alt="{html.escape(txt(alt.group(1)) if alt else "", quote=True)}" loading="lazy"></figure>')
    s = re.sub(r'<img[^>]*>', fix_img, s)

    # Divi buttons -> our button
    s = re.sub(r'<a class="et_pb_button[^"]*"([^>]*)>(.*?)</a>',
               lambda m: f'<a{m.group(1)} class="btn btn-primary">{txt(m.group(2)).title()}</a>',
               s, flags=re.S)

    # drop every wrapper element, keep its contents
    for tag in ['div', 'span', 'section', 'article', 'o:p', 'o', 'header', 'footer']:
        s = re.sub(r'</?' + re.escape(tag) + r'(\s[^>]*)?>', '', s, flags=re.I)

    # links: legacy absolute -> our paths
    def fix_href(m):
        u = html.unescape(m.group(1))
        if u.startswith(LEGACY_HOST):
            u = u[len(LEGACY_HOST):]
        if u.startswith('tel:'):
            return f'href="{lp.tel()}"'
        # Cloudflare email obfuscation leaves behind /cdn-cgi/l/email-protection#<hex>
        if '/cdn-cgi/l/email-protection' in u:
            return f'href="mailto:{lp.EMAIL}"'
        if u.startswith('/'):
            p = u.split('#')[0].split('?')[0].strip('/')
            u = slug_map.get(p, '/' + p if p else '/')
        return f'href="{u}"'
    s = re.sub(r'href="([^"]*)"', fix_href, s)
    s = re.sub(r'\shref="mailto:[^"]*"', f' href="mailto:{lp.EMAIL}"', s)

    # legacy contact details -> whichever number this page should show. Both
    # numbers appear in the legacy copy (the job-ad pages already used the main
    # line), so normalise either one.
    s = normalise_phone(s)
    s = s.replace('lincolnplumbingrooter@gmail.com', lp.EMAIL)
    s = re.sub(r'\[email(?:&#160;|&nbsp;| )?protected\]', lp.EMAIL, s)

    # strip attributes we don't want (keep href and the img src/alt/loading)
    s = re.sub(r'\s(?:class|style|title|id|width|height|decoding|lang|rel|target|sizes|srcset'
               r'|data-[\w-]+)="[^"]*"',
               lambda m: '' if 'class="btn' not in m.group(0) else m.group(0), s)
    s = re.sub(r'<(p|h[1-6]|li|ul|ol|strong|em)>\s*(?:&nbsp;|\s)*</\1>', '', s)
    s = re.sub(r'<h1[^>]*>.*?</h1>', '', s, flags=re.S)   # the template renders the h1
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'>\s*<(p|h2|h3|h4|ul|ol|li|figure|blockquote|table|tr|a class="btn)', r'>\n<\1', s)
    return s


def tidy_prose(body, h1):
    """Three cosmetic fixes on the imported prose:
    the legacy pages repeat their title as the first h2 (the template renders the
    h1 already), the Divi layouts sprinkle the same button after every section,
    and a run of stacked full-width images reads better as a 2-up row."""
    def norm(x):
        return re.sub(r'[^a-z0-9]+', '', txt(x).lower())

    first = re.match(r'\s*<h2[^>]*>(.*?)</h2>', body, re.S)
    if first and h1 and norm(first.group(1)) == norm(h1):
        body = body[first.end():].lstrip()

    seen = set()
    def dedupe_btn(m):
        label = norm(m.group(0))
        if label in seen:
            return ''
        seen.add(label)
        return m.group(0)
    body = re.sub(r'<a href="[^"]*" class="btn btn-primary">.*?</a>', dedupe_btn, body)

    # adjacent figures -> one row
    body = re.sub(r'(?:<figure>.*?</figure>\s*){2,}',
                  lambda m: '<div class="prose-figures">' + m.group(0).strip() + '</div>',
                  body, flags=re.S)
    return re.sub(r'\n{3,}', '\n\n', body).strip()


def extract(path, slug, slug_map):
    raw = re.sub(r'\s+', ' ', open(path, encoding='utf-8', errors='replace').read())
    t = re.search(r'<title[^>]*>(.*?)</title>', raw)
    d = re.search(r'<meta name="description" content="(.*?)"', raw)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', raw)
    pub = re.search(r'<meta property="article:published_time" content="([^"]+)"', raw)
    a = raw.find('class="entry-content"')
    b = raw.find('</article>', a)
    ec = raw[a + len('class="entry-content"') + 1:b] if a > 0 else ''
    body = clean_body(ec, slug_map)
    override = os.path.join(REPO_POSTS, slug + '.html')
    if slug in REPO_META and os.path.exists(override):
        body = normalise_phone(open(override).read().strip())
        m = REPO_META[slug]
        return {
            'slug': slug, 'legacy_url': f'{LEGACY_HOST}/{slug}/',
            'title': html.unescape(m['title']), 'description': html.unescape(m['description']),
            'h1': m['h1'], 'published': '', 'display_date': m['date'], 'is_post': True,
            'source': 'this site (rewritten before the swap)', 'body': body,
            'body_chars': len(txt(body)),
            'headings': [txt(x) for x in re.findall(r'<h2[^>]*>(.*?)</h2>', body)],
        }
    body = tidy_prose(body, txt(h1.group(1)) if h1 else '')
    lead_img = ''
    lead = re.match(r'\s*(?:<p>\s*)?<figure><img src="([^"]+)"[^>]*></figure>\s*(?:</p>)?', body)
    if lead:
        lead_img = lead.group(1)
        body = body[lead.end():].lstrip()
    if len(txt(body)) < 40:
        if slug == 'privacy-policy':
            body = PRIVACY_PLACEHOLDER.format(email=lp.EMAIL, phone=lp.phone())
        elif slug in EMPTY_FALLBACK:
            tgt = EMPTY_FALLBACK[slug]
            label = tgt.split('/')[-1].replace('-', ' ')
            body = (f'<p>This page covered our {label} work. The full detail now lives on '
                    f'our <a href="{slug_map.get(tgt, "/" + tgt)}">{label} page</a> — '
                    f'same service, same crew, more information.</p>\n'
                    f'<p><a class="btn btn-primary" href="{slug_map.get(tgt, "/" + tgt)}">'
                    f'Read About {label.title()}</a></p>')
    return {
        'slug': slug,
        'legacy_url': f'{LEGACY_HOST}/{slug}/',
        'title': txt(t.group(1)) if t else '',
        'description': txt(d.group(1)) if d else '',
        'h1': txt(h1.group(1)) if h1 else '',
        'published': pub.group(1)[:10] if pub else '',
        'is_post': False,
        'lead_img': lead_img,
        'body': body,
        'body_chars': len(txt(body)),
        'headings': [txt(x) for x in re.findall(r'<h2[^>]*>(.*?)</h2>', body)],
    }


# legacy pages whose entry-content is empty on the live site. The first three are
# duplicates of populated pages elsewhere in the tree; privacy-policy never had
# any text at all.
EMPTY_FALLBACK = {
    'leak-detection/rooter-services': 'drains-and-sewers/rooter-services',
    'leak-detection/sewer-line-repair': 'drains-and-sewers/sewer-line-repair',
    'leak-detection/sewer-line-replacement': 'drains-and-sewers/sewer-line-replacement',
}
PRIVACY_PLACEHOLDER = """<p><strong>[PLACEHOLDER — needs client copy.]</strong> This page existed on the
previous site but had no privacy policy text on it. Replace this block with the
real policy before launch.</p>
<p>If you need a starting point, it should cover: what information the site
collects (contact-form submissions, analytics, and advertising cookies), how it
is used and who it is shared with, how long it is kept, and how to request
deletion. Questions in the meantime: <a href="mailto:{email}">{email}</a> or
{phone}.</p>"""


ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/>'
         '<polyline points="12 5 19 12 12 19"/></svg>')


def head(p, url):
    noindex = '\n<meta name="robots" content="noindex">' if p['slug'] == 'meta-thank-you' else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{lp.e(p['title'])}</title>
<meta name="description" content="{lp.e(p['description'])}">
<link rel="canonical" href="{LEGACY_HOST}{url}">{noindex}
<link rel="icon" href="/images/logo.png">
<link rel="preload" href="/fonts/Inter-Variable.ttf?v={lp.V}" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="/css/style.css?v={lp.V}">
{tracking.head(p['slug'])}
</head>
<body>
{tracking.body(p['slug'])}'''


def crumbs(slug, titles, url_for):
    parts = slug.split('/')
    out = ['<a href="/">Home</a>']
    for i in range(len(parts) - 1):
        pth = '/'.join(parts[:i + 1])
        out.append(f'<a href="{url_for(pth)}">{lp.e(titles.get(pth, pth.replace("-", " ").title()))}</a>')
    out.append(f'<span>{lp.e(titles.get(slug, ""))}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <i>/</i> '.join(out) + '</nav>'


def page_hero(p, slug, titles, url_for):
    img = HERO.get(slug.split('/')[0], 'hero-van.jpg')
    lede = f'<p class="lede">{lp.e(p["description"])}</p>' if p['description'] else ''
    return f'''
<section class="hero hero-lp hero-compact">
  <div class="hero-media">
    <img src="/images/{img}" alt="" class="hero-video">
    <div class="hero-overlay"></div>
  </div>
  <div class="hero-grid-lines"></div>
  <div class="container">
    <div class="hero-content">
      {crumbs(slug, titles, url_for)}
      <h1>{lp.e(p['h1'] or p['title'])}</h1>
      {lede}
      <div class="hero-ctas">
        <a href="{lp.tel()}" class="btn btn-primary">Call {lp.phone()}</a>
        <a href="#quote" class="btn btn-secondary">Get A Free Quote</a>
      </div>
    </div>
  </div>
</section>
'''


def clip(text, cap):
    text = text or ''
    return text if len(text) <= cap else text[:cap].rsplit(' ', 1)[0] + '…'


def link_grid(eyebrow, h2, items, titles, url_for, cap=64):
    if not items:
        return ''
    cards = '\n'.join(
        f'''        <a class="lp-link" href="{url_for(c)}">{lp.e(clip(titles.get(c) or c, cap))}
          {ARROW}
        </a>''' for c in items)
    return f'''
<section class="section-tight bg-soft">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">{lp.e(eyebrow)}</span>
      <h2>{lp.e(h2)}</h2>
    </div>
    <div class="lp-links">
{cards}
    </div>
  </div>
</section>
'''


def quote(slug):
    sfx = 'body-' + re.sub(r'[^a-z0-9]+', '-', slug)[:40].strip('-')
    return f'''
<section class="section-tight bg-black blueprint-bg" id="quote">
  <div class="container" style="max-width:900px;">
    <div class="section-head center">
      <span class="eyebrow">Ready When You Are</span>
      <h2>Get Your Free Quote Today</h2>
      <p>Fill out the form below and our team will follow up directly — or give us a call anytime.</p>
    </div>
    <div class="form-shell">
      {lp.form(sfx, 700, 'Get A Free Quote')}
    </div>
    <div class="quote-contact">
      <a href="{lp.tel()}">Call {lp.phone()}</a>
      <a href="mailto:{lp.EMAIL}">Email Us</a>
    </div>
  </div>
</section>
'''


def render_page(p, url, slug, children, titles, url_for):
    return ''.join([
        head(p, url), lp.chrome_top(), '\n<main>',
        page_hero(p, slug, titles, url_for),
        f'''
<section class="section-tight">
  <div class="container">
    <div class="blog-post-body legacy-prose">
{p['body']}
    </div>
  </div>
</section>
''',
        link_grid('In This Section', 'Explore These Services', children, titles, url_for),
        quote(slug),
        lp.finance_band(),
        '</main>\n', lp.chrome_bottom(),
    ])


def render_post(p, url, slug, i, related, titles, url_for):
    # the post's own featured image if it had one, otherwise cycle our photos
    hero = p.get('lead_img') or '/images/' + POST_HEROES[i % len(POST_HEROES)]
    date = p.get('display_date', '')
    if not date and p['published']:
        y, m, d = p['published'].split('-')
        date = f'{MONTHS[int(m) - 1]} {int(d)}, {y}'
    rel = '\n'.join(
        f'''        <a class="lp-link" href="{url_for(r)}">{lp.e(clip(titles.get(r) or r, 58))}
          {ARROW}
        </a>''' for r in related)
    return ''.join([
        head(p, url), lp.chrome_top(), '\n<main>\n',
        f'''<section class="section-tight" style="padding-top:132px;">
  <div class="container">
    <div class="blog-post-header">
      {'<span class="blog-date">' + date + '</span>' if date else ''}
      <h1 style="margin-top:14px;">{lp.e(p['h1'] or p['title'])}</h1>
    </div>
    <div class="blog-post-hero"><img src="{hero}" alt="{lp.e(p['h1'])}"></div>
    <div class="blog-post-body legacy-prose">
{p['body']}
    </div>
    <div class="blog-post-cta">
      <div class="cta-band">
        <div>
          <h2>Need a plumber in the Inland Empire?</h2>
          <p>Licensed, insured, and available 24/7 — with upfront pricing before we start.</p>
        </div>
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
          <a href="{lp.tel()}" class="btn btn-primary">Call {lp.phone()}</a>
          <a href="#quote" class="btn btn-outline" style="border-color:rgba(255,255,255,0.5); color:#fff;">Free Estimate</a>
        </div>
      </div>
    </div>
    <div class="related-posts">
      <div class="section-head center">
        <span class="eyebrow">Keep Reading</span>
        <h2>More From The Blog</h2>
      </div>
      <div class="lp-links">
{rel}
      </div>
    </div>
  </div>
</section>
''',
        quote(slug), '</main>\n', lp.chrome_bottom(),
    ])



def blog_index(ordered, pages, titles, url_for):
    """Rebuild /blog/ as the index of every post, now living at root-level slugs."""
    cards = []
    for i, sl in enumerate(ordered):
        pg = pages[sl]
        date = pg.get('display_date', '')
        if not date and pg['published']:
            y, m, d = pg['published'].split('-')
            date = f'{MONTHS[int(m) - 1][:3]} {int(d)}, {y}'
        elif date:
            parts = date.split(' ')
            if parts and parts[0] in MONTHS:
                date = parts[0][:3] + ' ' + ' '.join(parts[1:])
        excerpt = pg['description'] or txt(pg['body'])[:170] + '…'
        cards.append(f'''        <a class="blog-card" href="{url_for(sl)}">
          <div class="blog-card-media"><img src="{pg.get('lead_img') or '/images/' + POST_HEROES[i % len(POST_HEROES)]}" alt="{lp.e(titles.get(sl, ""))}" loading="lazy"></div>
          <div class="blog-card-body">
            {'<span class="blog-date">' + lp.e(date) + '</span>' if date else ''}
            <h3>{lp.e(titles.get(sl, ""))}</h3>
            <p>{lp.e(excerpt)}</p>
            <span class="read-more">Read More &rarr;</span>
          </div>
        </a>''')
    p = {'slug': 'blog', 'title': 'Blog / News | Lincoln Plumbing & Rooter',
         'description': ('Practical plumbing advice from our licensed technicians — written for '
                         'Inland Empire homeowners and businesses.')}
    return ''.join([
        head(p, '/blog/'), lp.chrome_top(), '\n<main>\n',
        f'''  <section class="section-tight bg-soft" style="padding-top:132px;">
    <div class="container">
      <div class="section-head center">
        <span class="eyebrow">Blog / News</span>
        <h2>Plumbing Tips &amp; Guides</h2>
        <p>Practical advice from our own licensed technicians — {len(ordered)} articles for Inland Empire homeowners and businesses.</p>
      </div>
    </div>
  </section>
  <section class="section" style="padding-top:56px;">
    <div class="container">
      <div class="blog-grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>
''',
        quote('blog'), '</main>\n', lp.chrome_bottom(),
    ])


def site_index(page_slugs, ordered, titles, url_for, hubs):
    """/sitemap — a human index of everything, mirroring the legacy sitemap page."""
    def group(pred, heading):
        items = [s for s in page_slugs if pred(s)]
        if not items:
            return ''
        lis = '\n'.join(f'        <li><a href="{url_for(s)}">{lp.e(titles.get(s, s))}</a></li>'
                         for s in sorted(items))
        return f'''      <div class="index-col">
        <h3>{lp.e(heading)}</h3>
        <ul>
{lis}
        </ul>
      </div>
'''
    top = '''      <div class="index-col">
        <h3>Main Pages</h3>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/services">Services</a></li>
          <li><a href="/gallery">Photo Gallery</a></li>
          <li><a href="/about">Our Story</a></li>
          <li><a href="/contact">Contact</a></li>
          <li><a href="/blog/">Blog / News</a></li>
          <li><a href="/specials">Specials</a></li>
          <li><a href="/testimonials">Testimonials</a></li>
        </ul>
      </div>
'''
    lps = '\n'.join(f'        <li><a href="/{s}">{lp.e(lp.META[s][0])}</a></li>' for s in lp.SERVICE_SLUGS)
    lpcol = f'''      <div class="index-col">
        <h3>Service Landing Pages</h3>
        <ul>
{lps}
        </ul>
      </div>
'''
    posts = '\n'.join(f'        <li><a href="{url_for(s)}">{lp.e(titles.get(s, s))}</a></li>'
                      for s in ordered)
    cols = (top + lpcol
            + group(lambda s: s.startswith('plumbing-services'), 'Plumbing Services')
            + group(lambda s: s.startswith('drains-and-sewers'), 'Drains & Sewers')
            + group(lambda s: s.startswith('leak-detection'), 'Leak Detection'))
    locs = '\n'.join(f'        <li><a href="{url_for(s)}">{lp.e(titles.get(s, s))}</a></li>'
                      for s in sorted(x for x in page_slugs if x.startswith('service-locations')))
    pg = {'slug': 'sitemap', 'title': 'Sitemap | Lincoln Plumbing & Rooter',
          'description': 'Every page on the Lincoln Plumbing & Rooter site, in one place.'}
    return ''.join([
        head(pg, '/sitemap'), lp.chrome_top(), '\n<main>\n',
        f'''  <section class="section-tight bg-soft" style="padding-top:132px;">
    <div class="container">
      <div class="section-head center">
        <span class="eyebrow">Sitemap</span>
        <h2>Everything On This Site</h2>
      </div>
    </div>
  </section>
  <section class="section-tight">
    <div class="container">
      <div class="index-grid">
{cols}      </div>
      <div class="index-col" style="margin-top:48px;">
        <h3>Service Locations</h3>
        <ul class="index-posts">
{locs}
        </ul>
      </div>
      <div class="index-col" style="margin-top:48px;">
        <h3>Blog / News</h3>
        <ul class="index-posts">
{posts}
        </ul>
      </div>
    </div>
  </section>
''',
        quote('sitemap'), '</main>\n', lp.chrome_bottom(),
    ])


# ------------------------------------------------------------------- assembly
def plan():
    slugs = [l.strip() for l in open(SLUG_FILE) if l.strip()]
    page_slugs, post_slugs = [], []
    for s in slugs:
        if s in SKIP or not os.path.exists(os.path.join(RAW, s.replace('/', '~') + '.html')):
            continue
        (page_slugs if ('/' in s or s in HERO) else post_slugs).append(s)
    hubs = {s for s in page_slugs if any(o.startswith(s + '/') for o in page_slugs)}
    children = {h: sorted(o for o in page_slugs
                          if o.startswith(h + '/') and o.count('/') == h.count('/') + 1)
                for h in hubs}

    def url_for(s):
        return f'/{s}/' if s in hubs else f'/{s}'

    def path_for(s):
        return os.path.join(PUBLIC, s + ('/index.html' if s in hubs else '.html'))

    slug_map = {s: url_for(s) for s in page_slugs + post_slugs}
    slug_map.update({'': '/', 'about': '/about', 'contact': '/contact', 'blog': '/blog/'})
    slug_map.update({s: '/' + s for s in lp.PAGES})
    return page_slugs, post_slugs, hubs, children, url_for, path_for, slug_map


if __name__ == '__main__':
    page_slugs, post_slugs, hubs, children, url_for, path_for, slug_map = plan()

    pages, titles = {}, {}
    for s in page_slugs + post_slugs:
        lp.set_page(s)
        p = extract(os.path.join(RAW, s.replace('/', '~') + '.html'), s, slug_map)
        p['is_post'] = s in post_slugs
        p['url'] = url_for(s)
        pages[s] = p
        titles[s] = p['h1'] or re.split(r' [-|] ', p['title'])[0]

    json.dump(pages, open(os.path.join(ROOT, 'content', 'legacy-scrape', 'all-pages.json'), 'w'),
              indent=2, ensure_ascii=False)

    thin, written = [], 0
    for s in page_slugs:
        lp.set_page(s)
        out = render_page(pages[s], url_for(s), s, children.get(s, []), titles, url_for)
        os.makedirs(os.path.dirname(path_for(s)), exist_ok=True)
        open(path_for(s), 'w').write(re.sub(r'\n{3,}', '\n\n', out))
        written += 1
        if pages[s]['body_chars'] < 400 and s not in hubs:
            thin.append((s, pages[s]['body_chars']))

    ordered = sorted(post_slugs, key=lambda s: pages[s]['published'] or '0000', reverse=True)
    for i, s in enumerate(ordered):
        lp.set_page(s)
        related = [ordered[(i + k) % len(ordered)] for k in (1, 2, 3, 4)]
        out = render_post(pages[s], url_for(s), s, i, related, titles, url_for)
        open(path_for(s), 'w').write(re.sub(r'\n{3,}', '\n\n', out))
        written += 1
        if pages[s]['body_chars'] < 400:
            thin.append((s, pages[s]['body_chars']))

    lp.set_page('blog')
    open(os.path.join(PUBLIC, 'blog', 'index.html'), 'w').write(
        re.sub(r'\n{3,}', '\n\n', blog_index(ordered, pages, titles, url_for)))
    # sitemap.xml + robots.txt — the legacy site's robots.txt pointed at a Yoast
    # sitemap index, so search engines will come looking for one here too.
    lp.set_page('sitemap')
    static_urls = ['/', '/services', '/gallery', '/about', '/contact', '/blog/', '/sitemap']
    all_urls = static_urls + ['/' + s for s in lp.PAGES] + [url_for(s) for s in page_slugs] \
        + [url_for(s) for s in ordered]
    seen_u, xml = set(), ['<?xml version="1.0" encoding="UTF-8"?>',
                          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in all_urls:
        if u in seen_u or u == '/meta-thank-you':
            continue
        seen_u.add(u)
        xml.append(f'  <url><loc>{LEGACY_HOST}{u}</loc></url>')
    xml.append('</urlset>')
    open(os.path.join(PUBLIC, 'sitemap.xml'), 'w').write('\n'.join(xml) + '\n')
    open(os.path.join(PUBLIC, 'robots.txt'), 'w').write(
        'User-agent: *\nAllow: /\n\nSitemap: ' + LEGACY_HOST + '/sitemap.xml\n')
    written += 2

    open(os.path.join(PUBLIC, 'sitemap.html'), 'w').write(
        re.sub(r'\n{3,}', '\n\n', site_index(page_slugs, ordered, titles, url_for, hubs)))
    written += 2

    print(f'{written} files written  ({len(page_slugs)} pages, {len(post_slugs)} posts)')
    print(f'hubs ({len(hubs)}): ' + ', '.join(sorted(hubs)))
    if thin:
        print('THIN/EMPTY BODIES — check these:')
        for s, n in sorted(thin, key=lambda x: x[1]):
            print(f'   {n:5} chars  {s}')
