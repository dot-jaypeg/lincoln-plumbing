#!/usr/bin/env python3
"""Generate the 11 legacy-slug landing pages into public/ from
content/legacy-scrape/pages.json (produced by tools/parse-legacy.py), plus the
new landing pages in content/new-lps.json (e.g. /toilet-overflow).

The legacy WordPress site's copy is retained verbatim; only the chrome
(header/footer/nav), the design system, and the phone/email are this site's.
The GoodLeap financing band and the GHL "Meta Form" embeds are carried over.

Output files are plain, final HTML — same as every other page in public/.
Run:  python3 tools/build-legacy-lps.py
"""
import json, os, re, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracking

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = json.load(open(os.path.join(ROOT, 'content', 'legacy-scrape', 'pages.json')))
# Landing pages written for this site (no legacy original), same shape as
# pages.json and rendered with the same service-LP template.
PAGES.update(json.load(open(os.path.join(ROOT, 'content', 'new-lps.json'))))
PUBLIC = os.path.join(ROOT, 'public')

# ---------------------------------------------------------------- site config
# Cache-bust token: a hash of the asset contents, maintained by
# tools/bump-assets.py. Never hand-edit it — run that script after the builders.
def _asset_version():
    f = os.path.join(ROOT, 'content', 'asset-version.txt')
    return open(f).read().strip() if os.path.exists(f) else 'dev'


V = _asset_version()
# Two numbers, on purpose. The organic site shows the main line; the paid
# landing pages show the Google Ads call-tracking number, which is also the
# number the Ads snippet in tools/tracking.py is configured to swap.
PHONE = '909-780-0887'               # main line — organic pages
TEL = 'tel:19097800887'
LP_PHONE = '909-765-0236'            # call-tracking line — landing pages only
LP_TEL = 'tel:19097650236'
# Landing pages that run on their own Google Ads call number: slug -> (display, tel).
# Any slug not listed here shows the shared LP_PHONE / LP_TEL line above.
# Add a new line to LP_CALL_LINES in tools/tracking.py and CALL_LINES in
# public/thank-you.html too, and give it its own trigger in GTM-KF82PPKL.
LP_OWN_LINE = {
    'toilet-overflow': ('(909) 280-7894', 'tel:+19092807894'),   # Google Ads Call - Flooded Toilets
}

_page = None                        # slug currently being rendered


def set_page(slug):
    """Which page is being built, so phone()/tel() know which number to use."""
    global _page
    _page = slug


def is_lp(slug=None):
    return (slug if slug is not None else _page) in LP_SLUGS


def phone(slug=None):
    slug = slug if slug is not None else _page
    if slug in LP_OWN_LINE:
        return LP_OWN_LINE[slug][0]
    if slug in EMAIL_SLUGS:
        return EMAIL_PHONE
    return LP_PHONE if is_lp(slug) else PHONE


def tel(slug=None):
    slug = slug if slug is not None else _page
    if slug in LP_OWN_LINE:
        return LP_OWN_LINE[slug][1]
    if slug in EMAIL_SLUGS:
        return EMAIL_TEL
    return LP_TEL if is_lp(slug) else TEL
EMAIL = 'contact@lincolnp.com'
FORM_ID = 'dxqfiiA9bB1OLTNaNnRx'     # GHL "Meta Form" — same form on every legacy page
FORM_URL = f'https://link.advancedmarketers.co/widget/form/{FORM_ID}'
FORM_JS = 'https://link.advancedmarketers.co/js/form_embed.js'
GOODLEAP = ('https://www.goodleap.dev/lincolnplumbingandrooterinc/'
            'f5744564-ccff-4b24-838a-3f5c50c41422')

# slug -> (nav label, hero background image, short label for cross-links)
META = {
    'ga-plumbing-services':        ('Plumbing Services', 'work-prep.jpg'),
    'sewer-lines':                 ('Sewer Lines', 'work-commercial-drain.jpg'),
    'ga-tankless-water-heaters':   ('Tankless Water Heaters', 'work-attic-access.jpg'),
    'ga-testimonials':             ('Testimonials', 'team-two-techs.jpg'),
    'ga-water-heater':             ('Water Heaters', 'work-prep.jpg'),
    'ga-about-us':                 ('About Us', 'team-meeting.jpg'),
    'ga-contact':                  ('Contact', 'van-side.jpg'),
    'drain-cleaning':              ('Drain Cleaning', 'work-kitchen-drain.jpg'),
    'ga-garbage-disposal-services': ('Garbage Disposal', 'work-kitchen-repair.jpg'),
    'hydrojetting':                ('Hydrojetting', 'work-commercial-drain.jpg'),
    'ga-leak-detection':           ('Leak Detection', 'work-attic-access.jpg'),
    'toilet-overflow':             ('Toilet Overflow', 'work-bathroom-vanity.jpg'),  # content/new-lps.json
    'drain-cleaning-special':      ('$39 Drain Cleaning', 'work-kitchen-drain.jpg'),  # content/new-lps.json
    # Email-campaign offer pages (content/new-lps.json). Not paid LPs: see EMAIL_SLUGS.
    'holiday-plumbing-prep':       ('Holiday Plumbing Prep', 'lp-holiday-prep.jpg'),
    'water-heater-checkup':        ('Water Heater Checkup', 'lp-water-heater-checkup.jpg'),
    'plumbing-checkup':            ('Plumbing Checkup', 'lp-plumbing-checkup.jpg'),
    'refer-a-neighbor':            ('Refer A Neighbor', 'team-two-techs.jpg'),
}
# Offer pages the email campaigns link to. Paid-LP template and tracking (they
# are in tools/tracking.py's LP_GTM_PAGES: GTM-KF82PPKL, call_line, the GHL Meta
# Form redirecting to /thank-you), noindex like every LP, but kept out of
# LP_SLUGS so they show the email line (EMAIL_PHONE) rather than LP_PHONE.
EMAIL_SLUGS = {'holiday-plumbing-prep', 'water-heater-checkup', 'plumbing-checkup',
               'refer-a-neighbor'}
# The email campaigns' call line, shown on their offer pages (and in the emails,
# PHONE_DISPLAY in tools/build-emails.py). Given 2026-11-03.
EMAIL_PHONE = '909-766-9716'
EMAIL_TEL = 'tel:+19097669716'
# the eight service LPs, in the order they cross-link each other
SERVICE_SLUGS = ['ga-plumbing-services', 'drain-cleaning', 'hydrojetting', 'sewer-lines',
                 'ga-water-heater', 'ga-tankless-water-heaters', 'ga-leak-detection',
                 'ga-garbage-disposal-services']

# Pages that count as paid landing pages: the 11 this builder generates plus the
# two hand-coded paid pages generated by tools/build-legacy-all.py. These are the
# only pages that show the call-tracking number.
LP_SLUGS = (set(META) - EMAIL_SLUGS) | {'lp-job-ad', 'meta-thank-you'}


def e(s):
    """Escape for HTML text/attribute output."""
    return html.escape(s or '', quote=True)


