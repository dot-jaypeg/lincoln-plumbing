#!/usr/bin/env python3
"""Generate the four Lincoln Plumbing & Rooter email blasts into email-campaigns/.

Each email is a single self-contained HTML file built for email clients:
600px table layout, inline styles, a small <style> block for mobile and Outlook
fixes, VML buttons for Outlook, and absolute image URLs on the live site
(public/images/email/). No merge tags and no personalization: the platform
these go out from isn't decided yet, so the only thing to swap in before a send
is the unsubscribe link (UNSUBSCRIBE_HREF below).

Every button points at that email's offer page on the site (content/new-lps.json,
built by tools/build-legacy-lps.py), tagged with UTM parameters.

Run:  python3 tools/build-emails.py            # production files (live image URLs)
      python3 tools/build-emails.py --base URL # same, images from URL (local preview)
"""
import html, os, sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'email-campaigns')

SITE = 'https://www.lincolnplumbingandrooter.com'
IMG = SITE + '/images/email'
if '--base' in sys.argv:
    IMG = sys.argv[sys.argv.index('--base') + 1].rstrip('/')
    OUT = sys.argv[sys.argv.index('--base') + 2] if len(sys.argv) > sys.argv.index('--base') + 2 else OUT

# ---------------------------------------------------------------- brand facts
# The emails' own call line (given 2026-11-03), also shown on their offer pages
# (EMAIL_PHONE in build-legacy-lps.py). The rest of the site shows 909-780-0887.
PHONE_DISPLAY = '909-766-9716'
PHONE_E164 = '+19097669716'
TEL = f'tel:{PHONE_E164}'
EMAIL = 'contact@lincolnp.com'
ADDRESS = '738 S Waterman Ave C45, San Bernardino, CA 92408'
LEGAL = 'Lincoln Plumbing &amp; Rooter, INC'
LICENSE = 'Contractor License #1111400'
# The Google Reviews link the site's top bar uses. CONFIRM: swap for the GBP
# "write a review" short link (g.page/r/.../review) if the client has one.
GOOGLE_REVIEW = 'https://share.google/dAugpVXgXkDwGv2dv'
# Swap for the sending platform's unsubscribe tag before any send.
UNSUBSCRIBE_HREF = '[UNSUBSCRIBE_LINK]'

# --------------------------------------------------------------------- tokens
BLACK = '#0b0d11'
INK = '#14181f'
INK_SOFT = '#3d4552'
GRAY_600 = '#5b6472'
GRAY_200 = '#e3e7ec'
GRAY_100 = '#f1f3f6'
ORANGE = '#ff7b00'
ORANGE_DARK = '#e06600'      # button fill: white 20px bold on it passes 3:1 (large text)
ORANGE_LIGHT = '#fff1e2'
GOLD = '#ffb547'
GREEN = '#1f9d55'
RED = '#c8341f'
WHITE = '#ffffff'

HEAD_FONT = "'Antonio', 'Arial Narrow', 'Helvetica Neue', Arial, sans-serif"
BODY_FONT = "'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif"


def e(s):
    return html.escape(s, quote=True)


def url(slug, campaign, content):
    return (f'{SITE}/{slug}?utm_source=email&amp;utm_medium=email'
            f'&amp;utm_campaign={campaign}&amp;utm_content={content}')


# ----------------------------------------------------------------- components
def button(label, href, bg=ORANGE_DARK, color=WHITE, width=320):
    """Bulletproof button: VML roundrect for Outlook, padded <a> everywhere else."""
    return f'''<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" class="btn-table">
  <tr><td align="center" bgcolor="{bg}" style="border-radius:6px;">
    <!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{href}" style="height:58px;v-text-anchor:middle;width:{width}px;" arcsize="10%" stroke="f" fillcolor="{bg}"><w:anchorlock/><center style="color:{color};font-family:Arial,sans-serif;font-size:19px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;">{label}</center></v:roundrect><![endif]-->
    <!--[if !mso]><!-- --><a href="{href}" class="btn" style="display:inline-block;padding:19px 34px;font-family:{HEAD_FONT};font-size:20px;font-weight:700;line-height:20px;letter-spacing:1px;text-transform:uppercase;color:{color};text-decoration:none;border-radius:6px;background:{bg};mso-hide:all;">{label}</a><!--<![endif]-->
  </td></tr>
</table>'''


