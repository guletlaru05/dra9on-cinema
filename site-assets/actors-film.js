/* One muted photographic motion graphic; localized typography stays in HTML. */
(() => {
 'use strict';
 const root=document.querySelector('[data-actors-film]');if(!root)return;
 const video=root.querySelector('video'),button=root.querySelector('button');
 const type=root.querySelector('.actors-film-type'),name=root.querySelector('[data-film-name]');
 const scenes=JSON.parse(root.dataset.scenes),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const connection=navigator.connection;
 let visible=false,loaded=false,ready=document.readyState==='complete',userPaused=false,index=-1;
 const restricted=()=>reduced.matches||connection?.saveData||['slow-2g','2g'].includes(connection?.effectiveType);
 function label(){button.textContent=video.paused?'▶':'Ⅱ';button.setAttribute('aria-label',video.paused?button.dataset.play:button.dataset.pause);}
 function sync(){
  const next=Math.min(3,Math.floor(video.currentTime/5));
  if(next!==index){
   index=next;name.textContent=scenes[next];
   if(!reduced.matches){
    type.getAnimations({subtree:true}).forEach(animation=>animation.cancel());
    [name,type.querySelector('small')].forEach((node,i)=>node.animate([{transform:'translateY(12px)',opacity:0},{transform:'translateY(0)',opacity:1}],{duration:400,delay:i*80,easing:'ease-out',fill:'both'}));
   }
  }
  root.style.setProperty('--film-progress',String(video.currentTime/20));
 }
 function load(){
  if(loaded)return;loaded=true;
  video.src=matchMedia('(max-width:700px)').matches?video.dataset.mobile:video.dataset.desktop;
  video.load();
 }
 function play(manual=false){
  if(!manual&&(!ready||!visible||document.hidden||userPaused||restricted()))return;
  load();video.play().catch(()=>label());
 }
 button.hidden=false;
 button.addEventListener('click',()=>{if(video.paused){userPaused=false;play(true);}else{userPaused=true;video.pause();}});
 video.addEventListener('playing',()=>{root.classList.add('has-frame');sync();label();});
 video.addEventListener('pause',label);video.addEventListener('timeupdate',sync);
 video.addEventListener('error',()=>{root.classList.remove('has-frame');label();});
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(!visible)video.pause();else play();},{threshold:.15}).observe(root);
 window.addEventListener('load',()=>{ready=true;play();},{once:true});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();else play();});
 function preference(){if(restricted()){video.pause();root.classList.remove('has-frame');type.getAnimations({subtree:true}).forEach(animation=>animation.cancel());}else play();}
 reduced.addEventListener('change',preference);connection?.addEventListener('change',preference);
 label();
})();
