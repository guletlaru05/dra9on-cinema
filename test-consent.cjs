const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const code=fs.readFileSync('site-assets/consent.js','utf8');
const KEY='d9-external-media-choice-v1';
const saved=value=>JSON.stringify({value,expires:Date.now()+10000});
function setup({choice=null,lang='en',sources=[],modules=[],legacy={},base='',sessionState={},blocked=[],noAccess=false}={}){
 const nodes=[],requests=[],posterRequests=[],notices=[],cookieWrites=[],documentEvents={},windowEvents={};let reloads=0;
 function storage(initial={},kind){const map=new Map(Object.entries(initial));return {get length(){return map.size;},key:i=>[...map.keys()][i]??null,getItem:k=>{if(blocked.includes(kind))throw Error('Storage access denied');return map.get(k)??null;},setItem:(k,v)=>{if(blocked.includes(kind))throw Error('Storage quota or access denied');map.set(k,String(v));},removeItem:k=>{if(blocked.includes(kind))throw Error('Storage access denied');map.delete(k);},map};}
 const local=storage({...legacy,...(choice===null?{}:{[KEY]:choice})},'local'),session=storage({'d9-site-visits-v1-test':'old','unrelated-session':'keep',...sessionState},'session');
 function element(tag){
  const attrs=new Map(),e={tag,nodeType:1,children:[],events:{},hidden:false,disabled:false,title:'',className:'',parentElement:null,focused:false};nodes.push(e);
  e.classList={toggle:(name,on)=>{const values=new Set(e.className.split(' ').filter(Boolean));on?values.add(name):values.delete(name);e.className=[...values].join(' ');}};
  e.setAttribute=(k,v)=>{attrs.set(k,String(v));if(k==='src')(tag==='img'?posterRequests:requests).push(String(v));};e.getAttribute=k=>attrs.get(k)??null;e.removeAttribute=k=>attrs.delete(k);
  Object.defineProperty(e,'src',{get:()=>e.getAttribute('src')||'',set:v=>e.setAttribute('src',v)});
  e.append=(...items)=>items.forEach(item=>{item.parentElement=e;e.children.push(item);});e.prepend=(...items)=>items.reverse().forEach(item=>{item.parentElement=e;e.children.unshift(item);});
  e.before=item=>{const parent=e.parentElement;item.parentElement=parent;parent.children.splice(parent.children.indexOf(e),0,item);};
  e.after=item=>{const parent=e.parentElement;item.parentElement=parent;parent.children.splice(parent.children.indexOf(e)+1,0,item);};
  e.remove=()=>{const parent=e.parentElement;if(parent)parent.children.splice(parent.children.indexOf(e),1);e.parentElement=null;};
  e.addEventListener=(type,fn)=>{e.events[type]=fn;};e.focus=()=>{e.focused=true;};
  e.matches=selector=>selector==='iframe[data-external-src]'?e.tag==='iframe'&&attrs.has('data-external-src'):selector==='script[data-service-src]'?e.tag==='script'&&attrs.has('data-service-src'):selector==='main'?e.tag==='main':false;
  e.querySelectorAll=selector=>{const all=[];function walk(parent){parent.children.forEach(child=>{if(child.matches(selector))all.push(child);walk(child);});}walk(e);return all;};return e;
 }
 const body=element('body'),head=element('head'),main=element('main');main.id='main';body.append(main);
 const frames=sources.map(src=>{const frame=element('iframe');frame.setAttribute('data-external-src',src);frame.title='Example film';main.append(frame);return frame;});
 const serviceSources=modules.map(src=>{const script=element('script');script.type='module';script.setAttribute('data-service-src',src);head.append(script);return script;});
 const doc={documentElement:{lang},body,head,currentScript:{src:'https://dra9oncinema.com'+base+'/consent.js?v=test'},createElement:element,getElementById:id=>nodes.find(node=>node.id===id)||null,querySelector:selector=>selector==='main'?main:null,querySelectorAll:selector=>selector==='.privacy-controls a'?[]:[...body.querySelectorAll(selector),...head.querySelectorAll(selector)],addEventListener:(k,f)=>{documentEvents[k]=f;}};
 Object.defineProperty(doc,'cookie',{get:()=> '_ga=old; _ga_TEST=old; essential=ok; d9-consent=old',set:value=>cookieWrites.push(value)});
 const win={addEventListener:(k,f)=>{(windowEvents[k]??=[]).push(f);},dispatchEvent:event=>{notices.push(event);windowEvents[event.type]?.forEach(fn=>fn(event));return true;}};
 const context={window:win,document:doc,location:{hostname:'dra9oncinema.com',origin:'https://dra9oncinema.com',href:'https://dra9oncinema.com'+base+'/en/',reload:()=>reloads++},localStorage:local,sessionStorage:session,URL,Date,CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}}};
 if(noAccess)for(const name of ['localStorage','sessionStorage'])Object.defineProperty(context,name,{get(){throw Error('SecurityError');}});
 vm.runInNewContext(code,context);
 return {win,doc,nodes,requests,posterRequests,notices,cookieWrites,local,session,frames,serviceSources,documentEvents,windowEvents,get reloads(){return reloads;},button:text=>nodes.find(node=>node.tag==='button'&&node.textContent===text),play:service=>nodes.find(node=>node.className==='external-media-play'&&(node.getAttribute('aria-label')||'').includes(service)),banner:()=>nodes.find(node=>node.id==='consent-banner')};
}
const YT='https://www.youtube-nocookie.com/embed/sFw17ZPE42A?rel=0',IG='https://www.instagram.com/reel/DelRHYDunY-/embed/';
let a=setup({sources:[YT,IG],legacy:{'d9-analytics-consent-v1':saved('granted'),'d9-consent':'old','d9-site-visit-day-v1-test':'old','dra9on-portfolio-saved':'["keep"]'}});
assert.equal(a.requests.length,0);assert.equal(a.win.dataLayer,undefined);assert.equal(a.win.gtag,undefined);assert.equal(a.win.D9ExternalConsent.get(),null);assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);assert.equal(a.win.D9AnalyticsConsent.get(),'denied');assert.equal(a.banner().hidden,true);
const settingsOpener={focus(){this.focused=true;}};a.win.D9ExternalConsent.showSettings(settingsOpener);assert.equal(a.banner().hidden,false);assert.equal(a.button('Block').focused,true);
a.button('Close').events.click();assert.equal(a.banner().hidden,true);assert.equal(a.win.D9ExternalConsent.get(),null);assert.equal(a.requests.length,0);assert.equal(settingsOpener.focused,true);
a.win.D9ExternalConsent.showSettings(settingsOpener);let prevented=false;a.documentEvents.keydown({key:'Escape',preventDefault(){prevented=true;}});assert.equal(prevented,true);assert.equal(a.banner().hidden,true);assert.equal(a.requests.length,0);a.win.D9ExternalConsent.showSettings(settingsOpener);
assert.equal(a.local.getItem('d9-analytics-consent-v1'),null);assert.equal(a.local.getItem('d9-consent'),null);assert.equal(a.local.getItem('d9-site-visit-day-v1-test'),null);assert.equal(a.local.getItem('dra9on-portfolio-saved'),'["keep"]');assert.equal(a.session.getItem('d9-site-visits-v1-test'),null);assert.equal(a.session.getItem('unrelated-session'),'keep');assert(a.cookieWrites.every(value=>!value.startsWith('essential=')));
assert(a.frames.every(frame=>frame.hidden&&frame.getAttribute('src')===null));assert.equal(a.nodes.filter(node=>node.className.split(' ').includes('external-media-placeholder')).length,2);
assert(a.posterRequests.every(url=>url.startsWith('https://dra9oncinema.com/')));
a.button('Block').events.click();assert.equal(a.requests.length,0);assert.equal(a.win.D9ExternalConsent.get(),'denied');assert.equal(JSON.parse(a.local.getItem(KEY)).value,'denied');assert.equal(a.banner().hidden,true);assert.equal(settingsOpener.focused,true);
a.play('YouTube').events.click();assert.equal(a.win.D9ExternalConsent.canLoadMedia(),true);assert.equal(new URL(a.frames[0].getAttribute('src')).searchParams.get('autoplay'),'1');assert.equal(a.frames[1].getAttribute('src'),IG);assert.equal(a.win.D9AnalyticsConsent.get(),'denied');assert.equal(a.notices.filter(event=>event.type==='d9:analytics-consent').every(event=>event.detail.value==='denied'),true);
assert.equal(JSON.parse(a.local.getItem(KEY)).value,'granted');
const nextPage=setup({legacy:Object.fromEntries(a.local.map),sources:[YT]});assert.equal(nextPage.frames[0].getAttribute('src'),YT);assert.equal(nextPage.frames[0].hidden,false);
const twoFilms=setup({sources:[YT,'https://www.youtube-nocookie.com/embed/NV9PeKvKv7c?rel=0']});twoFilms.play('YouTube').events.click();assert.equal(new URL(twoFilms.frames[0].getAttribute('src')).searchParams.get('autoplay'),'1');assert.equal(new URL(twoFilms.frames[1].getAttribute('src')).searchParams.get('autoplay'),null);
const before=a.requests.length;a.win.D9ExternalConsent.prepare();assert.equal(a.requests.length,before);assert.equal(a.nodes.filter(node=>node.className.split(' ').includes('external-media-placeholder')).length,2);
a.win.D9ExternalConsent.denyMedia();assert.equal(a.reloads,1);assert(a.frames.every(frame=>frame.getAttribute('src')===null&&frame.hidden));
for(const choice of [saved('denied'),JSON.stringify({value:'granted',expires:0}),'{bad']){a=setup({choice,sources:[YT]});assert.equal(a.requests.length,0);assert.equal(a.banner().hidden,true);}
a=setup({choice:saved('granted'),sources:[YT]});assert.equal(a.requests.length,1);assert.equal(a.banner().hidden,true);
a.local.setItem(KEY,saved('denied'));a.windowEvents.storage.forEach(fn=>fn({key:KEY}));assert.equal(a.reloads,1);assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);
a.local.removeItem(KEY);a.windowEvents.storage.forEach(fn=>fn({key:KEY}));assert.equal(a.banner().hidden,true);assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);assert.equal(a.frames[0].getAttribute('src'),null);
a=setup({choice:saved('granted'),sources:['https://evil.example/embed/sFw17ZPE42A','https://www.instagram.com/reel/other/embed/','javascript:alert(1)']});assert.equal(a.requests.length,0);assert(a.frames.every(frame=>frame.hidden));
a=setup({choice:saved('granted'),sources:['https://www.youtube.com/embed/sFw17ZPE42A?rel=0']});assert.equal(a.frames[0].getAttribute('src'),YT);

