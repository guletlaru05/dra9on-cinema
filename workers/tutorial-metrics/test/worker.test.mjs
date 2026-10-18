import {test} from 'node:test';
import {createHash} from 'node:crypto';
import {generateKeyPair,SignJWT} from 'jose';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFile} from 'node:fs/promises';
import {createWorker,kstDay,SQL} from '../src/index.mjs';

const ORIGIN='https://dra9oncinema.com';
const NOW=new Date('2026-10-17T15:01:02.000Z');
const pair=await generateKeyPair('RS256');
const owner='owner@example.test',stamp=NOW.getTime()/1000;
const privateOptions={keys:pair.publicKey,date:NOW};
const ownerEnv={OWNER_EMAIL_SHA256:createHash('sha256').update(owner).digest('hex')};
async function ownerToken(changes={}){return new SignJWT({email:owner,email_verified:true,auth_time:stamp-100,firebase:{sign_in_provider:'google.com'},iss:'https://securetoken.google.com/dra9on-cinema-stats',aud:'dra9on-cinema-stats',sub:'uid',iat:stamp-50,exp:stamp+500,...changes}).setProtectedHeader({alg:'RS256'}).sign(pair.privateKey);}
 // 2026-10-18 in Korea
const REGISTRY={
  '/':{canonicalPath:'/',type:'page'},
  '/en/':{canonicalPath:'/',type:'page'},
  '/watch/example/':{canonicalPath:'/watch/example/',type:'page'},
  '/tutorials/example/':{canonicalPath:'/tutorials/example/',type:'tutorial'},
  '/en/tutorials/example/':{canonicalPath:'/tutorials/example/',type:'tutorial'},
  '/tutorials/another/':{canonicalPath:'/tutorials/another/',type:'tutorial'},
};
const SCHEMA=await readFile(new URL('../migrations/0001_aggregate_metrics.sql',import.meta.url),'utf8');

class D1 {
  constructor(){this.sql=new DatabaseSync(':memory:');this.sql.exec(SCHEMA);this.calls=[];}
  prepare(sql){
    const db=this;
    return {sql,values:[],bind(...values){return {...this,values};},
      async all(){return db.execute(this);}};
  }
  execute(statement){
    this.calls.push({sql:statement.sql,values:statement.values});
    const results=this.sql.prepare(statement.sql).all(...statement.values);
    return {success:true,results,meta:{changes:this.sql.prepare('SELECT changes() AS n').get().n}};
  }
  async batch(statements){
    this.sql.exec('BEGIN IMMEDIATE');
    try{const result=statements.map(stmt=>this.execute(stmt));this.sql.exec('COMMIT');return result;}
    catch(error){this.sql.exec('ROLLBACK');throw error;}
  }
  close(){this.sql.close();}
}

function setup(options={}){
  const DB=new D1();
  const env={DB,MAX_DAILY_EVENTS:'20000',REQUEST_LIMITER:{limit:async()=>({success:true})},WRITE_LIMITER:{limit:async()=>({success:true})},...ownerEnv};
  const worker=createWorker(REGISTRY,{now:()=>NOW,cache:null,privateOptions,...options});
  return {DB,env,worker};
}
function post(body={},extra={}){
  return new Request('https://metrics.example.workers.dev/event',{method:'POST',
    headers:{Origin:ORIGIN,'Content-Type':'application/json',...(extra.headers||{})},
    body:JSON.stringify({kind:'pageview',path:'/tutorials/example/',referrer:'direct',entry:true,...body}),...extra});
}
function get(path='/summary',origin=ORIGIN){return new Request('https://metrics.example.workers.dev'+path,{headers:origin?{Origin:origin}:{}});}
async function payload(worker,env,path='/private/visits'){
  const request=get(path);if(path==='/private/visits'||path==='/daily')request.headers.set('Authorization','Bearer '+await ownerToken());
  const response=await worker.fetch(request,env);
  assert.equal(response.status,200);
  return response.json();
}

test('empty database reports absent timestamps and real zero aggregates',async()=>{
  const {DB,worker,env}=setup();
  const result=await payload(worker,env);
  assert.deepEqual(result.today,{pageviews:0,entries:0});
  assert.deepEqual(result.total,{pageviews:0,entries:0});
  assert.equal(result.startedAt,null);assert.equal(result.updatedAt,null);
  assert.deepEqual(result.tutorials['/tutorials/example/'],{views:0,copies:0});
  DB.close();
});

