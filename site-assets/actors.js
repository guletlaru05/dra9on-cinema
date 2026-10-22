/* No analytics, cookies, storage, network requests or automatic email sending. */
(() => {
  'use strict';
  const opening = document.querySelector('[data-actors-motion]');
  if (opening) {
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    let visible = true, frame = 0, finished = false, timer;
    function settle() {
      clearTimeout(timer);
      finished = true;
      opening.classList.remove('is-preparing', 'is-entering');
      opening.classList.add('is-settled');
    }
    function updateParallax() {
      frame = 0;
      if (reduced.matches || !visible || !finished) return;
      const top = opening.getBoundingClientRect().top;
      const distance = Math.max(0, -top);
      // Move the complete photo frame: never crop faces or baked-in watermarks.
      opening.style.setProperty('--actor-drift', Math.min(10, distance * .025) + 'px');
      opening.style.setProperty('--actor-backdrop-drift', Math.min(24, distance * .06) + 'px');
    }
    function requestParallax() {
      if (!frame && visible && !reduced.matches && finished) frame = requestAnimationFrame(updateParallax);
    }
    reduced.addEventListener('change', () => {
      if (reduced.matches) {
        settle();
        cancelAnimationFrame(frame); frame = 0;
        opening.style.setProperty('--actor-drift', '0px');
        opening.style.setProperty('--actor-backdrop-drift', '0px');
      } else requestParallax(); // Never replay the entrance after a preference change.
    });
    if (reduced.matches) settle();
    else {
      opening.classList.add('is-preparing');
      const pictures = [...opening.querySelectorAll('.actor-card-photo img')];
      const ready = Promise.allSettled(pictures.map(img => img.decode ? img.decode() : Promise.resolve()));
      // Bounded image readiness; failed/slow images can never leave content hidden.
      Promise.race([ready, new Promise(resolve => setTimeout(resolve, 1000))]).then(() => {
        if (finished || reduced.matches) return;
        requestAnimationFrame(() => {
          if (finished || reduced.matches) return;
          opening.classList.remove('is-preparing');
          opening.classList.add('is-entering');
          timer = setTimeout(settle, 1150);
        });
      });
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        if (visible) requestParallax();
      }).observe(opening);
    }
    window.addEventListener('scroll', requestParallax, {passive:true});
    window.addEventListener('resize', requestParallax, {passive:true});
    window.addEventListener('pageshow', event => { if (event.persisted) settle(); });
    opening.addEventListener('focusin', settle);
  }
  document.querySelectorAll('[data-actor-image]').forEach(image => {
    image.addEventListener('contextmenu', event => event.preventDefault());
    image.addEventListener('dragstart', event => event.preventDefault());
  });
  const dialog = document.getElementById('actor-photo-dialog');
  if (dialog && typeof dialog.showModal === 'function') {
    document.querySelectorAll('[data-actor-photo]').forEach(button => button.addEventListener('click', () => {
      const image = dialog.querySelector('img');
      image.src = button.dataset.actorPhoto;
      image.alt = button.querySelector('img').alt;
      const caption = dialog.querySelector('[data-actor-dialog-caption]');
      if (caption) {
        caption.textContent = button.closest('.actor-behind-photo')?.querySelector('figcaption small')?.textContent || '';
        caption.hidden = !caption.textContent;
        dialog.classList.toggle('has-caption', Boolean(caption.textContent));
      }
      dialog.showModal();
    }));
    dialog.querySelector('[data-actor-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  }
  document.querySelectorAll('[data-actor-enquiry]').forEach(form => {
    const fields = form.elements;
    const query = new URLSearchParams(location.search);
    if (query.get('inquiry') === 'ai-actor') fields.inquiry.value = 'ai-actor';
    const wanted = query.get('actor');
    if (wanted && Array.from(fields.actor.options).some(option => option.value === wanted)) fields.actor.value = wanted;
    const labels = JSON.parse(form.dataset.labels);
    const compose = form.querySelector('[data-actor-compose]');
    function update() {
      const type = fields.inquiry.value === 'ai-actor' ? labels.type_actor : labels.type_general;
      const actor = fields.actor.selectedOptions[0].textContent;
      const subject = '[' + type + '] DRA9ON CINEMA' + (fields.actor.value ? ' / ' + actor : '');
      const body = [labels.type + ': ' + type, labels.actor + ': ' + actor, labels.project + ': ' + fields.project.value, '', labels.message + ':', fields.message.value].join('\n');
      compose.href = 'mailto:' + form.dataset.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    }
    form.addEventListener('input', update);
    form.addEventListener('change', update);
    form.addEventListener('submit', event => event.preventDefault());
    update();
  });
})();
