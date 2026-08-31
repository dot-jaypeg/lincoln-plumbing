const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

app.use(express.urlencoded({ extended: true }));

// Section hubs are directories with an index.html (public/plumbing-services/index.html
// -> /plumbing-services/). Scanned once at boot so the redirect middleware can tell
// a hub URL from a page URL without hitting the disk on every request.
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
// The two legacy shapes 301 to that canonical form so nothing that's already
// indexed or running in an ad breaks:
//   /hydrojetting.html  -> /hydrojetting
//   /hydrojetting/      -> /hydrojetting   (the old WordPress URLs had a slash)
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
  // Trailing slash: kept for paths that are a real directory with an index.html
  // (the section hubs — /plumbing-services/, /service-locations/fontana-ca/, …),
  // stripped for everything else.
  if (pathname.length > 1 && pathname.endsWith('/')) {
    if (!isDirIndex(pathname)) {
      return res.redirect(301, pathname.slice(0, -1) + suffix);
    }
  } else if (isDirIndex(pathname + '/')) {
    // ...and added back if it was missing
    return res.redirect(301, pathname + '/' + suffix);
  }

  // The ten posts that were rewritten for this site used to live at
  // /blog/<slug>; they are now served at the legacy root-level slug.
  const post = pathname.match(/^\/blog\/(.+)$/);
  if (post && post[1] !== 'index' && fs.existsSync(path.join(PUBLIC_DIR, `${post[1]}.html`))) {
    return res.redirect(301, `/${post[1]}${suffix}`);
  }

  next();
});

// `extensions: ['html']` is what makes /about resolve to public/about.html.
app.use(express.static(PUBLIC_DIR, { maxAge: '7d', extensions: ['html'] }));

// The site is otherwise pure static HTML/CSS/JS (public/). This is the one
// dynamic endpoint: the footer mini-form and the /contact page form POST here.
// The landing pages generated from the legacy site use the embedded GoHighLevel
// "Meta Form" instead, which posts straight to the CRM and never touches this.
// TODO: wire this up to email/CRM delivery once credentials are available — for
// now it just logs and redirects back with a success flag.
app.post('/contact', (req, res) => {
  const { name, phone, email, service, message } = req.body;

  console.log('New contact form submission:', {
    name,
    phone,
    email,
    service,
    message,
    receivedAt: new Date().toISOString()
  });

  const referer = req.get('Referer') || '/contact';
  const separator = referer.includes('?') ? '&' : '?';
  res.redirect(`${referer}${separator}sent=1`);
});

app.use((req, res) => {
  res.status(404).sendFile(path.join(PUBLIC_DIR, '404.html'));
});

app.listen(PORT, () => {
  console.log(`Lincoln Plumbing & Rooter site running on port ${PORT}`);
});
