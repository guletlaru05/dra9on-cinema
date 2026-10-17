const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const code=fs.readFileSync('site-assets/consent.js','utf8');
function setup(stored=null,host='dra9oncinema.com'){
 const listeners={},nodes=[],scripts=[],winEvents={},notices=[];let value=stored,reloads=0;
 function element(tag){const e={tag,children:[],events:{},hidden:false,setAttribute(){},append(...x){this.children.push(...x)},addEventListener(k,f){this.events[k]=f},focus(){}};nodes.push(e);return e;}
 const doc={documentElement:{lang:'en'},cookie:'_ga=old; _ga_TEST=old; essential=ok',referrer:'https://example.com/private?email=x',createElement:element,body:element('body'),head:{append:s=>scripts.push(s)},addEventListener:(k,f)=>listeners[k]=f};
 const win={addEventListener:(k,f)=>winEvents[k]=f,dispatchEvent:event=>{notices.push(event);winEvents[event.type]?.(event);return true;}};
 const context={window:win,document:doc,location:{hostname:host,origin:'https://'+host,pathname:'/en/',reload:()=>reloads++},localStorage:{getItem:()=>value,setItem:(k,v)=>value=v},URL,Date,CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}}};
 vm.runInNewContext(code,context);
 const button=text=>nodes.find(n=>n.tag==='button'&&n.textContent===text);
 return {win,scripts,doc,button,nodes,listeners,winEvents,notices,get stored(){return value},get reloads(){return reloads},events:()=>win.dataLayer.map(a=>Array.from(a))};
}
let a=setup();assert.equal(a.scripts.length,0);assert.equal(a.events()[0][1],'default');assert.equal(a.events()[0][2].analytics_storage,'denied');
assert.equal(a.win.D9AnalyticsConsent.get(),null);assert.equal(a.notices.length,1);assert.equal(a.notices[0].type,'d9:analytics-consent');assert.equal(a.notices[0].detail.value,null);
a.button('Decline analytics').events.click();assert.equal(a.scripts.length,0);assert.equal(JSON.parse(a.stored).value,'denied');
assert.equal(a.win.D9AnalyticsConsent.get(),'denied');assert.equal(a.notices.at(-1).detail.value,'denied');
a=setup();a.button('Allow analytics').events.click();assert.equal(a.scripts.length,1);assert.equal(a.events().find(e=>e[1]==='update')[2].ad_user_data,'denied');const cfg=a.events().find(e=>e[0]==='config')[2];assert.equal(cfg.page_location,'https://dra9oncinema.com/en/');assert.equal(cfg.page_referrer,'https://example.com');
assert.equal(a.win.D9AnalyticsConsent.get(),'granted');assert.equal(a.notices.at(-1).detail.value,'granted');assert.equal(a.nodes.find(n=>n.tag==='p').textContent.includes('Firebase'),true);
const link={href:'https://www.youtube.com/@dra9oncinema?sub_confirmation=1',closest:s=>s==='.hero'?{}:null};
a.listeners.click({target:{closest:s=>s==='a.subscribe-button'?link:null}});assert.equal(a.events().filter(e=>e[0]==='event'&&e[1]==='youtube_subscribe_click').length,1);
a.button('Decline analytics').events.click();assert.equal(a.win['ga-disable-G-TF7X8WSNGW'],true);assert.equal(a.reloads,1);
assert.equal(a.win.D9AnalyticsConsent.get(),'denied');assert.equal(a.notices.at(-1).detail.value,'denied');
a.listeners.click({target:{closest:s=>s==='a.subscribe-button'?link:null}});assert.equal(a.events().filter(e=>e[0]==='event').length,1);
const saved=v=>JSON.stringify({value:v,expires:Date.now()+10000});assert.equal(setup(saved('denied')).scripts.length,0);assert.equal(setup(saved('granted')).scripts.length,1);assert.equal(setup(JSON.stringify({value:'granted',expires:0})).scripts.length,0);assert.equal(setup('{bad').scripts.length,0);assert.equal(setup(saved('granted'),'127.0.0.1').scripts.length,0);
a=setup(saved('granted'));assert.equal(a.win.D9AnalyticsConsent.get(),'granted');assert.equal(a.notices[0].detail.value,'granted');a.winEvents.storage({key:'d9-analytics-consent-v1'});assert.equal(a.reloads,1);assert.equal(a.notices.length,2);
console.log('PASS: default/reject block tags; consent getter and initial/change events; grant enables analytics only; event gating; revocation; persistence; expiry; malformed state; local preview excluded; cross-tab reload.');