def fix(s):
    """Legacy copy carried over verbatim, except the phone number, which is
    normalised to whichever of the two numbers this page should show."""
    s = s or ''
    for legacy in ('(909) 765-0236', '(909)765-0236', '909-765-0236',
                   '(909) 780-0887', '(909)780-0887', '909-780-0887'):
        s = s.replace(legacy, phone())
    return s


def form(slot, height, title, lazy=None):
    """The GHL Meta Form embed. Only the id suffix varies per placement so two
    embeds on one page don't collide — same convention the legacy site used.

    Form embeds are never lazy-loaded. A `loading="lazy"` iframe is deferred
    past onLoad, and in a HAR from a real visit the hero embed was never
    requested at all — the form simply never appeared. There are at most two
    embeds per page and they are the entire point of the page, so both load
    eagerly."""
    fid = f'inline-{FORM_ID}-{slot}'
    if lazy is None:
        lazy = False
    loading = ' loading="lazy"' if lazy else ''
    return f'''<iframe src="{FORM_URL}" style="width:100%;height:{height}px;border:none" id="{fid}"
          data-layout="{{'id':'INLINE'}}" data-trigger-type="alwaysShow" data-trigger-value=""
          data-activation-type="alwaysActivated" data-activation-value=""
          data-deactivation-type="neverDeactivate" data-deactivation-value=""
          data-form-name="Meta Form" data-height="{height}" data-layout-iframe-id="{fid}"
          data-form-id="{FORM_ID}" title="{e(title)}"{loading}></iframe>'''


# ------------------------------------------------------------------- chrome
SOCIALS = [
    ('https://instagram.com/lincolnplumbingandrooterinc', 'Instagram',
     '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>'),
    ('https://www.facebook.com/profile.php?id=61578362589475', 'Facebook',
     '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>'),
    ('https://tiktok.com/@lincoln.plumbing1', 'TikTok',
     '<path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"/>'),
    ('https://biz.yelp.com/biz_info/-3HGIlGrV7CohN7PS1fmqg', 'Yelp',
     '<path d="M12 2l2.6 5.9 6.4.6-4.9 4.2 1.5 6.3L12 15.9 6.4 19l1.5-6.3-4.9-4.2 6.4-.6z"/>'),
]
PHONE_SVG = ('<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 '
             '19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 '
             '2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 '
             '2.81.7A2 2 0 0 1 22 16.92z"/>')
NAV = [('/', 'Home'), ('/services', 'Services'), ('/gallery', 'Gallery'),
       ('/blog/', 'Blog'), ('/about', 'Our Story'), ('/contact', 'Contact')]


def head(page):
    slug = page['slug']
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(fix(page['title']))}</title>
<meta name="description" content="{e(fix(page['description']))}">
<link rel="canonical" href="https://www.lincolnplumbingandrooter.com/{slug}">
<meta name="robots" content="noindex, follow">
<link rel="icon" href="/images/logo.png">
<link rel="preload" href="/fonts/Inter-Variable.ttf?v={V}" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="/css/style.css?v={V}">
{FLYER_CSS if page.get('layout') == 'flyer' else ''}{tracking.head(slug)}
</head>
<body>
{tracking.body(slug)}'''


def chrome_top():
    nav = '\n      '.join(f'<a href="{h}">{e(l)}</a>' for h, l in NAV)
    mob = '\n    '.join(f'<a href="{h}">{e(l)}</a>' for h, l in NAV)
    top_social = '\n      '.join(
        f'<a href="{h}" target="_blank" rel="noopener">{"Google Reviews" if n == "Instagram" else n}</a>'
        for h, n, _ in SOCIALS[:1]) if False else ''
    return f'''
<div class="top-bar">
  <div class="container">
    <div class="top-bar-left">
      <span>Contractor License #1111400</span>
      <a href="/contact">738 S Waterman Ave C45, San Bernardino, CA 92408</a>
    </div>
    <div class="top-bar-social">
      <a href="https://share.google/dAugpVXgXkDwGv2dv" target="_blank" rel="noopener">Google Reviews</a>
      <a href="https://biz.yelp.com/biz_info/-3HGIlGrV7CohN7PS1fmqg" target="_blank" rel="noopener">Yelp</a>
      <a href="https://instagram.com/lincolnplumbingandrooterinc" target="_blank" rel="noopener">Instagram</a>
      <a href="https://www.facebook.com/profile.php?id=61578362589475" target="_blank" rel="noopener">Facebook</a>
    </div>
  </div>
</div>

<header class="site-header">
  <div class="container">
    <a href="/" class="brand" aria-label="Lincoln Plumbing &amp; Rooter home">
      <img src="/images/logo.png" alt="Lincoln Plumbing &amp; Rooter logo">
    </a>

    <nav class="main-nav" aria-label="Primary">
      {nav}
    </nav>

    <div class="header-actions">
      <a href="#quote" class="btn btn-secondary">Book Free Estimate</a>
      <a href="{tel()}" class="btn-call">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{PHONE_SVG}</svg>
        <span>{phone()}</span>
      </a>
    </div>

    <button class="nav-toggle" aria-label="Open menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
    </button>
  </div>
</header>

<div class="mobile-nav" aria-hidden="true">
  <div class="mobile-nav-top">
    <img src="/images/logo.png" alt="Lincoln Plumbing &amp; Rooter logo">
    <button class="mobile-nav-close" aria-label="Close menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
  </div>
  <nav class="mobile-nav-links" aria-label="Mobile">
    {mob}
  </nav>
  <div class="mobile-nav-cta">
    <a href="{tel()}" class="btn btn-primary btn-block">Call {phone()}</a>
    <a href="#quote" class="btn btn-secondary btn-block">Book a Free Estimate</a>
  </div>
</div>

<div class="mobile-call-bar">
  <a href="{tel()}">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{PHONE_SVG}</svg>
    24/7 Emergency — Call {phone()}
  </a>
