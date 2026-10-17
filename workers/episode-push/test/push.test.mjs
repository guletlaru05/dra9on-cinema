import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFile} from 'node:fs/promises';
import {createWorker,sha,validEpisode,validEndpoint} from '../src/index.mjs';
import {notification} from '../notify.mjs';
import {buildPushPayload} from '@block65/webcrypto-web-push';
const schema=await readFile(new URL('../../tutorial-metrics/migrations/0004_episode_push.sql',import.meta.url),'utf8');
class D1{
 constructor(){this.sql=new DatabaseSync(':memory:');this.sql.exec('PRAGMA foreign_keys=ON');this.sql.exec(schema);}
 prepare(sql){const db=this;return {sql,values:[],bind(...values){return {...this,values};},async all(){return {results:db.sql.prepare(sql).all(...this.values)};}};}
 async batch(ops){this.sql.exec('BEGIN');try{const out=[];for(const op of ops)out.push(await op.all());this.sql.exec('COMMIT');return out;}catch(e){this.sql.exec('ROLLBACK');throw e;}}
}
const ORIGIN='https://dra9oncinema.com',secret='test-only-dispatch-secret',token='a'.repeat(64);
const pair=await crypto.subtle.generateKey({name:'ECDH',namedCurve:'P-256'},true,['deriveBits']);
const p256dh=Buffer.from(await crypto.subtle.exportKey('raw',pair.publicKey)).toString('base64url');
const auth=Buffer.alloc(16,8).toString('base64url');
function episode(id='newvideo001',when='2026-10-18T11:00:00Z',number=2){return {id,season:3,episode:number,publishedAt:when,image:'/assets/portfolio/'+id+'.jpg',locales:Object.fromEntries(['ko','en','ja','es'].map(lang=>[lang,{title:'FALL 707 '+lang,url:(lang==='ko'?'':'/'+lang)+'/watch/fall-707-s3-ep'+number+'/'}]))};}
async function setup(){let time=new Date('2026-10-18T10:00:00Z');const DB=new D1(),env={DB,DISPATCH_TOKEN_SHA256:await sha(secret),VAPID_PUBLIC_KEY:'public-key'},worker=createWorker({now:()=>time});
 const request=async(path,input={},headers={})=>worker.fetch(new Request('https://push.example'+path,{method:'POST',headers:{Origin:ORIGIN,'Content-Type':'application/json',...(['/sync','/batch','/ack'].includes(path)?{Authorization:'Bearer '+secret}:{}),...headers},body:JSON.stringify(input)}),env);
 const subscribe=(suffix='abc',lang='ko')=>request('/subscribe',{endpoint:'https://fcm.googleapis.com/fcm/send/'+suffix,keys:{p256dh,auth},lang,unsubscribeToken:token});
 const sync=episodes=>request('/sync',{episodes,revision:'a'.repeat(40),generatedAt:time.toISOString()});
 return {DB,env,worker,request,subscribe,sync,advance:hours=>{time=new Date(time.getTime()+hours*3600000);}};
}
test('origin, endpoint, curve, body and admin authentication are enforced',async()=>{
 const s=await setup();assert.equal((await s.subscribe()).status,200);
 assert.equal((await s.request('/subscribe',{endpoint:'http://127.0.0.1/internal'})).status,400);
 assert.equal((await s.request('/batch',{}, {Authorization:'Bearer wrong'})).status,401);
 assert.equal((await s.request('/batch',{}, {Origin:'https://evil.example'})).status,403);
 for(const url of ['https://fcm.googleapis.com.evil.example/fcm/send/token','https://web.push.apple.com:8443/x/abc','https://user:pass@fcm.googleapis.com/fcm/send/abc','https://127.0.0.1/a/b'])assert.equal(validEndpoint(url),false);
 assert.equal(validEndpoint('https://web.push.apple.com/QH/abc12345678'),true);
 const body={endpoint:'https://fcm.googleapis.com/fcm/send/invalidkey',keys:{p256dh:'A'.repeat(87),auth},lang:'ko',unsubscribeToken:token};assert.equal((await s.request('/subscribe',body)).status,400);
 assert.equal((await s.request('/subscribe',{...body,keys:{p256dh,auth},email:'owner@example.test'})).status,400);
});
test('initial feed is baseline only; new releases queue once and use subscription language',async()=>{
 const s=await setup();await s.subscribe('one','ja');
 const old=episode('oldvideo001','2026-10-17T10:00:00Z',1);
 assert.deepEqual(await (await s.sync([old])).json(),{initialized:true,newEpisodes:0});assert.equal((await (await s.request('/batch')).json()).deliveries.length,0);
 s.advance(2);const added=episode();assert.equal((await (await s.sync([old,added])).json()).newEpisodes,1);
 assert.equal((await (await s.sync([old,added])).json()).newEpisodes,0);
 const {deliveries}=await (await s.request('/batch')).json();assert.equal(deliveries.length,1);assert.equal(deliveries[0].lang,'ja');
 const note=notification(deliveries[0]);assert.equal(note.url,'/ja/watch/fall-707-s3-ep2/');assert.match(note.body,/第2話/);assert.equal(note.image,added.image);
 assert.equal((await (await s.request('/batch')).json()).deliveries.length,0,'leased deliveries cannot be double claimed');
 await s.request('/ack',{results:deliveries.map(r=>({event_id:r.event_id,sub_id:r.sub_id,lease:r.lease,status:201}))});
 s.advance(3);assert.equal((await (await s.request('/batch')).json()).deliveries.length,0,'sent deliveries are not replayed');
 await s.subscribe('late','es');assert.equal((await (await s.request('/batch')).json()).deliveries.length,0,'late subscriptions do not receive old releases');
});
test('unsubscribe requires its capability and removes queued deliveries; no PII columns',async()=>{
 const s=await setup();await s.subscribe();await s.sync([]);s.advance(2);await s.sync([episode()]);
 const endpoint='https://fcm.googleapis.com/fcm/send/abc';
 assert.equal((await s.request('/unsubscribe',{endpoint,unsubscribeToken:'b'.repeat(64)})).status,403);
 assert.equal((await s.request('/unsubscribe',{endpoint,unsubscribeToken:token})).status,200);
 assert.equal(s.DB.sql.prepare('SELECT COUNT(*) n FROM push_subscriptions').get().n,0);assert.equal(s.DB.sql.prepare('SELECT COUNT(*) n FROM push_deliveries').get().n,0);
 const names=s.DB.sql.prepare('PRAGMA table_info(push_subscriptions)').all().map(x=>x.name);assert.deepEqual(names,['id','endpoint','p256dh','auth','lang','delete_hash','created_at','updated_at']);
});
test('temporary delivery failure retries with bounded attempts; gone endpoints are deleted',async()=>{
 const s=await setup();await s.subscribe();await s.sync([]);s.advance(2);await s.sync([episode()]);
 const claim=async()=>(await (await s.request('/batch')).json()).deliveries;
 let batch=await claim();await s.request('/ack',{results:batch.map(r=>({event_id:r.event_id,sub_id:r.sub_id,lease:r.lease,status:500}))});assert.equal((await claim()).length,0);
 s.advance(2);batch=await claim();assert.equal(batch.length,1);await s.request('/ack',{results:batch.map(r=>({event_id:r.event_id,sub_id:r.sub_id,lease:r.lease,status:410}))});assert.equal(s.DB.sql.prepare('SELECT COUNT(*) n FROM push_subscriptions').get().n,0);
});
test('invalid or future episode routes cannot become outbound alerts',()=>{
 const item=episode();assert.equal(validEpisode(item,new Date('2026-10-18T12:00:00Z')),true);
 assert.equal(validEpisode(item,new Date('2026-10-17T12:00:00Z')),false);
 item.locales.en.url='https://evil.example/';assert.equal(validEpisode(item,new Date('2026-10-18T12:00:00Z')),false);
});
test('free storage cap rejects new subscriptions and never activates billing',async()=>{
 const s=await setup();const insert=s.DB.sql.prepare('INSERT INTO push_subscriptions VALUES(?,?,?,?,?,?,?,?)');for(let i=0;i<1000;i++)insert.run(String(i),'https://fcm.googleapis.com/fcm/send/'+i,p256dh,auth,'en',await sha(token),'2026-10-18T09:00:00Z','2026-10-18T09:00:00Z');assert.equal((await s.subscribe('overlimit')).status,429);
});
test('RFC 8291 payload decrypts back to the exact four-language notification, with VAPID',async()=>{
 const vapidPair=await crypto.subtle.generateKey({name:'ECDSA',namedCurve:'P-256'},true,['sign','verify']);const priv=await crypto.subtle.exportKey('jwk',vapidPair.privateKey);const pub=Buffer.from(await crypto.subtle.exportKey('raw',vapidPair.publicKey)).toString('base64url');
 const encoder=new TextEncoder(),concat=(...parts)=>Buffer.concat(parts.map(x=>Buffer.from(x)));
 async function hkdf(secret,salt,info,length){const key=await crypto.subtle.importKey('raw',secret,'HKDF',false,['deriveBits']);return new Uint8Array(await crypto.subtle.deriveBits({name:'HKDF',hash:'SHA-256',salt,info},key,length*8));}
 for(const lang of ['ko','en','ja','es']){
  const note=notification({episode:episode(),lang});const request=await buildPushPayload({data:note,options:{ttl:86400}},{endpoint:'https://web.push.apple.com/QH/test123456',keys:{p256dh,auth}},{subject:'https://dra9oncinema.com/',publicKey:pub,privateKey:priv.d});
  assert.equal(request.headers['content-encoding'],'aes128gcm');assert.match(request.headers.authorization,/^vapid t=/);assert.equal(request.body.length,4096);
  const bytes=request.body,salt=bytes.slice(0,16),serverRaw=bytes.slice(21,86),server=await crypto.subtle.importKey('raw',serverRaw,{name:'ECDH',namedCurve:'P-256'},false,[]);
  const shared=await crypto.subtle.deriveBits({name:'ECDH',public:server},pair.privateKey,256);const ikm=await hkdf(shared,Buffer.from(auth,'base64url'),concat(encoder.encode('WebPush: info\0'),Buffer.from(p256dh,'base64url'),serverRaw),32);
  const cek=await hkdf(ikm,salt,encoder.encode('Content-Encoding: aes128gcm\0'),16),nonce=await hkdf(ikm,salt,encoder.encode('Content-Encoding: nonce\0'),12);
  const key=await crypto.subtle.importKey('raw',cek,'AES-GCM',false,['decrypt']);const padded=new Uint8Array(await crypto.subtle.decrypt({name:'AES-GCM',iv:nonce},key,bytes.slice(86)));let end=padded.length-1;while(padded[end]===0)end--;assert.equal(padded[end],2);assert.deepEqual(JSON.parse(new TextDecoder().decode(padded.slice(0,end))),note);
 }
});