test('Korean and English aliases aggregate together, page landings stay separate from copy counts',async()=>{
  const {DB,worker,env}=setup();
  assert.equal((await worker.fetch(post({referrer:'google'}),env)).status,204);
  assert.equal((await worker.fetch(post({path:'/en/tutorials/example/',entry:false}),env)).status,204);
  assert.equal((await worker.fetch(post({kind:'copy',card:'prompt-1',entry:false}),env)).status,204);
  assert.equal((await worker.fetch(post({path:'/watch/example/',entry:false}),env)).status,204);
  const result=await payload(worker,env);
  assert.deepEqual(result.today,{pageviews:3,entries:1});
  assert.deepEqual(result.total,{pageviews:3,entries:1});
  assert.deepEqual(result.tutorials['/tutorials/example/'],{views:2,copies:1});
  assert.deepEqual(result.pages['/watch/example/'],{views:1,copies:0});
  assert.equal(result.pages['/library/'],undefined);
  assert.equal(result.referrers.total.google,1);assert.equal(result.referrers.total.direct,0);
  assert.equal(result.startedAt,NOW.toISOString());assert.equal(result.updatedAt,NOW.toISOString());
  assert.equal(result.day,'2026-10-18');
  const eventRows=DB.sql.prepare('SELECT * FROM daily_metrics').all();
  assert.ok(eventRows.every(row=>!row.path.startsWith('/en/')));
  assert.equal(DB.sql.prepare('SELECT events FROM daily_budget').get().events,4);
  DB.close();
});

test('strict validation rejects private paths, unknown fields, unsafe types and copy misuse before D1',async()=>{
  const invalid=[{path:'/library/'},{path:'/tutorials/example/?email=a@b.com'},
    {path:'https://dra9oncinema.com/'},{path:'/tutorials/unknown/'},{path:'/TUTORIALS/example/'},
    {kind:'login'},{kind:1},{entry:'true'},{referrer:'https://google.com/search?q=private'},
    {email:'person@example.com'},{fingerprint:'secret'},{ip:'1.2.3.4'},{userAgent:'browser'},
    {card:'prompt-1'},{kind:'copy',card:'prompt-1',entry:true},
    {kind:'copy',card:'prompt-1',entry:false,path:'/'},{kind:'copy',entry:false},
    {kind:'copy',card:'script',entry:false},{kind:'copy',card:'prompt-0',entry:false}];
  const {DB,worker,env}=setup();
  for(const body of invalid)assert.equal((await worker.fetch(post(body),env)).status,400,JSON.stringify(body));
  assert.equal(DB.calls.length,0);DB.close();
});

test('Origin gate, preflight and cookie-free response use no credentials',async()=>{
  const {DB,worker,env}=setup();
  for(const origin of ['https://evil.example','http://dra9oncinema.com','null']){
    const response=await worker.fetch(new Request('https://metrics.example.workers.dev/event',{
      method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:'{}'}),env);
    assert.equal(response.status,403);assert.equal(response.headers.get('Access-Control-Allow-Origin'),null);
  }
  assert.equal((await worker.fetch(new Request('https://metrics.example.workers.dev/event',{
    method:'POST',headers:{'Content-Type':'application/json'},body:'{}'}),env)).status,403);
  const response=await worker.fetch(new Request('https://metrics.example.workers.dev/event',{
    method:'OPTIONS',headers:{Origin:ORIGIN,'Access-Control-Request-Method':'POST'}}),env);
  assert.equal(response.status,204);assert.equal(response.headers.get('Access-Control-Allow-Origin'),ORIGIN);
  for(const name of ['Set-Cookie','Access-Control-Allow-Credentials'])assert.equal(response.headers.get(name),null);
  assert.equal(DB.calls.length,0);DB.close();
});

test('request maximum applies even without Content-Length, wrong MIME/query/method rejected',async()=>{
  const {DB,worker,env}=setup();
  const tooLarge=new Request('https://metrics.example.workers.dev/event',{method:'POST',
    headers:{Origin:ORIGIN,'Content-Type':'application/json'},body:'x'.repeat(1025)});
  assert.equal((await worker.fetch(tooLarge,env)).status,400);
  assert.equal((await worker.fetch(post({}, {headers:{Origin:ORIGIN,'Content-Type':'text/plain'}}),env)).status,400);
  assert.equal((await worker.fetch(get('/summary?secret=yes'),env)).status,400);
  assert.equal((await worker.fetch(get('/event'),env)).status,405);
  assert.equal((await worker.fetch(get('/unknown'),env)).status,404);
  assert.equal(DB.calls.length,0);DB.close();
});

