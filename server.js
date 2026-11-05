const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

// Section hubs are directories with an index.html (public/plumbing-services/index.html
// -> /plumbing-services/). Scanned once at boot so the routing below can tell a hub
// URL from a page URL without hitting the disk on every request.
const DIR_INDEXES = new Set();
(function scan(dir, prefix) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const url = `${prefix}${entry.name}/`;
    if (fs.existsSync(path.join(dir, entry.name, 'index.html'))) DIR_INDEXES.add(url);
    scan(path.join(dir, entry.name), url);
  }
})(PUBLIC_DIR, '/');
const isDirIndex = p => DIR_INDEXES.has(p);

// ---------------------------------------------------------------------------
// Clean URLs. Every page on disk is still a plain `.html` file in public/, but
// it is served without the extension: /hydrojetting, /ga-water-heater, /about.
//
// `.html` URLs 301 to the clean form — those were never public on the old site,
// so there's no chance of fighting a redirect a browser already has cached.
//
// Trailing slashes are deliberately NOT redirected. The old WordPress site
// permanently redirected /hydrojetting -> /hydrojetting/ (WP enforces the
// trailing slash), and browsers cache a 301 more or less forever. If we
// redirect the other way, a returning visitor ping-pongs between the two and
// gets ERR_TOO_MANY_REDIRECTS. So both forms serve the page with a 200 and the
// <link rel="canonical"> in the markup decides which one search engines index.
// ---------------------------------------------------------------------------
app.use((req, res, next) => {
  const [pathname, query = ''] = req.url.split('?');
  const suffix = query ? `?${query}` : '';

  if (pathname.endsWith('/index.html')) {
    return res.redirect(301, pathname.slice(0, -'index.html'.length) + suffix);
  }
  if (pathname.endsWith('.html')) {
    return res.redirect(301, pathname.slice(0, -'.html'.length) + suffix);
  }

  // The ten posts that were rewritten for this site used to live at
  // /blog/<slug>; they are now served at the legacy root-level slug.
  const post = pathname.match(/^\/blog\/(.+)$/);
  if (post && post[1] !== 'index' && fs.existsSync(path.join(PUBLIC_DIR, `${post[1]}.html`))) {
    return res.redirect(301, `/${post[1]}${suffix}`);
  }

  // Serve both slash forms rather than redirecting between them (see above):
  //   /plumbing-services  -> the hub's index.html
  //   /hydrojetting/      -> hydrojetting.html
  if (pathname.length > 1 && !pathname.endsWith('/') && isDirIndex(pathname + '/')) {
    req.url = pathname + '/' + suffix;
  } else if (pathname.length > 1 && pathname.endsWith('/') && !isDirIndex(pathname)) {
    req.url = pathname.slice(0, -1) + suffix;
  }

  next();
});

// Lead forms post straight from the browser to the GHL inbound webhook
// (public/js/lead-form.js). The URL lives in the GHL_WEBHOOK_URL Railway
// variable rather than in the repo, and reaches the page as this tiny script.
// It is not a secret (any visitor can read it), it just isn't hard-coded.
const GHL_WEBHOOK_URL = (process.env.GHL_WEBHOOK_URL || '').trim();
if (!GHL_WEBHOOK_URL) {
  console.warn('GHL_WEBHOOK_URL is not set: lead forms will show the phone number instead of sending.');
}
app.get('/js/lead-config.js', (req, res) => {
  res.type('application/javascript')
    .set('Cache-Control', 'no-cache, must-revalidate')
    .send(`window.LEAD_WEBHOOK_URL = ${JSON.stringify(GHL_WEBHOOK_URL)};\n`);
});

// ---------------------------------------------------------------------------
// Caching. Assets are versioned in their URL (/css/style.css?v=static-4), so
// they can be cached hard. HTML must NOT be: it was previously served with
// max-age=604800, which pinned every visitor to whatever markup was live when
// they first landed and meant a deploy couldn't reach them for a week. Pages
// now always revalidate — cheap, because express.static still sends an ETag, so
// an unchanged page is a 304 with no body.
// ---------------------------------------------------------------------------
const IMMUTABLE = /\.(?:css|js|png|jpe?g|gif|svg|webp|avif|ico|woff2?|ttf|eot|mp4|webm)$/i;

app.use(express.static(PUBLIC_DIR, {
  extensions: ['html'],           // what makes /about resolve to public/about.html
  etag: true,
  lastModified: true,
  setHeaders(res, filePath) {
    if (IMMUTABLE.test(filePath)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    } else {
      res.setHeader('Cache-Control', 'no-cache, must-revalidate');
    }
  },
}));

// One-shot escape hatch for browsers still holding cached markup from the old
// WordPress site (dead /wp-content assets -> unstyled page, missing lazy-load
// script -> the GoHighLevel form never initialises). Setting CLEAR_SITE_DATA=1
// in Railway makes every HTML response tell the browser to drop this origin's
// cache once. Turn it back off after a few days: it costs every visitor a
// cold cache on their next page view.
if (process.env.CLEAR_SITE_DATA === '1') {
  app.use((req, res, next) => {
    if (!path.extname(req.path)) res.setHeader('Clear-Site-Data', '"cache"');
    next();
  });
}

app.use((req, res) => {
  res.status(404)
    .set('Cache-Control', 'no-store')
    .sendFile(path.join(PUBLIC_DIR, '404.html'));
});

app.listen(PORT, () => {
  console.log(`Lincoln Plumbing & Rooter site running on port ${PORT}`);
});
