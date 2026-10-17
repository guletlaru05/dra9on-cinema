/* Public aggregates; consenting browsers count once per Korean calendar day. */
(()=>{
  'use strict';
  if(!['dra9oncinema.com','www.dra9oncinema.com'].includes(location.hostname)
    ||/^\/(?:en\/)?library(?:\/|$)/.test(location.pathname))return;
  const widgets=[...document.querySelectorAll('[data-site-visitors]')];
  if(!widgets.length)return;
  const en=document.documentElement.lang==='en',t=(ko,eng)=>en?eng:ko;
  let visible=false,readStarted=false,recording=false,attemptedDay=null;
  const day=()=>Math.floor((Date.now()+32400000)/86400000);
  const allowed=()=>window.D9AnalyticsConsent?.get()==='granted';
  const text=(selector,value)=>widgets.forEach(node=>{const target=node.querySelector(selector);if(target)target.textContent=value;});
  function paint(value){
    if(!value)return;
    if(!Number.isSafeInteger(value.total)||!Number.isSafeInteger(value.today)||value.total<0||value.today<0||value.day!==day())throw new Error('visits/invalid-display');
    text('[data-visits-today]',value.today.toLocaleString(en?'en-US':'ko-KR'));
    text('[data-visits-total]',value.total.toLocaleString(en?'en-US':'ko-KR'));
    const date=new Date(value.startedAt);
    text('[data-visits-since]',Number.isFinite(date.getTime())?t('집계 시작 ','Counting since ')+new Intl.DateTimeFormat(en?'en-US':'ko-KR',{year:'numeric',month:'2-digit',day:'2-digit',timeZone:'Asia/Seoul'}).format(date):'');
    text('[data-visits-status]','');
  }
  function failed(){
    text('[data-visits-today]','—');text('[data-visits-total]','—');text('[data-visits-since]','');
    text('[data-visits-status]',t('집계를 잠시 불러올 수 없습니다.','Counts are temporarily unavailable.'));
  }
  async function service(){
    await window.D9LoadEngagement?.();
    const api=window.D9Engagement;
    if(!api?.visitTotals||!api?.recordSiteVisit)throw new Error('visits/service-unavailable');
    return api;
  }
  async function read(){
    if(readStarted)return;
    readStarted=true;
    try{paint(await(await service()).visitTotals());}catch{failed();}
  }
  async function record(){
    if(!allowed()||recording||attemptedDay===day())return;
    recording=true;attemptedDay=day();
    try{
      const api=await service();
      if(!allowed())return;
      paint(await api.recordSiteVisit());
    }catch{if(visible)failed();}finally{recording=false;}
  }
  if('IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>{
      if(!entries.some(entry=>entry.isIntersecting))return;
      visible=true;observer.disconnect();read();
    },{rootMargin:'120px'});
    widgets.forEach(node=>observer.observe(node));
  }else{visible=true;read();}
  window.addEventListener('d9:analytics-consent',event=>{
    if(event.detail?.value==='granted'){attemptedDay=null;record();}
  });
  // Also supports returning after KST midnight without polling or extra listeners.
  document.addEventListener('visibilitychange',()=>{
    if(document.visibilityState!=='visible')return;
    if(visible){readStarted=false;read();}
    record();
  });
  record();
})();
