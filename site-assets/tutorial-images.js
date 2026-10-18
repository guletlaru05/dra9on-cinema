/* Native modal focus trap; close without navigating away or losing scroll position. */
(() => {
 'use strict';
 const main=document.querySelector('main'),dialog=document.querySelector('[data-tutorial-image-viewer]');
 if(!main||!dialog||typeof dialog.showModal!=='function')return;
 const image=document.createElement('img'),caption=dialog.querySelector('[data-enlarged-caption]');
 image.setAttribute('data-enlarged-image','');dialog.querySelector('[data-enlarged-mount]').append(image);
 const original=dialog.querySelector('[data-image-original]'),error=dialog.querySelector('[data-image-error]');
 let opener=null,overflow='';
 function open(source,element){
  opener=element;error.hidden=true;
  image.alt=source.alt||'';image.src=source.closest('a')?.href||source.currentSrc||source.src;
  caption.textContent=image.alt;original.href=image.src;
  overflow=document.documentElement.style.overflow;
  dialog.showModal();document.documentElement.style.overflow='hidden';
 }
 for(const source of main.querySelectorAll('img')){
  const link=source.closest('a');
  if(link&&!/\.(?:webp|png|jpe?g|avif|gif)(?:[?#].*)?$/i.test(link.href))continue;
  const element=link||source;
  if(!link){source.tabIndex=0;source.setAttribute('role','button');}
  element.classList.add('tutorial-zoomable');element.setAttribute('aria-haspopup','dialog');
  element.addEventListener('click',event=>{if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button!==0)return;event.preventDefault();open(source,element);});
  if(!link)element.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open(source,element);}});
 }
 image.addEventListener('error',()=>{error.hidden=false;});
 dialog.querySelector('[data-image-close]').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
 dialog.addEventListener('close',()=>{
  document.documentElement.style.overflow=overflow;
  image.removeAttribute('src');opener?.focus({preventScroll:true});
 });
})();
