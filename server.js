const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');

app.use(express.urlencoded({ extended: true }));
app.use(express.static(PUBLIC_DIR, { maxAge: '7d' }));

// The site is pure static HTML/CSS/JS (public/). This is the one dynamic
// endpoint: both the footer mini-form and the /contact.html page form POST
// here. TODO: wire this up to email/CRM delivery (e.g. HouseCall Pro or
// SendGrid) once credentials are available — for now it just logs and
// redirects back with a success flag.
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

  const referer = req.get('Referer') || '/contact.html';
  const separator = referer.includes('?') ? '&' : '?';
  res.redirect(`${referer}${separator}sent=1`);
});

app.use((req, res) => {
  res.status(404).sendFile(path.join(PUBLIC_DIR, '404.html'));
});

app.listen(PORT, () => {
  console.log(`Lincoln Plumbing & Rooter site running on port ${PORT}`);
});
