/* No form content is put in analytics, URLs, browser storage or console logs. */
(() => {
 'use strict';
 const dialog=document.getElementById('casting-dialog');
 if(!dialog)return;
 const form=dialog.querySelector('[data-casting-form]');
 let trigger=null,widget=null,scriptPromise=null,busy=false,token='',received=false;
 const labels=form?JSON.parse(form.dataset.labels):{};
 const status=form?.querySelector('[data-casting-status]');
 const retry=form?.querySelector('[data-casting-retry]');
 const submit=form?.querySelector('[type=submit]');
 const report=(key,error=false)=>{if(status){status.textContent=labels[key];status.dataset.error=String(error);}};
 function script(){
  if(window.turnstile)return Promise.resolve();
  if(scriptPromise)return scriptPromise;
  scriptPromise=new Promise((resolve,reject)=>{
   const item=document.createElement('script');item.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';item.async=true;
   const timer=setTimeout(()=>{item.remove();scriptPromise=null;reject(new Error('timeout'));},12000);
   item.onload=()=>{clearTimeout(timer);if(window.turnstile)resolve();else {scriptPromise=null;reject(new Error('load'));}};
   item.onerror=()=>{clearTimeout(timer);item.remove();scriptPromise=null;reject(new Error('load'));};
   document.head.append(item);
  });
  return scriptPromise;
 }
 async function security(){
  if(!form || widget!==null)return;
  retry.hidden=true;report('challenge');
  try {
   await script();
   if(!dialog.open)return;
   widget=window.turnstile.render(form.querySelector('[data-casting-turnstile]'),{
    sitekey:form.dataset.sitekey,action:'casting',theme:'dark',size:'flexible',
    callback:value=>{token=value;if(!received)status.textContent='';retry.hidden=true;},
    'expired-callback':()=>{token='';report('challenge');},
    'timeout-callback':()=>{token='';report('challenge');retry.hidden=false;},
    'error-callback':()=>{token='';report('security-error',true);retry.hidden=false;}
   });
  }catch{report('security-error',true);retry.hidden=false;}
 }
 document.querySelectorAll('[data-casting-open]').forEach(button=>button.addEventListener('click',event=>{
  if(typeof dialog.showModal!=='function')return;
  event.preventDefault();trigger=button;dialog.showModal();security();
 }));
 dialog.querySelector('[data-casting-close]').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
 dialog.addEventListener('close',()=>{
  if(widget!==null){window.turnstile?.remove(widget);widget=null;}token='';trigger?.focus();
 });
 // Only an explicit casting link opens this form on arrival; ordinary profiles
 // still load no challenge until their inquiry button is clicked.
 if(window.location?.search&&new URLSearchParams(window.location.search).get('casting')==='1'&&typeof dialog.showModal==='function'){
  trigger=document.querySelector('[data-casting-open]');dialog.showModal();security();
 }
 if(!form)return;
 retry.addEventListener('click',()=>{
  if(widget!==null){window.turnstile?.remove(widget);widget=null;}token='';security();
 });
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(busy || !form.reportValidity())return;
  if(!token){report('challenge',true);form.querySelector('[data-casting-turnstile]').scrollIntoView({block:'nearest'});return;}
  busy=true;received=false;submit.disabled=true;form.setAttribute('aria-busy','true');report('processing');
  const fields=form.elements;
  const data={};for(const name of ['company','contact','email','actor','purpose','message','website'])data[name]=fields.namedItem(name).value;
  data.consent=fields.namedItem('consent').checked;data.token=token;
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),25000);
  try {
   const response=await fetch(form.dataset.endpoint,{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify(data),signal:controller.signal});
   const result=await response.json();
   if(!response.ok || result.ok!==true){report(response.status===429?'rate':result.error==='challenge'?'challenge':'error',true);}
   else{form.reset();received=true;report('success');}
  }catch{report('error',true);}
  finally {
   clearTimeout(timer);busy=false;submit.disabled=false;form.removeAttribute('aria-busy');token='';
   if(widget!==null)window.turnstile?.reset(widget);
  }
 });
})();
