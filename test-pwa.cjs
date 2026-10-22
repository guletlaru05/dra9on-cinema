const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const code=fs.readFileSync('site-assets/service-worker-template.js','utf8').replace('__BASE_JSON__','""').replace('__VERSION__','test');
function setup({blocked=false,clients=[],keys=['dra9on-pwa-old','unrelated']}={}){const events={},saved=new Map(),requests=[],notifications=[],opened=[];let offline=false,skipped=0,claimed=0;
 const store={addAll:async paths=>{for(const p of paths){assert.equal(p.cache,'reload');saved.set(new URL(p.url).pathname,new Response('generic offline '+p.url));}},match:async p=>saved.get(p)};
 const self={location:{origin:'https://dra9oncinema.com'},addEventListener:(k,v)=>events[k]=v,skipWaiting:async()=>skipped++,clients:{claim:async()=>claimed++,matchAll:async()=>clients,openWindow:async url=>opened.push(url)},registration:{showNotification:async(title,options)=>notifications.push({title,options})}};
 const cache={open:async()=>{if(blocked)throw Error('Storage denied');return store;},keys:async()=>{if(blocked)throw Error('Storage denied');return keys;},delete:async k=>{requests.push(['delete',k]);keys=keys.filter(key=>key!==k);}};
 class RelativeRequest extends Request{constructor(url,options){super(new URL(url,self.location.origin),options);}}
 vm.runInNewContext(code,{self,caches:cache,URL,Response,Request:RelativeRequest,fetch:async(request,options)=>{requests.push([request.url,options]);if(offline)throw Error('offline');return new Response('fresh');}});
 const invoke=async(name,input={})=>{let result,work;events[name]({...input,waitUntil:p=>work=p,respondWith:p=>result=p});await work;return await result;};return {events,saved,requests,notifications,opened,invoke,get skipped(){return skipped;},get claimed(){return claimed;},disconnect:()=>offline=true};
}

test('upgrade clears owned old caches and refreshes same-origin pages once without touching auth popups',async()=>{
 const navigated=[],clients=['https://dra9oncinema.com/actors/?v=old#gallery','https://dra9oncinema.com/library/','https://dra9oncinema.com/__/auth/handler','https://dra9on-cinema.pages.dev/','https://guletlaru05.github.io/dra9on-cinema/'].map(url=>({url,navigate:async value=>navigated.push(value)}));
 const s=setup({clients});await s.invoke('install');await s.invoke('activate');await s.invoke('activate');
 assert.deepEqual(navigated,clients.slice(0,2).map(c=>c.url));assert.equal(s.skipped,1);assert.equal(s.claimed,2);
 assert(!s.requests.some(r=>r[0]==='delete'&&r[1]==='unrelated'));
 const fresh=setup({clients,keys:[]});await fresh.invoke('activate');assert.equal(navigated.length,2,'new installs do not refresh');
});

test('blocked storage cannot prevent activation or online navigation and has a readable offline fallback',async()=>{
 const s=setup({blocked:true});await s.invoke('install');await s.invoke('activate');assert.equal(s.skipped,1);assert.equal(s.claimed,1);
 const request={url:'https://dra9oncinema.com/library/',method:'GET',mode:'navigate'};
 assert.equal(await (await s.invoke('fetch',{request})).text(),'fresh');s.disconnect();
 const response=await s.invoke('fetch',{request});assert.equal(response.status,503);assert.match(await response.text(),/reconnect/);
});

test('activation completes before a recovery navigation resolves, avoiding a fetch/activate deadlock',async()=>{
 const s=setup({clients:[{url:'https://dra9oncinema.com/',navigate:()=>new Promise(()=>{})}]});
 let complete=false;void s.invoke('activate').then(()=>complete=true);
 await new Promise(resolve=>setImmediate(resolve));assert.equal(complete,true);
});
test('cache contains only generic offline screens/icons; private and public HTML always use network',async()=>{
 const s=setup();await s.invoke('install');assert.equal(s.saved.size,6);assert([...s.saved.keys()].every(p=>p.startsWith('/pwa/')));
 for(const route of ['/','/ja/','/watch/fall-707-s3-ep1/','/library/']){const result=await s.invoke('fetch',{request:{url:'https://dra9oncinema.com'+route,method:'GET',mode:'navigate'}});assert.equal(await result.text(),'fresh');assert.equal(s.requests.at(-1)[1].cache,'no-store');}
 assert.equal(s.saved.size,6,'no navigation cached');s.disconnect();const offline=await s.invoke('fetch',{request:{url:'https://dra9oncinema.com/es/library/',method:'GET',mode:'navigate'}});assert.match(await offline.text(),/offline-es/);
 await s.invoke('activate');assert(s.requests.some(r=>r[0]==='delete'&&r[1]==='dra9on-pwa-old'));assert(!s.requests.some(r=>r[0]==='delete'&&r[1]==='unrelated'));
});
test('never intercepts API, Firebase, media, POST or asset requests',async()=>{
 const s=setup();for(const request of [{url:'https://www.youtube.com/watch?v=x',method:'GET',mode:'navigate'},{url:'https://dra9oncinema.com/__/auth/handler',method:'GET',mode:'navigate'},{url:'https://dra9oncinema.com/api',method:'POST',mode:'navigate'},{url:'https://dra9oncinema.com/catalog.js',method:'GET',mode:'cors'}])assert.equal(await s.invoke('fetch',{request}),undefined);assert.equal(s.requests.length,0);
});
test('push shows a visible title and thumbnail; click only opens same-origin episode routes',async()=>{
 const s=setup();const note={id:'newvideo001',title:'새 회차',body:'공개',url:'/ja/watch/fall-707-s3-ep2/',image:'/assets/portfolio/newvideo001.jpg',lang:'ja'};await s.invoke('push',{data:{json:()=>note}});assert.equal(s.notifications.length,1);assert.equal(s.notifications[0].title,note.title);assert.equal(s.notifications[0].options.image,'https://dra9oncinema.com'+note.image);
 await s.invoke('notificationclick',{notification:{close(){},data:{url:'https://evil.example/'}}});assert.equal(s.opened.length,0);
 await s.invoke('notificationclick',{notification:{close(){},data:{url:note.url}}});assert.deepEqual(s.opened,['https://dra9oncinema.com'+note.url]);
 await s.invoke('push',{data:{json:()=>({...note,url:'https://evil.example/'})}});assert.equal(s.notifications.length,1);
});
