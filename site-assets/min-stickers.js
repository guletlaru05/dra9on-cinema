document.querySelectorAll('.min-stickers').forEach(section => {
  const dialog = section.querySelector('dialog');
  const artwork = dialog.querySelector('.min-sprite');
  const caption = dialog.querySelector('h3');
  let opener;
  section.querySelectorAll('[data-sticker]').forEach(button => {
    button.addEventListener('click', () => {
      opener = button;
      artwork.className = `min-sprite min-sprite-${button.dataset.sticker}`;
      caption.textContent = button.getAttribute('aria-label');
      dialog.showModal();
    });
  });
  dialog.querySelector('button').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => opener?.focus());
});
