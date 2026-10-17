/* Functional external-media choices only. No analytics tags or visitor identity. */
(() => {
 'use strict';
 const KEY='d9-external-media-choice-v1',TTL=180*86400000;
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
 function read(){
  try{const saved=JSON.parse(localStorage.getItem(KEY));return saved&&['granted','denied'].includes(saved.value)&&saved.expires>Date.now()?saved.value:null;}catch{return null;}
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
   if(url.hostname==='www.youtube-nocookie.com'&&/^\/embed\/[A-Za-z0-9_-]{11}$/.test(url.pathname)){
    return {url:url.href,service:'YouTube',watch:'https://www.youtube.com/watch?v='+url.pathname.split('/').pop()};
   }
   if(url.href==='https://www.instagram.com/reel/DelRHYDunY-/embed/'){
    return {url:url.href,service:'Instagram',watch:'https://www.instagram.com/reel/DelRHYDunY-/'};
   }
  }catch{}
  return null;
 }
 function syncFrame(frame,state){
  const allowed=choice==='granted'&&state.media;
  if(allowed){if(frame.getAttribute('src')!==state.media.url)frame.setAttribute('src',state.media.url);}
  else frame.removeAttribute('src');
  frame.hidden=!allowed;state.placeholder.hidden=!!allowed;
  frame.parentElement?.classList.toggle('external-media-blocked',!allowed);
 }
 function prepare(root=document){
  const candidates=[];
  if(root.matches?.('iframe[data-external-src]'))candidates.push(root);
  root.querySelectorAll?.('iframe[data-external-src]').forEach(frame=>candidates.push(frame));
  candidates.forEach(frame=>{
   let state=frames.get(frame);
   if(!state){
    const info=media(frame.getAttribute('data-external-src'));
    const placeholder=document.createElement('div');placeholder.className='external-media-placeholder';
    const title=document.createElement('strong');title.textContent=frame.title||t('외부 영상','External video');
    const description=document.createElement('p');
    description.textContent=info?t('허용하면 이 사이트의 YouTube·Instagram 영상이 연결되며, 각 서비스가 쿠키와 기기 정보를 처리할 수 있습니다. 선택은 이 브라우저에 저장됩니다.','Allowing connects YouTube and Instagram videos across this site. These services may process cookies and device information. Your choice is saved in this browser.'):t('이 외부 영상 주소는 허용되지 않았습니다. 원본 링크를 이용해 주세요.','This external embed address is not allowed. Use the original link instead.');
    placeholder.append(title,description);
    if(info){
     const load=document.createElement('button');load.type='button';load.textContent=t('외부 영상 허용하고 불러오기','Allow and load external media');
     load.addEventListener('click',()=>save('granted'));
     const watch=document.createElement('a');watch.href=info.watch;watch.target='_blank';watch.rel='noopener noreferrer';watch.textContent=t(info.service+'에서 보기 ↗','Watch on '+info.service+' ↗');
     const privacy=document.createElement('a');privacy.href=policy.href;privacy.textContent=t('개인정보처리방침','Privacy policy');
     placeholder.append(load,watch,privacy);
    }
    frame.before(placeholder);state={media:info,placeholder};frames.set(frame,state);
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
   const main=document.getElementById('main')||document.querySelector('main')||document.body;main.prepend(panel);
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
 function save(value){
  const wasGranted=choice==='granted';choice=value;
  try{localStorage.setItem(KEY,JSON.stringify({value,expires:Date.now()+TTL}));}catch{}
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
  const settings=event.target.closest?.('[data-cookie-settings]');
  if(settings){event.preventDefault();showSettings(settings);}
 });
 window.D9ExternalConsent=Object.freeze({get:()=>choice,canLoadMedia:()=>choice==='granted',grantMedia:()=>save('granted'),denyMedia:()=>save('denied'),showSettings,prepare});
 // Retained only for old integrations: analytics is never granted by media consent.
 window.D9AnalyticsConsent=Object.freeze({get:()=> 'denied'});
 window.addEventListener('storage',event=>{
  if(event.key!==KEY)return;const wasGranted=choice==='granted';choice=read();
  banner.hidden=true;frames.forEach((state,frame)=>syncFrame(frame,state));notify();
  if(wasGranted&&choice!=='granted')location.reload();
 });
 // Request permission inside the video slot. Open the page-wide settings bar
 // only when the visitor explicitly uses the footer settings control.
 clearLegacy();choice=read();prepare();notify();
 if(typeof MutationObserver==='function')new MutationObserver(records=>{
  records.forEach(record=>record.addedNodes.forEach(node=>{if(node.nodeType===1)prepare(node);}));
 }).observe(document.body,{childList:true,subtree:true});
})();
