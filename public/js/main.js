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
  // ---- Scroll reveal: fade/slide elements in as they enter the viewport ----
  const revealEls = document.querySelectorAll('[data-reveal]');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (revealEls.length && 'IntersectionObserver' in window && !reduceMotion) {
    const revObserver = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach((el) => revObserver.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  // ---- Count-up: animate stat numbers once they scroll into view ----------
  const counters = document.querySelectorAll('.num[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const runCount = (el) => {
      const target = parseFloat(el.getAttribute('data-count')) || 0;
      const valEl = el.querySelector('.val');
      if (!valEl) return;
      if (reduceMotion) { valEl.textContent = target; return; }
      const duration = 1400;
      let start = null;
      const step = (ts) => {
        if (start === null) start = ts;
        const p = Math.min((ts - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        valEl.textContent = Math.round(target * eased);
        if (p < 1) requestAnimationFrame(step);
        else valEl.textContent = target;
      };
      requestAnimationFrame(step);
    };
    const countObserver = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { runCount(entry.target); obs.unobserve(entry.target); }
      });
    }, { threshold: 0.5 });
    counters.forEach((el) => countObserver.observe(el));
  }

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
