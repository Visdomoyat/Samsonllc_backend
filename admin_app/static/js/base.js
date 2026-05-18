(function () {
  const header = document.getElementById('site-header');
  const toggle = document.getElementById('nav-toggle');
  const backdrop = document.getElementById('nav-backdrop');
  const nav = document.getElementById('main-nav');
  const mq = window.matchMedia('(max-width: 768px)');

  if (!header || !toggle || !backdrop || !nav) {
    return;
  }

  function isMobileNav() {
    return mq.matches;
  }

  function setOpen(open) {
    header.classList.toggle('is-nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('nav-open', open && isMobileNav());
    backdrop.hidden = !open;
  }

  function closeNav() {
    setOpen(false);
  }

  function openNav() {
    setOpen(true);
  }

  toggle.addEventListener('click', function () {
    const open = !header.classList.contains('is-nav-open');
    if (open) {
      openNav();
    } else {
      closeNav();
    }
  });

  backdrop.addEventListener('click', closeNav);

  nav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      if (isMobileNav()) {
        closeNav();
      }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && header.classList.contains('is-nav-open')) {
      closeNav();
      toggle.focus();
    }
  });

  mq.addEventListener('change', function () {
    if (!isMobileNav()) {
      closeNav();
    }
  });
})();
