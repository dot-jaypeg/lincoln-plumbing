# Lincoln Plumbing & Rooter, INC — Website

Pure static HTML/CSS/JS site for Lincoln Plumbing & Rooter, serving San Bernardino and the Inland Empire.

## Stack

- **Every page is a real, plain `.html` file** in `public/` — open any of them in a text editor and you'll see complete, final markup, no templating syntax, no build step to run to read or edit them.
- **URLs have no `.html` extension.** `public/hydrojetting.html` is served at `/hydrojetting`. `server.js` 301-redirects both older shapes to that canonical form: `/hydrojetting.html` → `/hydrojetting`, and `/hydrojetting/` → `/hydrojetting` (the old WordPress URLs all had a trailing slash). Internal links throughout `public/` are already extensionless — keep new ones that way.
- **`public/css/style.css`** is the entire design system (fonts, colors, layout, components). **`public/js/main.js`** handles the mobile nav drawer, the scroll-triggered header state on the homepage, and the contact-form success toast.
- **`server.js`** is a small Express app whose only jobs are: (1) serve the `public/` folder as static files with clean URLs, (2) 301 the legacy `.html` / trailing-slash URLs to their canonical form, and (3) handle the one dynamic thing a static site can't do on its own — receiving `POST /contact` from the contact forms. It does not template or generate any HTML.

## Local development

```bash
npm install
npm start        # http://localhost:3000
```

## Project structure

```
public/
  index.html, services.html, gallery.html, about.html, contact.html, 404.html
  blog/index.html, blog/<slug>.html        (10 posts)
  <11 legacy-slug landing pages>           (generated — see below)
  plumbing-services/, drains-and-sewers/,  (generated — 178 more legacy pages)
  leak-detection/, service-locations/,
  specials.html, testimonials.html, sitemap.html, …
  <89 root-level blog posts>.html
  sitemap.xml, robots.txt
  css/style.css, js/main.js
  images/, video/, fonts/
content/legacy-scrape/                     scraped copy from the old WordPress site
  <slug>.md, pages.json, raw-html/, README.md      (the 11 landing pages)
  all-slugs.txt, all-pages.json, raw-html-full/    (all 190 legacy URLs)
content/repo-posts/                        the 10 pre-swap rewritten posts
tools/parse-legacy.py                      raw-html/ -> pages.json
tools/build-legacy-lps.py                  pages.json -> public/<slug>.html
tools/build-legacy-all.py                  raw-html-full/ -> everything else
server.js         static file server, clean-URL redirects, POST /contact handler
```

## Legacy landing pages

Eleven pages carried over from the old WordPress/Divi site when the platform was
swapped, at their **original slugs**, so existing rankings, backlinks, and ad
destinations keep working:

`/ga-plumbing-services` · `/drain-cleaning` · `/hydrojetting` · `/sewer-lines` ·
`/ga-water-heater` · `/ga-tankless-water-heaters` · `/ga-leak-detection` ·
`/ga-garbage-disposal-services` · `/ga-about-us` · `/ga-testimonials` · `/ga-contact`

The `ga-` prefix on seven of them is inherited from the old site and is kept
deliberately — do not "clean it up" without 301s in place.

Their **copy is the legacy copy, verbatim**; only the chrome (header, nav,
footer), the design system, and the phone/email are this site's. They are
generated, not hand-written:

```bash
python3 tools/parse-legacy.py       # re-parse content/legacy-scrape/raw-html/ -> pages.json
python3 tools/build-legacy-lps.py   # pages.json -> public/<slug>.html
```

The output is plain final HTML like every other page, so **small edits can just
be made directly in `public/<slug>.html`** — but they'll be overwritten if the
builder is re-run, so anything structural belongs in `tools/build-legacy-lps.py`.

Two things about these pages differ from the rest of the site on purpose:

- **Lead capture is the client's GoHighLevel form, not `POST /contact`.** One
  form ("Meta Form", id `dxqfiiA9bB1OLTNaNnRx`, on `link.advancedmarketers.co`)
  is embedded twice per service page — once in the hero, once in the `#quote`
  section — plus once on `/ga-contact`. Only the iframe id suffix differs
  (`-hero`, `-final`, `-contact`) so two embeds on one page don't collide.
  `https://link.advancedmarketers.co/js/form_embed.js` at the end of the body is
  what resizes them.
