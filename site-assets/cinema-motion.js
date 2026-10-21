/* Progressive enhancement: content is visible if JS, motion or IO is unavailable. */
(() => {
  'use strict';
  const main = document.querySelector('main');
  if (!main) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const seen = new WeakSet();
  const pending = new Set();
  const cards = '.card,.actor-card,.note-tile,.tutorial-preview,.tutorial-scene,.notes-teaser';
  const privatePage = /\/library(?:\/|$)/.test(location.pathname);
  let observer;

  function show(node) {
    node.classList.remove('cinema-reveal-pending');
    pending.delete(node);
    observer?.unobserve(node);
  }

  function prepare(root = main) {
    // Decorative underlines use the element's background, never an input overlay.
    root.querySelectorAll('a,button,summary').forEach(link => {
      if (!link.textContent.trim() || link.querySelector('img,iframe,input,video') ||
          link.matches('.wordmark,.links-wordmark,.card-open,.actor-card-link,.icon-button,.card-save,.site-menu-toggle,[data-hero-prev],[data-hero-next],[data-hero-pause],[data-scroll],.external-media-play') ||
          link.closest('dialog,.functional-service-gate')) return;
      link.classList.add('cinema-link');
    });
    if (privatePage || motion.matches || !observer) return;
    const candidates = new Set();
    root.querySelectorAll(`section,article,${cards}`).forEach(node => {
      if (node.closest('#hero,dialog,form,.functional-service-gate,[role="status"]') ||
          node.matches('.continue-watching,[hidden]')) return;
      // Reveal a section heading and its cards independently, so translations
      // never stack to more than 18px on a single visible item.
      if (node.tagName === 'SECTION' && node.querySelector(`section,article,${cards}`)) {
        const heading = node.querySelector(':scope > .shelf-heading,:scope > h2,:scope > header');
        if (heading) candidates.add(heading);
      } else candidates.add(node);
    });
    candidates.forEach(node => {
      if (seen.has(node)) return;
      for (let parent = node.parentElement; parent && parent !== root; parent = parent.parentElement) {
        if (candidates.has(parent)) return;
      }
      seen.add(node);
      node.classList.add('cinema-reveal');
      // Keep first-screen content and currently focused controls visible.
      if (node.contains(document.activeElement) || node.getBoundingClientRect().top < innerHeight - 24) return;
      pending.add(node);
      node.classList.add('cinema-reveal-pending');
      observer.observe(node);
    });
  }

  function setup() {
    observer?.disconnect();
    pending.forEach(node => node.classList.remove('cinema-reveal-pending'));
    pending.clear();
    if (!motion.matches && 'IntersectionObserver' in window) {
      observer = new IntersectionObserver(entries => {
        entries.forEach(entry => { if (entry.isIntersecting) show(entry.target); });
      }, { threshold: 0, rootMargin: '0px 0px -24px 0px' });
    } else observer = null;
    prepare();
    prepare(document.querySelector('header') || main);
    prepare(document.querySelector('footer') || main);
  }

  document.addEventListener('focusin', event => {
    const node = event.target.closest('.cinema-reveal-pending');
    if (node) show(node);
  });
  window.addEventListener('pageshow', event => { if (event.persisted) pending.forEach(show); });
  motion.addEventListener('change', setup);
  window.D9CinemaMotion = Object.freeze({prepare});
  setup();
  // One animation per document; changing a shelf or hero slide never restarts it.
  if (!motion.matches) document.querySelector('body[data-page="home"] #hero-title')?.classList.add('cinema-title-enter');
})();
