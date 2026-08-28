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
  css/style.css, js/main.js
  images/, video/, fonts/
content/legacy-scrape/                     scraped copy from the old WordPress site
  <slug>.md, pages.json, raw-html/, README.md
tools/parse-legacy.py                      raw-html/ -> pages.json
tools/build-legacy-lps.py                  pages.json -> public/<slug>.html
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

Tracking that was on the legacy pages and is **not** in these files yet — decide
before launch whether to carry it over: GTM `GTM-NB7XCVVG`, GA4 `G-XL9X7ZMQ2J`,
Google Ads `AW-16721660937`.

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

## Cache-busting

Asset URLs are versioned (`/css/style.css?v=...`) so browsers fetch fresh CSS/JS/video after a deploy instead of serving a week-old cached copy. Since pages are static HTML now, this version string is baked into the files rather than computed per-request — if you change `style.css`, `main.js`, or the hero video, bump the `?v=` value across `public/*.html` and `public/blog/*.html` (find-and-replace) **and** the `V` constant in `tools/build-legacy-lps.py`, so visitors actually get the update. Currently `static-4`.

## Deployment

**GitHub:** push this repo as-is — `node_modules/`, original source photos/videos (`references/`), and the original font folder (`fonts/`) are git-ignored since everything actually used by the site is already optimized into `public/`.

**Railway:**
1. Create a new Railway project from this GitHub repo.
2. Railway auto-detects the Node app via `package.json` and runs `npm install` + `npm start` (see `railway.json`).
3. No environment variables are required for the current feature set.
4. Once deployed, point the production domain (`lincolnplumbingandrooter.com`) at the Railway service.