// Quota/SecurityError: session fallback survives same-tab navigation; if all
// storage is unavailable, the current page still works without a prompt loop.
a=setup({sources:[YT],blocked:['local']});a.play('YouTube').events.click();assert.equal(JSON.parse(a.session.getItem(KEY)).value,'granted');
const fallbackPage=setup({sources:[YT],blocked:['local'],sessionState:Object.fromEntries(a.session.map)});assert.equal(fallbackPage.frames[0].getAttribute('src'),YT);
for(const options of [{blocked:['local','session']},{noAccess:true}]){
 const blocked=setup({...options,sources:[YT]});blocked.play('YouTube').events.click();assert.equal(blocked.win.D9ExternalConsent.canLoadMedia(),true);blocked.win.D9ExternalConsent.prepare();assert.equal(blocked.requests.length,1);
}

// Cross-tab withdrawal must clear this tab's session copy, including clear().
a=setup({choice:saved('granted'),sessionState:{[KEY]:saved('granted')},sources:[YT]});
a.windowEvents.storage.forEach(fn=>fn({key:KEY,newValue:saved('denied')}));assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);assert.equal(JSON.parse(a.session.getItem(KEY)).value,'denied');assert.equal(a.reloads,1);
a=setup({choice:saved('granted'),sessionState:{[KEY]:saved('granted')},sources:[YT]});a.windowEvents.storage.forEach(fn=>fn({key:null}));assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);assert.equal(a.session.getItem(KEY),null);