def phone_line(dark=True, prefix='Or call'):
    c = 'rgba(255,255,255,0.78)' if dark else GRAY_600
    lc = GOLD if dark else ORANGE_DARK
    return (f'<p style="margin:16px 0 0;font-family:{BODY_FONT};font-size:15px;line-height:22px;color:{c};text-align:center;">'
            f'{prefix} <a href="{TEL}" style="color:{lc};font-weight:700;text-decoration:none;white-space:nowrap;">{PHONE_DISPLAY}</a>'
            f' &middot; open 24/7</p>')


def preheader(text):
    pad = '&zwnj;&nbsp;' * 60
    return (f'<div style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;">'
            f'{e(text)}{pad}</div>')


def topbar():
    return f'''<tr><td style="padding:12px 28px;background:{BLACK};font-family:{BODY_FONT};font-size:12px;line-height:18px;color:rgba(255,255,255,0.7);text-align:center;letter-spacing:0.04em;" class="px">
  Open 24/7 &nbsp;&middot;&nbsp; Licensed &amp; Insured &nbsp;&middot;&nbsp; {LICENSE}
</td></tr>'''


def header(home):
    return f'''<tr><td style="padding:22px 28px;background:{INK};border-bottom:3px solid {ORANGE};" class="px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td valign="middle" class="stack center" style="width:50%;">
        <a href="{home}" style="text-decoration:none;"><img src="{IMG}/email-logo.png" width="150" alt="Lincoln Plumbing &amp; Rooter" style="display:block;width:150px;max-width:150px;height:auto;border:0;color:{WHITE};font-family:{HEAD_FONT};font-size:22px;font-weight:700;"></a>
      </td>
      <td valign="middle" align="right" class="stack center hdr-phone" style="width:50%;font-family:{BODY_FONT};">
        <span style="display:block;font-size:11px;line-height:16px;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.6);">Call 24/7</span>
        <a href="{TEL}" style="display:inline-block;margin-top:2px;font-family:{HEAD_FONT};font-size:26px;line-height:30px;font-weight:700;color:{WHITE};text-decoration:none;letter-spacing:0.02em;">{PHONE_DISPLAY}</a>
      </td>
    </tr>
  </table>
</td></tr>'''


def hero_image(src, alt, href):
    return f'''<tr><td style="background:{BLACK};font-size:0;line-height:0;">
  <a href="{href}"><img src="{IMG}/{src}" width="600" alt="{e(alt)}" class="fluid" style="display:block;width:100%;max-width:600px;height:auto;border:0;"></a>
</td></tr>'''


def hero(eyebrow, line1, line2, lede, cta, href):
    return f'''<tr><td style="padding:44px 44px 48px;background:{BLACK};text-align:center;" class="px">
  <p style="margin:0 0 14px;font-family:{BODY_FONT};font-size:13px;line-height:18px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:{ORANGE};">{eyebrow}</p>
  <h1 style="margin:0;font-family:{HEAD_FONT};font-size:50px;line-height:54px;font-weight:700;text-transform:uppercase;color:{WHITE};letter-spacing:0.01em;" class="h1">{line1}<br><span style="color:{ORANGE};">{line2}</span></h1>
  <p style="margin:20px auto 30px;max-width:470px;font-family:{BODY_FONT};font-size:17px;line-height:27px;color:rgba(255,255,255,0.84);">{lede}</p>
  {button(cta, href)}
  {phone_line()}
</td></tr>'''


def section(inner, bg=WHITE, pad='44px 44px'):
    return f'<tr><td style="padding:{pad};background:{bg};" class="px">\n{inner}\n</td></tr>'


def heading(eyebrow, h2, sub='', dark=False, color_eyebrow=ORANGE_DARK):
    hc = WHITE if dark else INK
    sc = 'rgba(255,255,255,0.8)' if dark else INK_SOFT
    sub_html = (f'<p style="margin:12px auto 0;max-width:460px;font-family:{BODY_FONT};font-size:16px;line-height:25px;color:{sc};">{sub}</p>'
                if sub else '')
    return f'''<div style="text-align:center;">
  <p style="margin:0 0 10px;font-family:{BODY_FONT};font-size:12px;line-height:16px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:{color_eyebrow};">{eyebrow}</p>
  <h2 style="margin:0;font-family:{HEAD_FONT};font-size:34px;line-height:40px;font-weight:700;text-transform:uppercase;color:{hc};" class="h2">{h2}</h2>
  {sub_html}
</div>'''


