/* Functional external-media choices only. No analytics tags or visitor identity. */
(() => {
 'use strict';
 const KEY='d9-external-media-choice-v1',TTL=180*86400000;
 const mediaText={
  ko:{play:'동의하고 재생',notice:'재생하면 {service} 쿠키가 사용될 수 있습니다',privacy:'개인정보처리방침',revoked:'외부 영상 동의를 철회했습니다.'},
  en:{play:'Agree and play',notice:'Playing may use {service} cookies',privacy:'Privacy policy',revoked:'External-media consent withdrawn.'},
  ja:{play:'同意して再生',notice:'再生すると{service}のCookieが使用される場合があります',privacy:'プライバシーポリシー',revoked:'外部動画への同意を取り消しました。'},
  es:{play:'Aceptar y reproducir',notice:'Al reproducir se pueden usar cookies de {service}',privacy:'Política de privacidad',revoked:'Se ha retirado el consentimiento para vídeos externos.'},
 }[document.documentElement.lang]||{play:'Agree and play',notice:'Playing may use {service} cookies',privacy:'Privacy policy',revoked:'External-media consent withdrawn.'};
 const en=document.documentElement.lang==='en';
 const t=(ko,english)=>window.D9Locale?.translate(ko,english)??(en?english:ko);
 let choice=null,returnFocus=null;
 const frames=new Map();
 const services=new Map();
 const assetRoot=new URL('.',document.currentScript?.src||(location.origin+'/consent.js'));
 const servicePaths=new Map([
  [new URL('community.js',assetRoot).pathname,'board'],
  [new URL('library/library.js',assetRoot).pathname,'library'],
 ]);
 function parsed(raw){try{const saved=JSON.parse(raw);return saved&&['granted','denied'].includes(saved.value)&&Number.isFinite(saved.expires)&&saved.expires>Date.now()?saved:null;}catch{return null;}}
 function storage(kind){try{return kind==='local'?localStorage:sessionStorage;}catch{return null;}}
 function read(){
  const records=[];
  for(const kind of ['local','session']){try{const item=parsed(storage(kind)?.getItem(KEY));if(item)records.push(item);}catch{}}
  records.sort((a,b)=>(b.updated??b.expires-TTL)-(a.updated??a.expires-TTL));
  return records[0]?.value??null;
 }
 function remember(value){
  const record=JSON.stringify({value,expires:Date.now()+TTL,updated:Date.now()});
  // Session fallback is functional consent only; no cookies or visitor IDs.
  for(const kind of ['local','session']){try{storage(kind)?.setItem(KEY,record);}catch{}}
 }
 function clearLegacy(){
  const oldKeys=new Set(['d9-analytics-consent-v1','d9-consent']);
  for(let index=0;index<2;index++){
   try{const storage=index===0?localStorage:sessionStorage;const names=[];for(let i=0;i<storage.length;i++)names.push(storage.key(i));
    names.forEach(name=>{if(oldKeys.has(name)||/^d9-site-visit(?:-day)?s?-v1-/.test(name||''))storage.removeItem(name);});
    oldKeys.forEach(name=>storage.removeItem(name));
   }catch{}
  }
  try{document.cookie.split(';').forEach(part=>{
   const name=part.trim().split('=')[0];
   if(!/^_ga(?:_|$)/.test(name)&&name!=='d9-consent')return;
   ['',location.hostname,'.'+location.hostname,'.dra9oncinema.com'].forEach(domain=>{
    document.cookie=name+'=; Max-Age=0; Path=/; SameSite=Lax'+(domain?'; Domain='+domain:'');
   });
  });}catch{}
 }
 function media(raw){
  try{
   const url=new URL(raw,location.href);
   if(url.protocol!=='https:'||url.username||url.password)return null;
   if(['www.youtube-nocookie.com','youtube-nocookie.com','www.youtube.com','youtube.com'].includes(url.hostname)&&/^\/embed\/[A-Za-z0-9_-]{11}$/.test(url.pathname)&&!url.port){
    url.hostname='www.youtube-nocookie.com';
    return {url:url.href,service:'YouTube',id:url.pathname.split('/').pop(),watch:'https://www.youtube.com/watch?v='+url.pathname.split('/').pop()};
   }
   if(url.href==='https://www.instagram.com/reel/DelRHYDunY-/embed/'){
    return {url:url.href,service:'Instagram',watch:'https://www.instagram.com/reel/DelRHYDunY-/'};
   }
  }catch{}
  return null;
 }
 function syncFrame(frame,state){
  // Home facades always wait for their own play click, even when media
  // permission is already stored. Scrolling never connects a home iframe.
  const allowed=!!state.media&&(state.inline?choice==='granted'&&state.playRequested:choice==='granted');
  if(allowed){
   const url=new URL(state.media.url);
   // Only the clicked player starts. Remembered permission loads other players
   // without unexpectedly starting every video on the page.
   if(state.playRequested&&state.media.service==='YouTube'){url.searchParams.set('autoplay','1');url.searchParams.set('playsinline','1');}
   const permission=new Set((frame.getAttribute('allow')||'').split(';').map(s=>s.trim()).filter(Boolean));
   permission.add('autoplay');
   frame.setAttribute('allow',[...permission].join('; '));
   if(frame.getAttribute('src')!==url.href)frame.setAttribute('src',url.href);
  }else{frame.removeAttribute('src');state.playRequested=false;}
  frame.hidden=!allowed;state.placeholder.hidden=!!allowed;
  frame.parentElement?.classList.toggle('external-media-blocked',!allowed);
 }
 function poster(frame,info){
  const record=info.service==='YouTube'?window.PORTFOLIO?.find(item=>item.id===info.id):null;
  const fallback=new URL('external-media-poster.svg',assetRoot).href;
  const candidate=frame.getAttribute('data-external-poster')||record?.image||(info.service==='YouTube'?new URL('assets/portfolio/'+info.id+'.jpg',assetRoot).href:fallback);
  try{const url=new URL(candidate,location.href);return url.origin===location.origin&&!url.username&&!url.password?url.href:fallback;}catch{return fallback;}
 }
 function prepare(root=document){
  frames.forEach((state,frame)=>{if(frame.isConnected===false){frames.delete(frame);}});
  const candidates=[];
  if(root.matches?.('iframe[data-external-src],iframe[data-home-src]'))candidates.push(root);
  root.querySelectorAll?.('iframe[data-external-src],iframe[data-home-src]').forEach(frame=>candidates.push(frame));
  candidates.forEach(frame=>{
   let state=frames.get(frame);
   if(!state){
    const inline=document.body.dataset.page==='home'&&frame.hasAttribute('data-home-player');
    const info=media(frame.getAttribute(inline?'data-home-src':'data-external-src'));
    const placeholder=document.createElement('div');placeholder.className='external-media-placeholder';
    if(info){
     placeholder.classList.toggle('external-media-instagram',info.service==='Instagram');
     const load=document.createElement('button');load.type='button';load.className='external-media-play';load.setAttribute('aria-label',mediaText.play+' · '+info.service+' · '+(frame.title||''));
     {
      const image=document.createElement('img');image.src=poster(frame,info);image.alt='';image.decoding='async';image.loading=inline?'lazy':'eager';image.fetchPriority=inline?'auto':'high';image.width=720;image.height=405;
      const responsive=window.D9ResponsiveImages?.[info.id];
      image.srcset=frame.getAttribute('data-poster-srcset')||responsive?.srcset||'';image.sizes=frame.getAttribute('data-poster-sizes')||(inline?'(max-width:600px) 100vw, 400px':'100vw');
      if(responsive&&!frame.hasAttribute('data-external-poster'))image.src=responsive.src;
      image.addEventListener('error',()=>{const fallback=new URL('external-media-poster.svg',assetRoot).href;if(image.src!==fallback)image.src=fallback;});
      load.append(image);
     }
     const icon=document.createElement('span');icon.className='external-media-play-icon';icon.textContent='▶';icon.setAttribute('aria-hidden','true');
     const label=document.createElement('span');label.className='external-media-play-label';label.textContent=info.service+' · '+mediaText.play;
     load.append(icon,label);
     if(inline)placeholder.classList.add('home-media-facade');
     load.addEventListener('click',()=>{returnFocus=null;save('granted',frame);frame.focus();});
     const notice=document.createElement('p');notice.className='external-media-notice';
     const text=document.createElement('span');text.textContent=mediaText.notice.replace('{service}',info.service)+' · ';
     const privacy=document.createElement('a');privacy.href=policy.href;privacy.textContent=mediaText.privacy;
     notice.append(text,privacy);placeholder.append(load,notice);
    }else{
     const description=document.createElement('p');description.textContent=t('이 외부 영상 주소는 허용되지 않았습니다. 원본 링크를 이용해 주세요.','This external embed address is not allowed. Use the original link instead.');placeholder.append(description);
    }
    frame.before(placeholder);state={media:info,placeholder,inline};frames.set(frame,state);
   }
   syncFrame(frame,state);
  });
  prepareServices(root);
 }
 function prepareServices(root){
  const candidates=[];
  if(root.matches?.('script[data-service-src]'))candidates.push(root);
  root.querySelectorAll?.('script[data-service-src]').forEach(script=>candidates.push(script));
  candidates.forEach(source=>{
   if(services.has(source))return;
   let url;try{url=new URL(source.getAttribute('data-service-src'),location.href);}catch{return;}
   const kind=servicePaths.get(url.pathname);
   if(!kind||url.origin!==location.origin||url.username||url.password||url.hash)return;
   const panel=document.createElement('section');panel.className='functional-service-gate';
   const description=document.createElement('p');description.textContent=t('이 기능을 시작하면 Google Firebase 인증과 reCAPTCHA 보안 검증을 불러옵니다. 연결에 필요한 네트워크·기기 정보를 Google이 처리할 수 있습니다. 외부 영상 허용과는 별개이며 보안 검증은 유지합니다.','Starting this feature loads Google Firebase authentication and reCAPTCHA security verification. Google may process the network and device information needed for this connection. This is separate from external-media permission, and security protection stays enabled.');
   const button=document.createElement('button');button.type='button';button.textContent=kind==='board'?t('게시판 불러오기','Load board'):t('자료실 로그인 기능 준비','Enable library sign-in');
   const status=document.createElement('p');status.setAttribute('role','status');
   panel.append(description,button,status);
   const main=document.getElementById('main')||document.querySelector('main')||document.body;(kind==='board'&&document.getElementById('board')||main).prepend(panel);
   const state={loading:false};services.set(source,state);
   const connect=()=>{
    if(state.loading)return;state.loading=true;button.disabled=true;status.textContent=t('보안 연결을 준비하고 있습니다…','Preparing the secure connection…');
    const active=document.createElement('script');active.type='module';active.src=url.href;
    active.addEventListener('load',()=>{button.hidden=true;status.textContent=t('연결 기능이 준비되었습니다. 아래에서 계속 진행하세요.','The connection is ready. Continue below.');});
    active.addEventListener('error',()=>{state.loading=false;button.disabled=false;active.remove();status.textContent=t('연결하지 못했습니다. 네트워크를 확인하고 다시 시도하세요.','Could not connect. Check your network and retry.');});
    source.after(active);
   };
   button.addEventListener('click',connect);
   // Restore only the owner's previously successful library connection.
   // This flag starts authentication; it never grants access or enables media.
   if(kind==='library'){try{if(localStorage.getItem('d9-library-reconnect-v1')==='1')connect();}catch{}}

  });
 }
 const banner=document.createElement('section');banner.id='consent-banner';banner.className='external-consent-bar';banner.setAttribute('role','region');banner.setAttribute('aria-labelledby','consent-title');banner.hidden=true;
 const copy=document.createElement('div');copy.className='consent-copy';
 const title=document.createElement('h2');title.id='consent-title';title.textContent=t('외부 영상','External media');
 const description=document.createElement('p');description.textContent=t('허용하면 YouTube·Instagram에 연결됩니다.','Allow to connect to YouTube and Instagram.');
 copy.append(title,description);
 const actions=document.createElement('div');actions.className='consent-actions';
 const policy=document.createElement('a');
 const policyLink=Array.from(document.querySelectorAll('.privacy-controls a')).find(link=>/\/(?:en\/)?privacy\/$/.test(link.getAttribute('href')||''));
 policy.href=policyLink?.getAttribute('href')||(en?'/en':'')+'/privacy/';policy.textContent=t('자세히','Details');policy.setAttribute('aria-label',t('개인정보처리방침 보기','Read the privacy policy'));
 const reject=document.createElement('button');reject.type='button';reject.textContent=t('차단','Block');reject.setAttribute('aria-label',t('외부 영상 차단','Block external media'));
 const accept=document.createElement('button');accept.type='button';accept.className='consent-allow';accept.textContent=t('허용','Allow');accept.setAttribute('aria-label',t('외부 영상 허용','Allow external media'));
 const dismiss=document.createElement('button');dismiss.type='button';dismiss.className='consent-dismiss';dismiss.textContent=t('닫기','Close');dismiss.setAttribute('aria-label',t('선택을 바꾸지 않고 외부 영상 설정 닫기','Close external media settings without changing your choice'));
 actions.append(policy,reject,accept,dismiss);banner.append(copy,actions);document.body.append(banner);
 function notify(){
  window.dispatchEvent(new CustomEvent('d9:external-consent',{detail:{value:choice,canLoadMedia:choice==='granted'}}));
  window.dispatchEvent(new CustomEvent('d9:analytics-consent',{detail:{value:'denied'}}));
 }
 function save(value,playFrame=null){
  const wasGranted=choice==='granted';choice=value;
  remember(value);
  if(playFrame&&frames.has(playFrame))frames.get(playFrame).playRequested=true;
  banner.hidden=true;frames.forEach((state,frame)=>syncFrame(frame,state));notify();
  if(value==='denied'&&wasGranted){location.reload();return;}
  returnFocus?.focus();
 }
 function showSettings(opener){returnFocus=opener||null;banner.hidden=false;reject.focus();}
 function closeSettings(){banner.hidden=true;returnFocus?.focus();}
 dismiss.addEventListener('click',closeSettings);
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!banner.hidden){event.preventDefault();closeSettings();}});
 reject.addEventListener('click',()=>save('denied'));accept.addEventListener('click',()=>save('granted'));
 document.addEventListener('click',event=>{
  const revoke=event.target.closest?.('[data-external-media-revoke]');
  if(revoke){event.preventDefault();save('denied');const status=document.getElementById('external-media-revoke-status');if(status)status.textContent=mediaText.revoked;return;}
  const settings=event.target.closest?.('[data-cookie-settings]');
  if(settings){event.preventDefault();showSettings(settings);}
 });
 window.D9ExternalConsent=Object.freeze({get:()=>choice,canLoadMedia:()=>choice==='granted',grantMedia:()=>save('granted'),denyMedia:()=>save('denied'),showSettings,prepare});
 // Retained only for old integrations: analytics is never granted by media consent.
 window.D9AnalyticsConsent=Object.freeze({get:()=> 'denied'});
 window.addEventListener('storage',event=>{
  if(event.key!==KEY&&event.key!==null)return;const wasGranted=choice==='granted';
  if(event.newValue!==undefined||event.key===null){
   const received=event.key===null?null:parsed(event.newValue);choice=received?.value??null;
   try{const session=storage('session');received?session?.setItem(KEY,JSON.stringify(received)):session?.removeItem(KEY);}catch{}
  }else choice=read();
  banner.hidden=true;frames.forEach((state,frame)=>syncFrame(frame,state));notify();
  if(wasGranted&&choice!=='granted')location.reload();
 });
 window.addEventListener('pageshow',event=>{
  if(!event.persisted)return;const wasGranted=choice==='granted';choice=read();
  frames.forEach((state,frame)=>syncFrame(frame,state));notify();
  if(wasGranted&&choice!=='granted')location.reload();
 });
 // Request permission inside the video slot. Open the page-wide settings bar
 // only when the visitor explicitly uses the footer settings control.
 clearLegacy();choice=read();prepare();notify();
 if(typeof MutationObserver==='function')new MutationObserver(records=>{
  records.forEach(record=>record.addedNodes.forEach(node=>{if(node.nodeType===1)prepare(node);}));
 }).observe(document.body,{childList:true,subtree:true});
})();
