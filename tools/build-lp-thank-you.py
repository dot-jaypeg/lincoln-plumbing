#!/usr/bin/env python3
"""public/ga-thank-you.html -> public/<slug>-thank-you.html, one per paid LP with a form.

Each copy shows only its LP's own call line, configures Google Ads call tracking
for that line, and fires the AM Lead Form conversion. Point each LP's GHL form
redirect at its own page. /ga-thank-you stays as the shared fallback.

    python3 tools/build-lp-thank-you.py            # all of them
    python3 tools/build-lp-thank-you.py <slug> ... # just these
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import tracking  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / 'public'
TEMPLATE = PUBLIC / 'ga-thank-you.html'

# The LPs that embed a GHL form (ga-about-us and ga-testimonials have none).
LP_FORM_SLUGS = [
    'ga-plumbing-services', 'sewer-lines', 'ga-tankless-water-heaters',
    'ga-water-heater', 'ga-contact', 'drain-cleaning',
    'ga-garbage-disposal-services', 'hydrojetting', 'ga-leak-detection',
    'toilet-overflow',
]

# Google Ads call configs per call line, as Google sent them.
CALL_CONFIGS = {
    '909-765-0236': ('AW-16721660937/BQtCCIjq9NUcEImYwaU-', '(909)765-0236'),
    '909-280-7894': ('AW-16721660937/5dP7CJTmo6YdEImYwaU-', '(909) 280-7894'),
}
LEAD_CONVERSION = 'AW-16721660937/AZdYCOSk4dUcEImYwaU-'


def e164(line):
    return 'tel:+1' + line.replace('-', '')


def build(slug):
    line = tracking.call_line(slug)
    label, number = CALL_CONFIGS[line]
    h = TEMPLATE.read_text()

    def sub(pattern, repl, count=1):
        nonlocal h
        h, n = re.subn(pattern, repl, h, count=count, flags=re.S)
        assert n == count, (slug, pattern)

    sub(r'call 909-765-0236 for immediate help', f'call {line} for immediate help')
    sub(r'/ga-thank-you">', f'/{slug}-thank-you">')
    # The shared page reads the line from localStorage; these each know theirs.
    sub(r'<!-- Google Ads call line -->\n<script>.*?</script>\n',
        f'''<!-- Google Ads call line -->
<script>
  window.dataLayer = window.dataLayer || [];
  dataLayer.push({{'call_line': '{line}'}});
</script>
''')
    sub(r"(gtag\('config', ')AW-16721660937/[^']+(', \{\n    'phone_conversion_number': ')[^']+('\n)",
        rf"\g<1>{label}\g<2>{number}\g<3>")
    assert LEAD_CONVERSION in h
    sub(r'<a href="tel:[^"]+" class="btn btn-primary" id="call-cta">Call [0-9-]+ Now</a>',
        f'<a href="{e164(line)}" class="btn btn-primary" id="call-cta">Call {line} Now</a>')
    sub(r'\n    <script>\n      // Inline, so the number.*?</script>', '')

    out = PUBLIC / f'{slug}-thank-you.html'
    out.write_text(h)
    print(f'{out.relative_to(ROOT)}  ({line})')


if __name__ == '__main__':
    for slug in sys.argv[1:] or LP_FORM_SLUGS:
        build(slug)
