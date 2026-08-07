# Lincoln Plumbing & Rooter, INC — Website

Pure static HTML/CSS/JS site for Lincoln Plumbing & Rooter, serving San Bernardino and the Inland Empire.

## Stack

- **Every page is a real, plain `.html` file** in `public/` — open any of them in a text editor and you'll see complete, final markup, no templating syntax, no build step to run to read or edit them.
- **`public/css/style.css`** is the entire design system (fonts, colors, layout, components). **`public/js/main.js`** handles the mobile nav drawer, the scroll-triggered header state on the homepage, and the contact-form success toast.
- **`server.js`** is a ~30-line Express app whose only jobs are: (1) serve the `public/` folder as static files, and (2) handle the one dynamic thing a static site can't do on its own — receiving `POST /contact` from the contact forms. It does not template or generate any HTML.

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
  css/style.css, js/main.js
  images/, video/, fonts/
server.js         static file server + POST /contact handler
```

## Editing content

Since there's no templating layer, editing content means editing the relevant `.html` file(s) directly:

- **Site-wide bits** (phone number, address, nav, footer) are duplicated across every page — the header/nav/footer markup is identical in each `.html` file. If you change one (e.g. the phone number), use a project-wide find-and-replace across `public/*.html` and `public/blog/*.html` rather than editing pages one at a time.
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

Asset URLs are versioned (`/css/style.css?v=...`) so browsers fetch fresh CSS/JS/video after a deploy instead of serving a week-old cached copy. Since pages are static HTML now, this version string is baked into the files rather than computed per-request — if you change `style.css`, `main.js`, or the hero video, bump the `?v=` value across `public/*.html` and `public/blog/*.html` (find-and-replace) so visitors actually get the update.

## Deployment

**GitHub:** push this repo as-is — `node_modules/`, original source photos/videos (`references/`), and the original font folder (`fonts/`) are git-ignored since everything actually used by the site is already optimized into `public/`.

**Railway:**
1. Create a new Railway project from this GitHub repo.
2. Railway auto-detects the Node app via `package.json` and runs `npm install` + `npm start` (see `railway.json`).
3. No environment variables are required for the current feature set.
4. Once deployed, point the production domain (`lincolnplumbingandrooter.com`) at the Railway service.
