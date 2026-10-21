import {test} from 'node:test';
import assert from 'node:assert/strict';
import {main,readNotificationFeed} from '../notify.mjs';
const feed={revision:'a'.repeat(40),generatedAt:new Date().toISOString(),episodes:[{id:'newvideo001',season:3,episode:2,publishedAt:'2026-10-18T00:00:00Z',image:'/assets/portfolio/newvideo001.jpg',locales:Object.fromEntries(['ko','en','ja','es'].map(lang=>[lang,{title:'FALL 707',url:(lang==='ko'?'':'/'+lang)+'/watch/fall-707-s3-ep2/'}]))}]};
test('preview dry run performs one read and cannot dispatch or require secrets',async()=>{
 const calls=[];await main({PUSH_DRY_RUN:'true',PUSH_SITE_ORIGIN:'https://dra9on-cinema.pages.dev',EXPECTED_REVISION:feed.revision},async(url,options)=>{calls.push({url,options});return Response.json(feed);});
 assert.equal(calls.length,1);assert.equal(calls[0].options.method,undefined);assert.ok(calls[0].url.startsWith('https://dra9on-cinema.pages.dev/pwa/episodes.json?'));
 assert.equal(calls[0].options.headers,undefined);
});
test('preview cannot be a real dispatch source; wrong revisions stop before dispatch',async()=>{
 let reads=0;const fake=async()=>{reads++;return Response.json(feed);};
 await assert.rejects(main({PUSH_SITE_ORIGIN:'https://dra9on-cinema.pages.dev'},fake),/Unapproved/);assert.equal(reads,0);
 await assert.rejects(main({PUSH_DRY_RUN:'true',EXPECTED_REVISION:'b'.repeat(40)},fake),/revision/);assert.equal(reads,1);
 await assert.rejects(readNotificationFeed({PUSH_DRY_RUN:'true',PUSH_SITE_ORIGIN:'https://evil.example'},fake),/Unapproved/);
});