test('atomic UTC daily write budget rejects without increasing any aggregate',async()=>{
  const {DB,worker,env}=setup();env.MAX_DAILY_EVENTS='2';
  assert.equal((await worker.fetch(post(),env)).status,204);
  assert.equal((await worker.fetch(post({kind:'copy',card:'prompt-2',entry:false}),env)).status,204);
  assert.equal((await worker.fetch(post(),env)).status,429);
  assert.equal((await worker.fetch(post(),env)).status,429);
  const result=await payload(worker,env);
  assert.deepEqual(result.total,{pageviews:1,entries:1});
  assert.deepEqual(result.tutorials['/tutorials/example/'],{views:1,copies:1});
  assert.equal(DB.sql.prepare('SELECT day,events FROM daily_budget').get().day,'2026-10-17');
  assert.equal(DB.sql.prepare('SELECT events FROM daily_budget').get().events,2);
  DB.close();
});

test('startedAt remains the first actual accepted event',async()=>{
  const {DB,env}=setup();let date=new Date('2026-10-16T22:00:00Z');
  const worker=createWorker(REGISTRY,{now:()=>date,cache:null,privateOptions});
  await worker.fetch(post(),env);
  date=NOW;await worker.fetch(post(),env);
  const result=await payload(worker,env);
  assert.equal(result.startedAt,'2026-10-16T22:00:00.000Z');
  assert.equal(result.updatedAt,NOW.toISOString());DB.close();
});

test('failed aggregate batch rolls back the accepted budget and first-event timestamp',async()=>{
  const {DB,worker,env}=setup();
  const original=DB.execute.bind(DB);
  DB.execute=statement=>{if(statement.sql===SQL.lifetime)throw new Error('simulated storage failure');return original(statement);};
  assert.equal((await worker.fetch(post(),env)).status,503);
  assert.equal(DB.sql.prepare('SELECT COUNT(*) AS n FROM daily_budget').get().n,0);
  assert.equal(DB.sql.prepare('SELECT COUNT(*) AS n FROM daily_metrics').get().n,0);
  assert.equal(DB.sql.prepare('SELECT COUNT(*) AS n FROM metrics_metadata').get().n,0);
  DB.close();
});

test('weekly report uses seven KST days and independent top views/copies',async()=>{
  const {DB,env}=setup();let date=new Date('2026-10-10T16:00:00Z');
  const worker=createWorker(REGISTRY,{now:()=>date,cache:null,privateOptions});
  for(let i=0;i<5;i++)await worker.fetch(post({path:'/tutorials/another/'}),env); // Oct 11 KST, outside
  date=new Date('2026-10-11T15:01:00Z'); // Oct 12 KST, first included
  await worker.fetch(post({path:'/tutorials/another/',kind:'copy',card:'prompt-1',entry:false}),env);
  date=NOW;
  await worker.fetch(post(),env);await worker.fetch(post(),env);
  const report=await payload(worker,env,'/weekly');
  assert.equal(report.startDate,'2026-10-12');assert.equal(report.endDate,'2026-10-18');
  assert.equal(report.days,7);assert.equal(report.timezone,'Asia/Seoul');
  assert.equal(report.topViews[0].path,'/tutorials/example/');assert.equal(report.topViews[0].views,2);
  assert.equal(report.topCopies[0].path,'/tutorials/another/');assert.equal(report.topCopies[0].copies,1);
  DB.close();
});