def card_grid(cards):
    """2x2 grid of numbered cards; stacks on mobile."""
    rows = []
    for i in range(0, len(cards), 2):
        cells = []
        for j, (title, body) in enumerate(cards[i:i + 2]):
            n = i + j + 1
            pad = 'padding:0 8px 16px 0;' if j == 0 else 'padding:0 0 16px 8px;'
            cells.append(f'''<td valign="top" width="50%" class="stack" style="{pad}">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="padding:22px 20px;background:{WHITE};border-radius:10px;border-top:3px solid {ORANGE};box-shadow:0 1px 3px rgba(20,24,31,0.08);" class="card">
            <p style="margin:0 0 6px;font-family:{HEAD_FONT};font-size:15px;line-height:18px;font-weight:700;color:{ORANGE_DARK};">0{n}</p>
            <p style="margin:0 0 6px;font-family:{HEAD_FONT};font-size:21px;line-height:25px;font-weight:700;text-transform:uppercase;color:{INK};">{title}</p>
            <p style="margin:0;font-family:{BODY_FONT};font-size:14px;line-height:21px;color:{INK_SOFT};">{body}</p>
          </td>
        </tr></table>
      </td>''')
        rows.append('<tr>\n      ' + '\n      '.join(cells) + '\n    </tr>')
    return f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:28px;">
    {''.join(rows)}
  </table>'''


def checklist(items, dark=False, mark='&#10003;', mark_bg=ORANGE, mark_color=BLACK):
    """Icon list. Defaults to orange check marks; xlist() is the gray "x" version."""
    c = 'rgba(255,255,255,0.88)' if dark else INK_SOFT
    rows = ''.join(f'''<tr>
      <td valign="top" width="30" style="padding:0 0 12px;"><span style="display:inline-block;width:20px;height:20px;border-radius:10px;background:{mark_bg};color:{mark_color};font-family:Arial,sans-serif;font-size:13px;line-height:20px;font-weight:700;text-align:center;">{mark}</span></td>
      <td valign="top" style="padding:0 0 12px;font-family:{BODY_FONT};font-size:15px;line-height:21px;color:{c};">{it}</td>
    </tr>''' for it in items)
    return f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{rows}</table>'


def xlist(items):
    """Same layout as checklist(), with gray "x" marks for the downside column."""
    return checklist(items, mark='<span style="font-size:18px;line-height:20px;">&times;</span>',
                     mark_bg=GRAY_200, mark_color=INK_SOFT)


def offer_box(tag, big, sub, items=None, note=''):
    items_html = f'<div style="margin-top:22px;text-align:left;">{checklist(items, dark=True)}</div>' if items else ''
    note_html = (f'<p style="margin:14px 0 0;font-family:{BODY_FONT};font-size:12px;line-height:18px;color:rgba(255,255,255,0.6);">{note}</p>'
                 if note else '')
    return f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td style="padding:3px;background:{ORANGE};background-image:linear-gradient(115deg,#ff9d2e 0%,#ff7b00 45%,#e85f00 100%);border-radius:14px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td style="padding:30px 30px 28px;background:{INK};border-radius:11px;text-align:center;" class="card">
        <p style="margin:0;display:inline-block;padding:6px 14px;border-radius:30px;background:{ORANGE};font-family:{BODY_FONT};font-size:12px;line-height:14px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:{BLACK};">{tag}</p>
        <p style="margin:16px 0 0;font-family:{HEAD_FONT};font-size:40px;line-height:44px;font-weight:700;text-transform:uppercase;color:{WHITE};" class="h2">{big}</p>
        <p style="margin:10px auto 0;max-width:420px;font-family:{BODY_FONT};font-size:16px;line-height:24px;color:rgba(255,255,255,0.82);">{sub}</p>
        {items_html}{note_html}
      </td>
    </tr></table>
  </td></tr>
</table>'''


