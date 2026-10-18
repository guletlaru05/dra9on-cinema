import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFile} from 'node:fs/promises';
import {verifyFirebase,isOwner,sourcePost,ingest,boardFetch,boardScheduled,boardNotification} from '../src/board.mjs';
const schema=await readFile(new URL('../../tutorial-metrics/migrations/0005_owner_board.sql',import.meta.url),'utf8');
class D1{constructor(){this.sql=new DatabaseSync(':memory:');this.sql.exec(schema);}prepare(sql){const db=this;return {values:[],bind(...values){return {...this,values};},async all(){return {results:db.sql.prepare(sql).all(...this.values)};}};}}
const OWNER={sub:'real-owner-uid',email:'guletlaru05@gmail.com',email_verified:true,firebase:{sign_in_provider:'google.com'}},VISITOR={sub:'visitor-uid',firebase:{sign_in_provider:'anonymous'}};
const start=Date.parse('2026-10-18T12:40:00Z');
function post(id,time=start,answered=0){return {id,nickname:'팬',title:'캐릭터 질문 '+id,topic:'character',createdAt:new Date(time).toISOString(),updatedAt:new Date(time).toISOString(),answered,official:false};}
function request(route,input={},headers={}){return new Request('https://push.example/owner-board/'+route,{method:'POST',headers:{Origin:'https://dra9oncinema.com',Authorization:'Bearer test-fixture','Content-Type':'application/json','X-Firebase-AppCheck':'fixture',...headers},body:JSON.stringify(input)});}
test('owner verification requires verified Google identity, not a supplied email or nickname',async()=>{
 const DB=new D1(),env={DB,OWNER_BOARD_ENABLED:'true'};
 for(const claims of [VISITOR,{...OWNER,email_verified:false},{...OWNER,firebase:{sign_in_provider:'password'}},{...OWNER,email:'somebody@example.test'}]){assert.equal(isOwner(claims),false);assert.equal((await boardFetch(request('subscribe',{email:OWNER.email}),env,{verify:async()=>claims})).status,403);}
 assert.equal((await boardFetch(request('subscribe'),env,{verify:async()=>{throw Error();}})).status,401);
 assert.equal((await boardFetch(request('status',{}, {Origin:'https://evil.example'}),env,{verify:async()=>OWNER})).status,403);
 assert.equal(DB.sql.prepare('SELECT COUNT(*) n FROM board_owner_subscriptions').get().n,0);
});
test('real RSA signatures, audience, issuer and expiry are verified',async()=>{
 const pair=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',hash:'SHA-256',modulusLength:2048,publicExponent:new Uint8Array([1,0,1])},true,['sign','verify']);
 const jwk={...await crypto.subtle.exportKey('jwk',pair.publicKey),kid:'test-rsa-key'};const now=Date.now();
 const sign=async payload=>{const enc=v=>Buffer.from(JSON.stringify(v)).toString('base64url');const text=enc({alg:'RS256',kid:jwk.kid})+'.'+enc(payload);return text+'.'+Buffer.from(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',pair.privateKey,new TextEncoder().encode(text))).toString('base64url');};
 const p={...OWNER,aud:'dra9on-cinema-stats',iss:'https://securetoken.google.com/dra9on-cinema-stats',iat:Math.floor(now/1000)-10,exp:Math.floor(now/1000)+60,auth_time:Math.floor(now/1000)-20};
 const deps={now,fetcher:async()=>Response.json({keys:[jwk]})};assert.equal((await verifyFirebase(await sign(p),deps)).sub,OWNER.sub);
 for(const change of [{aud:'another-project'},{iss:'https://evil.example'},{exp:0},{iat:now},{auth_time:now}]){const invalid=await sign({...p,...change});await assert.rejects(()=>verifyFirebase(invalid,deps));}
 const token=await sign(p);await assert.rejects(()=>verifyFirebase(token.slice(0,-8)+'tampered',deps));
});
test('visitor cannot subscribe; owner endpoint is stored only in the separate owner table',async()=>{
 const DB=new D1(),env={DB,OWNER_BOARD_ENABLED:'true'},input={endpoint:'https://web.push.apple.com/real-owner',keys:{p256dh:'key',auth:'auth'},lang:'ko',unsubscribeToken:'a'.repeat(64)};
 assert.equal((await boardFetch(request('subscribe',input),env,{verify:async()=>OWNER,validSubscription:async()=>true,now:()=>start})).status,200);
 assert.equal(DB.sql.prepare('SELECT COUNT(*) n FROM board_owner_subscriptions').get().n,1);
 assert.equal((await boardFetch(request('unsubscribe',{endpoint:input.endpoint}),env,{verify:async()=>VISITOR})).status,403);
});
test('source event ignores forged client metadata and requires the real author',async()=>{
 const data={fields:Object.fromEntries(Object.entries({nickname:'원래 닉네임',title:'실제 제목',topic:'character',authorUid:VISITOR.sub,answer:''}).map(([k,v])=>[k,{stringValue:v}]))};data.fields.createdAt={timestampValue:new Date(start).toISOString()};data.fields.updatedAt=data.fields.createdAt;
 const source=await sourcePost('abc',request('event'),VISITOR,async()=>Response.json(data));assert.equal(source.title,'실제 제목');
 await assert.rejects(()=>sourcePost('abc',request('event'),{...VISITOR,sub:'different-user'},async()=>Response.json(data)));
 await assert.rejects(()=>sourcePost('abc',request('event'),OWNER,async()=>new Response('',{status:403})));
});
test('posts inside ten minutes share one window; duplicate events do not create extra alerts',async()=>{
 const DB=new D1();await ingest(DB,post('one'),start);await ingest(DB,post('two',start+9*60000),start+9*60000);await ingest(DB,post('one'),start+9*60000);
 assert.equal(DB.sql.prepare('SELECT COUNT(*) n FROM board_notice_batches').get().n,1);assert.equal(DB.sql.prepare('SELECT COUNT(DISTINCT bucket_id) n FROM board_post_mirror').get().n,1);
 await ingest(DB,post('three',start+11*60000),start+11*60000);assert.equal(DB.sql.prepare('SELECT COUNT(*) n FROM board_notice_batches').get().n,2);
});
test('delivery uses only owner devices, batches once, and daily summary is at 22:00 KST',async()=>{
 const DB=new D1(),sent=[];DB.sql.exec("CREATE TABLE push_subscriptions(id TEXT,endpoint TEXT);INSERT INTO push_subscriptions VALUES('visitor','https://web.push.apple.com/visitor');");
 DB.sql.prepare('INSERT INTO board_owner_subscriptions VALUES(?,?,?,?,?,?,?,?)').run('owner','https://web.push.apple.com/owner','key','auth','ko',OWNER.sub,new Date(start-60000).toISOString(),new Date(start).toISOString());
 const env={DB,OWNER_BOARD_ENABLED:'true',VAPID_PRIVATE_KEY:'test',VAPID_PUBLIC_KEY:'test'};
 const deps={now:()=>start+11*60000,buildPush:async message=>({method:'POST',body:message.data}),fetcher:async(url,req)=>{sent.push({url,data:JSON.parse(req.body)});return new Response('',{status:201});}};
 await ingest(DB,post('one'),start);await ingest(DB,post('two',start+120000),start+120000);
 await boardScheduled(env,deps);assert.equal(sent.length,1);assert.equal(sent[0].url,'https://web.push.apple.com/owner');assert.equal(sent[0].data.title,'새 글 2개');
 await boardScheduled(env,deps);assert.equal(sent.length,1);
 await boardScheduled(env,{...deps,now:()=>Date.parse('2026-10-18T12:59:00Z')});assert.equal(sent.length,1);
 await boardScheduled(env,{...deps,now:()=>Date.parse('2026-10-18T13:00:00Z')});assert.equal(sent.length,2);assert.match(sent[1].data.body,/미답변 2개/);assert.match(sent[1].data.body,/초기 동기화 미완료/);
 await boardScheduled(env,{...deps,now:()=>Date.parse('2026-10-18T13:01:00Z')});assert.equal(sent.length,2);
});
test('notification links target the original post and language; daily summaries target the board',()=>{
 assert.equal(boardNotification([post('abc')],'new','ja').url,'/ja/lounge/#post-abc');
 assert.equal(boardNotification([post('abc'),post('def')],'new','es').url,'/es/lounge/#board');
 assert.match(boardNotification([],'daily','en',3,true).body,/3 unanswered/);
});
