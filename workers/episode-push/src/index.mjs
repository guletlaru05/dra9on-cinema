/* No provider credentials or request bodies are logged. VAPID private key stays in GitHub Secrets. */
import {requestGate} from '../../security/rate-limit.mjs';
import {SECURITY_HEADERS} from '../../security/headers.mjs';
import {boardFetch,boardScheduled} from './board.mjs';
const ORIGINS=new Set(['https://dra9oncinema.com','https://www.dra9oncinema.com']);
export const LANGS=['ko','en','ja','es'];
export const sha=async text=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))).map(x=>x.toString(16).padStart(2,'0')).join('');
const decode=value=>Uint8Array.from(atob(value.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-value.length%4)%4)),c=>c.charCodeAt(0));
export function validEndpoint(value){try{const url=new URL(value);return typeof value==='string'&&value.length<=2048&&url.protocol==='https:'&&!url.username&&!url.password&&!url.port&&!url.search&&!url.hash&&['fcm.googleapis.com','updates.push.services.mozilla.com','push.services.mozilla.com','web.push.apple.com'].includes(url.hostname)&&url.pathname.length>8;}catch{return false;}}
export async function validSubscription(input){
 if(!input||Object.keys(input).some(k=>!['endpoint','keys','lang','unsubscribeToken'].includes(k))||!validEndpoint(input.endpoint)||!LANGS.includes(input.lang)||!/^[a-f0-9]{64}$/.test(input.unsubscribeToken||''))return false;
 if(!input.keys||Object.keys(input.keys).some(k=>!['p256dh','auth'].includes(k))||typeof input.keys.p256dh!=='string'||typeof input.keys.auth!=='string'||!/^[\w-]{87}$/.test(input.keys.p256dh)||!/^[\w-]{22}$/.test(input.keys.auth))return false;
 try{const key=decode(input.keys.p256dh);if(key.length!==65||key[0]!==4||decode(input.keys.auth).length!==16)return false;await crypto.subtle.importKey('raw',key,{name:'ECDH',namedCurve:'P-256'},false,[]);return true;}catch{return false;}
}
export function validEpisode(input,date){
 if(!input||!/^[A-Za-z0-9_-]{11}$/.test(input.id)||!Number.isInteger(input.season)||input.season<1||input.season>99||!Number.isInteger(input.episode)||input.episode<1||input.episode>999)return false;
 if(typeof input.publishedAt!=='string'||!Number.isFinite(Date.parse(input.publishedAt))||Date.parse(input.publishedAt)>date.getTime())return false;
 if(input.image!=='/assets/portfolio/'+input.id+'.jpg'||!input.locales||Object.keys(input.locales).length!==4)return false;
 return LANGS.every(lang=>{const row=input.locales[lang];return row&&typeof row.title==='string'&&row.title.length>0&&row.title.length<=200&&row.url===(lang==='ko'?'':'/'+lang)+'/watch/fall-707-s'+input.season+'-ep'+input.episode+'/';});
}
const headers=origin=>({...SECURITY_HEADERS,'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Vary':'Origin',...(origin?{'Access-Control-Allow-Origin':origin}:{})});
const answer=(body,status=200,origin=null)=>new Response(JSON.stringify(body),{status,headers:headers(origin)});
async function body(request){
 if(!/^application\/json(?:;|$)/i.test(request.headers.get('Content-Type')||''))throw Error('mime');
 const reader=request.body?.getReader();if(!reader)throw Error('body');let size=0;const parts=[];
 try{while(true){const next=await reader.read();if(next.done)break;size+=next.value.byteLength;if(size>150000){await reader.cancel();throw Error('size');}parts.push(next.value);}}finally{reader.releaseLock();}
 return JSON.parse(await new Blob(parts).text());
}
const rows=async(db,sql,...values)=>(await db.prepare(sql).bind(...values).all()).results;
const first=async(db,sql,...values)=>(await rows(db,sql,...values))[0];
export function createWorker(options={}){
 const now=options.now||(()=>new Date());
 return {async fetch(request,env){
  const url=new URL(request.url),givenOrigin=request.headers.get('Origin'),origin=ORIGINS.has(givenOrigin)?givenOrigin:null;
  if(givenOrigin&&!origin)return answer({error:'Origin not allowed.'},403);
  if(url.search)return answer({error:'No query strings.'},400,origin);
  if(url.pathname.startsWith('/owner-board/')){const gate=await requestGate(request,env,'owner-board',request.method==='POST',now());if(gate!==200)return answer({error:'Request protection denied.'},gate,origin);return boardFetch(request,env,{validSubscription});}
  const admin=['/sync','/batch','/ack'].includes(url.pathname);
  if(request.method==='OPTIONS')return origin&&!admin?new Response(null,{status:204,headers:{...headers(origin),'Access-Control-Allow-Methods':'GET, POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'}}):answer({error:'Not allowed.'},403);
  if(admin){const auth=request.headers.get('Authorization')||'';if(!auth.startsWith('Bearer ')||auth.length>300||!env.DISPATCH_TOKEN_SHA256||await sha(auth.slice(7))!==env.DISPATCH_TOKEN_SHA256)return answer({error:'Dispatcher authentication required.'},401);}
  else if(!origin&&url.pathname!=='/key')return answer({error:'Origin required.'},403);
  if(!admin){const gate=await requestGate(request,env,'push',request.method==='POST',now());if(gate!==200){const response=answer({error:gate===429?'Too many requests. Please retry shortly.':'Request protection unavailable.'},gate,origin);if(gate===429)response.headers.set('Retry-After','60');return response;}}
  if(url.pathname==='/key'&&request.method==='GET')return env.VAPID_PUBLIC_KEY?answer({publicKey:env.VAPID_PUBLIC_KEY},200,origin):answer({error:'Not configured.'},503,origin);
  if(!['/subscribe','/unsubscribe','/sync','/batch','/ack'].includes(url.pathname))return answer({error:'Not found.'},404,origin);
  if(request.method!=='POST')return answer({error:'Method not allowed.'},405,origin);
  let input;try{input=await body(request);}catch{return answer({error:'Invalid body.'},400,origin);}
  const date=now(),stamp=date.toISOString(),db=env.DB;
  try{
   if(url.pathname==='/subscribe'){
    if(!await validSubscription(input))return answer({error:'Invalid subscription.'},400,origin);
    const id=await sha(input.endpoint),hash=await sha(input.unsubscribeToken),old=await first(db,'SELECT delete_hash,p256dh,auth,lang,updated_at FROM push_subscriptions WHERE id=?',id);
    if(old&&old.delete_hash!==hash)return answer({error:'Subscription capability does not match.'},403,origin);
    if(old&&old.p256dh===input.keys.p256dh&&old.auth===input.keys.auth&&old.lang===input.lang&&Date.parse(old.updated_at)>date.getTime()-86400000)return answer({saved:true},200,origin);
    // Bound storage and write use on the existing free plan. Never auto-upgrade.
    if(!old&&(await first(db,'SELECT COUNT(*) AS n FROM push_subscriptions')).n>=1000)return answer({error:'Free subscription limit reached.'},429,origin);
    const budget=await rows(db,'INSERT INTO push_subscription_budget(day,writes) VALUES(?,1) ON CONFLICT(day) DO UPDATE SET writes=writes+1 WHERE writes<1500 RETURNING writes',stamp.slice(0,10));
    if(!budget.length)return answer({error:'Daily subscription limit reached.'},429,origin);
    const saved=await rows(db,'INSERT INTO push_subscriptions(id,endpoint,p256dh,auth,lang,delete_hash,created_at,updated_at) SELECT ?,?,?,?,?,?,?,? WHERE EXISTS(SELECT 1 FROM push_subscriptions WHERE id=?) OR (SELECT COUNT(*) FROM push_subscriptions)<1000 ON CONFLICT(id) DO UPDATE SET p256dh=excluded.p256dh,auth=excluded.auth,lang=excluded.lang,updated_at=excluded.updated_at WHERE push_subscriptions.delete_hash=excluded.delete_hash RETURNING id',id,input.endpoint,input.keys.p256dh,input.keys.auth,input.lang,hash,stamp,stamp,id);
    if(!saved.length)return answer({error:'Free subscription limit reached.'},429,origin);
    return answer({saved:true},200,origin);
   }
   if(url.pathname==='/unsubscribe'){
    if(!input||Object.keys(input).some(k=>!['endpoint','unsubscribeToken'].includes(k))||!validEndpoint(input.endpoint)||!/^[a-f0-9]{64}$/.test(input.unsubscribeToken||''))return answer({error:'Invalid unsubscribe request.'},400,origin);
    const id=await sha(input.endpoint),hash=await sha(input.unsubscribeToken),old=await first(db,'SELECT delete_hash FROM push_subscriptions WHERE id=?',id);
    if(old&&old.delete_hash!==hash)return answer({error:'Subscription capability does not match.'},403,origin);
    await rows(db,'DELETE FROM push_subscriptions WHERE id=? AND delete_hash=?',id,hash);return answer({removed:true},200,origin);
   }
   if(url.pathname==='/sync'){
    if(!input||Object.keys(input).some(k=>!['episodes','revision','generatedAt'].includes(k))||!Array.isArray(input.episodes)||input.episodes.length>200||!/^[a-f0-9]{40}$/.test(input.revision||'')||!Number.isFinite(Date.parse(input.generatedAt))||date-Date.parse(input.generatedAt)>3*86400000||Date.parse(input.generatedAt)>date.getTime()+300000||!input.episodes.every(e=>validEpisode(e,date))||new Set(input.episodes.map(e=>e.id)).size!==input.episodes.length)return answer({error:'Invalid episode feed.'},400);
    const bootstrap=await first(db,"SELECT value FROM push_metadata WHERE key='initialized_at'");
    const seen=new Set((await rows(db,'SELECT id FROM push_seen')).map(r=>r.id));
    const fresh=bootstrap?input.episodes.filter(e=>!seen.has(e.id)&&Date.parse(e.publishedAt)>=Math.max(Date.parse(bootstrap.value),date.getTime()-7*86400000)):[];
    const operations=[db.prepare("INSERT INTO push_metadata(key,value) VALUES('initialized_at',?) ON CONFLICT(key) DO NOTHING").bind(stamp),db.prepare('DELETE FROM push_subscriptions WHERE updated_at<?').bind(new Date(date-180*86400000).toISOString()),db.prepare('DELETE FROM push_events WHERE created_at<?').bind(new Date(date-7*86400000).toISOString()),db.prepare('DELETE FROM push_subscription_budget WHERE day<?').bind(new Date(date-7*86400000).toISOString().slice(0,10))];
    for(const e of input.episodes)if(!seen.has(e.id))operations.push(db.prepare('INSERT OR IGNORE INTO push_seen(id) VALUES(?)').bind(e.id));
    for(const e of fresh){operations.push(db.prepare('INSERT OR IGNORE INTO push_events(id,payload,created_at) VALUES(?,?,?)').bind(e.id,JSON.stringify(e),stamp));operations.push(db.prepare('INSERT OR IGNORE INTO push_deliveries(event_id,sub_id,next_attempt_at) SELECT ?,id,? FROM push_subscriptions WHERE created_at<=?').bind(e.id,stamp,stamp));}
    await db.batch(operations);return answer({initialized:!bootstrap,newEpisodes:fresh.length});
   }
   if(url.pathname==='/batch'){
    if(!input||Object.keys(input).length)return answer({error:'Empty object required.'},400);
    const stale=new Date(date-10*60000).toISOString(),cutoff=new Date(date-3*86400000).toISOString();
    const pending=await rows(db,"SELECT d.event_id,d.sub_id,s.endpoint,s.p256dh,s.auth,s.lang,e.payload FROM push_deliveries d JOIN push_subscriptions s ON d.sub_id=s.id JOIN push_events e ON e.id=d.event_id WHERE d.attempts<3 AND e.created_at>=? AND ((d.state='pending' AND d.next_attempt_at<=?) OR (d.state='leased' AND d.lease_at<?)) ORDER BY e.created_at LIMIT 20",cutoff,stamp,stale);
    const lease=crypto.randomUUID(),claimed=[];
    for(const row of pending){const changed=await rows(db,"UPDATE push_deliveries SET state='leased',attempts=attempts+1,lease=?,lease_at=? WHERE event_id=? AND sub_id=? AND attempts<3 AND ((state='pending' AND next_attempt_at<=?) OR (state='leased' AND lease_at<?)) RETURNING event_id",lease,stamp,row.event_id,row.sub_id,stamp,stale);if(changed.length)claimed.push({...row,lease,episode:JSON.parse(row.payload),payload:undefined});}
    return answer({deliveries:claimed});
   }
   if(url.pathname==='/ack'){
    if(!input||!Array.isArray(input.results)||input.results.length>50||Object.keys(input).some(k=>k!=='results')||input.results.some(r=>!r||!/^[A-Za-z0-9_-]{11}$/.test(r.event_id||'')||!/^[a-f0-9]{64}$/.test(r.sub_id||'')||!/^[a-f0-9-]{36}$/.test(r.lease||'')||!Number.isInteger(r.status)||r.status<0||r.status>599))return answer({error:'Invalid acknowledgement.'},400);
    const operations=[];
    for(const row of input.results){
     if(row.status===404||row.status===410)operations.push(db.prepare("DELETE FROM push_subscriptions WHERE id=? AND EXISTS(SELECT 1 FROM push_deliveries WHERE event_id=? AND sub_id=? AND lease=? AND state='leased')").bind(row.sub_id,row.event_id,row.sub_id,row.lease));
     else{const state=row.status>=200&&row.status<300?'sent':row.status===0||row.status===429||row.status>=500?'pending':'failed';operations.push(db.prepare("UPDATE push_deliveries SET state=?,next_attempt_at=? WHERE event_id=? AND sub_id=? AND lease=? AND state='leased'").bind(state,new Date(date.getTime()+3600000).toISOString(),row.event_id,row.sub_id,row.lease));}
    }
    if(operations.length)await db.batch(operations);return answer({acknowledged:input.results.length});
   }
  }catch{return answer({error:'Notification service unavailable.'},503,origin);}
 },async scheduled(event,env,ctx){ctx.waitUntil(boardScheduled(env));}};
}
export default createWorker();
