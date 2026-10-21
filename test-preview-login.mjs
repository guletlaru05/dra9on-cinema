import test from 'node:test';import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';import vm from 'node:vm';
import authWorker,{handle} from './cloudflare/auth-proxy.mjs';
import {installPreviewLogin,PENDING,errorText,mobileBrowser} from './cloudflare/preview-login.mjs';
function fixture({nav={},pending=false,currentUser=null,result=null,blocked=false,popupError=null}={}){
 const nodes=new Map(['login','login-redirect','status'].map(id=>[id,{disabled:false,textContent:'',events:{},addEventListener(t,fn){this.events[t]=fn;}}]));
 const records=new Map(pending?[[PENDING,String(Date.now())]]:[]),messages=[],calls=[];
 const storage={getItem:k=>records.get(k),setItem:(k,v)=>{if(blocked)throw Error();records.set(k,v);},removeItem:k=>records.delete(k)};
 const auth={currentUser,authStateReady:async()=>{}};
 const login=installPreviewLogin({auth,GoogleAuthProvider:class{setCustomParameters(){}},signInWithPopup:()=>{calls.push('popup');return popupError?Promise.reject(popupError):Promise.resolve();},signInWithRedirect:()=>{calls.push('redirect');return Promise.resolve();},getRedirectResult:async()=>result,deadline:p=>p,document:{getElementById:id=>nodes.get(id)},window:{D9PreviewLibrary:{error:t=>messages.push(t)}},navigator:nav,storage});
 return {nodes,records,messages,calls,login};
}
test('iPhone uses same-window redirect; desktop popup is opened in click stack',async()=>{
 let f=fixture({nav:{userAgent:'iPhone'}});await f.nodes.get('login').events.click();assert.deepEqual(f.calls,['redirect']);assert.ok(f.records.has(PENDING));
 f=fixture();const p=f.nodes.get('login').events.click();assert.deepEqual(f.calls,['popup']);await p;
 assert.equal(mobileBrowser({platform:'MacIntel',maxTouchPoints:5}),true);
});
test('blocked storage, popup denied and empty redirect all have visible reasons',async()=>{
 let f=fixture({nav:{userAgent:'iPhone'},blocked:true});await f.nodes.get('login').events.click();assert.equal(f.calls.length,0);assert.match(f.messages.at(-1),/web-storage-unsupported/);
 f=fixture({popupError:{code:'auth/popup-blocked',message:'private detail'}});await f.nodes.get('login').events.click();assert.match(f.messages.at(-1),/팝업이 차단/);assert.equal(f.nodes.get('login').disabled,false);
 f=fixture({pending:true});await f.login.restore();assert.match(f.messages.at(-1),/redirect-empty/);assert.equal(f.records.has(PENDING),false);
 f=fixture({pending:true,currentUser:{}});await f.login.restore();assert.equal(f.messages.length,0);
 assert.ok(!errorText({code:'invalid token=private'}).includes('private'));
});
test('an unloaded login click starts preparation and timeout, not a dead button',()=>{
 const handlers={},nodes={login:{after(){}},'login-redirect':{}},feedback={setAttribute(){}};let connected=0,timeout;
 const connect={click(){connected++;}},document={getElementById:id=>nodes[id],createElement:()=>feedback,addEventListener:(t,f)=>handlers[t]=f,querySelector:()=>connect};
 const window={};vm.runInNewContext(readFileSync('cloudflare/login-bootstrap.js','utf8'),{location:{hostname:'dra9on-cinema.pages.dev'},document,window,sessionStorage:{getItem:()=>null},setTimeout:fn=>{timeout=fn;return 1;},clearTimeout(){}});
 handlers.click({target:{closest:()=>nodes.login},preventDefault(){},stopImmediatePropagation(){}});assert.equal(connected,1);assert.match(feedback.textContent,/준비/);
 timeout();assert.match(feedback.textContent,/module-not-ready/);window.D9PreviewLibrary.error('redirect failure');window.D9PreviewLibrary.ready();assert.equal(feedback.textContent,'redirect failure');
});
test('auth proxy has a fixed host/upstream and preserves query, never site credentials',async()=>{
 let seen;const request=new Request('https://dra9on-cinema.pages.dev/__/auth/iframe?apiKey=public&v=12',{headers:{Cookie:'private',Authorization:'Bearer private',Referer:'https://dra9on-cinema.pages.dev/library/'}});
 const response=await handle(request,{},async(url,options)=>{seen={url,options};return new Response('helper');});
 assert.equal(seen.url,'https://dra9on-cinema-stats.firebaseapp.com/__/auth/iframe?apiKey=public&v=12');assert.equal(seen.options.headers.has('cookie'),false);assert.equal(seen.options.headers.has('authorization'),false);assert.match(response.headers.get('cache-control'),/no-store/);
 assert.equal((await handle(new Request('https://other.pages.dev/__/auth/handler'),{})).status,403);
 assert.equal((await handle(new Request('https://dra9on-cinema.pages.dev/__/auth/handler',{method:'DELETE'}),{})).status,405);
 assert.equal((await handle(new Request('https://dra9on-cinema.pages.dev/actors/'),{ASSETS:{fetch:()=>new Response('static')}})).status,200);
});
test('Pages ExecutionContext does not replace the upstream fetch implementation',async()=>{
 const previous=globalThis.fetch;let fetched=false;
 try{globalThis.fetch=async()=>{fetched=true;return new Response('helper');};
  const response=await authWorker.fetch(new Request('https://dra9on-cinema.pages.dev/__/auth/iframe'),{},{waitUntil(){}});
  assert.equal(response.status,200);assert.equal(fetched,true);
 }finally{globalThis.fetch=previous;}
});
test('public Firebase initialization is served locally without another upstream request',async()=>{
 const response=await handle(new Request('https://dra9on-cinema.pages.dev/__/firebase/init.json'),{ASSETS:{fetch:async()=>new Response('{"projectId":"dra9on-cinema-stats"}')}},()=>{throw Error('No upstream for public init');});
 assert.equal(response.status,200);assert.equal((await response.json()).projectId,'dra9on-cinema-stats');assert.match(response.headers.get('cache-control'),/no-store/);
});
