const express = require('express');
const path = require('path');

const site = require('./data/site');
const services = require('./data/services');
const posts = require('./data/posts');
const icons = require('./data/icons');
const gallery = require('./data/gallery');

const app = express();
const PORT = process.env.PORT || 3000;

// Cache-busting token appended to static asset URLs as `?v=`. Static assets are
// served with a long max-age, so without this, browsers that visited before a
// deploy keep using their stale cached CSS/JS/video until it expires. Railway
// sets RAILWAY_GIT_COMMIT_SHA per deploy; falling back to boot time covers
// local dev and any environment that doesn't provide it.
const ASSET_VERSION = process.env.RAILWAY_GIT_COMMIT_SHA || String(Date.now());

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public'), { maxAge: '7d' }));

// Make shared data available to every view without passing it explicitly each time.
app.use((req, res, next) => {
  res.locals.site = site;
  res.locals.icons = icons;
  res.locals.currentPath = req.path;
  res.locals.v = ASSET_VERSION;
  next();
});

function sortedPosts() {
  return [...posts].sort((a, b) => new Date(b.date) - new Date(a.date));
}

app.get('/', (req, res) => {
  res.render('index', {
    title: `${site.shortName} | Trusted Plumbers in San Bernardino & the Inland Empire`,
    description: 'Family-owned plumbing company serving the Inland Empire since 2021. 24/7 emergency service, free estimates, and licensed technicians you can trust.',
    services,
    recentPosts: sortedPosts().slice(0, 3)
  });
});

app.get('/services', (req, res) => {
  res.render('services', {
    title: `Plumbing Services | ${site.shortName}`,
    description: 'Water heaters, drain cleaning & hydrojetting, sewer lines & slab leaks, and general plumbing repair for the Inland Empire.',
    services
  });
});

app.get('/gallery', (req, res) => {
  res.render('gallery', {
    title: `Photo Gallery | ${site.shortName}`,
    description: 'A look at real jobs, real trucks, and the real team behind Lincoln Plumbing & Rooter.',
    gallery
  });
});

app.get('/about', (req, res) => {
  res.render('about', {
    title: `Our Story | ${site.shortName}`,
    description: 'Founded by two brothers in 2021, Lincoln Plumbing & Rooter has grown into a trusted name across the Inland Empire.'
  });
});

app.get('/contact', (req, res) => {
  res.render('contact', {
    title: `Contact Us | ${site.shortName}`,
    description: 'Schedule a free estimate or reach our team 24/7 for emergency plumbing service.',
    sent: req.query.sent === '1'
  });
});

app.post('/contact', (req, res) => {
  const { name, phone, email, service, message } = req.body;

  // TODO: wire this up to email/CRM delivery (e.g. HouseCall Pro or SendGrid) once credentials are available.
  console.log('New contact form submission:', {
    name,
    phone,
    email,
    service,
    message,
    receivedAt: new Date().toISOString()
  });

  const redirectTo = req.get('Referer') && req.get('Referer').includes('/contact') ? '/contact' : (req.get('Referer') || '/');
  const separator = redirectTo.includes('?') ? '&' : '?';
  res.redirect(`${redirectTo}${separator}sent=1`);
});

app.get('/blog', (req, res) => {
  res.render('blog/index', {
    title: `Blog | ${site.shortName}`,
    description: 'Plumbing tips, guides, and news from the Lincoln Plumbing & Rooter team.',
    posts: sortedPosts()
  });
});

app.get('/blog/:slug', (req, res, next) => {
  const post = posts.find((p) => p.slug === req.params.slug);
  if (!post) return next();

  const all = sortedPosts();
  const index = all.findIndex((p) => p.slug === post.slug);
  const related = all.filter((p) => p.slug !== post.slug).slice(0, 3);

  res.render('blog/post', {
    title: `${post.title} | ${site.shortName}`,
    description: post.excerpt,
    post,
    related
  });
});

app.use((req, res) => {
  res.status(404).render('404', {
    title: `Page Not Found | ${site.shortName}`,
    description: 'The page you were looking for could not be found.'
  });
});

app.listen(PORT, () => {
  console.log(`Lincoln Plumbing & Rooter site running on port ${PORT}`);
});
