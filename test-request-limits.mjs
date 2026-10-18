import {test} from 'node:test';
import assert from 'node:assert/strict';
import {requestGate} from './workers/security/rate-limit.mjs';
import {createWorker as metrics} from './workers/tutorial-metrics/src/index.mjs';
import {createWorker as push} from './workers/episode-push/src/index.mjs';
const date=new Date('2026-10-18T00:00:00Z');
const req=(path,method='GET')=>new Request('https://example.test'+path,{method,headers:{Origin:'https://dra9oncinema.com','CF-Connecting-IP':'192.0.2.8','Content-Type':'application/json'},...(method==='POST'?{body:'{}'}:{})});
test('blocked clients never reach storage, private readers, or subscription parsing',async()=>{
 const env={REQUEST_LIMITER:{limit:async()=>({success:false})},WRITE_LIMITER:{limit:async()=>{throw Error('must not call');}},DB:new Proxy({},{get(){throw Error('storage must not be touched');}})};
 for(const [worker,path,method] of [[metrics({}),'/event','POST'],[metrics({}),'/summary','GET'],[metrics({}),'/private/collect','POST'],[push(),'/subscribe','POST'],[push(),'/unsubscribe','POST'],[push(),'/key','GET']]){
  const r=await worker.fetch(req(path,method),env);assert.equal(r.status,429,path);assert.equal(r.headers.get('Retry-After'),'60');assert.equal(r.headers.get('Cache-Control'),'no-store');assert.equal(r.headers.get('Access-Control-Allow-Origin'),'https://dra9oncinema.com');
  assert.equal(r.headers.get('X-Frame-Options'),'DENY');assert.ok(r.headers.get('Strict-Transport-Security'));assert.match(r.headers.get('Content-Security-Policy'),/frame-ancestors 'none'/);
 }
});
test('missing or failed bindings fail closed, writes have their own tighter budget',async()=>{
 assert.equal(await requestGate(req('/'),{},'metrics',false,date),503);
 assert.equal(await requestGate(req('/'),{REQUEST_LIMITER:{limit:async()=>{throw Error('offline');}}},'metrics',false,date),503);
 assert.equal(await requestGate(req('/'),{REQUEST_LIMITER:{limit:async()=>({success:true})},WRITE_LIMITER:{limit:async()=>({success:false})}},'metrics',true,date),429);
});
test('security key rotates hourly, excludes raw address, and ignores spoofed forwarding headers',async()=>{
 const keys=[],env={REQUEST_LIMITER:{limit:async input=>{keys.push(input.key);return {success:true};}}};
 const a=req('/summary'),b=req('/weekly');b.headers.set('X-Forwarded-For','198.51.100.9');
 assert.equal(await requestGate(a,env,'metrics',false,date),200);await requestGate(b,env,'metrics',false,date);
 assert.equal(keys[0],keys[1]);assert.match(keys[0],/^[a-f0-9]{64}$/);assert.ok(!keys[0].includes('192.0.2.8'));
 await requestGate(a,env,'metrics',false,new Date(date.getTime()+3600000));assert.notEqual(keys[0],keys[2]);
 await requestGate(a,env,'push',false,date);assert.notEqual(keys[0],keys[3]);
});
test('a rate-limit binding cannot replace dispatcher authentication',async()=>{
 const r=await push().fetch(req('/batch','POST'),{});assert.equal(r.status,401);
});
