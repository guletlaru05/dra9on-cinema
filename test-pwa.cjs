const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const code=fs.readFileSync('site-assets/service-worker-template.js','utf8').replace('__BASE_JSON__','""').replace('__VERSION__','test');
function setup(){const events={},saved=new Map(),requests=[],notifications=[],opened=[];let offline=false;
 const store={addAll:async paths=>{for(const p of paths)saved.set(p,new Response('generic offline '+p));},match:async p=>saved.get(p)};
 const self={location:{origin:'https://dra9oncinema.com'},addEventListener:(k,v)=>events[k]=v,skipWaiting:async()=>{},clients:{claim:async()=>{},matchAll:async()=>[],openWindow:async url=>opened.push(url)},registration:{showNotification:async(title,options)=>notifications.push({title,options})}};
 const cache={open:async()=>store,keys:async()=>['dra9on-pwa-old','unrelated'],delete:async k=>{requests.push(['delete',k]);}};
 vm.runInNewContext(code,{self,caches:cache,URL,Response,fetch:async(request,options)=>{requests.push([request.url,options]);if(offline)throw Error('offline');return new Response('fresh');}});
 const invoke=async(name,input={})=>{let result,work;events[name]({...input,waitUntil:p=>work=p,respondWith:p=>result=p});await work;return await result;};return {events,saved,requests,notifications,opened,invoke,disconnect:()=>offline=true};
}
test('cache contains only generic offline screens/icons; private and public HTML always use network',async()=>{
 const s=setup();await s.invoke('install');assert.equal(s.saved.size,6);assert([...s.saved.keys()].every(p=>p.startsWith('/pwa/')));
 for(const route of ['/','/ja/','/watch/fall-707-s3-ep1/','/library/']){const result=await s.invoke('fetch',{request:{url:'https://dra9oncinema.com'+route,method:'GET',mode:'navigate'}});assert.equal(await result.text(),'fresh');assert.equal(s.requests.at(-1)[1].cache,'no-store');}
 assert.equal(s.saved.size,6,'no navigation cached');s.disconnect();const offline=await s.invoke('fetch',{request:{url:'https://dra9oncinema.com/es/library/',method:'GET',mode:'navigate'}});assert.match(await offline.text(),/offline-es/);
 await s.invoke('activate');assert(s.requests.some(r=>r[0]==='delete'&&r[1]==='dra9on-pwa-old'));assert(!s.requests.some(r=>r[0]==='delete'&&r[1]==='unrelated'));
});
test('never intercepts API, Firebase, media, POST or asset requests',async()=>{
 const s=setup();for(const request of [{url:'https://www.youtube.com/watch?v=x',method:'GET',mode:'navigate'},{url:'https://dra9oncinema.com/api',method:'POST',mode:'navigate'},{url:'https://dra9oncinema.com/catalog.js',method:'GET',mode:'cors'}])assert.equal(await s.invoke('fetch',{request}),undefined);assert.equal(s.requests.length,0);
});
test('push shows a visible title and thumbnail; click only opens same-origin episode routes',async()=>{
 const s=setup();const note={id:'newvideo001',title:'새 회차',body:'공개',url:'/ja/watch/fall-707-s3-ep2/',image:'/assets/portfolio/newvideo001.jpg',lang:'ja'};await s.invoke('push',{data:{json:()=>note}});assert.equal(s.notifications.length,1);assert.equal(s.notifications[0].title,note.title);assert.equal(s.notifications[0].options.image,'https://dra9oncinema.com'+note.image);
 await s.invoke('notificationclick',{notification:{close(){},data:{url:'https://evil.example/'}}});assert.equal(s.opened.length,0);
 await s.invoke('notificationclick',{notification:{close(){},data:{url:note.url}}});assert.deepEqual(s.opened,['https://dra9oncinema.com'+note.url]);
 await s.invoke('push',{data:{json:()=>({...note,url:'https://evil.example/'})}});assert.equal(s.notifications.length,1);
});
