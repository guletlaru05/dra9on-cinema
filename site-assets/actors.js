/* No analytics, cookies, storage, network requests or automatic email sending. */
(() => {
  'use strict';
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
