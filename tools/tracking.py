#!/usr/bin/env python3
"""The legacy site's analytics/advertising tags, reproduced as they were installed.

Distribution on the old site, which this mirrors exactly:
  * Google Tag Manager, GA4 and Google Ads  -> every page
  * Meta Pixel                              -> only the paid-traffic pages
                                               (the 8 service LPs, /lp-job-ad,
                                               /meta-thank-you)

Consumed by tools/build-legacy-lps.py and tools/build-legacy-all.py, and applied
to the hand-written pages in public/ by tools/apply-tracking.py.
"""

GTM_ID = 'GTM-NB7XCVVG'
# The paid landing pages run on their own container instead of GTM_ID.
# Same set as LP_SLUGS in build-legacy-lps.py — keep the two in step.
LP_GTM_ID = 'GTM-KF82PPKL'
LP_GTM_PAGES = {
    'ga-plumbing-services', 'sewer-lines', 'ga-tankless-water-heaters', 'ga-testimonials',
    'ga-water-heater', 'ga-about-us', 'ga-contact', 'drain-cleaning',
    'ga-garbage-disposal-services', 'hydrojetting', 'ga-leak-detection', 'toilet-overflow',
    'lp-job-ad', 'meta-thank-you',
}


def gtm_id(slug=None):
    return LP_GTM_ID if slug in LP_GTM_PAGES else GTM_ID


# Google Ads call line each paid LP shows. GTM-KF82PPKL owns call tracking on the
# LPs: it has one "Calls from Website" tag per line, and each must fire only
# where its own line is shown. So the LPs publish their line to the dataLayer as
# `call_line` (the GTM triggers key on it) and remember it in localStorage, so
# the shared /thank-you page the GHL form redirects to can show - and report -
# the line of the LP the lead came from. Keep in step with LP_PHONE /
# LP_OWN_LINE in build-legacy-lps.py and CALL_LINES in public/thank-you.html.
LP_CALL_LINE = '909-765-0236'
LP_CALL_LINES = {
    'toilet-overflow': '909-280-7894',
}


def call_line(slug=None):
    return LP_CALL_LINES.get(slug, LP_CALL_LINE)


GA4_ID = 'G-XL9X7ZMQ2J'
ADS_ID = 'AW-16721660937'
ADS_CALL_LABEL = 'AW-16721660937/BQtCCljq9NUcElmYwaU-'
# Google Ads swaps this number wherever it appears on the page. It is the LPs'
# call-tracking line, but the LPs no longer carry these hard-coded configs (see
# head()): their call tracking is in GTM-KF82PPKL. On the organic pages, which
# show the main line, this config is a no-op.
ADS_CALL_NUMBER = '(909)765-0236'
# Conversion label for the main organic line (909-780-0887), shown site-wide.
MAIN_CALL_LABEL = 'AW-16721660937/oj6tCMzeopcdEImYwaU-'
MAIN_CALL_NUMBER = '(909)780-0887'
# Conversion label for the Google Business Profile tracking line. This number
# isn't shown anywhere on the site - it's what GBP itself displays - so the
# config is just there to record conversions, with no number swap to fire.
GBP_CALL_LABEL = 'AW-16721660937/yy13COq3mpcdEImYwaU-'
GBP_CALL_NUMBER = '(909)675-1272'
META_PIXEL_ID = '1083376654248929'

# pages that carried the Meta Pixel on the legacy site
PIXEL_PAGES = {
    'ga-plumbing-services', 'drain-cleaning', 'hydrojetting', 'sewer-lines',
    'ga-water-heater', 'ga-tankless-water-heaters', 'ga-leak-detection',
    'ga-garbage-disposal-services', 'lp-job-ad', 'meta-thank-you',
    'toilet-overflow',              # new paid LP (content/new-lps.json)
}

HEAD_MARKER = '<!-- tracking:head -->'
BODY_MARKER = '<!-- tracking:body -->'


def head(slug=None):
    """Everything that went in <head>, in the legacy site's order."""
    if slug in LP_GTM_PAGES:
        # Call tracking on the LPs is GTM-KF82PPKL's job (see LP_CALL_LINES).
        # The hard-coded configs below would swap (909)765-0236 on every LP
        # regardless of GTM's triggers, so the LPs only publish their line.
        ads = f'''<!-- Google Ads call line -->
<script>
  window.dataLayer = window.dataLayer || [];
  dataLayer.push({{'call_line': '{call_line(slug)}'}});
  try {{ localStorage.setItem('call_line', '{call_line(slug)}'); }} catch (e) {{}}
</script>
'''
    else:
        ads = f'''<!-- Google Ads -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ADS_ID}"></script>
<script>
  gtag('config', '{ADS_CALL_LABEL}', {{
    'phone_conversion_number': '{ADS_CALL_NUMBER}'
  }});
  gtag('config', '{MAIN_CALL_LABEL}', {{
    'phone_conversion_number': '{MAIN_CALL_NUMBER}'
  }});
  gtag('config', '{GBP_CALL_LABEL}', {{
    'phone_conversion_number': '{GBP_CALL_NUMBER}'
  }});
</script>
'''
    out = f'''{HEAD_MARKER}
<!-- Google tag (gtag.js) - GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA4_ID}');
</script>
{ads}<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{gtm_id(slug)}');</script>
<!-- End Google Tag Manager -->'''
    if slug in PIXEL_PAGES:
        out += f'''
<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{META_PIXEL_ID}');
fbq('track', 'PageView');
</script>
<!-- End Meta Pixel Code -->'''
    return out


def body(slug=None):
    """Everything that went immediately after <body>."""
    out = f'''{BODY_MARKER}
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id(slug)}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->'''
    if slug in PIXEL_PAGES:
        out += f'''
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={META_PIXEL_ID}&ev=PageView&noscript=1" /></noscript>'''
    return out
