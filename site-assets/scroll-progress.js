/* The CSS path has no scroll listener. The fallback writes only scaleX in rAF. */
(() => {
 'use strict';
 const bar=document.getElementById('d9-scroll-progress');if(!bar)return;
 const fill=bar.firstElementChild,root=document.scrollingElement||document.documentElement;
 const native=Boolean(window.CSS?.supports('animation-timeline: scroll(root block)'));
 bar.dataset.driver=native?'css':'js';
 let range=0,queued=false,measure=true;
 function update(){
  queued=false;
  if(measure){range=Math.max(0,root.scrollHeight-root.clientHeight);bar.hidden=range<=1;measure=false;}
  if(!native)fill.style.transform='scaleX('+Math.min(1,Math.max(0,range?root.scrollTop/range:0))+')';
 }
 function schedule(resize=false){measure=measure||resize;if(!queued){queued=true;requestAnimationFrame(update);}}
 if(!native)addEventListener('scroll',()=>schedule(),{passive:true});
 addEventListener('resize',()=>schedule(true),{passive:true});
 addEventListener('pageshow',()=>schedule(true));
 document.addEventListener('load',()=>schedule(true),true);
 if(window.ResizeObserver){const observer=new ResizeObserver(()=>schedule(true));observer.observe(document.documentElement);if(document.body)observer.observe(document.body);}
 else if(window.MutationObserver)new MutationObserver(()=>schedule(true)).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden','open']});
 document.fonts?.ready.then(()=>schedule(true));
 schedule(true);
})();
