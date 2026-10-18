/* Owner-only alerts. Firebase identity and source documents are verified server-side.
   No Firebase credentials/tokens, request bodies or delivery endpoints are logged. */
import {buildPushPayload} from '@block65/webcrypto-web-push';
import {SECURITY_HEADERS} from '../../security/headers.mjs';
const PROJECT='dra9on-cinema-stats',OWNER='guletlaru05@gmail.com';
const JWKS='https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com';
const ORIGINS=new Set(['https://dra9oncinema.com','https://www.dra9oncinema.com']);
const topics=new Set(['story','making','character','other']);
let keyCache=null,keyExpiry=0;
const bytes=s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-s.length%4)%4)),c=>c.charCodeAt(0));
const part=s=>JSON.parse(new TextDecoder().decode(bytes(s)));
export async function verifyFirebase(token,{fetcher=fetch,now=Date.now()}={}){
 if(typeof token!=='string'||token.length>16000)throw Error('auth');
 const pieces=token.split('.');if(pieces.length!==3)throw Error('auth');
 const [h,p]=pieces.slice(0,2).map(part),seconds=now/1000;
 if(h.alg!=='RS256'||typeof h.kid!=='string'||p.aud!==PROJECT||p.iss!=='https://securetoken.google.com/'+PROJECT||typeof p.sub!=='string'||!p.sub.length||p.sub.length>128||!Number.isFinite(p.exp)||p.exp<=seconds||!Number.isFinite(p.iat)||p.iat>seconds||!Number.isFinite(p.auth_time)||p.auth_time>seconds)throw Error('auth');
 if(!keyCache||keyExpiry<=now){const r=await fetcher(JWKS,{redirect:'error',signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('keys');const d=await r.json();if(!Array.isArray(d.keys))throw Error('keys');keyCache=d.keys;keyExpiry=now+Math.min(3600,Number((r.headers.get('Cache-Control')||'').match(/max-age=(\d+)/)?.[1]||300))*1000;}
 const jwk=keyCache.find(k=>k.kid===h.kid);if(!jwk)throw Error('auth');
 const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);
 if(!await crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,bytes(pieces[2]),new TextEncoder().encode(pieces[0]+'.'+pieces[1])))throw Error('auth');
 return p;
}
export const isOwner=p=>p?.email===OWNER&&p.email_verified===true&&p.firebase?.sign_in_provider==='google.com';
const hash=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))).map(n=>n.toString(16).padStart(2,'0')).join('');
const all=async(db,sql,...args)=>(await db.prepare(sql).bind(...args).all()).results;
const one=async(db,sql,...args)=>(await all(db,sql,...args))[0];
const iso=ms=>new Date(ms).toISOString();
export async function sourcePost(id,request,claims,fetcher=fetch){
 if(!/^[A-Za-z0-9_-]{1,128}$/.test(id||''))throw Error('id');
 const appCheck=request.headers.get('X-Firebase-AppCheck');if(!appCheck||appCheck.length>10000)throw Error('appcheck');
 const response=await fetcher('https://firestore.googleapis.com/v1/projects/'+PROJECT+'/databases/(default)/documents/communityPosts/'+id,{headers:{Authorization:request.headers.get('Authorization'),'X-Firebase-AppCheck':appCheck},redirect:'error',signal:AbortSignal.timeout(15000)});
 if(!response.ok)throw Error('source');const record=await response.json(),f=record.fields;
 const s=k=>f?.[k]?.stringValue;
 if(!f||(!isOwner(claims)&&s('authorUid')!==claims.sub)||!topics.has(s('topic'))||s('nickname')?.length<2||s('nickname')?.length>24||s('title')?.length<2||s('title')?.length>120||!Number.isFinite(Date.parse(f.createdAt?.timestampValue))||!Number.isFinite(Date.parse(f.updatedAt?.timestampValue)))throw Error('source');
 return {id,nickname:s('nickname'),title:s('title'),topic:s('topic'),createdAt:iso(Date.parse(f.createdAt.timestampValue)),updatedAt:iso(Date.parse(f.updatedAt.timestampValue)),answered:s('answer')?.length>=2?1:0,official:f.official?.booleanValue===true};
}
export async function ingest(db,p,date,{baseline=false}={}){
 if(p.official)return;
 const old=await one(db,'SELECT source_updated_at FROM board_post_mirror WHERE id=?',p.id);
 if(old&&old.source_updated_at>=p.updatedAt)return;
 let bucket=null;
 if(!old&&!baseline&&date-Date.parse(p.createdAt)<15*60000){
  // D1 serializes this single conditional statement: concurrent posts cannot
  // create competing open ten-minute windows.
  await all(db,"INSERT INTO board_notice_batches(id,kind,due_at,created_at) SELECT ?,'new',?,? WHERE NOT EXISTS(SELECT 1 FROM board_notice_batches WHERE kind='new' AND due_at>?)",'new-'+crypto.randomUUID(),iso(date+600000),iso(date),iso(date));
  bucket=(await one(db,"SELECT id FROM board_notice_batches WHERE kind='new' AND due_at>? ORDER BY created_at LIMIT 1",iso(date))).id;
 }
 await all(db,'INSERT INTO board_post_mirror(id,nickname,title,topic,created_at,source_updated_at,answered,bucket_id,seen_at) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET nickname=excluded.nickname,title=excluded.title,topic=excluded.topic,source_updated_at=excluded.source_updated_at,answered=excluded.answered,seen_at=excluded.seen_at WHERE excluded.source_updated_at>board_post_mirror.source_updated_at',p.id,p.nickname,p.title,p.topic,p.createdAt,p.updatedAt,p.answered,bucket,iso(date));
}
export async function boardFetch(request,env,deps={}){
 const origin=request.headers.get('Origin');if(!ORIGINS.has(origin))return new Response('',{status:403});
 const headers={...SECURITY_HEADERS,'Content-Type':'application/json','Cache-Control':'no-store','Access-Control-Allow-Origin':origin,'Vary':'Origin'};
 const reply=(v,status=200)=>new Response(JSON.stringify(v),{status,headers});
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers:{...headers,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Authorization, Content-Type, X-Firebase-AppCheck'}});
 if(request.method!=='POST')return reply({error:'Method not allowed'},405);
 if(!/^application\/json(?:;|$)/i.test(request.headers.get('Content-Type')||''))return reply({error:'JSON required'},400);
 const route=new URL(request.url).pathname;
 if(!['/owner-board/subscribe','/owner-board/unsubscribe','/owner-board/event','/owner-board/baseline','/owner-board/status','/owner-board/removed','/owner-board/digest'].includes(route))return reply({error:'Not found'},404);
 const token=(request.headers.get('Authorization')||'').match(/^Bearer (.+)$/)?.[1];let claims;
 try{claims=await (deps.verify||verifyFirebase)(token);}catch{return reply({error:'Firebase authentication required'},401);}
 if(route!=='/owner-board/event'&&!isOwner(claims))return reply({error:'Owner only'},403);
 if(env.OWNER_BOARD_ENABLED!=='true')return reply({error:'Board notification deployment pending'},503);
 if(env.WRITE_LIMITER&&!await env.WRITE_LIMITER.limit({key:'board-'+await hash(claims.sub)}).then(x=>x.success))return reply({error:'Rate limited'},429);
 let input;try{const reader=request.body?.getReader();if(!reader)throw Error();let size=0;const parts=[];try{while(true){const next=await reader.read();if(next.done)break;size+=next.value.byteLength;if(size>16000){await reader.cancel();throw Error();}parts.push(next.value);}}finally{reader.releaseLock();}input=JSON.parse(await new Blob(parts).text());if(!input||typeof input!=='object'||Array.isArray(input))throw Error();}catch{return reply({error:'Invalid body'},400);}
 const now=deps.now?.()||Date.now(),db=env.DB;
 try{
  if(route==='/owner-board/subscribe'){
   if(!await deps.validSubscription?.(input))return reply({error:'Invalid subscription'},400);
   if((await one(db,'SELECT COUNT(*) AS n FROM board_owner_subscriptions')).n>=10&&!await one(db,'SELECT id FROM board_owner_subscriptions WHERE id=?',await hash(input.endpoint)))return reply({error:'Owner device limit'},429);
   const id=await hash(input.endpoint);
   await all(db,'INSERT INTO board_owner_subscriptions(id,endpoint,p256dh,auth,lang,owner_uid,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET p256dh=excluded.p256dh,auth=excluded.auth,lang=excluded.lang,owner_uid=excluded.owner_uid,updated_at=excluded.updated_at',id,input.endpoint,input.keys.p256dh,input.keys.auth,input.lang,claims.sub,iso(now),iso(now));
   return reply({saved:true,ownerOnly:true});
  }
  if(route==='/owner-board/unsubscribe'){
   if(typeof input.endpoint!=='string'||input.endpoint.length>2048)return reply({error:'Invalid endpoint'},400);
   await all(db,'DELETE FROM board_owner_subscriptions WHERE id=? AND owner_uid=?',await hash(input.endpoint),claims.sub);return reply({removed:true});
  }
  if(route==='/owner-board/status'){
   const stats=await one(db,'SELECT COUNT(*) AS total,SUM(CASE WHEN answered=0 THEN 1 ELSE 0 END) AS unanswered FROM board_post_mirror');
   const meta=await one(db,"SELECT value FROM board_notify_metadata WHERE key='baseline_complete_at'");
   return reply({baselineComplete:!!meta,...stats});
  }
  if(route==='/owner-board/digest'){
   const day=new Date(now+9*3600000).toISOString().slice(0,10),start=Date.parse(day+'T00:00:00+09:00');
   const items=await all(db,'SELECT id,nickname,title,topic,answered FROM board_post_mirror WHERE created_at>=? AND created_at<? ORDER BY created_at LIMIT 501',iso(start),iso(start+86400000));
   const stats=await one(db,'SELECT COUNT(*) AS n FROM board_post_mirror WHERE answered=0');const baseline=!!await one(db,"SELECT value FROM board_notify_metadata WHERE key='baseline_complete_at'");
   return reply({day,items:items.slice(0,500),truncated:items.length>500,unanswered:stats.n,baselineComplete:baseline});
  }
  if(route==='/owner-board/removed'){
   if(!/^[A-Za-z0-9_-]{1,128}$/.test(input.id||''))return reply({error:'Invalid ID'},400);
   const check=request.headers.get('X-Firebase-AppCheck');if(!check)return reply({error:'Security verification required'},403);
   const response=await (deps.fetcher||fetch)('https://firestore.googleapis.com/v1/projects/'+PROJECT+'/databases/(default)/documents/communityPosts/'+input.id,{headers:{Authorization:request.headers.get('Authorization'),'X-Firebase-AppCheck':check},redirect:'error',signal:AbortSignal.timeout(15000)});
   if(response.status!==404)return reply({error:'The source does not confirm removal'},409);
   await all(db,'DELETE FROM board_post_mirror WHERE id=?',input.id);return reply({removed:true});
  }
  const ids=route==='/owner-board/baseline'?input.ids:[input.id];
  if(!Array.isArray(ids)||(!ids.length&&!(route==='/owner-board/baseline'&&input.complete===true))||ids.length>10||ids.some(id=>!/^[A-Za-z0-9_-]{1,128}$/.test(id||'')))return reply({error:'Invalid IDs'},400);
  // Never trust a client-supplied nickname/title/topic; re-read each real post.
  for(const id of ids)await ingest(db,await sourcePost(id,request,claims,deps.fetcher),now,{baseline:route==='/owner-board/baseline'});
  if(route==='/owner-board/baseline'&&input.complete===true)await all(db,"INSERT INTO board_notify_metadata(key,value) VALUES('baseline_complete_at',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",iso(now));
  return reply({saved:ids.length});
 }catch{return reply({error:'Source verification or notification storage unavailable'},503);}
}
export function boardNotification(rows,kind,lang,unanswered=0,baseline=true){
 const labels={ko:{new:n=>'새 글 '+n+'개',daily:'오늘의 팬 라운지',unanswered:n=>'미답변 '+n+'개',partial:'기존 글 초기 동기화 미완료'},en:{new:n=>n+' new posts',daily:'Today in the Fan Lounge',unanswered:n=>n+' unanswered',partial:'Initial board sync incomplete'},ja:{new:n=>'新着投稿'+n+'件',daily:'今日のファンラウンジ',unanswered:n=>'未回答'+n+'件',partial:'初期同期未完了'},es:{new:n=>n+' nuevas publicaciones',daily:'Hoy en el salón de fans',unanswered:n=>n+' sin responder',partial:'Sincronización inicial incompleta'}};
 const l=labels[lang]||labels.en,prefix=lang==='ko'?'':'/'+lang;
 const title=kind==='daily'?l.daily:rows.length===1?rows[0].nickname+' · '+rows[0].title:l.new(rows.length);
 const topic={ko:{story:'이야기',making:'제작',character:'캐릭터',other:'기타'},en:{story:'Story',making:'Filmmaking',character:'Character',other:'Other'},ja:{story:'物語',making:'制作',character:'登場人物',other:'その他'},es:{story:'Historia',making:'Creación',character:'Personaje',other:'Otros'}}[lang]||{};
 const list=rows.map(r=>r.nickname+' · '+r.title+' ['+(topic[r.topic]||r.topic)+']').join('\n');
 return {kind:'owner-board',id:kind+'-'+Date.now(),title,body:(kind==='daily'?l.unanswered(unanswered)+(baseline?'':' · '+l.partial)+'\n':'')+list,url:prefix+'/lounge/#'+(kind==='new'&&rows.length===1?'post-'+rows[0].id:'board'),lang};
}
export async function boardScheduled(env,deps={}){
 if(env.OWNER_BOARD_ENABLED!=='true'||!env.VAPID_PRIVATE_KEY||!env.VAPID_PUBLIC_KEY)return {configured:false};
 const now=deps.now?.()||Date.now(),db=env.DB,stamp=iso(now),kst=new Date(now+9*3600000),day=kst.toISOString().slice(0,10);
 const start=iso(Date.parse(day+'T00:00:00+09:00')),end=iso(Date.parse(day+'T00:00:00+09:00')+86400000);
 if(kst.getUTCHours()>=22)await all(db,"INSERT OR IGNORE INTO board_notice_batches(id,kind,due_at,created_at) VALUES(?,'daily',?,?)",'daily-'+day,stamp,stamp);
 await all(db,'DELETE FROM board_owner_subscriptions WHERE updated_at<?',iso(now-180*86400000));
 const batches=await all(db,'SELECT * FROM board_notice_batches WHERE due_at<=? AND created_at>=? ORDER BY due_at LIMIT 5',stamp,iso(now-86400000));
 let sent=0;
 for(const batch of batches){
  // Snapshot eligible owner devices once. Visitor episode subscriptions are never queried.
  await all(db,'INSERT OR IGNORE INTO board_notice_deliveries(event_id,sub_id) SELECT ?,id FROM board_owner_subscriptions WHERE created_at<=?',batch.id,batch.created_at);
  const deliveries=await all(db,"SELECT d.*,s.endpoint,s.p256dh,s.auth,s.lang FROM board_notice_deliveries d JOIN board_owner_subscriptions s ON s.id=d.sub_id WHERE d.event_id=? AND d.attempts<3 AND (d.state='pending' OR (d.state='leased' AND d.lease_at<?)) LIMIT 10",batch.id,iso(now-600000));
  const batchDay=batch.id.replace('daily-',''),dailyStart=batch.kind==='daily'?Date.parse(batchDay+'T00:00:00+09:00'):null;
  const items=await all(db,batch.kind==='daily'?'SELECT * FROM board_post_mirror WHERE created_at>=? AND created_at<? ORDER BY created_at':'SELECT * FROM board_post_mirror WHERE bucket_id=? ORDER BY created_at',...(batch.kind==='daily'?[iso(dailyStart),iso(dailyStart+86400000)]:[batch.id]));
  if(batch.kind==='new'&&!items.length){await all(db,"UPDATE board_notice_deliveries SET state='sent' WHERE event_id=?",batch.id);continue;}
  const pending=await one(db,'SELECT COUNT(*) AS n FROM board_post_mirror WHERE answered=0');const baseline=!!await one(db,"SELECT value FROM board_notify_metadata WHERE key='baseline_complete_at'");
  for(const row of deliveries){
   const lease=crypto.randomUUID();const changed=await all(db,"UPDATE board_notice_deliveries SET state='leased',attempts=attempts+1,lease=?,lease_at=? WHERE event_id=? AND sub_id=? AND attempts<3 AND (state='pending' OR (state='leased' AND lease_at<?)) RETURNING event_id",lease,stamp,batch.id,row.sub_id,iso(now-600000));if(!changed.length)continue;
   let status=0;
   try{const payload=boardNotification(items,batch.kind,row.lang,pending.n,baseline);payload.id=batch.id;if(new TextEncoder().encode(JSON.stringify(payload)).length>2800){payload.body=payload.body.slice(0,500)+'\n…';}const req=await (deps.buildPush||buildPushPayload)({data:JSON.stringify(payload),options:{ttl:3600}},{endpoint:row.endpoint,keys:{p256dh:row.p256dh,auth:row.auth}},{subject:'https://dra9oncinema.com/',publicKey:env.VAPID_PUBLIC_KEY,privateKey:env.VAPID_PRIVATE_KEY});const response=await (deps.fetcher||fetch)(row.endpoint,{...req,redirect:'error',signal:AbortSignal.timeout(15000)});status=response.status;await response.body?.cancel();}catch{}
   if(status===404||status===410)await all(db,'DELETE FROM board_owner_subscriptions WHERE id=?',row.sub_id);
   const state=status>=200&&status<300?'sent':status===0||status===429||status>=500?'pending':'failed';
   await all(db,'UPDATE board_notice_deliveries SET state=? WHERE event_id=? AND sub_id=? AND lease=?',state,batch.id,row.sub_id,lease);if(state==='sent')sent++;
  }
 }
 // Keep public post metadata only for operation; remove notification bookkeeping after 7 days.
 await all(db,'DELETE FROM board_notice_deliveries WHERE event_id IN (SELECT id FROM board_notice_batches WHERE created_at<?)',iso(now-7*86400000));
 await all(db,'DELETE FROM board_notice_batches WHERE created_at<?',iso(now-7*86400000));
 return {configured:true,sent};
}
