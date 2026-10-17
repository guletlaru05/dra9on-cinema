const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const code=fs.readFileSync('site-assets/pwa.js','utf8');
function setup({ios=false,standalone=false,stored={}}={}){
 const nodes=[],events={},map=new Map(Object.entries(stored));let permissionRequests=0,registrations=0,prompts=0;
 const element=tag=>{const node={tag,children:[],events:{},hidden:false,disabled:false,removed:false,append(...children){this.children.push(...children);},setAttribute(){},addEventListener(type,fn){this.events[type]=fn;},remove(){this.removed=true;}};nodes.push(node);return node;};
 const localStorage={getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v),removeItem:k=>map.delete(k)};
 const notification={permission:'default',requestPermission:()=>{permissionRequests++;return Promise.resolve('denied');}};
 const registration={pushManager:{getSubscription:async()=>null}};
 const window={isSecureContext:true,PushManager:class{},Notification:notification,addEventListener:(k,fn)=>events[k]=fn};
 vm.runInNewContext(code,{window,document:{currentScript:{dataset:{pwaBase:''}},documentElement:{lang:'ko'},createElement:element,body:element('body')},navigator:{serviceWorker:{register:async()=>{registrations++;return registration;}},userAgent:ios?'iPhone Version/17.0 Mobile Safari/604.1':'Chrome/130',standalone,platform:ios?'iPhone':'Win32',maxTouchPoints:ios?5:0},Notification:notification,matchMedia:()=>({matches:standalone}),location:{pathname:'/',origin:'https://dra9oncinema.com'},localStorage,crypto:require('node:crypto').webcrypto,URL,Uint8Array,AbortSignal,atob,fetch:()=>{throw Error('Unexpected network request');}});
 return {nodes,events,map,get permissions(){return permissionRequests;},get registrations(){return registrations;},prompt:async()=>prompts++,button:text=>nodes.find(n=>n.tag==='button'&&n.textContent===text)};
}
test('permission is never requested on load; only the explicit notification button asks',async()=>{
 const s=setup();await new Promise(resolve=>setImmediate(resolve));assert.equal(s.permissions,0);assert.equal(s.registrations,1);
 await s.button('새 회차 알림 받기').events.click();assert.equal(s.permissions,1);
});
test('iPhone Safari hint appears once; browser tab cannot request notifications',()=>{
 const s=setup({ios:true});assert(s.nodes.some(n=>n.className==='pwa-ios-tip'));assert.equal(s.map.get('d9-ios-install-tip-v1'),'1');assert.equal(s.button('새 회차 알림 받기').hidden,true);assert.equal(s.permissions,0);
 s.button('닫기').events.click();assert.equal(s.nodes.find(n=>n.className==='pwa-ios-tip').removed,true);
 const again=setup({ios:true,stored:Object.fromEntries(s.map)});assert(!again.nodes.some(n=>n.className==='pwa-ios-tip'));
});
test('installed iPhone app enables opt-in alerts, with no install hint or automatic permission',()=>{
 const s=setup({ios:true,standalone:true});assert(!s.nodes.some(n=>n.className==='pwa-ios-tip'));assert.equal(s.button('새 회차 알림 받기').hidden,false);assert.equal(s.permissions,0);
});
test('Android install button uses the browser prompt and hides once installed',async()=>{
 const s=setup();assert.equal(s.button('앱 설치').hidden,true);let prompted=0;
 s.events.beforeinstallprompt({preventDefault(){},prompt:async()=>prompted++,userChoice:Promise.resolve({outcome:'accepted'})});assert.equal(s.button('앱 설치').hidden,false);
 await s.button('앱 설치').events.click();assert.equal(prompted,1);assert.equal(s.button('앱 설치').hidden,true);
 s.events.appinstalled();assert.equal(s.button('앱 설치').hidden,true);
});