- **Their footer has a "Service Pages" column instead of the mini request-service
  form**, so an LP has exactly one lead path rather than two competing ones.

Also carried over from the legacy site: the **GoodLeap financing band** (links to
the client's GoodLeap application) and, on `/ga-testimonials`, the four real
**Yelp review embeds** (`yelp.com/embed/widgets.js`).

### Tracking

All four tags from the legacy site are wired in, reproduced snippet-for-snippet
and with the same page distribution the old site used. The snippets live in one
place, `tools/tracking.py`:

| Tag | ID | Where |
|---|---|---|
| Google Tag Manager | `GTM-NB7XCVVG` | every page |
| GA4 | `G-XL9X7ZMQ2J` | every page |
| Google Ads | `AW-16721660937` | every page |
| Meta Pixel | `1083376654248929` | the 8 service LPs, `/lp-job-ad`, `/meta-thank-you` |

The Meta Pixel really was only on those ten pages on the legacy site — the
paid-traffic ones. It was not on `/ga-about-us`, `/ga-contact` or
`/ga-testimonials`, and it is not on them here either.

The generated pages pick the tags up from the builders. The six hand-written
pages get them from a separate script, which strips any existing tracking markup
before inserting so it is safe to re-run after editing a page:

```bash
python3 tools/apply-tracking.py
```

The Google Ads snippet also carries the call-conversion config from the legacy
site, which pairs with the two phone numbers described below:

```js
gtag('config', 'AW-16721660937/BQtCCljq9NUcElmYwaU-', {
  'phone_conversion_number': '(909)765-0236'
});
```

### One thing to confirm in Google Ads

The legacy site carried **two different conversion labels** for the same
conversion action — `AW-16721660937/BQtCCljq9NUcElmYwaU-` on all 190 pages (from
the theme header) and `AW-16721660937/BQtCCIjq9NUcEImYwaU-` on the 11 hand-coded
landing pages. They differ only in `l` vs `I`, which is the classic
copy-by-hand mistake, so one of them almost certainly records nothing. This repo
uses the 190-page variant. Worth confirming against the Ads UI and correcting
`ADS_CALL_LABEL` in `tools/tracking.py` if it's the wrong one.

## Paid landing pages are isolated

The 13 paid pages are a closed funnel, deliberately sealed off from the organic
site in both directions:

- **No organic page links to one.** Not from the nav, the footer, `/services`, or
  `/sitemap`. Where a legacy page's body copy linked to a landing page, the link
  is remapped to the organic page covering the same service (`/drain-cleaning` →
  `/drains-and-sewers/drain-cleaning`, `/ga-contact` → `/contact`, and so on).
- **No landing page links to the organic site.** They get their own chrome —
  `lp_chrome_top()` / `lp_chrome_bottom()` in `tools/build-legacy-lps.py`: an
  address strip, a logo, a quote button and the tracking phone number, and a
  one-line footer. No nav, no breadcrumb. This is how the legacy LPs were built
  too; their markup had no navigation at all. Internal links inside imported LP
  body copy are unwrapped to plain text.
- **`noindex, follow` on all 13, and none of them are in `sitemap.xml`.** This
  also settles the duplicate-content overlap: `/ga-water-heater` vs
  `/plumbing-services/water-heaters/`, `/ga-contact` vs `/contact`,
  `/ga-testimonials` vs `/testimonials` and so on. The organic tree owns those
  topics; the LPs just serve ads.

They still cross-link *each other* ("Other Services We Offer"), which keeps paid
visitors inside the paid set.

`LP_SLUGS` in `tools/build-legacy-lps.py` is the single definition of what counts
as a paid page. Everything above — chrome, phone number, `noindex`, sitemap
exclusion, link remapping — is driven off it, so moving a page in or out of the
funnel is a one-line change plus a rebuild.

## Two phone numbers

| Number | Shown on |
|---|---|
| **909-780-0887** — main line | the organic site: `/`, `/services`, `/gallery`, `/about`, `/contact`, the whole service tree, the service-location pages, `/blog/` and all 89 posts |
| **909-765-0236** — Google Ads call-tracking line | the 13 paid landing pages: the 11 legacy LPs plus `/lp-job-ad` and `/meta-thank-you` |

This is what makes the Google Ads `phone_conversion_number` above work: it swaps
the tracking number, which only ever appears on landing pages, so number
swapping fires on paid traffic and is a no-op on organic pages.

Both numbers are defined once, at the top of `tools/build-legacy-lps.py`
(`PHONE`/`TEL` and `LP_PHONE`/`LP_TEL`), together with `LP_SLUGS` — the set of
pages that count as landing pages. `phone()` and `tel()` return the right one
for whichever page is being built, and both builders use them, so the header,
the mobile call bar, every CTA, the footer and the imported body copy all agree
on a single page. The legacy copy mentions both numbers in half a dozen
formats; `normalise_phone()` rewrites every one of them to the right number for
the page rather than trusting the source.

If you change a number, change it there and re-run both builders plus
`python3 tools/apply-tracking.py` — don't hand-edit the pages.

Because the two page sets are fully isolated (above), a visitor can't cross from
one to the other and see the "wrong" number mid-session.

### The GHL form's on-submit behaviour

Read straight out of the form's own config: `actionType: "2"`, `redirectUrl: ""`
— **the form does not redirect anywhere.** On submit it swaps the iframe for
GoHighLevel's stock inline message, *"😊 We appreciate your feedback! Thank you
for taking the time to complete this form."* That is generic survey wording, not
plumbing-lead wording. `/meta-thank-you` (below) exists but nothing in the form
points at it. Worth fixing in GHL, not here.

The form is also protected by Cloudflare Turnstile, so it can't be submitted by
a script — test submissions have to be done by hand in a browser.

## Everything else from the legacy site

The other 178 pages in the old sitemap — the service tree, the service-location
pages, the utility pages and the blog — are ordinary Divi/WordPress pages whose
content lives in `<article><div class="entry-content">`, so they're generated by
a second, separate pipeline:

```bash
python3 tools/build-legacy-all.py     # raw-html-full/ -> all-pages.json -> public/**
```

It reads `content/legacy-scrape/raw-html-full/` (one file per URL, `/` in the
slug written as `~`) and `content/legacy-scrape/all-slugs.txt` (the URL list,
taken from the legacy Yoast sitemap). It also writes `public/sitemap.xml`,
`public/robots.txt`, `public/sitemap.html`, and rebuilds `public/blog/index.html`.

What it produces:

| Section | Count | URL shape |
|---|---|---|
| `/plumbing-services/` + children | 18 | hub keeps its trailing slash, children don't |
| `/drains-and-sewers/` + children | 7 | " |
| `/leak-detection/` + children | 7 | " |
| `/service-locations/` + 8 cities × 5 services | 49 | " |
| Utility pages | 6 | `/specials`, `/testimonials`, `/sitemap`, `/privacy-policy`, `/lp-job-ad`, `/meta-thank-you` |
| Blog posts | 89 | root-level, e.g. `/how-hard-water-can-damage-your-plumbing…` |

Things worth knowing about it:

- **Blog posts are root-level**, because that's where they were on the legacy
  site (`/why-drain-odors-develop…`, not `/blog/why-drain-odors-develop…`).
  `/blog/` is the index of all 89.
- **Ten posts had already been rewritten for this site** and lived at
  `/blog/<slug>`. Their approved copy is snapshotted in `content/repo-posts/` and
  still wins — it's just served at the legacy root slug now, with `/blog/<slug>`
  301-ing there.
- **Section hubs are `<dir>/index.html`** and keep their trailing slash
  (`/plumbing-services/`); leaf pages are `<name>.html` and have it stripped.
  `server.js` scans `public/` once at boot to tell the two apart.
- **Prose is tidied, not rewritten**: the leading `<h2>` that just repeats the
  page title is dropped, repeated Divi buttons are deduplicated, runs of stacked
  images become a 2-up row, and a post's own featured image is lifted out of the
  body to become its hero (78 of 89 posts have one).
- **102 content images** were pulled down to `public/images/legacy/` and
  optimised with `sips` (147MB → 27MB).
- **Four legacy pages ship with an empty body on the live site.**
  `/leak-detection/rooter-services`, `/leak-detection/sewer-line-repair` and
  `/leak-detection/sewer-line-replacement` are empty duplicates of the populated
  `/drains-and-sewers/*` pages, so they now point at those. `/privacy-policy`
  never had any policy text — it carries a visible **[PLACEHOLDER]** block that
  needs real copy before launch.
- `/meta-thank-you` is kept `noindex`, as it was on the legacy site, and carries
  no quote form — it's a confirmation page.
- **`/lp-job-ad` is the one page the generic importer doesn't do justice.** It's
  a bespoke recruiting LP built around two videos, a lead-gated video unlock and
  a custom ticker, and flattening it to prose loses that layout. Its two videos
  are also **404 on the legacy site**, so they couldn't be imported — each slot
  carries a visible `[PLACEHOLDER — video needed.]` note instead. The page is
  readable and its GHL application forms work, but it wants a proper hand-build
  like the other LPs got.

Pages deliberately **not** taken from the legacy site, because this site already
has its own approved versions at the same URLs: `/` , `/about`, `/contact`.

## Editing content

Since there's no templating layer, editing content means editing the relevant `.html` file(s) directly:

- **Site-wide bits** (phone number, address, nav, footer) are duplicated across every page — the header/nav/footer markup is identical in each `.html` file. If you change one (e.g. the phone number), use a project-wide find-and-replace across `public/*.html` and `public/blog/*.html` rather than editing pages one at a time — and update the constants at the top of `tools/build-legacy-lps.py` too, or the next build of the landing pages will put the old value back.
- **Adding a blog post**: copy an existing `public/blog/<slug>.html`, edit its content, and add a matching card (image/title/excerpt/link) to `public/blog/index.html` and to the "From the Blog" section in `public/index.html`.

## Contact form

`POST /contact` (used by both the footer mini-form on every page and the full form on `contact.html`) currently logs submissions to the server console and redirects back to the referring page with `?sent=1`. `public/js/main.js` watches for that query param and shows a success toast client-side (there's no server-rendered confirmation anymore, since pages are static).

It is **not yet wired to email or a CRM** — hook it up to an email service (e.g. Resend, SendGrid) or HouseCall Pro's API once credentials are available, inside the `app.post('/contact', ...)` handler in `server.js`.

## Homepage hero video

The homepage hero uses a looping muted background video (`public/video/hero-loop.mp4` / `.webm`), transcoded from the client's raw 4K source (`references/Lincoln Plumbing 2/VIDEOS/Lincolns plumbing Landing page.mp4`, ~128MB) down to 1080p/no-audio (~6MB each format) since the raw file is far too large to serve or commit. `public/images/hero-poster.jpg` is a still frame shown before the video loads.

To re-encode (no system ffmpeg needed — this machine doesn't have one; `npm install ffmpeg-static` in a scratch directory gets a working binary):
```bash
ffmpeg -i "source.mp4" -vf "scale=1920:-2" -an -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart public/video/hero-loop.mp4
ffmpeg -i "source.mp4" -vf "scale=1920:-2" -an -c:v libvpx-vp9 -b:v 0 -crf 34 -row-mt 1 public/video/hero-loop.webm
ffmpeg -ss 00:00:01.2 -i "source.mp4" -frames:v 1 -vf "scale=1920:-2" -q:v 4 public/images/hero-poster.jpg
```

## Caching

This bit caused a real incident after the platform swap, so it's worth reading
before changing.

**HTML is never cached.** Pages are served `Cache-Control: no-cache,
must-revalidate`. They used to be served `public, max-age=604800` — the same
7-day header as the assets — which meant a returning visitor's browser rendered
whatever markup it had from its last visit *without contacting the server at
all*, and no deploy could reach them for a week. `express.static` still sends an
ETag, so an unchanged page revalidates as a 304 with no body; the cost of this is
close to nothing.

**Assets are cached forever, and versioned by content hash.** `?v=` is a hash of
`style.css` + `main.js` + the font, maintained by `tools/bump-assets.py`. It used
to be a hand-typed token (`?v=static-4`), which is a trap: append to `style.css`,
forget to bump, and returning visitors keep the old stylesheet under the same URL
while the new markup expects new classes. A content hash can't drift.

So the build order is:

```bash
python3 tools/build-legacy-lps.py
python3 tools/build-legacy-all.py
python3 tools/apply-tracking.py
python3 tools/bump-assets.py      # last — it stamps the hash into every page
```

**Trailing slashes are not redirected.** Both `/hydrojetting` and
`/hydrojetting/` return 200; `<link rel="canonical">` decides which one is
indexed. This is deliberate: the old WordPress site permanently redirected
`/hydrojetting` → `/hydrojetting/`, browsers cache a 301 more or less forever,
and redirecting the other way makes a returning visitor ping-pong between the two
until Chrome gives up with `ERR_TOO_MANY_REDIRECTS`. Don't reintroduce a
slash redirect in either direction.

`.html` URLs still 301 to the clean form — those were never public on the old
site, so there's no cached redirect to fight.

**Form embeds are never `loading="lazy"`.** A HAR from a real visit showed the
above-the-fold GoHighLevel iframe never being requested at all — `onLoad`
completed at 550ms with zero requests to the widget. Lazy iframes are deferred
past `onLoad` and, on that page, indefinitely. `form()` in
`tools/build-legacy-lps.py` emits them eagerly.

**Emergency escape hatch.** Setting `CLEAR_SITE_DATA=1` in Railway makes every
HTML response send `Clear-Site-Data: "cache"`, which tells browsers to drop this
origin's cache once. It only reaches browsers that actually make a request, so it
does nothing for one already serving a page out of cache — see the note below.
Turn it off after a few days; it costs every visitor a cold cache.

## The apex domain

`lincolnplumbingandrooter.com` (no www) is not served by this app. Railway needs
a CNAME for a custom domain, a CNAME is illegal at a zone apex, and GoDaddy DNS
has no ALIAS/ANAME record to work around that. What's there instead is GoDaddy
Domain Forwarding, which only handles the bare root and drops both the path and
the query string:

```
https://lincolnplumbingandrooter.com/             -> 301 to the www root, ?gclid dropped
https://lincolnplumbingandrooter.com/hydrojetting -> 404 (awselb)
```

Two consequences worth knowing: any ad click that lands on the apex loses its
`gclid`, and any deep link to the apex is dead. The canonical has always been
`www` (that's what the old site used and what Google has indexed), so organic
search is unaffected — the exposure is ad final URLs, Google Business Profile,
citations and bookmarks.

Options, cheapest first:

1. **Point everything at `www`.** Ad final URLs, GBP, citations. The apex root
   already redirects, so someone typing the bare domain still lands on the
   homepage. This alone closes the attribution hole.
2. **Serve the apex properly without moving DNS** — `tools/apex-redirect/` is a
   two-file site that 301s the apex to `www` preserving path and query. It goes
   on any host that serves an apex from a plain A record (Netlify, free), and
   needs only an A record change in GoDaddy. See that folder's README.
3. **Move DNS to Cloudflare, keeping the registrar at GoDaddy.** Cloudflare
   flattens CNAMEs at the apex, so the apex can point straight at Railway.
   Cleanest long term. Copy every existing record first — especially MX, SPF,
   DKIM and DMARC — or email breaks the moment the nameservers cut over.

### If stale markup is still in the wild

A browser holding an HTML response with a live `max-age` doesn't ask the server
anything, so nothing deployed here can reach it. What does:

- **Change the URL.** Adding or changing a query parameter on Google Ads
  destination URLs (`?v=2`) creates a new cache key and serves fresh markup
  immediately. This is the fix for paid traffic.
- **Wait it out.** Worst case is 7 days from the visitor's last page view, after
  which the no-cache header above applies and it can't recur.
- **A hard reload** (Cmd/Ctrl+Shift+R) for anyone you can reach directly.

## Deployment

**GitHub:** push this repo as-is — `node_modules/`, original source photos/videos (`references/`), and the original font folder (`fonts/`) are git-ignored since everything actually used by the site is already optimized into `public/`.

**Railway:**
1. Create a new Railway project from this GitHub repo.
2. Railway auto-detects the Node app via `package.json` and runs `npm install` + `npm start` (see `railway.json`).
3. No environment variables are required for the current feature set.
4. Once deployed, point the production domain (`lincolnplumbingandrooter.com`) at the Railway service.