def two_offers(a, b):
    """Side-by-side offer cards (stack on mobile). a/b = (title, kicker, items)."""
    def col(t, kicker, items, side):
        pad = 'padding:0 8px 0 0;' if side == 0 else 'padding:0 0 0 8px;'
        cls = 'stack stack-first' if side == 0 else 'stack'
        return f'''<td valign="top" width="50%" class="{cls}" style="{pad}">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="padding:26px 22px;background:{INK};border-radius:12px;border-top:4px solid {ORANGE};" class="card">
            <p style="margin:0 0 6px;font-family:{BODY_FONT};font-size:11px;line-height:14px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:{GOLD};">{kicker}</p>
            <p style="margin:0 0 16px;font-family:{HEAD_FONT};font-size:26px;line-height:30px;font-weight:700;text-transform:uppercase;color:{WHITE};">{t}</p>
            {checklist(items, dark=True)}
          </td>
        </tr></table>
      </td>'''
    return f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:28px;">
    <tr>
      {col(*a, 0)}
      {col(*b, 1)}
    </tr>
  </table>'''


def review_quote():
    # Real review, verbatim from the site (shown on the LPs). Excerpted with "…".
    return f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td style="padding:30px 32px;background:{GRAY_100};border-radius:12px;border-left:4px solid {ORANGE};" class="card">
    <p style="margin:0 0 12px;font-size:20px;line-height:20px;color:{ORANGE};letter-spacing:3px;" aria-label="5 out of 5 stars">&#9733;&#9733;&#9733;&#9733;&#9733;</p>
    <p style="margin:0;font-family:{BODY_FONT};font-size:17px;line-height:27px;color:{INK};font-style:italic;">&ldquo;Lincoln Plumbing quickly responded and made this process easy and affordable. Ivan and Noel are very professional and experienced, found the problem right away&hellip;&rdquo;</p>
    <p style="margin:14px 0 0;font-family:{BODY_FONT};font-size:14px;line-height:20px;font-weight:700;color:{INK_SOFT};">Ericka M.</p>
  </td></tr>
</table>'''


def trust_strip():
    items = [('24/7', 'Emergency service'), ('Upfront', 'Pricing, no surprises'), ('Licensed', '&amp; insured')]
    cells = ''.join(f'''<td valign="top" width="33%" class="stack" style="padding:0 6px 0;text-align:center;">
        <p style="margin:0;font-family:{HEAD_FONT};font-size:28px;line-height:32px;font-weight:700;text-transform:uppercase;color:{ORANGE};">{a}</p>
        <p style="margin:4px 0 14px;font-family:{BODY_FONT};font-size:13px;line-height:18px;color:rgba(255,255,255,0.75);">{b}</p>
      </td>''' for a, b in items)
    return f'''<tr><td style="padding:30px 32px 16px;background:{INK};border-top:1px solid rgba(255,255,255,0.08);" class="px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      {cells}
  </tr></table>
</td></tr>'''


def final_cta(eyebrow, h2, sub, cta, href):
    return f'''<tr><td style="padding:50px 44px 52px;background:{BLACK};text-align:center;" class="px">
  {heading(eyebrow, h2, sub, dark=True, color_eyebrow=ORANGE)}
  <div style="height:28px;line-height:28px;font-size:0;">&nbsp;</div>
  {button(cta, href)}
  {phone_line()}
</td></tr>'''


def footer(reason):
    return f'''<tr><td style="padding:30px 36px 36px;background:{GRAY_100};text-align:center;font-family:{BODY_FONT};font-size:12px;line-height:19px;color:{GRAY_600};" class="px">
  <p style="margin:0 0 8px;font-weight:700;color:{INK_SOFT};">{LEGAL}</p>
  <p style="margin:0 0 8px;">{ADDRESS}<br>
    <a href="{TEL}" style="color:{INK_SOFT};text-decoration:none;font-weight:700;">{PHONE_DISPLAY}</a> &middot;
    <a href="mailto:{EMAIL}" style="color:{INK_SOFT};text-decoration:none;">{EMAIL}</a><br>{LICENSE}</p>
  <p style="margin:14px 0 0;">{reason}<br>
    <a href="{UNSUBSCRIBE_HREF}" style="color:{GRAY_600};text-decoration:underline;">Unsubscribe</a> &middot;
    <a href="{SITE}/privacy-policy" style="color:{GRAY_600};text-decoration:underline;">Privacy Policy</a> &middot;
    <a href="{SITE}" style="color:{GRAY_600};text-decoration:underline;">lincolnplumbingandrooter.com</a></p>
</td></tr>'''