</div>
'''


def lp_chrome_top(slug):
    """Chrome for a paid landing page. The legacy LPs carried no navigation at
    all — just an address/phone strip and the logo — so paid traffic had nowhere
    to go but the form or the phone. This keeps that: nothing here links off the
    page, so paid visitors never wander into the organic site (and never see the
    main phone number instead of the tracking one)."""
    return f"""
<div class="lp-topstrip">
  <div class="container">
    <span>Contractor License #1111400</span>
    <span>738 S Waterman Ave C45, San Bernardino, CA 92408</span>
    <span>Open 24 Hours, 7 Days a Week</span>
  </div>
</div>

<header class="lp-header">
  <div class="container">
    <img src="/images/logo.png" alt="Lincoln Plumbing &amp; Rooter logo">
    <div class="lp-header-actions">
      <a href="#quote" class="btn btn-secondary btn-sm">Get A Free Quote</a>
      <a href="{tel()}" class="btn-call">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{PHONE_SVG}</svg>
        <span>{phone()}</span>
      </a>
    </div>
  </div>
</header>

<div class="mobile-call-bar">
  <a href="{tel()}">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{PHONE_SVG}</svg>
    24/7 Emergency — Call {phone()}
  </a>
</div>
"""


def lp_chrome_bottom(slug):
    """One-line footer, as the legacy LPs had. No navigation, no links out."""
    return f"""
<footer class="lp-footer">
  <div class="container">
    <img src="/images/logo.png" alt="Lincoln Plumbing &amp; Rooter logo">
    <p>
      <a href="{tel()}">{phone()}</a> &middot;
      <a href="mailto:{EMAIL}">{EMAIL}</a> &middot;
      738 S Waterman Ave C45, San Bernardino, CA 92408
    </p>
    <p class="lp-footer-legal">
      &copy; 2026 Lincoln Plumbing &amp; Rooter, INC. All rights reserved.
      Contractor License #1111400. Licensed &amp; insured. Available 24/7.
    </p>
  </div>
</footer>

<script src="{FORM_JS}"></script>

</body>
</html>
"""


def chrome_bottom():
    socials = '\n          '.join(
        f'<a href="{h}" target="_blank" rel="noopener" aria-label="{n}">\n'
        f'            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{svg}</svg>\n'
        f'          </a>' for h, n, svg in SOCIALS)
    return f'''
<footer class="site-footer">
  <div class="footer-top">
    <div class="container footer-grid">
      <div class="footer-brand">
        <img src="/images/logo.png" alt="Lincoln Plumbing &amp; Rooter logo">
        <p>Family-owned and operated, serving the Inland Empire with honest, high-quality plumbing since 2021.</p>
        <div class="footer-socials">
          {socials}
        </div>
      </div>

      <div class="footer-col">
        <h4>Quick Links</h4>
        <ul>
          <li><a href="/services">Our Services</a></li>
          <li><a href="/gallery">Photo Gallery</a></li>
          <li><a href="/blog/">Blog / News</a></li>
          <li><a href="/specials">Specials</a></li>
          <li><a href="/testimonials">Testimonials</a></li>
          <li><a href="/about">Our Story</a></li>
          <li><a href="/contact">Contact Us</a></li>
          <li><a href="/sitemap">Sitemap</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4>Browse Services</h4>
        <ul>
          <li><a href="/plumbing-services/">Plumbing Services</a></li>
          <li><a href="/drains-and-sewers/">Drains &amp; Sewers</a></li>
          <li><a href="/plumbing-services/water-heaters/">Water Heaters</a></li>
          <li><a href="/leak-detection/">Leak Detection</a></li>
          <li><a href="/service-locations/">Service Locations</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h4>Contact</h4>
        <ul>
          <li><a href="{tel()}">{phone()}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><address>738 S Waterman Ave C45<br>San Bernardino, CA 92408</address></li>
          <li>24/7 — Emergency Service Available Around the Clock</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="footer-bottom">
    <div class="container">
      <p>&copy; 2026 Lincoln Plumbing &amp; Rooter, INC. All rights reserved.</p>
      <p class="footer-legal-links"><a href="/privacy-policy">Privacy Policy</a></p>
    </div>
  </div>
</footer>

<script src="/js/main.js?v={V}"></script>
<script src="{FORM_JS}"></script>

</body>
</html>
'''


# ------------------------------------------------------------------ sections
def hero(page, form_slot='hero'):
    slug = page['slug']
    h = page['hero']
    img = META[slug][1]
    lines = h['h1_lines']
    h1 = e(fix(lines[0]))
    if len(lines) > 1:
        h1 += '<br><span class="hl">' + e(fix(lines[1])) + '</span>'
    badges = ''.join(f'<span>{e(fix(b))}</span>' for b in h['badges'])
    stats = ''.join(f'<div><b>{e(s["value"])}</b><span>{e(fix(s["label"]))}</span></div>'
                    for s in h['stats'])
    formcard = ''
    if form_slot:
        formcard = f'''
      <div class="hero-form-card">
        <h2>Get A Free Quote</h2>
        <p>Tell us what's going on — our team follows up directly.</p>
        {form(form_slot, 640, 'Get A Free Quote')}
      </div>'''
    return f'''
<section class="hero hero-lp">
  <div class="hero-media">
    <img src="/images/{img}" alt="Lincoln Plumbing &amp; Rooter technician at work" class="hero-video">
    <div class="hero-overlay"></div>
  </div>
  <div class="hero-grid-lines"></div>
  <div class="container hero-split">
    <div class="hero-content">
      {'<div class="lp-badges">' + badges + '</div>' if badges else ''}
      <h1>{h1}</h1>
      {'<p class="lede">' + e(fix(h['lede'])) + '</p>' if h['lede'] else ''}
      <div class="hero-ctas">
        <a href="{tel()}" class="btn btn-primary">Call {phone()}</a>
        <a href="#quote" class="btn btn-secondary">Get A Free Quote</a>
      </div>
      {'<div class="hero-stats">' + stats + '</div>' if stats else ''}
    </div>{formcard}
  </div>
</section>
'''


def marquee(items):
    if not items:
        return ''
    run = ''.join(f'{e(fix(i))}<i>/</i>' for i in items)
    return f'''
<div class="marquee" aria-hidden="true">
  <div class="marquee-track">
    <span>{run}</span><span>{run}</span>
  </div>
</div>
'''


def section_head(d, center=True, dark=False):
    if not d.get('h2'):
        return ''
    cls = 'section-head center' if center else 'section-head'
    return f'''      <div class="{cls}">
        <span class="eyebrow{'' if not dark else ''}">{e(fix(d.get('eyebrow', '')))}</span>
        <h2>{e(fix(d['h2']))}</h2>
        {'<p>' + e(fix(d['sub'])) + '</p>' if d.get('sub') else ''}
      </div>
'''


def signs(d):
    if not d.get('cards'):
        return ''
    cards = '\n'.join(f'''        <div class="service-card">
          <h3>{e(fix(c['title']))}</h3>
          <p>{e(fix(c['body']))}</p>
        </div>''' for c in d['cards'])
    return f'''
<section class="section-tight bg-soft">
  <div class="container">
{section_head(d)}    <div class="services-grid">
{cards}
    </div>
  </div>
</section>
'''


def compare(d):
    if not d.get('cards'):
        return ''
    cols = '\n'.join(f'''        <div class="compare-card{' highlight' if 'highlight' in c['classes'] else ''}">
          <h3>{e(fix(c['title']))}</h3>
          <ul>
{chr(10).join('            <li>' + e(fix(i)) + '</li>' for i in c['items'])}
          </ul>
        </div>''' for c in d['cards'])
    return f'''
<section class="section-tight">
  <div class="container">
{section_head(d)}    <div class="compare-grid">
{cols}
    </div>
  </div>
</section>
'''


def steps(d):
    if not d.get('cards'):
        return ''
    cards = '\n'.join(f'''        <div class="step-card">
          <div class="stepnum">{e(c['num'])}</div>
          <h3>{e(fix(c['title']))}</h3>
          <p>{e(fix(c['body']))}</p>
        </div>''' for c in d['cards'])
    return f'''
