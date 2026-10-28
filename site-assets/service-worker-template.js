/* Public HTML is NEVER saved. Only the generic offline screen and app icons are cached. */
const BASE=__BASE_JSON__,CACHE='dra9on-pwa-__VERSION__';
const offline=lang=>BASE+'/pwa/offline-'+lang+'.html';
const language=path=>path.slice(BASE.length).split('/')[1];
const langs=new Set(['ko','en','ja','es']);
self.addEventListener('install',event=>{event.waitUntil((async()=>{
 // A blocked/quota-limited CacheStorage must never prevent an online recovery.
 try{
  const cache=await caches.open(CACHE);
  await cache.addAll([...langs].map(offline).concat([BASE+'/pwa/icon-192.png',BASE+'/pwa/icon-512.png']).map(url=>new Request(url,{cache:'reload'})));
 }catch{}
 await self.skipWaiting();
})());});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{
 let upgrading=false;
 try{
  const previous=(await caches.keys()).filter(k=>k.startsWith('dra9on-pwa-')&&k!==CACHE);
  upgrading=previous.length>0;
  await Promise.all(previous.map(k=>caches.delete(k)));
 }catch{}
 await self.clients.claim();
 // Activation runs once per version. Refresh even old pages without an update
 // listener, without deleting cookies, Firebase IndexedDB or push subscriptions.
 // Keep Google's auth helper/popup in place while it completes a sign-in.
 if(upgrading){
  const windows=await self.clients.matchAll({type:'window',includeUncontrolled:true});
  for(const client of windows){
   // Do not await navigate(): its fetch waits for activation to finish.
   // Waiting here would deadlock the very page we are trying to recover.
   try{const url=new URL(client.url);if(url.origin===self.location.origin&&url.pathname.startsWith(BASE+'/')&&!url.pathname.startsWith(BASE+'/__/')&&'navigate'in client)void client.navigate(url.href).catch(()=>{});}catch{}
  }
 }
})());});
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==self.location.origin||event.request.mode!=='navigate'||url.pathname.startsWith(BASE+'/__/'))return;
 event.respondWith((async()=>{
  try{return await fetch(event.request,{cache:'no-store'});}
  catch{
   const lang=language(url.pathname);
   try{const fallback=await (await caches.open(CACHE)).match(offline(langs.has(lang)?lang:'ko'));if(fallback)return fallback;}catch{}
   return new Response('Offline — please reconnect and reload.',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8','Cache-Control':'no-store'}});
  }
 })());
});
function safePage(value){
 try{const url=new URL(value,self.location.origin),episode=new RegExp('^'+BASE+'/(?:en/|ja/|es/)?watch/fall-707-s[1-9][0-9]*-ep[1-9][0-9]*(?:-part[1-9][0-9]{0,2})?/$').test(url.pathname)&&!url.hash,board=new RegExp('^'+BASE+'/(?:en/|ja/|es/)?lounge/$').test(url.pathname)&&/^#(?:board|post-[A-Za-z0-9_-]{1,128})$/.test(url.hash);return url.origin===self.location.origin&&!url.search&&(episode||board)?url.href:null;}catch{return null;}
}
self.addEventListener('push',event=>{event.waitUntil((async()=>{
 let data;try{data=event.data.json();}catch{return;}
 const url=safePage(data.url);if(!url||typeof data.title!=='string'||data.title.length>240)return;
 const image=typeof data.image==='string'?new URL(data.image,self.location.origin):null;
 await self.registration.showNotification(data.title,{body:String(data.body||'').slice(0,data.kind==='owner-board'?2000:240),icon:BASE+'/pwa/icon-192.png',badge:BASE+'/pwa/icon-192.png',...(image?.origin===self.location.origin&&image.pathname.startsWith(BASE+'/assets/portfolio/')?{image:image.href}:{}),tag:'dra9on-'+(data.kind==='owner-board'?'board-':'episode-')+String(data.id||'').slice(0,80),data:{url},lang:langs.has(data.lang)?data.lang:'en'});
})());});
self.addEventListener('notificationclick',event=>{
 event.notification.close();const url=safePage(event.notification.data?.url);if(!url)return;
 event.waitUntil((async()=>{const clients=await self.clients.matchAll({type:'window',includeUncontrolled:true});for(const client of clients){if(new URL(client.url).origin===self.location.origin&&'navigate'in client){await client.navigate(url);return client.focus();}}return self.clients.openWindow(url);})());
});
