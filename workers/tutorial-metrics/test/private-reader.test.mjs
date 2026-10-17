import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {generateKeyPair,SignJWT} from 'jose';
import {readFileSync} from 'node:fs';
import {verifyOwner,privateRequest,readPublic,extractSource,trustedUrl} from '../src/private-reader.mjs';
const date=new Date('2026-10-18T09:00:00Z'),stamp=date.getTime()/1000;
const pair=await generateKeyPair('RS256');
const owner='owner@example.test',env={OWNER_EMAIL_SHA256:createHash('sha256').update(owner).digest('hex')};
async function token(changes={},key=pair.privateKey){return new SignJWT({email:owner,email_verified:true,auth_time:stamp-100,firebase:{sign_in_provider:'google.com'},iss:'https://securetoken.google.com/dra9on-cinema-stats',aud:'dra9on-cinema-stats',sub:'uid',iat:stamp-50,exp:stamp+500,...changes}).setProtectedHeader({alg:'RS256',kid:'test'}).sign(key);}
const options={keys:pair.publicKey,date};
test('signed Firebase token, verified owner, audience, expiry and provider required',async()=>{
 assert.equal(await verifyOwner(await token(),env,options),'uid');
 for(const change of [{email:'stranger@example.test'},{email_verified:false},{firebase:{sign_in_provider:'password'}},{auth_time:stamp+100},{aud:'other-project'},{exp:stamp-100}])await assert.rejects(()=>token(change).then(jwt=>verifyOwner(jwt,env,options)));
 const other=await generateKeyPair('RS256');await assert.rejects(()=>token({},other.privateKey).then(jwt=>verifyOwner(jwt,env,options)));
});
test('source read uses an exact host allowlist, rechecks redirects, never forwards credentials',async()=>{
 for(const url of ['https://127.0.0.1','https://higgsfield.ai.evil.test','https://unknown.test','http://higgsfield.ai','https://user:pass@higgsfield.ai'])assert.throws(()=>trustedUrl(url));
 await assert.rejects(()=>readPublic('https://higgsfield.ai/',async(url,init)=>{assert.equal(init.headers.Authorization,undefined);assert.equal(init.headers.Cookie,undefined);assert.equal(init.redirect,'manual');return new Response('',{status:302,headers:{location:'http://169.254.169.254/'}});}));
});
test('full original prompt entities and whitespace survive HTML parsing',()=>{
 const raw='  Korean “대사”\n&lt;camera&gt; &amp; motion\n\nlast  ';
 const result=extractSource('<title>Test</title><main><p>'+'설명 '.repeat(100)+'</p><pre>'+raw+'</pre></main><footer>Not article</footer>','https://higgsfield.ai/a');
 assert.equal(result.prompts[0],'  Korean “대사”\n<camera> & motion\n\nlast  ');assert.equal(result.category,'프롬프트');assert.ok(!result.body.includes('Not article'));
 assert.throws(()=>extractSource('<main>Log in to continue</main>','https://www.instagram.com/reel/a/'),/원문/);
 assert.throws(()=>extractSource('<main><pre>'+'a'.repeat(100001)+'</pre></main>','https://higgsfield.ai/a'),/요약 저장하지/);
});
test('private endpoint rejects outsiders, never caches, enforces 50 daily reads',async()=>{
 const sql=new DatabaseSync(':memory:');sql.exec(readFileSync(new URL('../migrations/0002_private_read_budget.sql',import.meta.url),'utf8'));
 const database={prepare(query){return {bind(...args){return {async all(){return {results:sql.prepare(query).all(...args)};}};}};}};
 const config={...env,DB:database},origin='https://dra9oncinema.com';
 const make=async jwt=>new Request('https://worker/private/collect',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json',Authorization:'Bearer '+jwt},body:JSON.stringify({url:'https://higgsfield.ai/a'})});
 assert.equal((await privateRequest(await make('forged'),config,origin,options)).status,403);
 assert.equal((await privateRequest(await make(await token()),config,null,options)).status,403);
 const fetcher=async()=>new Response('<main>'+('Public tutorial. '.repeat(30))+'</main>',{headers:{'content-type':'text/html'}});
 const jwt=await token();for(let n=0;n<50;n++){const response=await privateRequest(await make(jwt),config,origin,{...options,fetcher});assert.equal(response.headers.get('Cache-Control'),'no-store');assert.equal((await response.json()).status,'saved');}
 const limited=await privateRequest(await make(jwt),config,origin,{...options,fetcher});assert.equal((await limited.json()).deferred,true);
 assert.equal(sql.prepare('SELECT reads FROM private_read_budget').get().reads,50);sql.close();
});
