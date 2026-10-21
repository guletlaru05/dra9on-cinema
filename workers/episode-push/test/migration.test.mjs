import {test} from 'node:test';
import assert from 'node:assert/strict';
import {main,readNotificationFeed} from '../notify.mjs';
import {createWorker as pushWorker} from '../src/index.mjs';
import {createWorker as metricsWorker} from '../../tutorial-metrics/src/index.mjs';
const feed={revision:'a'.repeat(40),generatedAt:new Date().toISOString(),episodes:[{id:'newvideo001',season:3,episode:2,publishedAt:'2026-10-18T00:00:00Z',image:'/assets/portfolio/newvideo001.jpg',locales:Object.fromEntries(['ko','en','ja','es'].map(lang=>[lang,{title:'FALL 707',url:(lang==='ko'?'':'/'+lang)+'/watch/fall-707-s3-ep2/'}]))}]};
test('canonical dry run performs one read and cannot dispatch or require secrets',async()=>{
 const calls=[];await main({PUSH_DRY_RUN:'true',PUSH_SITE_ORIGIN:'https://dra9oncinema.com',EXPECTED_REVISION:feed.revision},async(url,options)=>{calls.push({url,options});return Response.json(feed);});
 assert.equal(calls.length,1);assert.equal(calls[0].options.method,undefined);assert.ok(calls[0].url.startsWith('https://dra9oncinema.com/pwa/episodes.json?'));
 assert.deepEqual(calls[0].options.headers,{'User-Agent':'DRA9ON-deploy-check/1.0','Accept':'application/json'});
});
test('preview cannot be a real dispatch source; wrong revisions stop before dispatch',async()=>{
 let reads=0;const fake=async()=>{reads++;return Response.json(feed);};
 await assert.rejects(main({PUSH_SITE_ORIGIN:'https://dra9on-cinema.pages.dev'},fake),/Unapproved/);
 await assert.rejects(main({PUSH_DRY_RUN:'true',PUSH_SITE_ORIGIN:'https://dra9on-cinema.pages.dev'},fake),/Unapproved/);assert.equal(reads,0);
 await assert.rejects(main({PUSH_DRY_RUN:'true',EXPECTED_REVISION:'b'.repeat(40)},fake),/revision/);assert.equal(reads,1);
 await assert.rejects(readNotificationFeed({PUSH_DRY_RUN:'true',PUSH_SITE_ORIGIN:'https://evil.example'},fake),/Unapproved/);
});
test('only canonical origin is trusted; private data still requires owner authentication',async()=>{
 const approved='https://dra9oncinema.com',env={VAPID_PUBLIC_KEY:'public-test-key',REQUEST_LIMITER:{limit:async()=>({success:true})},WRITE_LIMITER:{limit:async()=>({success:true})}};
 const key=await pushWorker().fetch(new Request('https://push.example/key',{headers:{Origin:approved}}),env);
 assert.equal(key.status,200);assert.equal(key.headers.get('Access-Control-Allow-Origin'),approved);
 const locked=await metricsWorker().fetch(new Request('https://metrics.example/private/visits',{headers:{Origin:approved}}),env);
 assert.equal(locked.status,401);assert.equal(locked.headers.get('Access-Control-Allow-Origin'),approved);
 for(const origin of ['https://dra9on-cinema.pages.dev','https://another.pages.dev','https://evil.dra9on-cinema.pages.dev','https://dra9on-cinema.pages.dev.evil.example']){
  assert.equal((await pushWorker().fetch(new Request('https://push.example/key',{headers:{Origin:origin}}),env)).status,403);
  assert.equal((await metricsWorker().fetch(new Request('https://metrics.example/private/visits',{headers:{Origin:origin}}),env)).status,403);
 }
});

test('public feed denial gives only the HTTP status, never provider body',async()=>{
 await assert.rejects(readNotificationFeed({PUSH_DRY_RUN:'true'},async()=>new Response('private diagnostic body',{status:403})),/^Error: Published episode feed unavailable \(HTTP 403\)\.$/);
});

test('validated canonical snapshot avoids a second bot-challenged HTTP read and rejects stale revisions',async()=>{
 let calls=0;const never=async()=>{calls++;throw Error('unexpected HTTP read');};
 const env={PUSH_VERIFIED_FEED_FILE:'true',EXPECTED_REVISION:feed.revision};
 assert.equal((await readNotificationFeed(env,never,async()=>JSON.stringify(feed))).revision,feed.revision);
 assert.equal(calls,0);
 await assert.rejects(readNotificationFeed({...env,EXPECTED_REVISION:'b'.repeat(40)},never,async()=>JSON.stringify(feed)),/revision/);
});