<section class="section-tight bg-soft">
  <div class="container">
{section_head(d)}    <div class="step-grid">
{cards}
    </div>
  </div>
</section>
'''


def why(d):
    if not d.get('cards'):
        return ''
    tiles = '\n'.join(f'''        <div class="why-tile">
          <div class="why-ic emoji">{c['icon']}</div>
          <h3>{e(fix(c['title']))}</h3>
          <p>{e(fix(c['body']))}</p>
        </div>''' for c in d['cards'])
    return f'''
<section class="section-tight bg-ink blueprint-bg">
  <div class="container">
{section_head(d)}    <div class="why-grid">
{tiles}
    </div>
  </div>
</section>
'''


def stats_band(items):
    if not items:
        return ''
    cells = '\n'.join(f'''        <div class="counter-item">
          <div class="num">{e(s['value'])}</div>
          <div class="lbl">{e(fix(s['label']))}</div>
        </div>''' for s in items)
    return f'''
<section class="section-sm bg-black">
  <div class="container">
    <div class="counter-row">
{cells}
    </div>
  </div>
</section>
'''


def testimonial(t):
    if not t.get('quote'):
        return ''
    return f'''
<section class="section-tight">
  <div class="container" style="max-width:840px;">
    <div class="testimonial-card">
      <div class="stars" aria-label="5 out of 5 stars">★★★★★</div>
      <p>{e(fix(t['quote']))}</p>
      <div class="testimonial-author"><strong>{e(t['who'])}</strong></div>
    </div>
  </div>
</section>
'''


def area(d):
    if not d.get('chips'):
        return ''
    chips = '\n'.join(f'        <span class="city-chip">{e(c)}</span>' for c in d['chips'])
    return f'''
<section class="section-tight area-band slash-top slash-bottom">
  <div class="container">
    <span class="eyebrow" style="color:rgba(255,255,255,0.9);">{e(fix(d.get('eyebrow', 'Where We Work')))}</span>
    <h2 style="color:#fff; margin-top:16px;">{e(fix(d['h2']))}</h2>
    {'<p class="lede" style="color:rgba(255,255,255,0.9); max-width:720px;">' + e(fix(d['sub'])) + '</p>' if d.get('sub') else ''}
    <div class="city-cloud">
{chips}
    </div>
  </div>
</section>
'''


def cross_links(slug):
    others = [s for s in SERVICE_SLUGS if s != slug]
    cards = '\n'.join(f'''        <a class="lp-link" href="/{s}">{e(META[s][0])}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
        </a>''' for s in others)
    return f'''
<section class="section-tight">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">More From Lincoln</span>
      <h2>Other Services We Offer</h2>
    </div>
    <div class="lp-links">
{cards}
    </div>
  </div>
</section>
'''


def quote_section(d, slot='final', height=700):
    d = d or {}
    return f'''
<section class="section-tight bg-black blueprint-bg" id="quote">
  <div class="container" style="max-width:900px;">
    <div class="section-head center">
      <span class="eyebrow">{e(fix(d.get('eyebrow') or 'Ready When You Are'))}</span>
      <h2>{e(fix(d.get('h2') or 'Get Your Free Quote Today'))}</h2>
      <p>{e(fix(d.get('sub') or "Fill out the form below and our team will follow up directly — or give us a call anytime."))}</p>
    </div>
    <div class="form-shell">
      {form(slot, height, 'Get A Free Quote')}
    </div>
    <div class="quote-contact">
      <a href="{tel()}">Call {phone()}</a>
      <a href="mailto:{EMAIL}">Email Us</a>
    </div>
  </div>
</section>
'''


def finance_band():
    return f'''
<section class="section-tight bg-soft finance-band">
  <div class="container finance-grid">
    <div>
      <span class="eyebrow">Financing</span>
      <h2>Flexible Payment Options With GoodLeap</h2>
      <p>We have partnered with GoodLeap to offer flexible payment options for your project. GoodLeap uses a soft credit check until funding and the highest score from all 3 bureaus to see if you qualify. It also takes just a few minutes to get started.</p>
      <a href="{GOODLEAP}" target="_blank" rel="noopener" class="btn btn-primary">Get Started</a>
    </div>
    <div class="finance-note">
      <strong>Soft credit check</strong>
      <span>No impact to your score until funding</span>
      <strong>Minutes to apply</strong>
      <span>Uses the highest score from all 3 bureaus</span>
    </div>
  </div>
</section>
'''


# --------------------------------------------------------- page-specific bits
def services_grid(d):
    if not d.get('cards'):
        return ''
    link_for = {'Plumbing Services': '/ga-plumbing-services',
                'Drains & Sewers': '/drain-cleaning',
                'Leak Detection': '/ga-leak-detection',
                'Sewer Line Repair': '/sewer-lines',
                'Water Heaters': '/ga-water-heater'}
    cards = []
    for c in d['cards']:
        href = link_for.get(c['title'])
        link = (f'\n          <a class="service-link" href="{href}">Learn more '
                '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>') if href else ''
        cards.append(f'''        <div class="service-card">
          <h3>{e(fix(c['title']))}</h3>
          <p>{e(fix(c['body']))}</p>{link}
        </div>''')
    return f'''
<section class="section-tight bg-soft">
  <div class="container">
{section_head(d)}    <div class="services-grid">
{chr(10).join(cards)}
    </div>
  </div>
</section>
'''


def commitment_section():
    return f'''
<section class="section-tight">
  <div class="container" style="max-width:900px;">
    <div class="section-head center">
      <span class="eyebrow">Our Commitment</span>
      <h2>Discover Our Commitment To Quality Service</h2>
    </div>
    <p class="lede">Plumbing is an essential part of maintaining a safe and comfortable home or business environment. From routine maintenance to emergency repairs, our skilled plumbers are equipped to handle all types of plumbing issues.</p>
    <p class="lede" style="margin-top:18px;">We offer comprehensive services that ensure your plumbing systems function smoothly, preventing costly damages and providing you with peace of mind — for both residential and commercial clients throughout San Bernardino and the Inland Empire.</p>
    <div style="margin-top:32px;"><a href="{tel()}" class="btn btn-primary">Call {phone()}</a></div>
  </div>
</section>
'''


def yelp_section(page):
    revs = page['yelp_reviews']
    if not revs:
        return ''
    slides = '\n'.join(f'''        <div class="yelp-slide">
          <span class="yelp-review" data-review-id="{r['review_id']}" data-hostname="www.yelp.com">Read <a href="https://www.yelp.com/user_details?userid={r['user_id']}" rel="nofollow noopener">{e(r['name'])}</a>'s <a href="https://www.yelp.com/biz/lincoln-plumbing-and-rooter-san-bernardino-2?hrid={r['review_id']}" rel="nofollow noopener">review</a> of <a href="https://www.yelp.com/biz/-3HGIlGrV7CohN7PS1fmqg" rel="nofollow noopener">Lincoln Plumbing &amp; Rooter</a> on <a href="https://www.yelp.com" rel="nofollow noopener">Yelp</a></span>
        </div>''' for r in revs)
    return f'''
