import test from 'node:test';
import assert from 'node:assert/strict';
import {handle,validate,compose,ORIGIN,DESTINATION} from './core.mjs';
const sample={company:'DRA9ON 테스트',contact:'테스트 담당자',email:'guletlaru05@gmail.com',actor:'min-seoa',purpose:'advertising',message:'자동 접수 기능 확인용 테스트 문의입니다.',consent:true,website:'',token:'test-token'};
function setup({verification={success:true,hostname:'dra9oncinema.com',action:'casting'},limited=false,delivery=false}={}){
 let sent=[],verified=0;
 const env={TURNSTILE_SECRET:'test-secret',CASTING_EMAIL:{},INQUIRY_LIMITER:{async limit({key}){assert.match(key,/^[a-f0-9]{64}$/);return {success:!limited};}}};
 const deps={async verify(){verified++;return verification;},async send(raw){if(delivery)throw Error('private delivery detail');sent.push(raw);}};
 const req=(data=sample,origin=ORIGIN)=>new Request('https://example.com/inquiry',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json','CF-Connecting-IP':'192.0.2.1'},body:JSON.stringify(data)});
 return {env,deps,req,sent,get verified(){return verified;}};
}
test('validated inquiry sends to only the fixed verified owner and returns no personal content',async()=>{
 const s=setup(),r=await handle(s.req(),s.env,s.deps),result=await r.json();assert.equal(r.status,200);assert.equal(result.ok,true);assert.equal(s.sent.length,1);assert.equal(r.headers.get('Cache-Control'),'no-store');assert.equal(r.headers.get('Access-Control-Allow-Origin'),ORIGIN);assert.match(s.sent[0],new RegExp('To: '+DESTINATION.replaceAll('.','\\.')));assert.equal(Object.keys(result).sort().join(','),'id,ok');
 const encoded=s.sent[0].split('\r\n\r\n')[1].replaceAll('\r\n','');assert.match(Buffer.from(encoded,'base64').toString('utf8'),/테스트 담당자/);
});
test('all four actor slugs and purposes work',()=>{for(const actor of ['min-seoa','yeonhwa','yuna','haseul'])for(const purpose of ['advertising','music-video','other'])assert.ok(validate({...sample,actor,purpose}));});
test('wrong origins, preview, absent origin and preflight cannot send',async()=>{
 for(const origin of ['https://evil.example','https://dra9on-cinema.pages.dev','null','']){const s=setup(),r=await handle(s.req(sample,origin),s.env,s.deps);assert.equal(r.status,403);assert.equal(r.headers.get('Access-Control-Allow-Origin'),null);assert.equal(s.sent.length,0);}
 const s=setup(),r=await handle(new Request('https://example.com/inquiry',{method:'OPTIONS',headers:{Origin:ORIGIN}}),s.env,s.deps);assert.equal(r.status,204);assert.equal(s.verified,0);
});
test('invalid, replayed and wrong-host/action security results never send',async()=>{
 for(const verification of [{success:false},{success:true,hostname:'localhost',action:'casting'},{success:true,hostname:'dra9oncinema.com',action:'login'}]){const s=setup({verification}),r=await handle(s.req(),s.env,s.deps);assert.equal(r.status,403);assert.equal(s.sent.length,0);}
});
test('header injection, unknown actors, missing consent and honeypot are rejected before verification',async()=>{
 for(const invalid of [{email:'a@example.com\r\nBcc: evil@example.com'},{contact:'name\r\nX: value'},{actor:'constructor'},{purpose:'other\nBcc:'},{consent:false},{website:'https://spam.example'},{message:'short'},{company:'x'.repeat(121)},{token:''}]){const s=setup(),r=await handle(s.req({...sample,...invalid}),s.env,s.deps);assert.equal(r.status,400);assert.equal(s.verified,0);assert.equal(s.sent.length,0);}
});
test('oversize, bad JSON and non-JSON requests cannot send',async()=>{
 for(const [body,type,status] of [['x'.repeat(20001),'application/json',413],['{','application/json',400],['{}','text/plain',415]]){const s=setup(),r=await handle(new Request('https://example.com/inquiry',{method:'POST',headers:{Origin:ORIGIN,'Content-Type':type},body}),s.env,s.deps);assert.equal(r.status,status);assert.equal(s.sent.length,0);}
});
test('rate limit, absent bindings and failed delivery never claim success or leak errors',async()=>{
 let s=setup({limited:true});assert.equal((await handle(s.req(),s.env,s.deps)).status,429);assert.equal(s.verified,0);
 s=setup();delete s.env.TURNSTILE_SECRET;assert.equal((await handle(s.req(),s.env,s.deps)).status,503);
 s=setup({delivery:true});const r=await handle(s.req(),s.env,s.deps);assert.equal(r.status,502);assert.deepEqual(await r.json(),{ok:false,error:'delivery'});
});
test('MIME message cannot redirect recipients or expose the security token',()=>{
 const raw=compose(validate(sample),'123');assert.match(raw,/Reply-To: guletlaru05@gmail.com/);assert.doesNotMatch(raw,/Bcc:|test-token|test-secret/);
 const words=raw.match(/=\?UTF-8\?B\?[^?]+\?=/g);assert.ok(words.every(word=>word.length<=75));assert.match(words.map(word=>Buffer.from(word.slice(10,-2),'base64').toString('utf8')).join(''),/AI 배우 섭외.*민서아 대위/);
});
