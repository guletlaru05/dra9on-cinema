/* Read-only build-time YouTube counts. No browser identity or playback ledger. */
(() => {
 const en=document.documentElement.lang!=='ko',works=window.PORTFOLIO||[];
 const t=(ko,english)=>window.D9Locale?.translate(ko,english)??(en?english:ko);
 const value=id=>works.find(v=>v.id===id)?.apiViewCount;
 function paint(node,id){const raw=value(id);if(typeof raw!=='string'||!/^(?:0|[1-9][0-9]*)$/.test(raw)){node.hidden=true;return;}node.hidden=false;node.textContent=t('YouTube 조회수 ','YouTube views ')+raw;node.title=t('YouTube Data API 제공값 · 하루 1회 갱신','Exact YouTube Data API value · refreshed daily');}
 window.D9Engagement={
  observeCard(node,id){paint(node,id);},
  attach(id,frame,container){container.querySelector('.film-engagement')?.remove();if(!(container.closest('.watch-primary')||container).querySelector('.youtube-api-watch')){const row=document.createElement('div');row.className='film-engagement';paint(row,id);container.append(row);}window.D9ExternalConsent?.prepare(frame.parentElement);}
 };
 window.dispatchEvent(new Event('d9-engagement-ready'));
})();
