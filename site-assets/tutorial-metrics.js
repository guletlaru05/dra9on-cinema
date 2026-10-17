/* Numeric aggregates only. No analytics cookies, browser IDs or persistent storage. */
(() => {
 'use strict';
 const meta=name=>document.querySelector('meta[name="'+name+'"]')?.content||'';
 const endpoint=meta('d9-metrics-endpoint'),path=meta('d9-metrics-path'),canonical=meta('d9-metrics-canonical');
 const en=document.documentElement.lang==='en',t=(ko,english)=>window.D9Locale?.translate(ko,english)??(en?english:ko);
 const isTutorial=meta('d9-tutorial')==='true';
 const production=['dra9oncinema.com','www.dra9oncinema.com'].includes(location.hostname);
 const noTracking=navigator.globalPrivacyControl===true||navigator.doNotTrack==='1';
 const enabled=!!endpoint&&production&&!noTracking;
 let summary=null,activeSort='latest';
 let referrer='direct',entry=true;
 try{const u=new URL(document.referrer);entry=u.origin!==location.origin;if(!entry)referrer='direct';else{const host=u.hostname.replace(/^www\./,'');const names={'google.com':'google','google.co.kr':'google','naver.com':'naver','youtube.com':'youtube','youtu.be':'youtube','instagram.com':'instagram','l.instagram.com':'instagram','x.com':'x','t.co':'x'};referrer=names[host]||'other';}}catch{}
 const send=(kind,card)=>{
  if(!enabled)return;
  const body={kind,path,entry:kind==='pageview'&&entry,referrer};
  if(card)body.card=card;
  fetch(endpoint+'/event',{method:'POST',mode:'cors',credentials:'omit',referrerPolicy:'no-referrer',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),keepalive:true}).catch(()=>{});
 };
 const canonicalLink=node=>{try{let p=new URL(node.href,location.href).pathname;const match=p.match(/\/(?:en\/)?tutorials\/([^/]+)\/$/);return match?'/tutorials/'+match[1]+'/':null;}catch{return null;}};
 const dataFor=node=>summary?.tutorials?.[canonicalLink(node)]||null;
 const totalLabel=value=>t('조회 ','Views ')+String(value.views)+t(' · 프롬프트 복사 ',' · Prompt copies ')+String(value.copies);
 const homeTemplate=document.querySelector('[data-home-tutorial-candidates]');
 const cards=[...(homeTemplate?homeTemplate.content.querySelectorAll('.tutorial-preview'):document.querySelectorAll('.tutorial-lesson-list .tutorial-preview'))];
 const initialOrder=new Map(cards.map((node,i)=>[node,i]));
 const count=n=>Number.isSafeInteger(n)&&n>=0;
 function validSummary(value){
  if(!value||!value.tutorials||typeof value.tutorials!=='object'||Array.isArray(value.tutorials))return false;
  return Object.entries(value.tutorials).every(([key,total])=>/^\/tutorials\/[A-Za-z0-9_-]+\/$/.test(key)&&total&&count(total.views)&&count(total.copies));
 }
 function sortList(){const list=document.querySelector('[data-tutorial-list]');if(!list)return;[...cards].sort((a,b)=>activeSort==='popular'?((dataFor(b)?.views||0)-(dataFor(a)?.views||0)||initialOrder.get(a)-initialOrder.get(b)):initialOrder.get(a)-initialOrder.get(b)).forEach(n=>list.append(n));}
 function paint(){
  const sortStatus=document.querySelector('[data-tutorial-sort-status]');if(sortStatus)sortStatus.textContent='';
  for(const node of cards){const value=dataFor(node);if(!value)continue;let badge=node.querySelector('.tutorial-metric');if(!badge){badge=document.createElement('span');badge.className='tutorial-metric';(node.querySelector('div')||node).append(badge);}badge.textContent=totalLabel(value);}
  sortList();
  if(homeTemplate){const homeList=document.querySelector('#tutorials .tutorial-lesson-list');const ranked=[...cards].sort((a,b)=>(dataFor(b)?.views||0)-(dataFor(a)?.views||0)||initialOrder.get(a)-initialOrder.get(b));homeList.replaceChildren(...ranked.slice(0,3).map(n=>n.cloneNode(true)));}
  const popular=document.querySelector('[data-popular-tutorials]'),list=popular?.querySelector('[data-popular-list]');
  if(popular&&list){const top=cards.filter(n=>(dataFor(n)?.views||0)>0).sort((a,b)=>(dataFor(b)?.views||0)-(dataFor(a)?.views||0)||initialOrder.get(a)-initialOrder.get(b)).slice(0,3);if(top.length){for(const node of top)list.append(node.cloneNode(true));popular.hidden=false;popular.querySelector('[data-popular-status]').textContent=t('실제 조회 합계 기준 · 집계 후 자동 갱신','Actual view totals · Updated automatically');}}
 }
 document.querySelectorAll('[data-tutorial-sort]').forEach(button=>button.addEventListener('click',()=>{
  const popular=button.dataset.tutorialSort==='popular',list=document.querySelector('[data-tutorial-list]');if(!list)return;activeSort=popular?'popular':'latest';
  document.querySelectorAll('[data-tutorial-sort]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  sortList();
  const status=document.querySelector('[data-tutorial-sort-status]');if(status)status.textContent=popular&&!summary?t('집계 연결 후 실제 조회수로 정렬됩니다.','Actual-view sorting is available after analytics is connected.'):'';
 }));
 if(isTutorial){
  [...document.querySelectorAll('main pre')].forEach((pre,index)=>{
   const button=document.createElement('button'),status=document.createElement('span');button.type='button';button.className='prompt-copy';button.textContent=t('프롬프트 복사','Copy prompt');button.dataset.promptCard='prompt-'+(index+1);status.className='prompt-copy-status';status.setAttribute('role','status');pre.after(button,status);
   button.addEventListener('click',async()=>{try{await navigator.clipboard.writeText((pre.querySelector('code')||pre).textContent);status.textContent=t('복사했어요.','Copied.');send('copy',button.dataset.promptCard);}catch{status.textContent=t('복사하지 못했어요. 텍스트를 선택해 복사해 주세요.','Copy failed. Select the text and copy it.');}});
  });
 }
 if(enabled)send('pageview');
 if(endpoint&&production){fetch(endpoint+'/summary',{credentials:'omit',referrerPolicy:'no-referrer'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(value=>{if(!validSummary(value))throw Error();summary=value;paint();}).catch(()=>{document.querySelectorAll('[data-visits-status]').forEach(n=>n.textContent=t('집계를 잠시 불러올 수 없습니다.','Counts are temporarily unavailable.'));});}
 else document.querySelectorAll('[data-visits-status]').forEach(n=>n.textContent=t('통계 서비스 연결 대기 중입니다.','Analytics connection is pending.'));
})();
