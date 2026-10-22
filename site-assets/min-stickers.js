document.querySelectorAll('.min-stickers').forEach(section => {
  const cards = [...section.querySelectorAll('[data-sticker]')];
  const grid = section.querySelector('.sticker-grid');
  const expand = section.querySelector('.sticker-expand');
  const dialog = section.querySelector('.sticker-dialog');
  if (!cards.length || !grid || !expand || !dialog) return;
  const artwork = dialog.querySelector('.sticker-large');
  const caption = dialog.querySelector('h3');
  const position = dialog.querySelector('.sticker-position');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const coarse = matchMedia('(hover: none), (pointer: coarse)');
  const phone = matchMedia('(max-width: 600px)');
  const tablet = matchMedia('(max-width: 1000px)');
  let expanded = false, selected = 0, opener = null;
  const seen = new WeakSet(), timers = new WeakMap();
  function animate(card) {
    if (reduced.matches) return;
    clearTimeout(timers.get(card));
    // Alternating animation names restarts taps without a forced layout read.
    card.classList.toggle('sticker-replay');
    card.classList.add('sticker-moving');
    timers.set(card, setTimeout(() => card.classList.remove('sticker-moving'), 600));
  }
  const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
    entries.forEach(({target, isIntersecting}) => {
      if (isIntersecting && coarse.matches && !reduced.matches && !seen.has(target)) {
        seen.add(target); animate(target); observer.unobserve(target);
      }
    });
  }, {threshold: 0.35}) : null;
  function updateRows() {
    const limit = (phone.matches ? 3 : tablet.matches ? 4 : 6) * 2;
    if (!expanded && cards.slice(limit).includes(document.activeElement)) expand.focus();
    cards.forEach((card, i) => { card.hidden = !expanded && i >= limit; });
    expand.hidden = cards.length <= limit;
    expand.setAttribute('aria-expanded', String(expanded));
    expand.querySelector('.sticker-more').hidden = expanded;
    expand.querySelector('.sticker-less').hidden = !expanded;
    expand.querySelector('[aria-hidden]').textContent = expanded ? ' −' : ' ＋';
  }
  expand.addEventListener('click', () => { expanded = !expanded; updateRows(); });
  phone.addEventListener('change', updateRows);
  tablet.addEventListener('change', updateRows);
  updateRows();
  function show(index) {
    selected = (index + cards.length) % cards.length;
    const card = cards[selected];
    artwork.src = card.dataset.full;
    artwork.alt = card.getAttribute('aria-label');
    caption.textContent = artwork.alt;
    position.textContent = `${selected + 1} / ${cards.length}`;
  }
  cards.forEach((card, index) => {
    observer?.observe(card);
    card.addEventListener('pointerenter', event => {
      if (event.pointerType === 'mouse' && !coarse.matches) animate(card);
    });
    card.addEventListener('click', () => {
      animate(card); opener = card; show(index); dialog.showModal();
      dialog.dataset.motion = card.dataset.motion; animate(dialog);
    });
  });
  dialog.querySelector('.sticker-prev').addEventListener('click', () => show(selected - 1));
  dialog.querySelector('.sticker-next').addEventListener('click', () => show(selected + 1));
  dialog.querySelector('.sticker-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); show(selected + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
  let touch = null;
  const stage = dialog.querySelector('.sticker-stage');
  stage.addEventListener('touchstart', event => {
    const point = event.touches[0]; touch = {x: point.clientX, y: point.clientY};
  }, {passive: true});
  stage.addEventListener('touchend', event => {
    if (!touch) return;
    const point = event.changedTouches[0];
    const dx = point.clientX - touch.x, dy = point.clientY - touch.y;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5) show(selected + (dx < 0 ? 1 : -1));
    touch = null;
  }, {passive: true});
  dialog.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => opener?.focus());
  reduced.addEventListener('change', () => {
    if (reduced.matches) section.querySelectorAll('.sticker-moving').forEach(item => item.classList.remove('sticker-moving'));
  });
  section.addEventListener('dragstart', event => { if (event.target.tagName === 'IMG') event.preventDefault(); });
  section.addEventListener('contextmenu', event => { if (event.target.tagName === 'IMG') event.preventDefault(); });
});