def doc(title, pre, rows, notes):
    return f'''<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no, date=no, address=no, email=no">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>{e(title)}</title>
<!--
{notes}
-->
<!--[if mso]><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml><![endif]-->
<!--[if !mso]><!-->
<link href="https://fonts.googleapis.com/css2?family=Antonio:wght@700&amp;family=Inter:wght@400;700&amp;display=swap" rel="stylesheet">
<!--<![endif]-->
<style>
  body, table, td, a {{ -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }}
  table, td {{ mso-table-lspace:0pt; mso-table-rspace:0pt; border-collapse:collapse; }}
  img {{ -ms-interpolation-mode:bicubic; border:0; outline:none; text-decoration:none; }}
  body {{ margin:0 !important; padding:0 !important; width:100% !important; }}
  a[x-apple-data-detectors] {{ color:inherit !important; text-decoration:none !important; }}
  .btn:hover {{ filter:brightness(1.08); }}
  @media screen and (max-width:620px) {{
    .container {{ width:100% !important; }}
    .px {{ padding-left:22px !important; padding-right:22px !important; }}
    .stack {{ display:block !important; width:100% !important; padding-left:0 !important; padding-right:0 !important; box-sizing:border-box; }}
    .stack-first {{ padding-bottom:14px !important; }}
    .center {{ text-align:center !important; }}
    .center img {{ margin:0 auto !important; }}
    .hdr-phone {{ padding-top:14px !important; }}
    .h1 {{ font-size:40px !important; line-height:44px !important; }}
    .h2 {{ font-size:30px !important; line-height:34px !important; }}
    .card {{ padding-left:20px !important; padding-right:20px !important; }}
    .btn {{ display:block !important; padding-left:18px !important; padding-right:18px !important; }}
    .btn-table {{ width:100% !important; }}
    .fluid {{ width:100% !important; height:auto !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:{GRAY_200};">
{preheader(pre)}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{GRAY_200};">
  <tr><td align="center" style="padding:24px 10px;">
    <!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" class="container" style="width:600px;max-width:600px;background:{WHITE};">
{rows}
    </table>
    <!--[if mso]></td></tr></table><![endif]-->
  </td></tr>
</table>
</body>
</html>
'''


# --------------------------------------------------------------------- emails
CUSTOMER_REASON = "You're receiving this because you're a Lincoln Plumbing &amp; Rooter customer."
EMAILS = []


def email(fn):
    EMAILS.append(fn)
    return fn


@email
def holiday():
    slug, camp = 'holiday-plumbing-prep', 'holiday-prep'
    u = lambda c: url(slug, camp, c)
    rows = [
        topbar(), header(u('logo')),
        hero('Holiday Plumbing Prep', 'Holiday-proof', 'your plumbing.',
             "Full houses, big meals and back-to-back showers are hard on drains and water heaters. "
             "A quick visit now means no backed-up sink on the big day and no cold showers while family's in town.",
             'Book My Holiday Prep', u('hero')),
        hero_image('email-holiday.jpg', 'Lincoln Plumbing & Rooter technician working under a kitchen sink', u('image')),
        section(heading('Pick Your Prep', 'Two ways to get ready',
                        'Book one or both. You get upfront pricing before any work starts.')
                + two_offers(('Drain Clean', 'Kitchen &amp; bath',
                              ['Clears grease and food buildup', 'Kitchen, bath or main line', 'Camera inspection if a line keeps clogging']),
                             ('Water Heater Flush', 'More hot water',
                              ['Flushes out sediment', 'Checks the relief valve and connections', 'Quieter, more efficient tank'])),
                bg=WHITE),
        # CONFIRM: no price or firm book-by date in the brief. Add both here once the client confirms.
        section(offer_box('Book Before The Holidays', 'Beat the holiday rush',
                          'Our schedule fills up fast before Thanksgiving and Christmas. Book now to get the day and time you want.'),
                bg=WHITE, pad='0 44px 44px'),
        section(heading('Where It Goes Wrong', 'Where holidays hit your plumbing')
                + card_grid([('Kitchen drains', 'Grease, peels and scraps from holiday cooking pile up in the line and the disposal.'),
                             ('Extra showers', 'Houseguests drain a sediment-filled water heater faster than you think.'),
                             ('Guest bathrooms', 'Toilets that sit unused most of the year suddenly get worked hard.'),
                             ('Main sewer line', 'With every fixture running, a partial blockage finally shows itself.')]),
                bg=GRAY_100),
        section(review_quote(), bg=WHITE),
        trust_strip(),
        final_cta('Don’t wait for the clog', 'Get ready before the guests do',
                  'Reserve your pre-holiday drain clean or water heater flush today.',
                  'Book My Holiday Prep', u('footer-cta')),
        footer(CUSTOMER_REASON),
    ]
    return ('01-holiday-proof-your-plumbing.html',
            'Holiday-proof your plumbing',
            'Book a pre-holiday drain clean or water heater flush before our schedule fills up.',
            rows,
            ['Before the guests arrive: is your plumbing ready?',
             'Holiday-proof your plumbing (before the rush)',
             'Full house this year? Your drains will feel it'],
            'CONFIRM before sending: offer price and a firm book-by date (brief gave neither; copy says "book before the holidays").')


