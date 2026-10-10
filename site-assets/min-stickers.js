document.querySelectorAll('.min-stickers').forEach(section => {
  const prepareArtwork=()=>section.classList.add('sticker-art-ready');
  if('IntersectionObserver' in window){
    const artObserver=new IntersectionObserver(entries=>{
      if(entries.some(entry=>entry.isIntersecting)){prepareArtwork();artObserver.disconnect();}
    },{rootMargin:'200px'});
    artObserver.observe(section);
  }else prepareArtwork();
  section.addEventListener('focusin',prepareArtwork);

  const dialog = section.querySelector('.sticker-dialog');
  const gallery = section.querySelector('.sticker-gallery');
  const showAll = section.querySelector('.sticker-show-all');
  if (gallery && showAll) {
    showAll.addEventListener('click', () => {prepareArtwork();gallery.showModal();});
    gallery.querySelector('.gallery-close').addEventListener('click', () => gallery.close());
    gallery.addEventListener('close', () => showAll.focus());
    gallery.addEventListener('click', event => {
      const box = gallery.getBoundingClientRect();
      if (event.target === gallery && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) gallery.close();
    });
  }
  const artwork = dialog.querySelector('.min-sprite');
  const caption = dialog.querySelector('h3');
  let opener;
  section.querySelectorAll('[data-sticker]').forEach(button => {
    button.addEventListener('click', () => {
      prepareArtwork();opener = button;
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
