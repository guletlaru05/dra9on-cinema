import test from 'node:test';
import assert from 'node:assert/strict';
import {createLinkPreview} from './site-assets/library/link-preview.js';
import {recommendSettings,incompatibleModel} from './site-assets/library/scene-assist.js';
const url='https://www.threads.com/@sample/post/Example';
const record={title:'Example',body:'  original\n\nprompt  ',prompts:['  original\n\nprompt  '],author:'@sample'};
test('preview shares in-flight reads and save reuses complete source without another read',async()=>{
 let calls=0;const events=[];
 const preview=createLinkPreview({read:async()=>{calls++;return{status:'saved',record};},onUpdate:e=>events.push(e)});
 const [a,b]=await Promise.all([preview.load(url),preview.load(url)]);
 assert.equal(a,b);assert.equal(calls,1);assert.equal((await preview.load(url)).record.body,record.body);
 assert.equal(calls,1);assert.equal(events.at(-1).phase,'ready');assert.equal(events.at(-1).record.author,'@sample');
 await preview.load(url,{force:true});assert.equal(calls,2);
});
test('old URL and logout invalidate delayed responses; internal URLs are never read',async()=>{
 const events=[],resolvers=[];let calls=0;
 const preview=createLinkPreview({read:()=>{calls++;return new Promise(resolve=>resolvers.push(resolve));},onUpdate:e=>events.push(e)});
 const first=preview.load(url);await Promise.resolve();preview.select(url+'B');
 resolvers[0]({status:'saved',record});assert.equal(await first,null);assert.equal(events.at(-1).phase,'idle');
 const second=preview.load(url+'B');await Promise.resolve();preview.clear();resolvers[1]({status:'saved',record});assert.equal(await second,null);assert.equal(events.at(-1).phase,'idle');
 for(const target of ['http://example.com','https://127.0.0.1','https://user:password@example.com'])assert.equal(await preview.load(target),null);
 assert.equal(calls,2);
});
test('blocked and unavailable source cannot masquerade as a saved original',async()=>{
 for(const response of [{status:'failed',reason:'Login required'},{deferred:true,reason:'Quota'},{}]){
  const events=[];const preview=createLinkPreview({read:async()=>response,onUpdate:e=>events.push(e)});
  const result=await preview.load(url);assert.notEqual(events.at(-1).phase,'ready');assert.equal(result.record,undefined);
 }
});
test('scene suggestions separate media models, detect vertical delivery and relevant tags',()=>{
 const video=recommendSettings('비 오는 지하 주차장. 어둠에서 뒤돌아본다. 릴스 영상','영상');
 assert.equal(video.model,'Seedance 2.5');assert.equal(video.ratio,'9:16');assert.ok(video.tags.includes('조명'));assert.ok(video.tags.includes('카메라'));
 assert.equal(recommendSettings('텍스트가 들어가는 포스터','이미지').model,'GPT Image 2.5 (Higgsfield)');
 assert.equal(recommendSettings('시네마틱 조명','이미지').model,'Midjourney (ZCRE)');
 assert.ok(incompatibleModel('영상','Midjourney (ZCRE)'));assert.ok(!incompatibleModel('영상','Kling'));assert.ok(incompatibleModel('이미지','Seedance 2.5'));
});