@email
def water_heater():
    slug, camp = 'water-heater-checkup', 'water-heater-age'
    u = lambda c: url(slug, camp, c)
    tiers = [(GREEN, '0–7 years', 'Likely fine', 'Flush it once a year to keep it that way.'),
             (ORANGE, '8–11 years', 'Time to take a look', 'Get it inspected before small problems turn into a leak.'),
             (RED, '12+ years', 'Plan your replacement', 'Replace it on your schedule, not after it fails.')]
    tier_rows = ''.join(f'''<tr><td style="padding:0 0 12px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td width="8" style="background:{c};border-radius:8px 0 0 8px;font-size:0;line-height:0;">&nbsp;</td>
        <td style="padding:18px 20px;background:{GRAY_100};border-radius:0 8px 8px 0;" class="card">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
            <td valign="middle" width="34%" class="stack" style="font-family:{HEAD_FONT};font-size:28px;line-height:32px;font-weight:700;text-transform:uppercase;color:{INK};">{age}</td>
            <td valign="middle" class="stack" style="font-family:{BODY_FONT};">
              <p style="margin:0;font-size:16px;line-height:22px;font-weight:700;color:{INK};">{title}</p>
              <p style="margin:2px 0 0;font-size:14px;line-height:20px;color:{INK_SOFT};">{body}</p>
            </td>
          </tr></table>
        </td>
      </tr></table>
    </td></tr>''' for c, age, title, body in tiers)
    rows = [
        topbar(), header(u('logo')),
        hero('The 60-second age check', 'How old is your', 'water heater?',
             "Check the label on the side of the tank. Most tank water heaters last about 8 to 12 years, "
             "and they rarely give much warning before they quit.",
             'Book My Free Inspection', u('hero')),
        hero_image('email-water-heater.jpg', 'Lincoln Plumbing & Rooter technician Ivan in a safety vest', u('image')),
        section(heading('Find Your Number', 'What your water heater’s age means',
                        'The manufacture date is usually printed on the label or in the serial number.')
                + f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:28px;">{tier_rows}</table>',
                bg=WHITE),
        section(offer_box('8+ years? Time to look', 'Free water heater inspection',
                          'A licensed Lincoln tech checks your water heater top to bottom and gives you a straight answer: repair it, maintain it or replace it.',
                          ['Age, corrosion and leak check', 'Relief valve, connections and venting', 'Upfront pricing on anything that needs work',
                           'Tank and tankless options, with financing through GoodLeap']),
                bg=WHITE, pad='0 44px 44px'),
        section(heading('Don’t ignore these', 'Signs it’s on borrowed time')
                + card_grid([('Rusty water', 'Discolored hot water can mean the tank is corroding inside.'),
                             ('Popping noises', 'Rumbling or popping usually means sediment has built up.'),
                             ('Runs out fast', 'Hot water that doesn’t last like it used to.'),
                             ('Moisture at the base', 'Any water around the tank is worth a call today.')]),
                bg=GRAY_100),
        section(review_quote(), bg=WHITE),
        trust_strip(),
        final_cta('Free inspection', 'Know before it quits',
                  'Book your free water heater inspection and find out how much life yours has left.',
                  'Book My Free Inspection', u('footer-cta')),
        footer(CUSTOMER_REASON),
    ]
    return ('02-how-old-is-your-water-heater.html',
            'How old is your water heater?',
            '8+ years old? It’s time for a look. Book a free water heater inspection.',
            rows,
            ['How old is your water heater?',
             '8+ years old? Your water heater needs a look',
             'The 60-second check that could save you a cold shower'],
            'CONFIRM before sending: the free inspection (from the brief). No replacement discount amount was given, so none is advertised.')


