/* Last episode and completion flags stay in this browser. No network ledger. */
(()=>{
 'use strict';
 const episodes=works=>works.filter(v=>/^s[1-9][0-9]*$/.test(v.category)&&(!v.releaseAt||Date.now()>=Date.parse(v.releaseAt))).sort((a,b)=>a.season-b.season||a.episode-b.episode);
 function recommend(record,works){
  const list=episodes(works),last=list.find(v=>v.id===record?.lastId);if(!last)return null;
  const done=new Set(Array.isArray(record.completed)?record.completed:[]),season=list.filter(v=>v.season===last.season);
  const nextSeason=list.find(v=>v.season>last.season);
  if(season.every(v=>done.has(v.id)))return nextSeason?{work:nextSeason,nextSeason:true}:null;
  if(!done.has(last.id))return {work:last,nextSeason:false};
  const next=season.find(v=>v.episode>last.episode&&!done.has(v.id))||season.find(v=>!done.has(v.id));
  return next?{work:next,nextSeason:false}:null;
 }
 if(typeof module!=='undefined')module.exports={recommend};
 if(typeof document==='undefined')return;
 const KEY='d9-continue-v1',works=window.PORTFOLIO||[],list=episodes(works),byId=new Map(list.map(v=>[v.id,v]));
 const lang=document.documentElement.lang,labels={ko:{continue:'부터 이어보기',next:'다음 시즌 시작',clear:'이어보기 기록 지우기',done:'이 회차 다 봤어요',saved:'완료로 저장됨',note:'기록은 이 브라우저에만 저장됩니다.'},en:{continue:'Continue from',next:'Start the next season',clear:'Clear continue-watching history',done:'I finished this episode',saved:'Marked as watched',note:'History stays in this browser only.'},ja:{continue:'から続きを見る',next:'次のシーズンへ',clear:'視聴履歴を消去',done:'このエピソードを見終わった',saved:'視聴済みに保存しました',note:'履歴はこのブラウザ内にのみ保存されます。'},es:{continue:'Continuar desde',next:'Empezar la siguiente temporada',clear:'Borrar el historial',done:'Ya vi este episodio',saved:'Marcado como visto',note:'El historial se guarda solo en este navegador.'}};
 const text=labels[lang]||labels.en;let enabled=true,widget=null,markButton=null,activeId=null;
 function read(){try{const saved=JSON.parse(localStorage.getItem(KEY));if(saved?.version!==1||!byId.has(saved.lastId))return null;return {version:1,lastId:saved.lastId,completed:[...new Set(Array.isArray(saved.completed)?saved.completed:[])].filter(id=>byId.has(id)).slice(0,120)};}catch{enabled=false;return null;}}
 let record=read();
 function write(value){try{localStorage.setItem(KEY,JSON.stringify(value));record=value;return true;}catch{enabled=false;widget?.remove();markButton?.remove();return false;}}
 function open(id){if(!enabled||!byId.has(id))return;activeId=id;write({version:1,lastId:id,completed:record?.completed||[]});}
 function complete(id){if(!enabled||!byId.has(id))return;if(write({version:1,lastId:id,completed:[...new Set([...(record?.completed||[]),id])].slice(-120)})&&markButton){markButton.textContent=text.saved;markButton.disabled=true;}}
 function paintHome(){
  widget?.remove();if(!enabled||!record)return;const result=recommend(record,works);if(!result)return;
  const {work,nextSeason}=result;widget=document.createElement('section');widget.className='continue-watching';widget.setAttribute('aria-label',text.continue);
  const link=document.createElement('a');link.href=work.path;const ep='S'+work.season+' · EP.'+String(work.episode).padStart(2,'0');
  link.textContent=nextSeason?text.next+' · '+ep:(lang==='ko'||lang==='ja'?ep+text.continue:text.continue+' '+ep);
  const note=document.createElement('span');note.textContent=text.note;
  const clear=document.createElement('button');clear.type='button';clear.textContent='×';clear.setAttribute('aria-label',text.clear);
  clear.addEventListener('click',()=>{try{localStorage.removeItem(KEY);}catch{}record=null;widget.remove();});
  widget.append(link,note,clear);document.querySelector('main')?.prepend(widget);
 }
 if(document.body.dataset.page==='home')paintHome();
 if(document.body.dataset.page==='watch'&&byId.has(document.body.dataset.id)){
  open(document.body.dataset.id);
  if(enabled){markButton=document.createElement('button');markButton.type='button';markButton.className='text-button continue-mark';markButton.textContent=record?.completed.includes(activeId)?text.saved:text.done;markButton.disabled=record?.completed.includes(activeId);markButton.title=text.note;markButton.addEventListener('click',()=>complete(activeId));document.querySelector('.watch-actions')?.append(markButton);}
 }
 let apiPromise;const players=new WeakSet();
 function iframeApi(){
  if(window.YT?.Player)return Promise.resolve(window.YT);
  if(!apiPromise)apiPromise=new Promise(resolve=>{const previous=window.onYouTubeIframeAPIReady;window.onYouTubeIframeAPIReady=()=>{if(typeof previous==='function')previous();resolve(window.YT);};const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';script.onerror=()=>{apiPromise=null;};document.head.append(script);});
  return apiPromise;
 }
 function preparePlayers(){
  if(!enabled||!window.D9ExternalConsent?.canLoadMedia())return;
  document.querySelectorAll('iframe[data-external-src]').forEach(frame=>{
   if(players.has(frame)||!frame.getAttribute('src'))return;
   let url;try{url=new URL(frame.src);}catch{return;}
   if(url.hostname!=='www.youtube-nocookie.com')return;const id=url.pathname.split('/').pop();if(!byId.has(id))return;
   players.add(frame);open(id);if(!frame.id)frame.id='continue-player-'+id;
   iframeApi().then(YT=>{if(frame.isConnected&&window.D9ExternalConsent?.canLoadMedia())new YT.Player(frame.id,{events:{onStateChange:event=>{if(event.data===YT.PlayerState.ENDED)complete(id);}}});});
  });
 }
 window.addEventListener('d9:external-consent',preparePlayers);
 new MutationObserver(preparePlayers).observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['src']});
 window.addEventListener('storage',event=>{if(event.key===KEY){record=read();if(document.body.dataset.page==='home')paintHome();}});
 preparePlayers();
})();