<section class="section-tight bg-soft">
  <div class="container">
      <div class="section-head center">
        <span class="eyebrow">Straight From Yelp</span>
        <h2>Real Reviews From Real Customers</h2>
      </div>
    <div class="yelp-grid">
{slides}
    </div>
  </div>
</section>

<script async src="https://www.yelp.com/embed/widgets.js"></script>
'''


def review_cta(page):
    links = '\n'.join(
        f'        <a href="{l["href"]}" target="_blank" rel="noopener" class="btn btn-outline">{e(l["label"])}</a>'
        for l in page['platform_links'])
    return f'''
<section class="section-tight">
  <div class="container" style="max-width:840px; text-align:center;">
    <span class="eyebrow">Worked With Us Before?</span>
    <h2 style="margin-top:16px;">Leave Us A Review</h2>
    <p class="lede">If we've taken care of you, we'd genuinely appreciate you sharing your experience — it helps other homeowners in the Inland Empire find us.</p>
    <div class="platform-row">
{links}
    </div>
  </div>
</section>
'''


def info_cards(page):
    cards = []
    for c in page['info_cards']:
        body = fix(c['body'])
        if 'Call Us' == c['title']:
            inner = f'<a href="{tel()}">{phone()}</a>'
        elif 'Email Us' == c['title']:
            inner = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
        else:
            inner = '<p>' + e(body).replace(' | ', '<br>') + '</p>'
        cards.append(f'''        <div class="info-card">
          <div class="info-ic emoji">{c['icon']}</div>
          <h3>{e(c['title'])}</h3>
          {inner}
        </div>''')
    return f'''
<section class="section-tight">
  <div class="container">
    <div class="info-grid">
{chr(10).join(cards)}
    </div>
  </div>
</section>
'''


def contact_form_map():
    return f'''
<section class="section-tight bg-soft" id="quote">
  <div class="container contact-layout">
    <div>
      <span class="eyebrow">Get In Touch</span>
      <h2 style="margin-top:16px;">Send Us A Message</h2>
      <p>Fill out the form and our team will follow up directly, usually within one business day.</p>
      <div class="form-shell light">
        {form('contact', 700, 'Contact Us', lazy=False)}
      </div>
    </div>
    <div class="map-panel">
      <iframe src="https://www.google.com/maps?q=738+S+Waterman+Ave+%23C45,+San+Bernardino,+CA+92408&amp;output=embed"
        title="Lincoln Plumbing &amp; Rooter location" loading="lazy" allowfullscreen
        referrerpolicy="no-referrer-when-downgrade"></iframe>
    </div>
  </div>
</section>
'''


def simple_cta(eyebrow, h2, sub):
    return f'''
<section class="section-tight bg-black blueprint-bg" id="quote">
  <div class="container" style="max-width:820px; text-align:center;">
    <span class="eyebrow">{e(eyebrow)}</span>
    <h2 style="margin-top:16px;">{e(h2)}</h2>
    <p>{e(sub)}</p>
    <div class="hero-ctas" style="justify-content:center;">
      <a href="{tel()}" class="btn btn-primary">Call {phone()}</a>
      <a href="mailto:{EMAIL}" class="btn btn-secondary">Email Us</a>
    </div>
  </div>
