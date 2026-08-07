(function () {
  const toggle = document.querySelector('.nav-toggle');
  const closeBtn = document.querySelector('.mobile-nav-close');
  const drawer = document.querySelector('.mobile-nav');

  function openDrawer() {
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    drawer.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (toggle && drawer) toggle.addEventListener('click', openDrawer);
  if (closeBtn && drawer) closeBtn.addEventListener('click', closeDrawer);
  if (drawer) {
    drawer.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeDrawer));
  }

  // Toggle a body-level "scrolled" state: drives the header shadow on every
  // page, and the transparent-over-hero -> solid-white transition on home.
  const onScroll = () => {
    document.body.classList.toggle('scrolled', window.scrollY > 8);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // The contact form (footer mini-form or the full /contact.html form) posts
  // to the server and redirects back with ?sent=1. Since pages are static,
  // there's no server-rendered confirmation banner — show a toast instead,
  // then clean the query param off the URL.
  const params = new URLSearchParams(window.location.search);
  if (params.get('sent') === '1') {
    const toast = document.createElement('div');
    toast.className = 'alert-success alert-toast';
    toast.textContent = "Thanks — your request was received. Our team will call you back shortly.";
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => toast.classList.remove('show'), 6000);
    setTimeout(() => toast.remove(), 6500);

    params.delete('sent');
    const query = params.toString();
    window.history.replaceState({}, '', window.location.pathname + (query ? `?${query}` : ''));
  }
})();