// Returning from BFCache rechecks expiry/revocation rather than retaining a
// stale in-memory grant. Privacy-policy withdrawal uses the same safe path.
a=setup({choice:saved('granted'),sources:[YT]});a.local.setItem(KEY,saved('denied'));a.windowEvents.pageshow.forEach(fn=>fn({persisted:true}));assert.equal(a.frames[0].getAttribute('src'),null);
a=setup({choice:saved('granted'),sources:[YT]});a.documentEvents.click({target:{closest:selector=>selector==='[data-external-media-revoke]'?{}:null},preventDefault(){}});assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);assert.equal(a.reloads,1);
for(const lang of ['ko','en','ja','es']){a=setup({lang,sources:[YT,IG]});assert(a.play('YouTube'));assert(a.play('Instagram'));assert.equal(a.nodes.filter(n=>n.className==='external-media-notice').length,2);}
a=setup({lang:'ko',modules:['/community.js?v=x','/library/library.js?v=x','https://evil.example/community.js','/other.js']});assert.equal(a.requests.length,0);assert.equal(a.nodes.filter(node=>node.className==='functional-service-gate').length,2);
a.button('게시판 불러오기').events.click();assert.equal(a.requests.length,1);assert.equal(a.requests[0],'https://dra9oncinema.com/community.js?v=x');assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);assert.equal(a.win.D9AnalyticsConsent.get(),'denied');
const active=a.nodes.find(node=>node.tag==='script'&&node.src==='https://dra9oncinema.com/community.js?v=x');assert.equal(active.type,'module');active.events.error();assert.equal(a.button('게시판 불러오기').disabled,false);a.button('게시판 불러오기').events.click();a.nodes.filter(node=>node.tag==='script'&&node.src).at(-1).events.load();assert.equal(a.button('게시판 불러오기').hidden,true);
a=setup({base:'/project',modules:['/project/community.js?v=x','/community.js?v=x']});assert.equal(a.nodes.filter(node=>node.className==='functional-service-gate').length,1);a.button('Load board').events.click();assert.equal(a.requests[0],'https://dra9oncinema.com/project/community.js?v=x');
// A remembered private-library connection restores only its auth module.
// It must not silently enable the board, external videos, or analytics.
a=setup({legacy:{'d9-library-reconnect-v1':'1'},modules:['/library/library.js?v=remember','/community.js?v=x'],sources:[YT,IG]});
assert.deepEqual(a.requests,['https://dra9oncinema.com/library/library.js?v=remember']);
assert.equal(a.win.D9ExternalConsent.canLoadMedia(),false);assert.equal(a.win.D9AnalyticsConsent.get(),'denied');
assert(a.frames.every(frame=>frame.getAttribute('src')===null));
a.win.D9ExternalConsent.prepare();assert.equal(a.requests.length,1);
a.nodes.find(node=>node.tag==='script'&&node.src.includes('library/library.js')).events.error();
assert.equal(a.button('Enable library sign-in').disabled,false);
a.button('Enable library sign-in').events.click();assert.equal(a.requests.length,2);
a=setup({legacy:{'d9-library-reconnect-v1':'invalid'},modules:['/library/library.js?v=x']});assert.equal(a.requests.length,0);
console.log('PASS: no analytics or pre-consent media requests; exact embed allowlist; original links; consent persistence/expiry/revocation; legacy-only cleanup; denied analytics compatibility; explicit protected-service loading; module retry and project base paths.');