</section>
'''


# ------------------------------------------------------------- flyer layout
# Promo LPs with "layout": "flyer" in content/new-lps.json (first:
# /drain-cleaning-special). Modelled on the Octo /120-drain-cleaning and
# capridrains.com promo pages: full-width hero photo, one big poster-style
# coupon with a big call button under it, a short services list, icon cards,
# real job photos, reviews and a call-me-back form. Same GHL Meta Form, call
# line and tracking as every other LP; only the page body differs.
#
# The hero and coupon take an image when one exists ("hero_image",
# "coupon.image"). Until then the coupon is drawn in HTML/CSS. Styles are
# inlined in <head> so style.css (and every page's asset hash) is untouched.
FLYER_CSS = """<style>
  .fl { --fl-navy: #0a2047; --fl-navy-2: #123a7a; --fl-cream: #f6f1e7; --fl-red: #d92d20; }
  .fl-head { position: sticky; top: 0; z-index: 50; background: linear-gradient(#26262a, #121212);
    border-bottom: 3px solid var(--orange); }
  .fl-head .container { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 76px; }
  .fl-head img { height: 54px; width: auto; }
  .fl-open { display: flex; align-items: center; gap: 8px; color: #fff; font-weight: 700; font-size: 0.82rem;
    letter-spacing: 0.06em; text-transform: uppercase; }
  .fl-open::before { content: ''; width: 9px; height: 9px; border-radius: 50%; background: #22c55e;
    box-shadow: 0 0 0 4px rgba(34,197,94,0.25); }
  .fl-head-actions { display: flex; gap: 10px; align-items: center; }
  .fl-btn { display: inline-flex; align-items: center; justify-content: center; gap: 10px; min-height: 44px;
    padding: 10px 20px; border-radius: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.02em;
    text-decoration: none; border: 2px solid transparent; line-height: 1.1; }
  .fl-btn-call { background: linear-gradient(180deg, #ff9d2e, #e85f00); color: #fff; border-color: #b84a00;
    box-shadow: 0 4px 0 #8a3800, 0 10px 24px rgba(232,95,0,0.35); text-shadow: 0 1px 0 rgba(0,0,0,0.3); }
  .fl-btn-call:hover { filter: brightness(1.06); color: #fff; }
  .fl-btn-dark { background: #000; color: #fff; border-color: rgba(255,255,255,0.35); }
  .fl-btn-dark:hover { background: #fff; color: #000; }
  .fl-btn svg { flex: none; }
  .fl-btn-xl { width: 100%; font-size: clamp(1.35rem, 4.6vw, 1.9rem); padding: 18px 22px; border-radius: 14px; }
  .fl :focus-visible { outline: 3px solid var(--blue); outline-offset: 3px; }
  .skip-link { position: absolute; left: 12px; top: -60px; z-index: 100; background: #fff; color: #000;
    padding: 10px 16px; border-radius: 8px; font-weight: 700; }
  .skip-link:focus { top: 12px; }

  .fl-hero { position: relative; background: #121212; height: clamp(250px, 40vw, 600px); overflow: hidden; }
  .fl-hero > img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .fl-sticker { position: absolute; top: 18px; left: clamp(12px, 4vw, 48px); transform: rotate(-6deg);
    background: #fff; color: #111; border: 3px solid #111; border-radius: 12px; padding: 8px 14px; text-align: center;
    font-family: var(--font-heading); font-weight: 700; text-transform: uppercase; line-height: 1.05;
    box-shadow: 4px 4px 0 #111; font-size: clamp(0.8rem, 1.6vw, 1.15rem); }
  .fl-sticker .stars { color: #f5a400; letter-spacing: 2px; display: block; font-size: 1.1em; }
  .fl-plate { position: absolute; left: 50%; bottom: clamp(14px, 3vw, 36px); transform: translateX(-50%);
    background: rgba(10,10,10,0.82); border: 2px solid var(--orange); border-radius: 10px; color: #fff;
    padding: 8px 22px; text-align: center; white-space: nowrap; font-family: var(--font-heading); font-weight: 700;
    text-transform: uppercase; font-style: italic; font-size: clamp(1rem, 2.6vw, 1.9rem); letter-spacing: 0.02em; }
  .fl-plate small { display: block; font-size: 0.5em; color: var(--orange-2); font-style: normal; letter-spacing: 0.12em; }

  .fl-h { font-family: var(--font-heading); font-weight: 700; font-style: italic; text-transform: uppercase;
    letter-spacing: 0.01em; line-height: 1; color: #111; text-align: center; font-size: clamp(2rem, 5vw, 3rem); }
  .fl-sub { text-align: center; color: var(--orange-dark); font-family: var(--font-heading); font-weight: 700;
    font-style: italic; text-transform: uppercase; font-size: clamp(1rem, 2.4vw, 1.3rem); margin-top: 6px; }
  .fl-sec { padding: clamp(48px, 7vw, 72px) 0; }
  .fl-cream { background: var(--fl-cream); }
  .fl-white { background: #fff; }
  .fl-stone { background: #e9e6e1; }

  .fl-offer .container { max-width: 520px; text-align: center; }
  .fl-offer h1 { font-family: var(--font-heading); font-weight: 700; font-style: italic; text-transform: uppercase;
    font-size: clamp(1.6rem, 5vw, 2.3rem); line-height: 1.05; color: #111; margin-bottom: 18px; }
  .fl-offer h1 span { color: var(--orange-dark); display: block; }
  .fl-coupon-wrap { border: 3px solid #111; border-radius: 16px; padding: 6px; background: #111;
    box-shadow: 0 18px 40px rgba(0,0,0,0.28); transform: rotate(-1deg); }
  .fl-coupon-wrap img { width: 100%; height: auto; display: block; border-radius: 11px; }
  .fl-coupon { position: relative; overflow: hidden; border-radius: 11px; color: #fff; padding: 30px 18px 0;
    background:
      radial-gradient(circle at 18% 22%, rgba(120,200,255,0.55) 0 3px, transparent 4px),
      radial-gradient(circle at 82% 16%, rgba(120,200,255,0.55) 0 4px, transparent 5px),
      radial-gradient(circle at 90% 46%, rgba(120,200,255,0.45) 0 3px, transparent 4px),
      radial-gradient(circle at 10% 58%, rgba(120,200,255,0.45) 0 5px, transparent 6px),
      radial-gradient(ellipse at 50% 112%, #59b8ff 0%, rgba(30,120,230,0.6) 30%, transparent 62%),
      linear-gradient(180deg, var(--fl-navy-2) 0%, var(--fl-navy) 70%); }
  .fl-coupon-kicker { font-family: var(--font-heading); font-weight: 700; font-style: italic; text-transform: uppercase;
    font-size: clamp(2.2rem, 9vw, 3.3rem); line-height: 0.95; text-shadow: 3px 3px 0 #000, 0 0 18px rgba(0,0,0,0.4); }
  .fl-coupon-price { font-family: var(--font-heading); font-weight: 700; font-style: italic; line-height: 0.85;
    font-size: clamp(6.5rem, 30vw, 9.5rem); color: #fff; margin-top: 6px;
    text-shadow: 0 4px 0 #e85f00, 0 8px 0 #8a3800, 0 14px 26px rgba(0,0,0,0.55); }
  .fl-coupon-price sup { font-size: 0.45em; vertical-align: top; position: relative; top: 0.18em; }
  .fl-coupon-pill { display: inline-block; margin-top: 16px; background: #000; border: 2px solid rgba(255,255,255,0.6);
    border-radius: 999px; padding: 6px 16px; font-weight: 800; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; }
  .fl-coupon-ribbon { margin: 16px -30px 0; transform: rotate(-3deg); background: linear-gradient(90deg, #e85f00, #ff9d2e, #e85f00);
    color: #fff; padding: 10px 30px; font-family: var(--font-heading); font-weight: 700; font-style: italic; text-transform: uppercase;
    font-size: clamp(1.25rem, 5vw, 1.7rem); text-shadow: 2px 2px 0 rgba(0,0,0,0.45); box-shadow: 0 6px 14px rgba(0,0,0,0.35); }
  .fl-coupon-drain { display: block; margin: 16px auto 4px; width: 62%; max-width: 230px; height: auto; }
  .fl-coupon-strip { margin: 0 -18px; background: #000; padding: 10px; font-weight: 800; font-size: 0.82rem;
    letter-spacing: 0.08em; text-transform: uppercase; }
  .fl-offer .fl-btn-xl { margin-top: 26px; }
  .fl-alert { display: flex; gap: 10px; align-items: flex-start; text-align: left; margin-top: 14px; border: 2px solid var(--orange);
    background: #fff; border-radius: 10px; padding: 10px 14px; color: var(--fl-red); font-weight: 700; font-size: 0.92rem; line-height: 1.35; }
  .fl-alert::before { content: ''; flex: none; width: 10px; height: 10px; margin-top: 5px; border-radius: 50%; background: var(--fl-red);
    box-shadow: 0 0 0 4px rgba(217,45,32,0.18); }
  .fl-fine { margin-top: 14px; font-size: 0.82rem; color: #4a4a4a; line-height: 1.5; }
  .fl-fine a { color: var(--orange-dark); font-weight: 700; }

  .fl-list { list-style: none; padding: 0; margin: 34px auto 0; max-width: 760px; display: grid;
    grid-template-columns: 1fr 1fr; gap: 0 34px; }
  .fl-list li { display: flex; gap: 10px; align-items: center; padding: 11px 0; border-bottom: 1px solid #e3ded4;
    font-weight: 700; color: #1b1b1b; }
  .fl-list li svg { flex: none; color: var(--blue); }

  .fl-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 34px; }
  .fl-card { background: #fff; border: 2px solid var(--orange); border-radius: 12px; padding: 20px; }
  .fl-card .ic { width: 40px; height: 40px; display: grid; place-items: center; border-radius: 10px;
    background: var(--orange-light); color: var(--orange-dark); border: 1px solid #f3c99b; }
  .fl-card h3 { margin-top: 14px; font-size: 1.05rem; color: #111; }
  .fl-card p { margin-top: 6px; font-size: 0.92rem; color: #4a4a4a; line-height: 1.5; }

  .fl-row-head { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
  .fl-row-head .fl-h { text-align: left; }
  .fl-tag { background: #fff; border: 1px solid #cfc8bb; border-radius: 999px; padding: 6px 14px; font-size: 0.74rem;
    font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: #333; }
  .fl-jobs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 28px; }
  .fl-job { background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #d9d3c7; }
  .fl-job img { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; display: block; }
  .fl-job p { display: flex; gap: 8px; align-items: center; padding: 12px 14px; font-weight: 700; color: #1b1b1b; font-size: 0.95rem; }
  .fl-job p svg { color: var(--success); flex: none; }

  .fl-reviews { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 28px; }
  .fl-review { background: #fff; border-radius: 14px; padding: 22px; border: 1px solid #e3e3e3;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06); display: flex; flex-direction: column; }
  .fl-review .stars { color: #f5a400; letter-spacing: 3px; font-size: 1.05rem; }
  .fl-review blockquote { margin: 12px 0 0; color: #222; line-height: 1.55; font-size: 0.95rem; flex: 1; }
  .fl-review cite { display: block; margin-top: 16px; font-style: normal; font-weight: 800; color: #111; }
  .fl-review cite small { display: block; font-weight: 600; color: #666; margin-top: 2px; }

  .fl-cta { display: grid; grid-template-columns: 1fr 1.1fr; gap: 40px; align-items: center; }
  .fl-cta .fl-h { text-align: left; }
  .fl-cta-copy p { margin-top: 14px; color: #333; font-size: 1.02rem; line-height: 1.55; }
  .fl-cta-copy .fl-btn-call { margin-top: 22px; font-size: 1.25rem; padding: 14px 24px; }
  .fl-form { background: linear-gradient(#1f1f23, #111); border-radius: 16px; padding: 22px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
  .fl-form h2 { font-family: var(--font-heading); font-weight: 700; font-style: italic; text-transform: uppercase; color: #fff;
    font-size: clamp(1.7rem, 4vw, 2.2rem); line-height: 1; }
  .fl-form > p { color: rgba(255,255,255,0.75); margin-top: 6px; font-size: 0.92rem; }
  .fl-form-promo { display: flex; gap: 10px; align-items: center; margin-top: 14px; border: 1px dashed var(--orange-2);
    background: rgba(255,123,0,0.12); border-radius: 10px; padding: 10px 12px; color: #fff; font-weight: 800; font-size: 0.86rem;
    text-transform: uppercase; letter-spacing: 0.03em; }
  .fl-form-promo small { display: block; color: var(--orange-2); font-size: 0.7rem; letter-spacing: 0.1em; }
  .fl-form-frame { margin-top: 14px; background: #fff; border-radius: 12px; overflow: hidden; }
  .fl-form-note { margin-top: 12px; text-align: center; color: rgba(255,255,255,0.75); font-size: 0.9rem; }
  .fl-form-note a { color: var(--orange-2); font-weight: 800; }

  @media (max-width: 900px) {
    .fl-open { display: none; }
    .fl-head .fl-btn-dark { display: none; }
    .fl-cards, .fl-jobs, .fl-reviews { grid-template-columns: 1fr 1fr; }
    .fl-cta { grid-template-columns: 1fr; }
    .fl-cta .fl-h, .fl-cta-copy { text-align: center; }
  }
  @media (max-width: 600px) {
    .fl-head img { height: 44px; }
    .fl-head .fl-btn-call { padding: 8px 12px; font-size: 0.9rem; }
    .fl-list { grid-template-columns: 1fr; }
    .fl-cards, .fl-jobs, .fl-reviews { grid-template-columns: 1fr; }
    .fl-row-head { justify-content: center; }
    .fl-row-head .fl-h { text-align: center; }
    .fl-plate { white-space: normal; width: max-content; max-width: 92%; }
  }
</style>
"""

# Small line icons (24x24, stroke) for the flyer's lists and cards.
ICONS = {
    'drop':   '<path d="M12 2.7s-6 6.6-6 11a6 6 0 0 0 12 0c0-4.4-6-11-6-11z"/>',
    'check':  '<polyline points="20 6 9 17 4 12"/>',
    'tag':    '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    'clock':  '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
    'home':   '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    'bolt':   '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    'pin':    '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    'card':   '<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>',
    'star':   '<polygon points="12 2 15 8.5 22 9.3 17 14 18.2 21 12 17.8 5.8 21 7 14 2 9.3 9 8.5 12 2"/>',
}


def icon(name, size=18):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def call_btn(cls='fl-btn fl-btn-call', size=20):
    return (f'<a href="{tel()}" class="{cls}"><svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{PHONE_SVG}</svg>{phone()}</a>')


def flyer_top():
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<header class="fl-head">
  <div class="container">
    <img src="/images/logo.png" alt="Lincoln Plumbing &amp; Rooter">
    <span class="fl-open">Open Now &middot; Emergency Line 24/7</span>
    <div class="fl-head-actions">
      {call_btn()}
      <a href="#quote" class="fl-btn fl-btn-dark">Get A Free Quote</a>
    </div>
  </div>
</header>

<div class="mobile-call-bar">
  <a href="{tel()}">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{PHONE_SVG}</svg>
    24/7 Emergency: Call {phone()}
  </a>
</div>
"""


def flyer_hero(p):
    h = p['hero']
    sticker = ''
    if h.get('sticker'):
        sticker = (f'<div class="fl-sticker"><span class="stars" aria-hidden="true">★★★★★</span>'
                   f'{e(fix(h["sticker"]))}</div>')
    plate = ''
    if h.get('plate'):
        plate = (f'<div class="fl-plate">{e(fix(h["plate"]))}'
                 f'{"<small>" + e(fix(h["plate_small"])) + "</small>" if h.get("plate_small") else ""}</div>')
    pos = h.get('image_position', 'center')
    return f"""
<section class="fl-hero">
  <img src="/images/{e(h['image'])}" alt="{e(fix(h['alt']))}" style="object-position:{e(pos)}" fetchpriority="high">
  {sticker}
  {plate}
</section>
"""


DRAIN_SVG = """<svg class="fl-coupon-drain" viewBox="0 0 240 120" aria-hidden="true">
          <g stroke="#bfe6ff" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.9">
            <path d="M120 70 Q120 30 120 6"/><path d="M120 70 Q98 34 72 14"/><path d="M120 70 Q142 34 168 14"/>
            <path d="M120 70 Q80 46 40 40"/><path d="M120 70 Q160 46 200 40"/>
          </g>
          <ellipse cx="120" cy="92" rx="92" ry="22" fill="#9aa4b1" stroke="#e6ebf1" stroke-width="4"/>
          <ellipse cx="120" cy="92" rx="70" ry="15" fill="#2b313a"/>
          <g stroke="#c9d1db" stroke-width="5">
            <line x1="72" y1="92" x2="168" y2="92"/><line x1="88" y1="81" x2="88" y2="103"/>
            <line x1="104" y1="78" x2="104" y2="106"/><line x1="120" y1="77" x2="120" y2="107"/>
            <line x1="136" y1="78" x2="136" y2="106"/><line x1="152" y1="81" x2="152" y2="103"/>
          </g>
        </svg>"""


def flyer_offer(p):
    c = p['coupon']
    if c.get('image'):
        art = f'<img src="/images/{e(c["image"])}" alt="{e(fix(c["alt"]))}" width="{c.get("width", 1000)}" height="{c.get("height", 1250)}">'
    else:
        art = f"""<div class="fl-coupon" role="img" aria-label="{e(fix(c['alt']))}">
        <div class="fl-coupon-kicker" aria-hidden="true">{e(fix(c['kicker']))}</div>
        <div class="fl-coupon-price" aria-hidden="true"><sup>$</sup>{e(c['price'])}</div>
        <div class="fl-coupon-pill" aria-hidden="true">{e(fix(c['pill']))}</div>
        <div class="fl-coupon-ribbon" aria-hidden="true">{e(fix(c['ribbon']))}</div>
        {DRAIN_SVG}
        <div class="fl-coupon-strip" aria-hidden="true">{e(fix(c['strip']))}</div>
      </div>"""
    h1 = p['h1']
    return f"""
<section class="fl-sec fl-cream fl-offer" id="offer">
  <div class="container">
    <h1>{e(fix(h1[0]))} <span>{e(fix(h1[1]))}</span></h1>
    <div class="fl-coupon-wrap">
      {art}
    </div>
    {call_btn('fl-btn fl-btn-call fl-btn-xl', 30)}
    <p class="fl-alert">{e(fix(p['alert']))}</p>
    <p class="fl-fine">{e(fix(p['terms']))} <a href="#quote">Or request service online</a></p>
  </div>
</section>
"""


def flyer_services(d):
    items = '\n'.join(f'      <li>{icon("drop")}{e(fix(i))}</li>' for i in d['items'])
    return f"""
<section class="fl-sec fl-white">
  <div class="container">
    <h2 class="fl-h">{e(fix(d['h2']))}</h2>
    <p class="fl-sub">{e(fix(d['sub']))}</p>
    <ul class="fl-list">
{items}
    </ul>
  </div>
</section>
"""


def flyer_why(d):
    cards = '\n'.join(f"""      <div class="fl-card">
        <div class="ic">{icon(c['icon'], 20)}</div>
        <h3>{e(fix(c['title']))}</h3>
        <p>{e(fix(c['body']))}</p>
      </div>""" for c in d['cards'])
    return f"""
<section class="fl-sec fl-cream">
  <div class="container">
    <h2 class="fl-h">{e(fix(d['h2']))}</h2>
    <div class="fl-cards">
{cards}
    </div>
  </div>
</section>
"""


def flyer_jobs(d):
    items = '\n'.join(f"""      <figure class="fl-job">
        <img src="/images/{e(j['image'])}" alt="{e(fix(j['alt']))}" loading="lazy">
        <p>{icon('check')}{e(fix(j['caption']))}</p>
      </figure>""" for j in d['items'])
    return f"""
<section class="fl-sec fl-stone">
  <div class="container">
    <div class="fl-row-head">
      <h2 class="fl-h">{e(fix(d['h2']))}</h2>
      <span class="fl-tag">{e(fix(d['tag']))}</span>
    </div>
    <div class="fl-jobs">
{items}
    </div>
  </div>
</section>
"""


def flyer_reviews(d):
    items = '\n'.join(f"""      <figure class="fl-review">
        <div class="stars" aria-label="5 out of 5 stars">★★★★★</div>
        <blockquote>&ldquo;{e(r['quote'])}&rdquo;</blockquote>
        <figcaption><cite>{e(r['who'])}<small>{e(r['service'])}</small></cite></figcaption>
      </figure>""" for r in d['items'])
    return f"""
<section class="fl-sec fl-white">
  <div class="container">
    <h2 class="fl-h">{e(fix(d['h2']))}</h2>
    <p class="fl-sub">{e(fix(d['sub']))}</p>
    <div class="fl-reviews">
{items}
    </div>
  </div>
</section>
"""


def flyer_cta(d):
    return f"""
<section class="fl-sec fl-cream" id="quote">
  <div class="container fl-cta">
    <div class="fl-cta-copy">
      <h2 class="fl-h">{e(fix(d['h2']))}</h2>
      <p>{e(fix(d['sub']))}</p>
      {call_btn()}
      <p class="fl-alert">{e(fix(d['alert']))}</p>
    </div>
    <div class="fl-form">
      <h2>{e(fix(d['form_h']))}</h2>
      <p>{e(fix(d['form_sub']))}</p>
      <div class="fl-form-promo">{icon('tag', 20)}<span><small>Offer Applied</small>{e(fix(d['promo']))}</span></div>
      <div class="fl-form-frame">
        {form('final', 640, d['form_h'])}
      </div>
      <p class="fl-form-note">Or call <a href="{tel()}">{phone()}</a></p>
    </div>
  </div>
</section>
"""


def build_flyer(p):
    return [flyer_top(), '\n<main id="main" class="fl">',
            flyer_hero(p), flyer_offer(p), flyer_services(p['services']),
            flyer_why(p['why']), flyer_jobs(p['jobs']), flyer_reviews(p['reviews']),
            flyer_cta(p['cta'])]


# ------------------------------------------------------------------- assembly
def build(slug):
    set_page(slug)
    p = PAGES[slug]
    parts = [head(p)]
    if p.get('layout') == 'flyer':
        parts += build_flyer(p)
    else:
        parts += [lp_chrome_top(slug), '\n<main>']

    if p.get('layout') == 'flyer':
        pass
    elif slug == 'ga-about-us':
        parts += [hero(p, form_slot=None), marquee(p['ticker']),
                  commitment_section(), why(p['why']), stats_band(p['stats_grid']),
                  services_grid(p['services']), testimonial(p['testimonial']),
                  cross_links(slug), finance_band(),
                  simple_cta("Ready When You Are", "Let's Get Your Plumbing Sorted",
                             "Reach out today and our team will follow up directly — or give us a call anytime.")]
    elif slug == 'ga-testimonials':
        parts += [hero(p, form_slot=None), marquee(p['ticker']),
                  yelp_section(p), why(p['why']), review_cta(p),
                  cross_links(slug), finance_band(),
                  simple_cta("Ready When You Are", "Join Our List Of Happy Customers",
                             "Reach out today and our team will follow up directly — or give us a call anytime.")]
    elif slug == 'ga-contact':
        parts += [hero(p, form_slot=None), info_cards(p), contact_form_map(),
                  cross_links(slug), finance_band()]
    else:
        parts += [hero(p), marquee(p['ticker']),
                  signs(p['signs']), services_grid(p['services']),
                  compare(p['compare']), steps(p['how']), why(p['why']),
                  testimonial(p['testimonial']), area(p['area']),
                  cross_links(slug), finance_band(),
                  quote_section(p['quote_cta'])]

    parts += ['</main>\n', lp_chrome_bottom(slug)]
    out = ''.join(parts)
    out = re.sub(r'\n{3,}', '\n\n', out)
    path = os.path.join(PUBLIC, slug + '.html')
    open(path, 'w').write(out)
    return path, len(out)


if __name__ == '__main__':
    # `build-legacy-lps.py toilet-overflow` rebuilds just that page. Prefer it:
    # /ga-plumbing-services has been hand-edited since it was generated, and a
    # full rebuild overwrites it.
    for slug in sys.argv[1:] or PAGES:
        path, n = build(slug)
        print(f'{os.path.basename(path):34} {n:>7,} bytes')
