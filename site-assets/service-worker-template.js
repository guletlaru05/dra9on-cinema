/* Public HTML is NEVER saved. Only the generic offline screen and app icons are cached. */
const BASE=__BASE_JSON__,CACHE='dra9on-pwa-__VERSION__';
const offline=lang=>BASE+'/pwa/offline-'+lang+'.html';
const language=path=>path.slice(BASE.length).split('/')[1];
const langs=new Set(['ko','en','ja','es']);
self.addEventListener('install',event=>{event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);
 await cache.addAll([...langs].map(offline).concat([BASE+'/pwa/icon-192.png',BASE+'/pwa/icon-512.png']));
 await self.skipWaiting();
})());});
self.addEventListener('activate',event=>{event.waitUntil((async()=>{
 await Promise.all((await caches.keys()).filter(k=>k.startsWith('dra9on-pwa-')&&k!==CACHE).map(k=>caches.delete(k)));
 await self.clients.claim();
})());});
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==self.location.origin||event.request.mode!=='navigate')return;
 event.respondWith((async()=>{
  try{return await fetch(event.request,{cache:'no-store'});}
  catch{const lang=language(url.pathname);return await (await caches.open(CACHE)).match(offline(langs.has(lang)?lang:'ko'))||new Response('Offline',{status:503});}
 })());
});
function safePage(value){
 try{const url=new URL(value,self.location.origin),episode=new RegExp('^'+BASE+'/(?:en/|ja/|es/)?watch/fall-707-s[1-9][0-9]*-ep[1-9][0-9]*/$').test(url.pathname)&&!url.hash,board=new RegExp('^'+BASE+'/(?:en/|ja/|es/)?lounge/$').test(url.pathname)&&/^#(?:board|post-[A-Za-z0-9_-]{1,128})$/.test(url.hash);return url.origin===self.location.origin&&!url.search&&(episode||board)?url.href:null;}catch{return null;}
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
