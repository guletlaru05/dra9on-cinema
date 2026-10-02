(() => {
  const catalog=window.PORTFOLIO||[];
  const released=(v,now=Date.now())=>!v?.releaseAt||now>=Date.parse(v.releaseAt);
  const en=document.documentElement.lang==='en';
  const label=en?'Oct 2 · 18:10 KST':'10월 2일 · 18:10 공개';
  window.D9Release={released,label};
  const pending=new Set(catalog.filter(v=>!released(v)).map(v=>v.id));
  function paint(){
    for(const v of catalog.filter(v=>v.releaseAt)){
      const open=released(v);
      document.querySelectorAll('.next-episode').forEach(a=>{if(new URL(a.href).pathname===v.path)a.hidden=!open;});
      if(document.body.dataset.id===v.id){
        const frame=document.querySelector('[data-release-src]');
        const notice=document.querySelector('.release-notice');
        if(notice)notice.hidden=open;
        if(frame&&open){frame.src=frame.dataset.releaseSrc;frame.hidden=false;delete frame.dataset.releaseSrc;}
        document.querySelectorAll('.watch-actions a[href*="watch?v="],.playback-hint').forEach(a=>a.hidden=!open);
      }
      const badge=document.querySelector('.upcoming-episode');
      if(badge){badge.hidden=open;if(!open){badge.querySelector('span:last-child').textContent=label;}}
      const bio=document.querySelector('.bio-feature');
      if(bio&&new URL(bio.href).pathname===v.path){bio.querySelector('.bio-label').textContent=open?'LATEST EPISODE · S2 EP.06':label;bio.querySelector('strong').textContent=open?(en?'Watch latest episode':'최신화 보기'):(en?'Episode 6 · Coming soon':'6화 · 공개 예정');}
    }
  }
  function check(){
    paint();
    for(const id of [...pending])if(released(catalog.find(v=>v.id===id))){pending.delete(id);document.dispatchEvent(new CustomEvent('d9:released',{detail:{id}}));}
    if(!pending.size)clearInterval(timer);
  }
  paint();
  let timer=setInterval(check,1000);
  document.addEventListener('visibilitychange',check);
})();
