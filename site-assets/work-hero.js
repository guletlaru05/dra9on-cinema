/* One active muted clip, one late prefetch, and a poster-only constrained path. */
(() => {
 'use strict';
 function createWorkHero(root,env=window){
  const doc=env.document,config=JSON.parse(root.querySelector('[data-work-hero-config]').textContent);
  const slides=config.slides,media=root.querySelector('.hero-media'),poster=root.querySelector('.hero-image'),mobilePoster=root.querySelector('.hero-mobile-poster');
  const heading=root.querySelector('#hero-title'),label=root.querySelector('.d9-work-label'),description=root.querySelector('.d9-work-description');
  const view=root.querySelector('.hero-feature-link'),panel=root.querySelector('[role=tabpanel]');
  const tabs=[...root.querySelectorAll('[data-work-index]')],lines=tabs.map(t=>t.querySelector('i')),pause=root.querySelector('.d9-work-pause');
  const motion=env.matchMedia('(prefers-reduced-motion: reduce)'),mobile=env.matchMedia('(max-width:700px)'),large=env.matchMedia('(min-width:1600px)'),connection=env.navigator.connection;
  const constrained=()=>motion.matches||Boolean(connection?.saveData)||/^(slow-2g|2g|3g)$/.test(connection?.effectiveType||'')||(connection?.downlink>0&&connection.downlink<1.5);
  let index=0,ready=false,visible=!env.IntersectionObserver,paused=false,dialogOpen=false,active,spare;
  let frame=0,lastTick=null,elapsed=0,prepared=-1,starting=false,generation=0;
  const failed=new Set(),prefetchFailed=new Set();
  let lastFocus='';
  function focusAt(s,time=0){
   let focus=mobile.matches?s.focus?.mobile:s.focus?.desktop;
   for(const point of s.focusTrack||[]){if(time<point.at)break;focus=(mobile.matches?point.mobile:point.desktop)||focus;}
   focus=focus||'50% 30%';if(focus!==lastFocus){root.style.setProperty('--d9-hero-focus',focus);lastFocus=focus;}
  }
  function composition(s){
   focusAt(s);root.style.setProperty('--d9-hero-fit','cover');
   if(mobilePoster)mobilePoster.srcset=s.mobilePoster||s.poster;
   poster.src=mobile.matches&&s.mobilePoster&&!mobilePoster?s.mobilePoster:s.poster;
   poster.width=mobile.matches&&s.mobileWidth?s.mobileWidth:(s.width||960);
   poster.height=mobile.matches&&s.mobileHeight?s.mobileHeight:(s.height||540);
  }
  function createVideo(){
   const v=doc.createElement('video');v.muted=true;v.defaultMuted=true;v.playsInline=true;v.preload='none';v.disablePictureInPicture=true;
   v.setAttribute('muted','');v.setAttribute('playsinline','');v.setAttribute('aria-hidden','true');v.setAttribute('tabindex','-1');
   media.insertBefore(v,media.querySelector('.hero-shade'));return v;
  }
  active=createVideo();spare=createVideo();
  const canRun=()=>ready&&visible&&!paused&&!doc.hidden&&!root.hidden&&!dialogOpen;
  const posterOnly=()=>constrained()||failed.has(index);
  function release(v){v.pause();v.classList.remove('is-playing');if(v.getAttribute('src')){v.removeAttribute('src');v.load();}delete v.dataset.workIndex;}
  function clearSpare(){release(spare);prepared=-1;}
  function source(s,v){return mobile.matches?s.mobile:(v.canPlayType('video/webm')?(large.matches&&s.hdWebm?s.hdWebm:s.webm):(large.matches&&s.hdMp4?s.hdMp4:s.mp4));}
  function load(v,i){v.dataset.workIndex=String(i);v.preload='auto';v.src=source(slides[i],v);v.load();}
  function paintProgress(value){lines[index].style.transform='scaleX('+Math.min(1,Math.max(0,value))+')';}
  function updatePause(){pause.textContent=paused?'▶':'Ⅱ';pause.setAttribute('aria-label',paused?config.resume:config.pause);pause.setAttribute('aria-pressed',String(paused));}
  function schedule(){if(!frame&&canRun())frame=env.requestAnimationFrame(tick);}
  function fallBack(){failed.add(index);starting=false;release(active);clearSpare();elapsed=0;lastTick=null;schedule();}
  function startVideo(){
   if(!canRun()||posterOnly()||starting)return;
   if(active.dataset.workIndex!==String(index))load(active,index);
   if(!active.paused)return;
   const turn=generation;starting=true;
   Promise.resolve(active.play()).catch(error=>{if(turn===generation&&error?.name!=='AbortError')fallBack();}).finally(()=>{
    if(turn===generation){starting=false;if(canRun()&&active.paused&&!posterOnly())startVideo();}
   });
  }
  function sync(){
   if(constrained()){release(active);clearSpare();starting=false;}
   if(!canRun()){
    active.pause();if(frame)env.cancelAnimationFrame(frame);frame=0;lastTick=null;return;
   }
   if(!posterOnly())startVideo();schedule();
  }
  function select(next,focus=false){
   generation++;starting=false;index=(next+slides.length)%slides.length;elapsed=0;lastTick=null;
   // Reuse only the requested next clip. Manual jumps cancel unrelated prefetches.
   release(active);
   if(prepared===index){[active,spare]=[spare,active];prepared=-1;}else clearSpare();
   const s=slides[index];poster.src=s.poster;poster.alt=s.tab;composition(s);
   heading.textContent=s.title;label.textContent=s.label;description.textContent=s.description;view.href=s.url;if(s.viewLabel)view.textContent=s.viewLabel+' ↗';
   panel.setAttribute('aria-labelledby','work-tab-'+index);root.dataset.activeWork=s.id;
   tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));tab.setAttribute('tabindex',i===index?'0':'-1');lines[i].style.transform='scaleX(0)';});
   const strip=root.querySelector('.d9-work-tabs');
   if(mobile.matches&&strip?.scrollTo)strip.scrollTo({left:Math.max(0,tabs[index].offsetLeft-(strip.clientWidth-tabs[index].offsetWidth)/2),behavior:'auto'});
   if(focus){tabs[index].focus();tabs[index].scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'});}
   sync();
  }
  function tick(now){
   frame=0;if(!canRun()){lastTick=null;return;}
   if(posterOnly()){
    if(lastTick!==null)elapsed+=Math.min(now-lastTick,250);lastTick=now;
    paintProgress(elapsed/(slides[index].duration*1000));
    if(elapsed>=slides[index].duration*1000){select(index+1);return;}
   }else{
    focusAt(slides[index],active.currentTime);
    const duration=Number.isFinite(active.duration)?Math.min(active.duration,slides[index].duration):slides[index].duration;
    paintProgress(active.currentTime/duration);
    if(active.currentTime>=duration-1&&prepared<0&&!prefetchFailed.has((index+1)%slides.length)){prepared=(index+1)%slides.length;load(spare,prepared);}
    if(active.ended||active.currentTime>=duration-.03){select(index+1);return;}
   }
   schedule();
  }
  for(const v of [active,spare]){
   v.addEventListener('playing',()=>{if(v===active&&canRun()&&!posterOnly())v.classList.add('is-playing');else v.pause();});
   v.addEventListener('ended',()=>{if(v===active&&canRun()&&!posterOnly())select(index+1);});
   v.addEventListener('error',()=>{if(v===active&&v.getAttribute('src'))fallBack();else if(v===spare){prefetchFailed.add(prepared);clearSpare();}});
  }
  tabs.forEach((tab,i)=>{
   tab.addEventListener('click',()=>select(i));
   tab.addEventListener('keydown',event=>{
    let next;if(event.key==='ArrowRight')next=index+1;else if(event.key==='ArrowLeft')next=index-1;else if(event.key==='Home')next=0;else if(event.key==='End')next=slides.length-1;else return;
    event.preventDefault();select(next,true);
   });
  });
  pause.addEventListener('click',()=>{paused=!paused;if(!paused)failed.delete(index);updatePause();sync();});
  doc.addEventListener('visibilitychange',sync);
  if(env.IntersectionObserver)new env.IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();},{threshold:.1}).observe(root);
  if(env.MutationObserver)new env.MutationObserver(()=>{dialogOpen=Boolean(doc.querySelector('dialog[open]'));sync();}).observe(doc.body,{subtree:true,attributes:true,attributeFilter:['hidden','open']});
  motion.addEventListener?.('change',()=>{generation++;starting=false;lastTick=null;sync();});
  mobile.addEventListener?.('change',()=>{generation++;release(active);clearSpare();starting=false;composition(slides[index]);sync();});
  large.addEventListener?.('change',()=>{generation++;release(active);clearSpare();starting=false;sync();});
  connection?.addEventListener?.('change',()=>{generation++;starting=false;lastTick=null;sync();});
  const afterLoad=()=>env.requestAnimationFrame(()=>env.requestAnimationFrame(()=>{ready=true;sync();}));
  if(doc.readyState==='complete')afterLoad();else env.addEventListener('load',afterLoad,{once:true});
  updatePause();composition(slides[0]);root.dataset.activeWork=slides[0].id;
  return {select,sync};
 }
 if(typeof module!=='undefined'&&module.exports)module.exports={createWorkHero};
 if(typeof document!=='undefined'){const root=document.querySelector('[data-work-hero]');if(root)createWorkHero(root);}
})();
