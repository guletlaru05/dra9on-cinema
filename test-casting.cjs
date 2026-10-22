const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const code=fs.readFileSync('site-assets/casting.js','utf8');
function element(){return {listeners:{},dataset:{},hidden:false,textContent:'',addEventListener(k,f){this.listeners[k]=f;},setAttribute(){},removeAttribute(){},focus(){this.focused=true;},scrollIntoView(){},};}
function setup(result={ok:true},http=200){
 const trigger=element(),dialog=element(),close=element(),form=element(),status=element(),retry=element(),submit=element(),mount=element();
 let options,network=0,scriptLoads=0,reset=0,removed=0;
 form.dataset={endpoint:'https://dra9on-casting.tutorial-metrics.workers.dev/inquiry',sitekey:'public-key',labels:JSON.stringify(Object.fromEntries(['processing','challenge','security-error','success','error','rate'].map(k=>[k,k])))};
 const values={company:'Test company',contact:'Test',email:'test@example.com',actor:'min-seoa',purpose:'other',message:'This is a test message.',website:'',consent:true};
 form.elements={namedItem(name){return {value:values[name],checked:values[name]};}};
 form.reportValidity=()=>true;form.reset=()=>{reset++;};
 form.querySelector=selector=>({'[data-casting-status]':status,'[data-casting-retry]':retry,'[type=submit]':submit,'[data-casting-turnstile]':mount}[selector]);
 dialog.querySelector=selector=>({'[data-casting-form]':form,'[data-casting-close]':close}[selector]);
 dialog.showModal=()=>{dialog.open=true;};dialog.close=()=>{dialog.open=false;dialog.listeners.close();};
 const widget={render(node,opts){options=opts;return 'widget';},reset(){},remove(){removed++;}};
 const window={};
 const document={getElementById:()=>dialog,querySelectorAll:()=>[trigger],head:{append(item){scriptLoads++;window.turnstile=widget;queueMicrotask(()=>item.onload());}},createElement(){return {remove(){}};}};
 const context={document,window,setTimeout,clearTimeout,AbortController,fetch:async(url,args)=>{network++;assert.equal(url,form.dataset.endpoint);assert.equal(args.credentials,'omit');assert.equal(JSON.parse(args.body).actor,'min-seoa');return {ok:http===200,status:http,json:async()=>result};}};
 vm.runInNewContext(code,context);
 return {trigger,dialog,form,status,retry,submit,close,values,get network(){return network;},get scripts(){return scriptLoads;},get reset(){return reset;},get removed(){return removed;},async open(){trigger.listeners.click({preventDefault(){}});await new Promise(resolve=>setImmediate(resolve));},verify(){options.callback('valid-token');},async send(){await form.listeners.submit({preventDefault(){}});},widgetOptions:()=>options};
}
test('Turnstile is loaded only after an explicit form open and retains actor selection',async()=>{const s=setup();assert.equal(s.scripts,0);assert.equal(s.network,0);await s.open();assert.equal(s.scripts,1);assert.equal(s.widgetOptions().action,'casting');assert.equal(s.values.actor,'min-seoa');});
test('missing security token never sends; accepted delivery reports success only once and closes accessibly',async()=>{const s=setup();await s.open();await s.send();assert.equal(s.network,0);assert.equal(s.status.textContent,'challenge');s.verify();await s.send();assert.equal(s.network,1);assert.equal(s.reset,1);assert.equal(s.status.textContent,'success');assert.equal(s.submit.disabled,false);s.verify();assert.equal(s.status.textContent,'success');s.close.listeners.click();assert.equal(s.removed,1);assert.equal(s.trigger.focused,true);});
test('failed and rate-limited submissions retain entries and show a visible reason',async()=>{for(const status of [502,429]){const s=setup({ok:false,error:'delivery'},status);await s.open();s.verify();await s.send();assert.equal(s.reset,0);assert.equal(s.values.message,'This is a test message.');assert.equal(s.status.textContent,status===429?'rate':'error');assert.equal(s.status.dataset.error,'true');}});
test('security load errors have a retry without submitting or clearing entries',async()=>{const s=setup();await s.open();s.widgetOptions()['error-callback']();assert.equal(s.status.textContent,'security-error');assert.equal(s.retry.hidden,false);assert.equal(s.network,0);assert.equal(s.reset,0);});
