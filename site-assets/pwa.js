(()=>{
 'use strict';
 const script=document.currentScript,base=script?.dataset.pwaBase||'',endpoint='https://dra9on-episode-push.tutorial-metrics.workers.dev';
 const lang=['ko','en','ja','es'].includes(document.documentElement.lang)?document.documentElement.lang:'en';
 const copy={
 ko:{install:'앱 설치',notify:'새 회차 알림 받기',off:'새 회차 알림 끄기',tip:'공유 → 홈 화면에 추가로 앱처럼 열 수 있어요.',close:'닫기',ios:'아이폰 알림은 iOS 16.4 이상에서 홈 화면에 설치한 앱으로 열어야 받을 수 있습니다.',unsupported:'이 브라우저는 새 회차 알림을 지원하지 않습니다.',denied:'알림이 차단되어 있습니다. 브라우저 설정에서 허용해 주세요.',working:'알림을 연결하고 있습니다…',success:'새 회차 알림을 켰습니다.',stopped:'이 기기의 새 회차 알림을 껐습니다.',failed:'연결하지 못했습니다. 인터넷 연결을 확인하고 다시 시도해 주세요.',privacy:'허용하면 알림 주소·암호화 키·선택 언어만 저장합니다. 이름·이메일·시청 기록은 저장하지 않습니다.',full:'무료 구독 한도에 도달했습니다. 지금은 알림을 연결할 수 없습니다.'},
 en:{install:'Install app',notify:'Notify me of new episodes',off:'Turn off episode alerts',tip:'Share → Add to Home Screen to open this site as an app.',close:'Close',ios:'On iPhone, notifications require iOS 16.4 or later and opening the app from your Home Screen.',unsupported:'Episode alerts are not supported in this browser.',denied:'Notifications are blocked. Allow them in your browser settings.',working:'Connecting notifications…',success:'New episode notifications are on.',stopped:'Episode alerts are off on this device.',failed:'Could not connect. Check your internet connection and retry.',privacy:'If enabled, only your push address, encryption keys and selected language are saved. No name, email or viewing history is stored.',full:'The free subscription limit has been reached. Notifications are currently unavailable.'},
 ja:{install:'アプリをインストール',notify:'新エピソードの通知を受け取る',off:'新エピソードの通知をオフ',tip:'共有 → ホーム画面に追加でアプリとして開けます。',close:'閉じる',ios:'iPhoneの通知にはiOS 16.4以降が必要です。ホーム画面に追加したアプリから開いてください。',unsupported:'このブラウザは通知に対応していません。',denied:'通知がブロックされています。ブラウザ設定で許可してください。',working:'通知に接続中…',success:'新エピソードの通知をオンにしました。',stopped:'この端末の通知をオフにしました。',failed:'接続できませんでした。接続を確認して再試行してください。',privacy:'許可すると通知先・暗号化キー・選択言語のみを保存します。名前・メール・視聴履歴は保存しません。',full:'無料枠の登録上限に達しました。現在、通知を登録できません。'},
 es:{install:'Instalar aplicación',notify:'Avisarme de nuevos episodios',off:'Desactivar avisos de episodios',tip:'Compartir → Añadir a pantalla de inicio para abrir como aplicación.',close:'Cerrar',ios:'En iPhone, los avisos requieren iOS 16.4 o posterior y abrir la aplicación desde la pantalla de inicio.',unsupported:'Este navegador no admite notificaciones.',denied:'Las notificaciones están bloqueadas. Permítelas en los ajustes del navegador.',working:'Conectando notificaciones…',success:'Avisos de nuevos episodios activados.',stopped:'Avisos desactivados en este dispositivo.',failed:'No se pudo conectar. Comprueba la conexión e inténtalo de nuevo.',privacy:'Si aceptas, solo guardamos la dirección push, claves de cifrado e idioma. No guardamos nombre, correo ni historial de visionado.',full:'Se ha alcanzado el límite gratuito de suscripciones. Los avisos no están disponibles por ahora.'}
 }[lang];
 if(!('serviceWorker'in navigator)||!window.isSecureContext)return;
 const register=()=>navigator.serviceWorker.register(base+'/sw.js',{scope:base+'/',updateViaCache:'none'});
 let currentRegistration=null,lastUpdate=Date.now();
 const registration=register().then(reg=>{currentRegistration=reg;return navigator.serviceWorker.ready;}).catch(()=>null);
 // Long-lived installed apps also check on returning to the foreground.
 // Activation owns the single refresh; a controllerchange reload here would double it.
 window.addEventListener('focus',()=>{
  if(!currentRegistration||Date.now()-lastUpdate<60000)return;
  lastUpdate=Date.now();void currentRegistration.update().catch(()=>{});
 });
 // Private pages get the generic offline fallback but no subscription controls.
 if(location.pathname.startsWith(base+'/library/'))return;
 const standalone=()=>matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
 const ios=/iP(?:hone|ad|od)/.test(navigator.userAgent)||navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1;
 const safari=ios&&/Safari/.test(navigator.userAgent)&&!/CriOS|FxiOS|EdgiOS|OPiOS/.test(navigator.userAgent);
 const area=document.createElement('section');area.className='pwa-controls';area.setAttribute('aria-label','DRA9ON CINEMA APP');
 const install=document.createElement('button');install.type='button';install.className='pwa-install';install.textContent=copy.install;install.hidden=true;
 const notify=document.createElement('button');notify.type='button';notify.textContent=copy.notify;
 const note=document.createElement('p');note.textContent=copy.privacy;
 const status=document.createElement('p');status.setAttribute('role','status');area.append(install,notify,note,status);document.body.append(area);
 let installPrompt=null;
 window.addEventListener('beforeinstallprompt',event=>{event.preventDefault();installPrompt=event;if(!standalone())install.hidden=false;});
 window.addEventListener('appinstalled',()=>{installPrompt=null;install.hidden=true;});
 install.addEventListener('click',async()=>{if(!installPrompt)return;await installPrompt.prompt();await installPrompt.userChoice;installPrompt=null;install.hidden=true;});
 if(safari&&!standalone()){
  let seen=true;try{seen=localStorage.getItem('d9-ios-install-tip-v1')==='1';if(!seen)localStorage.setItem('d9-ios-install-tip-v1','1');}catch{}
  if(!seen){const tip=document.createElement('aside');tip.className='pwa-ios-tip';const text=document.createElement('p');text.textContent=copy.tip;const close=document.createElement('button');close.type='button';close.textContent=copy.close;close.addEventListener('click',()=>tip.remove());tip.append(text,close);document.body.append(tip);}
 }
 const canPush='PushManager'in window&&'Notification'in window&&(!ios||standalone());
 if(!canPush){notify.hidden=true;status.textContent=ios?copy.ios:copy.unsupported;return;}
 const TOKEN_KEY='d9-push-delete-token-v1';let subscribed=false;
 function token(){try{let value=localStorage.getItem(TOKEN_KEY);if(!/^[a-f0-9]{64}$/.test(value||'')){value=[...crypto.getRandomValues(new Uint8Array(32))].map(x=>x.toString(16).padStart(2,'0')).join('');localStorage.setItem(TOKEN_KEY,value);}return value;}catch{throw Error('storage');}}
 const bodyFor=sub=>({...sub.toJSON(),expirationTime:undefined,lang,unsubscribeToken:token()});
 async function api(route,body){const result=await fetch(endpoint+route,{method:'POST',credentials:'omit',cache:'no-store',referrerPolicy:'no-referrer',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(15000)});if(!result.ok)throw Error(result.status===429?'full':'network');return result;}
 const bytes=value=>Uint8Array.from(atob(value.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-value.length%4)%4)),c=>c.charCodeAt(0));
 async function refresh(){const reg=await registration;if(!reg)return;const sub=await reg.pushManager.getSubscription();subscribed=!!sub;notify.textContent=subscribed?copy.off:copy.notify;if(sub){try{await api('/subscribe',bodyFor(sub));}catch{status.textContent=copy.failed;}}}
 // No permission request on load. Reuse only a subscription the visitor already granted.
 void refresh().catch(()=>{});
 notify.addEventListener('click',async()=>{
  if(notify.disabled)return;notify.disabled=true;
  try{
   // Request permission synchronously from the visitor's click, before any network await.
   const permission=subscribed?null:Notification.permission==='default'?Notification.requestPermission():Promise.resolve(Notification.permission);
   if(permission&&await permission!=='granted'){status.textContent=copy.denied;return;}
   status.textContent=copy.working;const reg=await registration;if(!reg)throw Error('registration');
   let sub=await reg.pushManager.getSubscription();
   if(subscribed&&sub){
    // Browser opt-out must still work if storage was cleared or the server is offline.
    let removed=true;try{await api('/unsubscribe',{endpoint:sub.endpoint,unsubscribeToken:token()});}catch{removed=false;}
    await sub.unsubscribe();if(removed){try{localStorage.removeItem(TOKEN_KEY);}catch{}}
    subscribed=false;notify.textContent=copy.notify;status.textContent=copy.stopped+(removed?'':' '+copy.failed);return;
   }
   if(!sub){const response=await fetch(endpoint+'/key',{credentials:'omit',cache:'no-store',referrerPolicy:'no-referrer'});if(!response.ok)throw Error('key');const data=await response.json();sub=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:bytes(data.publicKey)});}
   try{await api('/subscribe',bodyFor(sub));}catch(error){await sub.unsubscribe();throw error;}
   subscribed=true;notify.textContent=copy.off;status.textContent=copy.success;
  }catch(error){status.textContent=error.message==='full'?copy.full:copy.failed;}finally{notify.disabled=false;}
 });
})();