@email
def checkup():
    slug, camp = 'plumbing-checkup', 'annual-checkup'
    u = lambda c: url(slug, camp, c)
    rows = [
        topbar(), header(u('logo')),
        hero('Welcome back', 'It’s been a while.', 'Let’s check in.',
             "Thank you for trusting Lincoln Plumbing &amp; Rooter. It's been a while since we've seen you, "
             "so we're offering returning customers special savings on a whole-home plumbing inspection.",
             'Book My Checkup', u('hero')),
        hero_image('email-checkup.jpg', 'Two Lincoln Plumbing & Rooter technicians in the company shop', u('image')),
        # CONFIRM: loyalty discount amount not in the brief. Put it in the big line once confirmed.
        section(offer_box('Returning customers only', 'Loyalty savings on a whole-home inspection',
                          'One visit, every major part of your plumbing, with a clear rundown of what’s working and what isn’t.',
                          ['Water heater and relief valve', 'Hidden leaks and water pressure', 'Drains, sewer line and fixtures',
                           'Upfront pricing on anything worth fixing']),
                bg=WHITE, pad='44px 44px'),
        section(heading('What we check', 'Your whole-home inspection',
                        'Small fixes now cost far less than big repairs later.')
                + card_grid([('Water heater', 'Age, sediment, relief valve and connections.'),
                             ('Leaks &amp; pressure', 'Hidden drips, running toilets and pressure that’s too high for your pipes.'),
                             ('Drains &amp; sewer', 'Slow drains, gurgling and early signs of a main-line blockage.'),
                             ('Fixtures &amp; valves', 'Faucets, shut-offs and supply lines that are wearing out.')]),
                bg=GRAY_100),
        section(f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td valign="top" width="50%" class="stack" style="padding-right:12px;">
        <p style="margin:0 0 14px;font-family:{HEAD_FONT};font-size:22px;line-height:26px;font-weight:700;text-transform:uppercase;color:{GRAY_600};">Without a checkup</p>
        {xlist(['Slow leaks run up the water bill for months', 'A worn shut-off fails when you need it', 'Problems show up at the worst time'])}
      </td>
      <td valign="top" width="50%" class="stack" style="padding-left:12px;">
        <p style="margin:0 0 14px;font-family:{HEAD_FONT};font-size:22px;line-height:26px;font-weight:700;text-transform:uppercase;color:{ORANGE_DARK};">With a Lincoln checkup</p>
        {checklist(['A clear list of what needs attention', 'Upfront pricing, no pressure', 'You decide what to fix and when'])}
      </td>
    </tr></table>''', bg=WHITE),
        section(review_quote(), bg=WHITE, pad='0 44px 44px'),
        trust_strip(),
        final_cta('Welcome back', 'Book your annual checkup',
                  'Mention you’re a returning customer when you book.',
                  'Book My Checkup', u('footer-cta')),
        footer(CUSTOMER_REASON),
    ]
    return ('03-annual-plumbing-checkup.html',
            'It’s been a while since we’ve seen you',
            'Returning customers get loyalty savings on a whole-home plumbing inspection.',
            rows,
            ['It’s been a while since we’ve seen you',
             'A thank-you for coming back: loyalty savings inside',
             'When did someone last check your plumbing?'],
            'CONFIRM before sending: the loyalty discount amount (brief gave none; copy says "loyalty savings").')


@email
def referral():
    slug, camp = 'refer-a-neighbor', 'refer-a-neighbor'
    lp = f'{SITE}/{slug}?utm_source=email&utm_medium=referral&utm_campaign={camp}'
    share = ('mailto:?subject=' + quote('$25 off with Lincoln Plumbing & Rooter')
             + '&amp;body=' + quote('I use Lincoln Plumbing & Rooter and thought of you. Book through this link, '
                                    'mention my name, and we both get $25 off:\n\n' + lp))
    u = lambda c: url(slug, camp, c)
    give_get = f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:28px;"><tr>
      <td valign="top" width="50%" class="stack stack-first" style="padding:0 8px 0 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="padding:28px 20px;background:{INK};border-radius:12px;text-align:center;" class="card">
            <p style="margin:0;font-family:{BODY_FONT};font-size:12px;line-height:16px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:{GOLD};">They get</p>
            <p style="margin:6px 0 4px;font-family:{HEAD_FONT};font-size:64px;line-height:66px;font-weight:700;color:{ORANGE};">$25</p>
            <p style="margin:0;font-family:{BODY_FONT};font-size:15px;line-height:21px;color:rgba(255,255,255,0.82);">off their first service</p>
          </td></tr></table>
      </td>
      <td valign="top" width="50%" class="stack" style="padding:0 0 0 8px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
          <td style="padding:28px 20px;background:{INK};border-radius:12px;text-align:center;" class="card">
            <p style="margin:0;font-family:{BODY_FONT};font-size:12px;line-height:16px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:{GOLD};">You get</p>
            <p style="margin:6px 0 4px;font-family:{HEAD_FONT};font-size:64px;line-height:66px;font-weight:700;color:{ORANGE};">$25</p>
            <p style="margin:0;font-family:{BODY_FONT};font-size:15px;line-height:21px;color:rgba(255,255,255,0.82);">off your next service</p>
          </td></tr></table>
      </td>
    </tr></table>'''
    steps = card_grid([('Share this email', 'Forward it, or tap the button below to send it to a neighbor, friend or family member.'),
                       ('They book with us', 'They call or book online and mention your name.'),
                       ('They save $25', '$25 comes off their first service with Lincoln.'),
                       ('You save $25', 'We take $25 off your next service as a thank-you.')])
    review_ask = f'''<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td style="padding:34px 30px;background:{ORANGE_LIGHT};border-radius:14px;text-align:center;border:1px solid #ffd9b0;" class="card">
    <p style="margin:0 0 10px;font-size:26px;line-height:26px;color:{ORANGE};letter-spacing:4px;" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</p>
    <p style="margin:0;font-family:{HEAD_FONT};font-size:30px;line-height:34px;font-weight:700;text-transform:uppercase;color:{INK};" class="h2">Got 30 seconds?</p>
    <p style="margin:10px auto 24px;max-width:420px;font-family:{BODY_FONT};font-size:16px;line-height:24px;color:{INK_SOFT};">
      If we did a good job for you, a quick Google review helps your neighbors find a plumber they can trust. It means a lot to our small team.</p>
    {button('Leave A Google Review', GOOGLE_REVIEW, bg=INK, color=WHITE, width=300)}
  </td></tr>
</table>'''
    rows = [
        topbar(), header(u('logo')),
        hero('Thank you', 'Thanks for trusting', 'Lincoln.',
             "Customers like you are how a local business grows. Know a neighbor, friend or family member who needs a plumber? "
             "Send them our way and you'll both get $25 off.",
             'Share With A Neighbor', share),
        hero_image('email-referral.jpg', 'Two Lincoln Plumbing & Rooter technicians standing by the company van', u('image')),
        section(heading('Give $25, get $25', 'Good neighbors save together') + give_get, bg=WHITE),
        section(heading('How it works', 'Four simple steps') + steps, bg=GRAY_100),
        section(review_ask, bg=WHITE),
        trust_strip(),
        final_cta('Refer a neighbor', 'Share the savings',
                  f'Tap below to email a friend, or send them to <a href="{u("footer-link")}" style="color:{GOLD};text-decoration:underline;">lincolnplumbingandrooter.com/refer-a-neighbor</a>.',
                  'Share With A Neighbor', share),
        footer(CUSTOMER_REASON),
    ]
    return ('04-refer-a-neighbor.html',
            'Refer a neighbor: $25 for you, $25 for them',
            'Thank you for being a customer. Send a neighbor our way and you both get $25 off.',
            rows,
            ['Thank you. Here’s $25 for you and a neighbor.',
             'Know someone who needs a plumber? You both get $25',
             'A thank-you from Lincoln Plumbing & Rooter'],
            'CONFIRM before sending: how the client tracks referrals and applies the $25 rewards; '
            'the Google review link (currently the site\'s share.google link, swap for the GBP write-a-review link).')


def main():
    os.makedirs(OUT, exist_ok=True)
    index = []
    for fn in EMAILS:
        name, title, pre, rows, subjects, confirm = fn()
        notes = ('  Lincoln Plumbing & Rooter email: ' + title + '\n'
                 '  Generated by tools/build-emails.py. Edit the generator, not this file.\n'
                 '  Subject line options:\n' + ''.join(f'    - {s}\n' for s in subjects) +
                 f'  Preheader: {pre}\n'
                 f'  Before sending: replace {UNSUBSCRIBE_HREF} with the platform\'s unsubscribe tag.\n'
                 f'  {confirm}')
        out = doc(title, pre, '\n'.join(rows), notes.replace('--', '-'))
        open(os.path.join(OUT, name), 'w').write(out)
        index.append((name, title, pre, subjects))
        print(f'{name:40} {len(out):>7,} bytes')
    return index


if __name__ == '__main__':
    main()
