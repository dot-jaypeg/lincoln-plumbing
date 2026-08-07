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
})();
