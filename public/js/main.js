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

  // Sticky header shadow on scroll
  const header = document.querySelector('.site-header');
  if (header) {
    const onScroll = () => {
      header.style.boxShadow = window.scrollY > 8 ? '0 4px 16px rgba(20,24,31,0.06)' : 'none';
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();
