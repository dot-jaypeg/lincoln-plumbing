const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

app.use(express.urlencoded({ extended: true }));

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
  // trailing slash on anything but the site root or a real directory index
  if (pathname.length > 1 && pathname.endsWith('/') && pathname !== '/blog/') {
    return res.redirect(301, pathname.slice(0, -1) + suffix);
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
