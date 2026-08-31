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
GA4_ID = 'G-XL9X7ZMQ2J'
ADS_ID = 'AW-16721660937'
ADS_CALL_LABEL = 'AW-16721660937/BQtCCljq9NUcElmYwaU-'
# Google Ads swaps this number wherever it appears on the page. It is the
# call-tracking line, which is shown only on the landing pages (see LP_PHONE in
# build-legacy-lps.py) - so the swap fires there and is a no-op on the organic
# pages, which show the main line. That is the intended behaviour.
ADS_CALL_NUMBER = '(909)765-0236'
META_PIXEL_ID = '1083376654248929'

# pages that carried the Meta Pixel on the legacy site
PIXEL_PAGES = {
    'ga-plumbing-services', 'drain-cleaning', 'hydrojetting', 'sewer-lines',
    'ga-water-heater', 'ga-tankless-water-heaters', 'ga-leak-detection',
    'ga-garbage-disposal-services', 'lp-job-ad', 'meta-thank-you',
}

HEAD_MARKER = '<!-- tracking:head -->'
BODY_MARKER = '<!-- tracking:body -->'


def head(slug=None):
    """Everything that went in <head>, in the legacy site's order."""
    out = f'''{HEAD_MARKER}
<!-- Google tag (gtag.js) - GA4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA4_ID}');
</script>
<!-- Google Ads -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ADS_ID}"></script>
<script>
  gtag('config', '{ADS_CALL_LABEL}', {{
    'phone_conversion_number': '{ADS_CALL_NUMBER}'
  }});
</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{GTM_ID}');</script>
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
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->'''
    if slug in PIXEL_PAGES:
        out += f'''
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={META_PIXEL_ID}&ev=PageView&noscript=1" /></noscript>'''
    return out
