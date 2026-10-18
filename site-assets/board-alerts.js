/* Uses the already signed-in board user. No visitor login UI or automatic permission prompt. */
const ENDPOINT='https://dra9on-episode-push.tutorial-metrics.workers.dev',QUEUE='d9-board-notice-pending-v1';
export function createBoardAlerts({auth,owner,appCheckToken,t,baseline}){
 const on=document.getElementById('board-notify-on'),off=document.getElementById('board-notify-off'),status=document.getElementById('board-notify-status');
 if(!on||!off)return {post:async()=>{},changed:async()=>{},removed:async()=>{},session:async()=>{}};
 if(document.body.dataset.loungePreview==='true'){on.disabled=off.disabled=true;status.textContent=t('미리보기에서는 실제 알림을 등록하거나 발송하지 않습니다.','This preview does not register or send real notifications.');return {post:async()=>{},changed:async()=>{},removed:async()=>{},session:async()=>{}};}
 const lang=document.documentElement.lang;let syncing=false;
 const tell=s=>status.textContent=s;
 async function api(route,input){const user=auth.currentUser;if(!user)throw Error('auth');const [token,check]=await Promise.all([user.getIdToken(),appCheckToken()]);const r=await fetch(ENDPOINT+'/owner-board/'+route,{method:'POST',credentials:'omit',cache:'no-store',referrerPolicy:'no-referrer',headers:{Authorization:'Bearer '+token,'X-Firebase-AppCheck':check.token,'Content-Type':'application/json'},body:JSON.stringify(input),signal:AbortSignal.timeout(20000)});if(!r.ok)throw Error(r.status===503?'pending':'network');return r.json();}
 function queue(){try{return JSON.parse(localStorage.getItem(QUEUE)||'[]').filter(id=>/^[A-Za-z0-9_-]{1,128}$/.test(id)).slice(-20);}catch{return [];}}
 async function post(id){const ids=[...new Set([...queue(),id])].slice(-20);try{localStorage.setItem(QUEUE,JSON.stringify(ids));}catch{}try{await api('event',{id});try{localStorage.setItem(QUEUE,JSON.stringify(queue().filter(x=>x!==id)));}catch{}}catch{/* The public post is already saved. Retry only this real post ID later. */}}
 const reg=async()=>{if(!('serviceWorker'in navigator)||!('PushManager'in window)||!('Notification'in window))throw Error('unsupported');const ios=/iP(?:hone|ad|od)/.test(navigator.userAgent)||navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1;if(ios&&!matchMedia('(display-mode: standalone)').matches&&!navigator.standalone)throw Error('ios');return navigator.serviceWorker.ready;};
 const key=s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-s.length%4)%4)),c=>c.charCodeAt(0));
 const random=()=>Array.from(crypto.getRandomValues(new Uint8Array(32))).map(x=>x.toString(16).padStart(2,'0')).join('');
 on.addEventListener('click',async()=>{
  if(!owner(auth.currentUser))return;
  on.disabled=true;
  try{
   // Check deployment before asking for OS permission or creating a subscription.
   await api('status',{});
   const ios=/iP(?:hone|ad|od)/.test(navigator.userAgent);if(ios&&!matchMedia('(display-mode: standalone)').matches&&!navigator.standalone)throw Error('ios');
   // Explicit owner click is the only place we ask for notification permission.
   if(!('Notification'in window)||await Notification.requestPermission()!=='granted')throw Error('permission');
   const registration=await reg();let subscription=await registration.pushManager.getSubscription();
   if(!subscription){const r=await fetch(ENDPOINT+'/key',{credentials:'omit',cache:'no-store'});if(!r.ok)throw Error('key');subscription=await registration.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:key((await r.json()).publicKey)});}
   const data=subscription.toJSON();await api('subscribe',{endpoint:data.endpoint,keys:data.keys,lang,unsubscribeToken:random()});
   tell(t('이 기기의 운영자 전용 알림을 켰습니다. 다른 방문자에게는 보내지 않습니다.','Owner-only alerts are enabled on this device. Visitors do not receive these alerts.'));
  }catch(error){tell(error.message==='ios'?t('아이폰은 홈 화면에 설치한 앱에서 알림을 켜주세요.','On iPhone, enable alerts from the installed Home Screen app.'):error.message==='pending'?t('알림 서버 배포와 기기 검증이 아직 완료되지 않았습니다.','Notification deployment and device verification are still pending.'):t('알림을 연결하지 못했습니다. 브라우저 권한과 연결 상태를 확인해 주세요.','Could not enable alerts. Check browser permission and your connection.'));}finally{on.disabled=false;}
 });
 off.addEventListener('click',async()=>{if(!owner(auth.currentUser))return;off.disabled=true;try{const subscription=await(await reg()).pushManager.getSubscription();if(subscription)await api('unsubscribe',{endpoint:subscription.endpoint});tell(t('이 기기의 게시판 알림을 껐습니다. 새 회차 알림 설정은 유지됩니다.','Board alerts are off on this device. Episode-alert settings are unchanged.'));}catch{tell(t('해제하지 못했습니다. 다시 시도해 주세요.','Could not disable alerts. Please retry.'));}finally{off.disabled=false;}});
 async function session(){
  if(!auth.currentUser)return;
  for(const id of queue())await post(id);
  if(owner(auth.currentUser)&&!syncing){syncing=true;try{await baseline(async(ids,complete)=>api('baseline',{ids,complete}));const digest=await api('digest',{});if(owner(auth.currentUser)){let box=document.getElementById('board-owner-digest');if(!box){box=document.createElement('section');box.id='board-owner-digest';document.getElementById('board-owner-panel').append(box);}box.replaceChildren();const title=document.createElement('h3');title.textContent=t('오늘의 글 · 미답변','Today’s posts · Unanswered');const count=document.createElement('p');count.textContent=digest.baselineComplete?t('미답변','Unanswered')+' '+digest.unanswered:t('기존 글 초기 동기화 미완료','Initial board sync incomplete');box.append(title,count);const list=document.createElement('ul');for(const item of digest.items){const row=document.createElement('li'),link=document.createElement('a');link.href=(lang==='ko'?'':'/'+lang)+'/lounge/#post-'+encodeURIComponent(item.id);link.textContent=item.nickname+' · '+item.title;row.append(link);list.append(row);}box.append(list);}}catch{/* Do not claim an exact unanswered count until the baseline is complete. */}finally{syncing=false;}}
 }
 async function removed(id){if(!owner(auth.currentUser))return;try{await api('removed',{id});}catch{tell(t('글은 숨겼지만 알림 목록 갱신이 지연되고 있습니다.','The post is hidden, but the notification index update is delayed.'));}}
 return {post,changed:post,removed,session};
}
