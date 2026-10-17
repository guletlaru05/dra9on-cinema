/* Behavioral checks against the actual client with a fake Firebase transport. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const engagement=fs.readFileSync('site-assets/engagement.js','utf8').replace(/\bimport\(/g,'importSDK(');
const widgetCode=fs.readFileSync('site-assets/visitors.js','utf8');
const flush=async()=>{for(let i=0;i<15;i++)await new Promise(setImmediate);};
function environment({consent='granted',host='dra9oncinema.com',path='/',now=Date.parse('2026-10-17T10:00:00Z')}={}){
  const records=new Map(),local=new Map(),session=new Map(),calls={auth:0,reads:0,transactions:0,writes:0,imports:0,check:0};
  const stamp=ms=>({toDate:()=>new Date(ms),toMillis:()=>ms});
  let currentTime=now,onToken,onRead,onFetch,fetchStatus;
  class Clock extends Date{constructor(...args){super(...(args.length?args:[currentTime]));}static now(){return currentTime;}}
  const store=m=>({getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)});
  const app={getApps:()=>[],initializeApp:()=>({})};
  const check={ReCaptchaEnterpriseProvider:class{},initializeAppCheck:()=>({}),getToken:async()=>{calls.check++;await onToken?.();return {token:'test'};}};
  const identity={currentUser:null,authStateReady:async()=>{}};
  const auth={getAuth:()=>identity,signInAnonymously:async()=>{calls.auth++;identity.currentUser={uid:'browser-a'};}};
  const api={getFirestore:()=>({}),doc:(_db,...parts)=>parts.join('/'),Timestamp:{fromMillis:stamp},serverTimestamp:()=>({serverTime:true}),
    runTransaction:async(_db,action)=>{
      calls.transactions++;const writes=[];
      const result=await action({get:async p=>{await onRead?.(p);return {data:()=>records.get(p)};},set:(p,v)=>writes.push([p,v])});
      for(const [p,v] of writes){records.set(p,Object.fromEntries(Object.entries(v).map(([k,x])=>[k,x?.serverTime?stamp(currentTime):x])));calls.writes++;}
      return result;
    }};
  const modules={'firebase-app.js':app,'firebase-app-check.js':check,'firebase-auth.js':auth,'firebase-firestore.js':api};
  const window={D9_ENGAGEMENT_CONFIG:{projectId:'test',appCheckSiteKey:'public-test'},D9AnalyticsConsent:{get:()=>consent},dispatchEvent(){}};
  const document={documentElement:{lang:'en'},querySelectorAll:()=>[]};
  const fetch=async url=>{
    calls.reads++;if(fetchStatus)return {status:fetchStatus,ok:false};
    const path=url.split('/documents/')[1];await onFetch?.(path);const record=records.get(path);
    if(!record)return {status:404,ok:false};
    const fields=Object.fromEntries(Object.entries(record).map(([k,v])=>[k,v?.toDate?{timestampValue:v.toDate().toISOString()}:{integerValue:String(v)}]));
    return {status:200,ok:true,json:async()=>({fields})};
  };
  const context={window,document,location:{hostname:host,pathname:path},Date:Clock,URL,Event:class{},Map,Promise,Number,JSON,Math,Error,
    sessionStorage:store(session),localStorage:store(local),fetch,IntersectionObserver:class{observe(){}unobserve(){}},
    importSDK:async url=>{calls.imports++;return modules[url.split('/').at(-1)];}};
  vm.runInNewContext(engagement,context);
  return {window,api:window.D9Engagement,records,local,session,calls,stamp,
    set consent(v){consent=v;},set now(v){currentTime=v;},get now(){return currentTime;},
    set onToken(f){onToken=f;},set onRead(f){onRead=f;},set onFetch(f){onFetch=f;},set fetchStatus(v){fetchStatus=v;}};
}
function widgetEnvironment({consent=null,host='dra9oncinema.com',path='/'}={}){
  const nodes=Object.fromEntries(['today','total','status','since'].map(k=>[k,{textContent:k==='today'||k==='total'?'—':''}]));
  const widget={querySelector:selector=>nodes[selector.match(/data-visits-(\w+)/)[1]]};
  const events={},docEvents={},calls={load:0,read:0,record:0};let observer,onLoad;
  const now=Date.parse('2026-10-17T10:00:00Z');
  const value={day:Math.floor((now+32400000)/86400000),total:23,today:4,startedAt:'2026-10-17T09:00:00Z'};
  class Clock extends Date{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}}
  const window={D9AnalyticsConsent:{get:()=>consent},D9Engagement:{visitTotals:async()=>{calls.read++;return value;},recordSiteVisit:async()=>{calls.record++;return {...value,today:5,total:24};}},
    D9LoadEngagement:async()=>{calls.load++;await onLoad?.();},addEventListener:(k,f)=>events[k]=f,
    IntersectionObserver:class{constructor(f){observer=f;}observe(){}disconnect(){}}};
  const document={documentElement:{lang:'en'},visibilityState:'visible',querySelectorAll:()=>[widget],addEventListener:(k,f)=>docEvents[k]=f};
  vm.runInNewContext(widgetCode,{window,document,location:{hostname:host,pathname:path},Date:Clock,Intl,Number,Math,Error,
    IntersectionObserver:window.IntersectionObserver});
  return {nodes,calls,events,docEvents,get consent(){return consent;},set consent(v){consent=v;},set onLoad(f){onLoad=f;},
    intersect:()=>observer?.([{isIntersecting:true}])};
}
(async()=>{
  let e=environment({consent:'denied'});
  assert.equal(await e.api.recordSiteVisit(),null);assert.equal(e.calls.imports,0);assert.equal(e.calls.auth,0);
  for(const options of [{host:'localhost'},{host:'127.0.0.1'},{path:'/library/'},{path:'/en/library/'}]){
    e=environment(options);assert.equal(await e.api.recordSiteVisit(),null);assert.equal(e.calls.imports,0);
  }
  e=environment({consent:null});e.records.set('siteVisits/summary',{total:9,startedAt:e.stamp(e.now-86400000)});
  let totals=await e.api.visitTotals();assert.equal(totals.today,0);assert.equal(totals.total,9);assert.equal(e.calls.auth,0);
  await e.api.visitTotals();assert.equal(e.calls.reads,2,'aggregate cache should prevent extra reads');
  e.fetchStatus=403;await assert.rejects(e.api.visitTotals({force:true}));
  e=environment({consent:null});
  const concurrentDay=Math.floor((e.now+32400000)/86400000),concurrentStart=e.stamp(e.now-1000);
  e.records.set('siteVisits/summary',{total:1,startedAt:concurrentStart});
  e.records.set('siteVisitDays/'+concurrentDay,{day:concurrentDay,visits:1});
  e.onFetch=path=>{if(path.startsWith('siteVisitDays/')){
    // Another browser commits between aggregate reads. Summary-first would
    // retain 1 while reading the new daily 2 and incorrectly reject the result.
    e.records.set('siteVisits/summary',{total:2,startedAt:concurrentStart});
    e.records.set('siteVisitDays/'+concurrentDay,{day:concurrentDay,visits:2});
  }};
  totals=await e.api.visitTotals();assert.equal(totals.total,2);assert.equal(totals.today,2);
  e=environment();await Promise.all([e.api.recordSiteVisit(),e.api.recordSiteVisit()]);
  assert.equal(e.calls.auth,1);assert.equal(e.calls.transactions,1);assert.equal(e.calls.writes,3);
  assert.equal(e.records.get('siteVisits/summary').total,1);assert.equal(e.records.get('siteVisitBrowsers/browser-a').day,Math.floor((e.now+32400000)/86400000));
  assert.equal((await e.api.visitTotals()).startedAt,new Date(e.now).toISOString());
  await e.api.recordSiteVisit();assert.equal(e.calls.transactions,1,'local marker skips repeat work');
  e.local.clear();await e.api.recordSiteVisit();assert.equal(e.calls.transactions,2);assert.equal(e.calls.writes,3,'server UID dedup remains authoritative after marker removal');
  const firstStart=e.records.get('siteVisits/summary').startedAt.toMillis();
  e.now+=86400000;await e.api.recordSiteVisit();assert.equal(e.calls.writes,6);assert.equal(e.records.get('siteVisits/summary').total,2);
  assert.equal(e.records.get('siteVisits/summary').startedAt.toMillis(),firstStart,'starting timestamp must be preserved');
  e=environment();e.onToken=()=>{e.consent='denied';};assert.equal(await e.api.recordSiteVisit(),null);assert.equal(e.calls.auth,0);assert.equal(e.calls.writes,0);
  e=environment();e.onRead=()=>{e.consent=null;};assert.equal(await e.api.recordSiteVisit(),null);assert.equal(e.calls.writes,0);
  e=environment();await assert.rejects(e.api.visitTotals(),/not-started/);
  e.records.set('siteVisits/summary',{total:-5,startedAt:e.stamp(e.now)});await assert.rejects(e.api.visitTotals(),/invalid-totals/);
  e=environment();let crossed=false;e.onRead=()=>{if(!crossed){crossed=true;e.now=Date.parse('2026-10-17T15:00:00Z');}};
  await e.api.recordSiteVisit();assert.equal(e.calls.transactions,2);assert.equal(e.calls.writes,3,'midnight race retries once without writing yesterday');
  let w=widgetEnvironment();await flush();assert.equal(w.calls.load,0,'footer reads stay lazy without consent');w.intersect();await flush();assert.equal(w.calls.read,1);assert.equal(w.calls.record,0);assert.equal(w.nodes.total.textContent,'23');
  w.consent='granted';w.events['d9:analytics-consent']({detail:{value:'granted'}});await flush();assert.equal(w.calls.record,1);assert.equal(w.nodes.total.textContent,'24');
  w=widgetEnvironment();w.onLoad=()=>{w.consent='denied';};w.consent='granted';w.events['d9:analytics-consent']({detail:{value:'granted'}});await flush();assert.equal(w.calls.record,0,'revocation while loading blocks the write');
  for(const options of [{host:'localhost'},{path:'/library/'}]){w=widgetEnvironment({...options,consent:'granted'});await flush();assert.equal(w.calls.load,0);}
  console.log('PASS: consent/expiry guards, preview/library exclusions, public reads without auth, 5-minute cache, missing/error totals, atomic three-document writes, UID/day dedup, cross-day increment, preserved server start date, concurrent calls, async revocation, KST midnight retry, footer lazy loading and consent events.');
})().catch(error=>{console.error(error);process.exitCode=1;});
