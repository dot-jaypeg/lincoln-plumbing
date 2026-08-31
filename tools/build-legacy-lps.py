#!/usr/bin/env python3
"""Generate the 11 legacy-slug landing pages into public/ from
content/legacy-scrape/pages.json (produced by tools/parse-legacy.py).

The legacy WordPress site's copy is retained verbatim; only the chrome
(header/footer/nav), the design system, and the phone/email are this site's.
The GoodLeap financing band and the GHL "Meta Form" embeds are carried over.

Output files are plain, final HTML — same as every other page in public/.
Run:  python3 tools/build-legacy-lps.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = json.load(open(os.path.join(ROOT, 'content', 'legacy-scrape', 'pages.json')))
PUBLIC = os.path.join(ROOT, 'public')

# ---------------------------------------------------------------- site config
V = 'static-4'                       # cache-bust token, must match public/*.html
PHONE = '909-780-0887'               # this site's number (legacy site used 909-765-0236)
TEL = 'tel:19097800887'
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
}
# the eight service LPs, in the order they cross-link each other
SERVICE_SLUGS = ['ga-plumbing-services', 'drain-cleaning', 'hydrojetting', 'sewer-lines',
                 'ga-water-heater', 'ga-tankless-water-heaters', 'ga-leak-detection',
                 'ga-garbage-disposal-services']


def e(s):
    """Escape for HTML text/attribute output."""
    return html.escape(s or '', quote=True)


def fix(s):
    """Legacy copy carried over verbatim, except the phone number, which is
    replaced with this site's number so the whole site is consistent."""
    s = s or ''
    s = s.replace('(909) 765-0236', PHONE).replace('(909)765-0236', PHONE)
    return s


def form(slot, height, title):
    """The GHL Meta Form embed. Only the id suffix varies per placement so two
    embeds on one page don't collide — same convention the legacy site used."""
    fid = f'inline-{FORM_ID}-{slot}'
    return f'''<iframe src="{FORM_URL}" style="width:100%;height:{height}px;border:none" id="{fid}"
          data-layout="{{'id':'INLINE'}}" data-trigger-type="alwaysShow" data-trigger-value=""
          data-activation-type="alwaysActivated" data-activation-value=""
          data-deactivation-type="neverDeactivate" data-deactivation-value=""
          data-form-name="Meta Form" data-height="{height}" data-layout-iframe-id="{fid}"
          data-form-id="{FORM_ID}" title="{e(title)}" loading="lazy"></iframe>'''


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
<link rel="icon" href="/images/logo.png">
<link rel="preload" href="/fonts/Inter-Variable.ttf?v={V}" as="font" type="font/ttf" crossorigin>
<link rel="stylesheet" href="/css/style.css?v={V}">
</head>
<body>'''


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
      <a href="{TEL}" class="btn-call">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{PHONE_SVG}</svg>
        <span>{PHONE}</span>
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
    <a href="{TEL}" class="btn btn-primary btn-block">Call {PHONE}</a>
    <a href="#quote" class="btn btn-secondary btn-block">Book a Free Estimate</a>
  </div>
</div>

<div class="mobile-call-bar">
  <a href="{TEL}">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{PHONE_SVG}</svg>
    24/7 Emergency — Call {PHONE}
  </a>
</div>
'''


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
          <li><a href="/leak-detection/">Leak Detection</a></li>
          <li><a href="/service-locations/">Service Locations</a></li>
          {chr(10).join(f'          <li><a href="/{s}">{e(META[s][0])}</a></li>' for s in SERVICE_SLUGS[:3])}
        </ul>
      </div>

      <div class="footer-col">
        <h4>Contact</h4>
        <ul>
          <li><a href="{TEL}">{PHONE}</a></li>
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
      <p class="footer-license">Contractor License #1111400</p>
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
        <a href="{TEL}" class="btn btn-primary">Call {PHONE}</a>
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
      <a href="{TEL}">Call {PHONE}</a>
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
    <div style="margin-top:32px;"><a href="{TEL}" class="btn btn-primary">Call {PHONE}</a></div>
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
            inner = f'<a href="{TEL}">{PHONE}</a>'
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
        {form('contact', 700, 'Contact Us')}
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
      <a href="{TEL}" class="btn btn-primary">Call {PHONE}</a>
      <a href="mailto:{EMAIL}" class="btn btn-secondary">Email Us</a>
    </div>
  </div>
</section>
'''


# ------------------------------------------------------------------- assembly
def build(slug):
    p = PAGES[slug]
    parts = [head(p), chrome_top(), '\n<main>']

    if slug == 'ga-about-us':
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

    parts += ['</main>\n', chrome_bottom()]
    out = ''.join(parts)
    out = re.sub(r'\n{3,}', '\n\n', out)
    path = os.path.join(PUBLIC, slug + '.html')
    open(path, 'w').write(out)
    return path, len(out)


if __name__ == '__main__':
    for slug in PAGES:
        path, n = build(slug)
        print(f'{os.path.basename(path):34} {n:>7,} bytes')
