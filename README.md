# Lincoln Plumbing & Rooter, INC — Website

Node/Express + EJS site for Lincoln Plumbing & Rooter, serving San Bernardino and the Inland Empire.

## Stack

- **Express** serves the routes and renders **EJS** templates (`views/`) — plain HTML in the browser, shared header/footer via server-side includes so there's no duplicated markup across pages.
- **Static assets** (images, fonts, CSS, JS) live in `public/` and are served directly.
- **Content** (services, blog posts, gallery images, site/business info) lives in `data/*.js` as plain objects — edit those files to change copy, add a blog post, or update contact info without touching templates.

## Local development

```bash
npm install
npm start        # http://localhost:3000
```

## Project structure

```
data/            business info, services, blog posts, gallery, icon SVGs
views/           EJS templates (pages + partials/header, footer, trust-bar)
public/          images, video (hero background loop), fonts, css/style.css, js/main.js
server.js        Express app + routes
```

## Adding a blog post

Add an object to the array in `data/posts.js` (slug, title, date, image, excerpt, body as an HTML string). It will automatically appear on `/blog` and be reachable at `/blog/<slug>` — no other changes needed.

## Contact form

`POST /contact` (used by both the footer mini-form and the full `/contact` page form) currently logs submissions to the server console and redirects back with a success message. It is **not yet wired to email or a CRM** — hook it up to an email service (e.g. Resend, SendGrid) or HouseCall Pro's API once credentials are available, inside the `app.post('/contact', ...)` handler in `server.js`.

## Homepage hero video

The homepage hero uses a looping muted background video (`public/video/hero-loop.mp4` / `.webm`), transcoded from the client's raw 4K source (`references/Lincoln Plumbing 2/VIDEOS/Lincolns plumbing Landing page.mp4`, ~128MB) down to 1080p/no-audio (~6MB each format) since the raw file is far too large to serve or commit. `public/images/hero-poster.jpg` is a still frame shown before the video loads.

To re-encode (no system ffmpeg needed — this machine doesn't have one; `npm install ffmpeg-static` in a scratch directory gets a working binary):
```bash
ffmpeg -i "source.mp4" -vf "scale=1920:-2" -an -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart public/video/hero-loop.mp4
ffmpeg -i "source.mp4" -vf "scale=1920:-2" -an -c:v libvpx-vp9 -b:v 0 -crf 34 -row-mt 1 public/video/hero-loop.webm
ffmpeg -ss 00:00:01.2 -i "source.mp4" -frames:v 1 -vf "scale=1920:-2" -q:v 4 public/images/hero-poster.jpg
```

## Deployment

**GitHub:** push this repo as-is — `node_modules/`, original source photos/videos (`references/`), and the original font folder (`fonts/`) are git-ignored since everything actually used by the site is already optimized into `public/`.

**Railway:**
1. Create a new Railway project from this GitHub repo.
2. Railway auto-detects the Node app via `package.json` and runs `npm install` + `npm start` (see `railway.json`).
3. No environment variables are required for the current feature set.
4. Once deployed, point the production domain (`lincolnplumbingandrooter.com`) at the Railway service.
