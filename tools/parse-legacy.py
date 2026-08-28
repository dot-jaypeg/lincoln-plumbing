#!/usr/bin/env python3
"""Parse the legacy (WordPress/Divi) landing pages saved in
content/legacy-scrape/raw-html/ into a normalized JSON structure.

The legacy LPs were hand-coded HTML inside a Divi code module, so their markup
is consistent enough to parse section by section: .hero, .ticker, .signs-grid,
.compare-grid, .how-grid, .why-grid, .testimonial-card, .area-section, #quote.

Output: content/legacy-scrape/pages.json — the input to tools/build-legacy-lps.py.
"""
import json, os, re, html, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'content', 'legacy-scrape', 'raw-html')
OUT = os.path.join(ROOT, 'content', 'legacy-scrape', 'pages.json')

SLUGS = ['ga-plumbing-services', 'sewer-lines', 'ga-tankless-water-heaters',
         'ga-testimonials', 'ga-water-heater', 'ga-about-us', 'ga-contact',
         'drain-cleaning', 'ga-garbage-disposal-services', 'hydrojetting',
         'ga-leak-detection']


def txt(s):
    s = re.sub(r'<br\s*/?>', ' | ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def block(body, cls):
    """Return the inner HTML of the first <div class="...cls..."> ... balanced."""
    m = re.search(r'<div class="[^"]*\b' + cls + r'\b[^"]*">', body)
    if not m:
        return None
    i = m.end()
    depth = 1
    for t in re.finditer(r'</?div\b', body[i:]):
        depth += 1 if t.group(0) == '<div' else -1
        if depth == 0:
            return body[i:i + t.start()]
    return body[i:]


def cards(scope, cls):
    if not scope:
        return []
    out = []
    for m in re.finditer(r'<div class="([^"]*\b' + cls + r'\b[^"]*)">', scope):
        i = m.end()
        depth = 1
        for t in re.finditer(r'</?div\b', scope[i:]):
            depth += 1 if t.group(0) == '<div' else -1
            if depth == 0:
                inner = scope[i:i + t.start()]
                break
        else:
            inner = scope[i:]
        h = re.search(r'<h3[^>]*>(.*?)</h3>', inner, re.S)
        p = re.search(r'<p[^>]*>(.*?)</p>', inner, re.S)
        num = re.search(r'<span class="num">(.*?)</span>|<div class="stepnum">(.*?)</div>', inner, re.S)
        icon = re.search(r'<div class="icon">(.*?)</div>', inner, re.S)
        out.append({
            'classes': m.group(1),
            'num': txt(num.group(1) or num.group(2)) if num else '',
            'icon': txt(icon.group(1)) if icon else '',
            'title': txt(h.group(1)) if h else '',
            'body': txt(p.group(1)) if p else '',
            'items': [txt(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', inner, re.S)],
        })
    return out


def head(section):
    """eyebrow / h2 / p out of a .section-head (falling back to the section
    itself for the sections that don't wrap their heading in one)."""
    if not section:
        return {'eyebrow': '', 'h2': '', 'sub': ''}
    inner = block(section, 'section-head')
    if inner:
        section = inner
    eb = re.search(r'<span class="eyebrow">(.*?)</span>', section, re.S)
    h2 = re.search(r'<h2[^>]*>(.*?)</h2>', section, re.S)
    p = re.search(r'<p class="lede"[^>]*>(.*?)</p>|<p>(.*?)</p>', section, re.S)
    return {
        'eyebrow': txt(eb.group(1)) if eb else '',
        'h2': txt(h2.group(1)) if h2 else '',
        'sub': txt(p.group(1) or p.group(2)) if p else '',
    }


def sections(body):
    """Split the hand-coded body into <section> chunks keyed by their classes."""
    out = []
    for m in re.finditer(r'<section class="([^"]*)"[^>]*>', body):
        i = m.end()
        depth = 1
        for t in re.finditer(r'</?section\b', body[i:]):
            depth += 1 if t.group(0) == '<section' else -1
            if depth == 0:
                out.append((m.group(1), body[i:i + t.start()]))
                break
        else:
            out.append((m.group(1), body[i:]))
    return out


pages = {}
for slug in SLUGS:
    raw = open(os.path.join(RAW, slug + '.html'), encoding='utf-8', errors='replace').read()
    flat = re.sub(r'\s+', ' ', raw)

    title = txt(re.search(r'<title[^>]*>(.*?)</title>', flat).group(1))
    desc = re.search(r'<meta name="description" content="(.*?)"', flat)

    # the hand-coded LP body starts at the HERO comment and ends at its own footer
    start = flat.find('<!-- ================= HERO')
    if start < 0:
        start = flat.find('<section class="hero">')
    end = flat.find('<footer> <div class="wrap"> © 2026', start)
    body = flat[start:end if end > 0 else None]

    hero_scope = sections(body)
    hero = next((s for c, s in hero_scope if 'hero' in c.split()), '')
    badges = [txt(x) for x in re.findall(r'<div class="badge-row">(.*?)</div>', hero, re.S)]
    badges = re.findall(r'<span>(.*?)</span>', re.search(r'<div class="badge-row">(.*?)</div>', hero, re.S).group(1)) if 'badge-row' in hero else []
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', hero, re.S)
    h1_lines = []
    if h1:
        inner = h1.group(1)
        for part in re.split(r'<br\s*/?>', inner):
            h1_lines.append(txt(part))
    lede = re.search(r'<p class="lede"[^>]*>(.*?)</p>', hero, re.S)
    stats = [{'value': txt(a), 'label': txt(b)} for a, b in
             re.findall(r'<div><b>(.*?)</b><span>(.*?)</span></div>', hero, re.S)]
    ticker = [txt(x) for x in re.findall(r'<span>(.*?)</span>', block(body, 'ticker') or '')]
    seen, ticker_u = set(), []
    for t in ticker:
        if t not in seen:
            seen.add(t)
            ticker_u.append(t)

    signs_sec = next((s for c, s in hero_scope if 'signs-grid' in s), '')
    compare_sec = next((s for c, s in hero_scope if 'compare-grid' in s), '')
    how_sec = next((s for c, s in hero_scope if 'how-grid' in s), '')
    why_sec = next((s for c, s in hero_scope if 'why-grid' in s), '')
    area_sec = next((s for c, s in hero_scope if 'area-chips' in s), '')
    quote_sec = next((s for c, s in hero_scope if 'apply-section' in c or 'form-shell' in s), '')
    tcard = block(body, 'testimonial-card')


    # --- page-specific extras (services grid, stats, reviews, info cards) ---
    services_sec = next((sec for c, sec in hero_scope if 'services-grid' in sec), '')
    extras = {
        'services': dict(head(services_sec), cards=cards(block(services_sec, 'services-grid'), 'service-card')),
        'stats_grid': [{'value': txt(a), 'label': txt(b)} for a, b in
                       re.findall(r'<div><b>(.*?)</b><span>(.*?)</span></div>', block(body, 'stats-grid') or '', re.S)],
        'info_cards': [{'icon': txt(i), 'title': txt(t), 'body': txt(v)} for i, t, v in
                       re.findall(r'<div class="icon">(.*?)</div> <h3>(.*?)</h3> (.*?)</div>',
                                  block(body, 'info-grid') or '', re.S)],
        'yelp_reviews': [{'review_id': rid, 'user_id': uid, 'name': txt(name)} for rid, uid, name in
                         re.findall(r'data-review-id="([^"]+)"[^>]*>Read <a href="[^"]*userid=([^"]+)"'
                                    r'[^>]*>(.*?)</a>', body, re.S)],
        'platform_links': [{'href': h, 'label': txt(l)} for h, l in
                           re.findall(r'<a href="([^"]+)"[^>]*>([^<]*Review Us On[^<]*)</a>', body, re.S)],
        'commitment': {},
    }
    comm = next((sec for c, sec in hero_scope
                 if 'Commitment' in sec and 'section-head' in sec), '')
    if comm:
        extras['commitment'] = dict(head(comm),
                                    paras=[txt(x) for x in re.findall(r'<p>(.*?)</p>', comm, re.S)])
    final_sec = next((sec for c, sec in hero_scope if 'cta-section' in c), '')
    extras['final_cta'] = head(final_sec) if final_sec else {}

    pages[slug] = {
        'slug': slug,
        'legacy_url': f'https://www.lincolnplumbingandrooter.com/{slug}/',
        'title': title,
        'description': html.unescape(desc.group(1)) if desc else '',
        'hero': {
            'badges': [txt(b) for b in badges],
            'h1_lines': [l for l in h1_lines if l],
            'lede': txt(lede.group(1)) if lede else '',
            'stats': stats,
        },
        'ticker': ticker_u,
        'signs': dict(head(signs_sec), cards=cards(block(signs_sec, 'signs-grid'), 'sign-card')),
        'compare': dict(head(compare_sec), cards=cards(block(compare_sec, 'compare-grid'), 'compare-card')),
        'how': dict(head(how_sec), cards=cards(block(how_sec, 'how-grid'), 'how-card')),
        'why': dict(head(why_sec), cards=cards(block(why_sec, 'why-grid'), 'why-card')),
        'testimonial': {
            'quote': txt(re.search(r'<p>(.*?)</p>', tcard, re.S).group(1)) if tcard and re.search(r'<p>(.*?)</p>', tcard, re.S) else '',
            'who': txt(re.search(r'<div class="who">(.*?)</div>', tcard, re.S).group(1)) if tcard and 'class="who"' in tcard else '',
        },
        'area': dict(head(area_sec),
                     chips=[txt(x) for x in re.findall(r'<span>(.*?)</span>', block(area_sec, 'area-chips') or '')]),
        'quote_cta': head(quote_sec),
        'form_slots': sorted(set(re.findall(r'data-layout-iframe-id="inline-\w+-([a-z0-9-]+)"', flat))),
        **extras,
        'form_id': (re.search(r'data-form-id="(\w+)"', flat) or [None, ''])[1] if 'data-form-id' in flat else '',
    }

json.dump(pages, open(OUT, 'w'), indent=2, ensure_ascii=False)
for s, p in pages.items():
    print(f"{s:32} h1={' / '.join(p['hero']['h1_lines'])[:44]:46} signs={len(p['signs']['cards'])} cmp={len(p['compare']['cards'])} how={len(p['how']['cards'])} why={len(p['why']['cards'])} chips={len(p['area']['chips'])} slots={p['form_slots']}")