test('daily report returns only a bounded last-30-KST-day range and canonical public pages',async()=>{
  const {DB,env}=setup();let date=new Date('2026-09-17T15:00:00Z'); // Sep 18 KST, outside last30
  const worker=createWorker(REGISTRY,{now:()=>date,cache:null,privateOptions});
  await worker.fetch(post({referrer:'other'}),env);
  date=new Date('2026-09-18T15:00:00Z'); // Sep 19 KST, first included day
  await worker.fetch(post({path:'/watch/example/',referrer:'youtube'}),env);
  date=NOW;
  await worker.fetch(post({path:'/en/tutorials/example/',referrer:'google'}),env);
  const report=await payload(worker,env,'/daily');
  assert.equal(report.periodDays,30);
  assert.equal(report.startDate,'2026-09-19');assert.equal(report.endDate,'2026-10-18');
  assert.deepEqual(report.days.map(day=>day.day),['2026-09-19','2026-10-18']);
  assert.equal(report.days[0].referrers.youtube,1);
  assert.equal(report.days[1].referrers.google,1);
  assert.deepEqual(report.pages['/tutorials/example/'],{views:1,copies:0,entries:1});
  assert.deepEqual(report.pages['/watch/example/'],{views:1,copies:0,entries:1});
  assert.equal(report.pages['/en/tutorials/example/'],undefined);
  assert.equal(report.startedAt,'2026-09-17T15:00:00.000Z');
  assert.equal((await worker.fetch(get('/daily?days=9999'),env)).status,400);
  DB.close();
});

test('only aggregate columns are stored, not request identity or raw prompts',async()=>{
  const {DB,worker,env}=setup();
  const request=post({}, {headers:{Origin:ORIGIN,'Content-Type':'application/json',
    Cookie:'secret=browser-id','CF-Connecting-IP':'1.2.3.4','User-Agent':'test browser',
    Referer:'https://example.com/private?email=someone@example.com'}});
  assert.equal((await worker.fetch(request,env)).status,204);
  const values=JSON.stringify(DB.calls.flatMap(call=>call.values));
  for(const forbidden of ['1.2.3.4','browser-id','test browser','someone@example.com','prompt-'])assert.ok(!values.includes(forbidden));
  const tables=DB.sql.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().map(row=>row.name);
  assert.deepEqual(tables.sort(),['daily_budget','daily_metrics','lifetime_metrics','metrics_metadata']);
  assert.equal(DB.sql.prepare('SELECT COUNT(*) AS n FROM daily_metrics').get().n,1);
  DB.close();
});

test('unavailable D1 returns explicit failure, not fabricated zeros; public summary cached 60s',async()=>{
  const {DB,worker,env}=setup();
  const response=await worker.fetch(get(),env);
  assert.equal(response.headers.get('Cache-Control'),'public, max-age=60, s-maxage=60');
  assert.equal(response.headers.get('Set-Cookie'),null);
  const broken={DB:{prepare(){throw new Error('sensitive upstream text');}}};
  const unavailable=await worker.fetch(get(),broken);
  assert.equal(unavailable.status,503);
  assert.ok(!(await unavailable.text()).includes('sensitive'));
  DB.close();
});

test('KST midnight conversion is independent of host timezone',()=>{
  assert.equal(kstDay(new Date('2026-10-17T14:59:59Z')),'2026-10-17');
  assert.equal(kstDay(new Date('2026-10-17T15:00:00Z')),'2026-10-18');
  assert.match(SQL.daily,/WHERE changes\(\)=1/);
});


test('visitor totals require verified owner JWT; no cookies or shared cache, including /daily',async()=>{
 const {DB,worker,env}=setup();await worker.fetch(post(),env);
 for(const path of ['/private/visits','/daily']){
  const before=DB.calls.length;
  assert.equal((await worker.fetch(get(path),env)).status,401);
  for(const changes of [{email:'other@example.test'},{email_verified:false},{exp:stamp-1},{firebase:{sign_in_provider:'password'}}]){
   const req=get(path);req.headers.set('Authorization','Bearer '+await ownerToken(changes));assert.equal((await worker.fetch(req,env)).status,403);
  }
  assert.equal(DB.calls.length,before,'denied requests must not query private counts');
  const req=get(path);req.headers.set('Authorization','Bearer '+await ownerToken());const response=await worker.fetch(req,env);
  assert.equal(response.status,200);assert.equal(response.headers.get('Cache-Control'),'no-store');
 }
 const publicResponse=await worker.fetch(get('/summary'),env),data=await publicResponse.json();
 assert.deepEqual(Object.keys(data),['tutorials']);
 for(const forbidden of ['today','total','entries','referrers','startedAt','pages'])assert.equal(Object.hasOwn(data,forbidden),false);
 assert.deepEqual(data.tutorials['/tutorials/example/'],{views:1,copies:0});DB.close();
});
