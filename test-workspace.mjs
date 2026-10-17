import test from 'node:test';
import assert from 'node:assert/strict';
import {emptyWorkspace,applyAction,searchReferences,compileDraft,publicUrl,validateWorkspace,exportWorkspace} from './site-assets/library/workspace-core.js';
import {packPrivatePayload,unpackPrivatePayload} from './site-assets/library/library-transport.js';
const at='2026-10-18T09:00:00.000Z';
test('reference priority excludes irrelevant owner articles; original prompts survive',()=>{
 const original='  first line\nsecond line\n\n정확한 대사: “멈춰.”  ';
 const docs=[{id:'a',title:'역광 얼굴',body:'역광',tags:['조명'],source_type:'내 메모',prompts:[original]},{id:'b',title:'빛과 명암',body:'역광',tags:['조명'],source_type:'내 튜토리얼',url:'https://dra9oncinema.com/tutorials/a/',prompts:[original]},{id:'c',title:'음악',body:'음악',tags:[],source_type:'내 튜토리얼'}];
 const found=searchReferences('역광 조명',docs);assert.deepEqual(found.map(d=>d.id),['b','a']);assert.equal(found[0].prompts[0],original);
 const draft=compileDraft({scene:'여자가 뒤돌아본다',kind:'영상',dialogue:'“거기 누구야?”'},found);assert.match(draft.prompt,/“거기 누구야？”|“거기 누구야\?”/);assert.equal(draft.references[0].title,'빛과 명암');assert.match(draft.mode,/AI API 미사용/);
 assert.equal(searchReferences('외계어xyz',docs).length,0);
});
test('saved full prompts, private gzip export and optimistic conflict protection',async()=>{
 const prompt='하나\n'.repeat(2500),record={id:'draft:1',title:'장면',scene:'골목',prompt,kind:'이미지',model:'모델',ratio:'16:9',references:[],createdAt:at,updatedAt:at};
 let state=applyAction(emptyWorkspace(),{type:'save-draft',record});
 const newer={...record,prompt:prompt+'수정',updatedAt:'2026-10-18T09:01:00.000Z'};
 state=applyAction(state,{type:'save-draft',record:newer,expectedUpdatedAt:at});
 assert.throws(()=>applyAction(state,{type:'save-draft',record,expectedUpdatedAt:at}),/다른 기기/);
 const value=JSON.stringify({version:1,items:[{title:'기존 비급서',prompt:'원본'}],workspace:state});
 assert.equal(await unpackPrivatePayload(await packPrivatePayload(value)),value);
 assert.equal(exportWorkspace(state).workspace.drafts[0].prompt,prompt+'수정');
});
test('only matching pending source IDs are updated and full source is retained',()=>{
 const row={id:'link:1',url:'https://dra9oncinema.com/tutorials/a/',note:'',status:'pending',title:'',category:'',reason:'',createdAt:at,updatedAt:at};
 const initial=applyAction(emptyWorkspace(),{type:'add-link',record:row});
 assert.throws(()=>applyAction(initial,{type:'add-link',record:{...row,id:'link:2'}}),/이미 수집함/);
 const record={title:'원문',url:row.url,author:'공개 계정',category:'프롬프트',body:'본문',prompts:['a\n\nb'],tags:['카메라'],models:[]};
 const result={schema:'dra9on-site-results-v1',results:[{id:row.id,url:row.url,status:'saved',record}]};
 const state=applyAction(initial,{type:'sync-results',report:result,at});assert.equal(state.collected[0].prompts[0],'a\n\nb');assert.equal(state.inbox[0].status,'saved');
 const wrong=structuredClone(result);wrong.results[0].url='https://example.com/';assert.equal(applyAction(initial,{type:'sync-results',report:wrong,at}).inbox[0].status,'pending');
 assert.deepEqual(applyAction(state,{type:'sync-results',report:result,at}),state);
 assert.equal(applyAction(state,{type:'delete-link',id:row.id}).collected.length,0);
});
test('reject internal URLs and oversize data rather than truncate original prompts',()=>{
 for(const url of ['http://example.com','https://127.0.0.1','https://[::1]','https://10.0.0.1','https://a.local','https://user:pass@example.com'])assert.throws(()=>publicUrl(url));
 const state=emptyWorkspace();state.drafts=Array.from({length:51},(_,n)=>({id:'d'+n}));assert.throws(()=>validateWorkspace(state),/한도/);
});
