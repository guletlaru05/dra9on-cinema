import registry from '../registry.json' with {type:'json'};
import {privateRequest,verifyOwner} from './private-reader.mjs';
import {requestGate} from '../../security/rate-limit.mjs';
import {SECURITY_HEADERS} from '../../security/headers.mjs';

const PROD_ORIGINS = new Set(['https://dra9oncinema.com','https://www.dra9oncinema.com']);
const REFERRERS = ['direct','google','naver','youtube','instagram','x','other'];
const MAX_BYTES = 1024;
const MAX_EVENTS = 20000;
const KST_OFFSET = 9 * 60 * 60 * 1000;
const COUNTERS = ['views','copies','entries',...REFERRERS.map(name=>'ref_'+name)];
const SUM_SQL = COUNTERS.map(name=>`COALESCE(SUM(${name}),0) AS ${name}`).join(',');
const UPDATE_SQL = COUNTERS.map(name=>`${name}=${name}+excluded.${name}`).join(',');
const VALUE_SQL = COUNTERS.map(()=>'?').join(',');
export const SQL = Object.freeze({
  budget: `INSERT INTO daily_budget(day,events) VALUES(?,1)
    ON CONFLICT(day) DO UPDATE SET events=events+1 WHERE events<? RETURNING events`,
  daily: `INSERT INTO daily_metrics(day,path,${COUNTERS.join(',')},updated_at)
    SELECT ?,?,${VALUE_SQL},? WHERE changes()=1
    ON CONFLICT(day,path) DO UPDATE SET ${UPDATE_SQL},updated_at=excluded.updated_at`,
  lifetime: `INSERT INTO lifetime_metrics(path,${COUNTERS.join(',')},updated_at)
    SELECT ?,${VALUE_SQL},? WHERE changes()=1
    ON CONFLICT(path) DO UPDATE SET ${UPDATE_SQL},updated_at=excluded.updated_at`,
  started: `INSERT INTO metrics_metadata(key,value) SELECT 'startedAt',? WHERE changes()=1
    ON CONFLICT(key) DO NOTHING`,
  totals: `SELECT ${SUM_SQL},MAX(updated_at) AS updated_at FROM lifetime_metrics`,
  today: `SELECT ${SUM_SQL} FROM daily_metrics WHERE day=?`,
  pages: 'SELECT path,views,copies FROM lifetime_metrics',
  startedAt: "SELECT value FROM metrics_metadata WHERE key='startedAt'",
  weekly: `SELECT path,SUM(views) AS views,SUM(copies) AS copies FROM daily_metrics
    WHERE day>=? AND day<=? GROUP BY path`,
  dailyHistory: `SELECT day,${SUM_SQL},MAX(updated_at) AS updated_at FROM daily_metrics
    WHERE day>=? AND day<=? GROUP BY day ORDER BY day`,
  dailyPages: `SELECT path,SUM(views) AS views,SUM(copies) AS copies,SUM(entries) AS entries FROM daily_metrics
    WHERE day>=? AND day<=? GROUP BY path`,
});

function headers(origin, cache=false) {
  const result = {...SECURITY_HEADERS,'Content-Type':'application/json; charset=utf-8',
    'X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
    'Cache-Control':cache?'public, max-age=60, s-maxage=60':'no-store',
    'Vary':'Origin'};
  if(origin) result['Access-Control-Allow-Origin']=origin;
  return result;
}
function json(value,status=200,origin=null,cache=false) {
  return new Response(JSON.stringify(value),{status,headers:headers(origin,cache)});
}
function allowedOrigin(request, env) {
  const origin=request.headers.get('Origin');
  const configured=new Set((env.ALLOWED_ORIGINS||[...PROD_ORIGINS].join(',')).split(',').map(s=>s.trim()));
  return origin&&PROD_ORIGINS.has(origin)&&configured.has(origin)?origin:null;
}
export function kstDay(date) { return new Date(date.getTime()+KST_OFFSET).toISOString().slice(0,10); }
function dayBefore(date,days) { return kstDay(new Date(date.getTime()-days*86400000)); }
function count(value) {return Number.isSafeInteger(Number(value))&&Number(value)>=0?Number(value):0;}
function refs(row={}) {return Object.fromEntries(REFERRERS.map(name=>[name,count(row['ref_'+name])]));}

export function validateEvent(body, entries) {
  if(!body||typeof body!=='object'||Array.isArray(body))return null;
  const allowed=new Set(['kind','path','card','referrer','entry']);
  if(Object.keys(body).some(key=>!allowed.has(key)))return null;
  if(!['pageview','copy'].includes(body.kind)||typeof body.path!=='string'||body.path.length>256)return null;
  if(typeof body.entry!=='boolean'||!REFERRERS.includes(body.referrer))return null;
  const registered=Object.hasOwn(entries,body.path)?entries[body.path]:null;
  if(!registered||!['page','tutorial'].includes(registered.type)
    ||typeof registered.canonicalPath!=='string'||!registered.canonicalPath.startsWith('/'))return null;
  if(body.kind==='copy'){
    if(registered.type!=='tutorial'||body.entry||typeof body.card!=='string'||!/^prompt-[1-9][0-9]{0,2}$/.test(body.card))return null;
  }else if(Object.hasOwn(body,'card'))return null;
  return {kind:body.kind,path:registered.canonicalPath,entry:body.entry,referrer:body.referrer};
}

async function readSmallJson(request) {
  const length=request.headers.get('Content-Length');
  if(length&&(!/^\d+$/.test(length)||Number(length)>MAX_BYTES))throw new Error('size');
  if(!/^application\/json(?:\s*;|$)/i.test(request.headers.get('Content-Type')||''))throw new Error('type');
  if(!request.body)throw new Error('body');
  const reader=request.body.getReader();
  const chunks=[];
  let size=0;
  try{
    while(true){
      const {done,value}=await reader.read();
      if(done)break;
      size+=value.byteLength;
      if(size>MAX_BYTES){await reader.cancel();throw new Error('size');}
      chunks.push(value);
    }
  }finally{reader.releaseLock();}
  const bytes=new Uint8Array(size);let offset=0;
  for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}
  return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
}

export function eventStatements(db,event,date,maximum=MAX_EVENTS) {
  const day=kstDay(date),updated=date.toISOString();
  // The write budget follows UTC, matching D1's daily free allowance; reported
  // day aggregates follow Korea time. Three rows are updated per accepted event.
  const budgetDay=updated.slice(0,10);
  const views=event.kind==='pageview'?1:0,copies=event.kind==='copy'?1:0,entry=views&&event.entry?1:0;
  const values=[views,copies,entry,...REFERRERS.map(name=>entry&&name===event.referrer?1:0)];
  return [db.prepare(SQL.budget).bind(budgetDay,maximum),
    db.prepare(SQL.daily).bind(day,event.path,...values,updated),
    db.prepare(SQL.lifetime).bind(event.path,...values,updated),
    db.prepare(SQL.started).bind(updated)];
}

async function record(db,event,date,maximum) {
  // D1 batch is an atomic ordered transaction. changes() gates every later
  // aggregate on the accepted budget update, so rejected events write nothing.
  const result=await db.batch(eventStatements(db,event,date,maximum));
  return Boolean(result[0]?.results?.length);
}

async function summary(db,entries,date) {
  const results=await db.batch([db.prepare(SQL.totals),db.prepare(SQL.today).bind(kstDay(date)),
    db.prepare(SQL.pages),db.prepare(SQL.startedAt)]);
  const total=results[0].results[0]||{},today=results[1].results[0]||{};
  const tutorials={},pages={};
  for(const entry of Object.values(entries)){
    pages[entry.canonicalPath]={views:0,copies:0};
    if(entry.type==='tutorial')tutorials[entry.canonicalPath]={views:0,copies:0};
  }
  for(const row of results[2].results){
    const metrics={views:count(row.views),copies:count(row.copies)};
    if(Object.hasOwn(pages,row.path))pages[row.path]=metrics;
    if(Object.hasOwn(tutorials,row.path))tutorials[row.path]=metrics;
  }
  return {startedAt:results[3].results[0]?.value||null,updatedAt:total.updated_at||null,
    timezone:'Asia/Seoul',day:kstDay(date),
    today:{pageviews:count(today.views),entries:count(today.entries)},
    total:{pageviews:count(total.views),entries:count(total.entries)},
    referrers:{today:refs(today),total:refs(total)},tutorials,pages};
}

async function daily(db,entries,date) {
  const start=dayBefore(date,29),end=kstDay(date);
  const result=await db.batch([db.prepare(SQL.dailyHistory).bind(start,end),
    db.prepare(SQL.dailyPages).bind(start,end),db.prepare(SQL.startedAt)]);
  const allowed=new Set(Object.values(entries).map(entry=>entry.canonicalPath));
  const pages={};
  for(const row of result[1].results)if(allowed.has(row.path))pages[row.path]={views:count(row.views),copies:count(row.copies),entries:count(row.entries)};
  const days=result[0].results.map(row=>({day:row.day,pageviews:count(row.views),
    entries:count(row.entries),copies:count(row.copies),referrers:refs(row)}));
  return {timezone:'Asia/Seoul',startDate:start,endDate:end,periodDays:30,
    startedAt:result[2].results[0]?.value||null,days,pages};
}

async function weekly(db,entries,date) {
  const start=dayBefore(date,6),end=kstDay(date);
  const rows=await db.prepare(SQL.weekly).bind(start,end).all();
  const allowed=new Set(Object.values(entries).filter(entry=>entry.type==='tutorial').map(entry=>entry.canonicalPath));
  const tutorials=rows.results.filter(row=>allowed.has(row.path)).map(row=>({path:row.path,views:count(row.views),copies:count(row.copies)}));
  const sortBy=key=>[...tutorials].sort((a,b)=>b[key]-a[key]||a.path.localeCompare(b.path)).slice(0,5);
  return {timezone:'Asia/Seoul',startDate:start,endDate:end,days:7,
    topViews:sortBy('views'),topCopies:sortBy('copies')};
}

export function createWorker(entries,options={}) {
  const now=options.now||(()=>new Date());
  return {async fetch(request,env,ctx={waitUntil:()=>{}}){
    const url=new URL(request.url),origin=allowedOrigin(request,env);
    if(url.search)return json({error:'Query strings are not accepted.'},400,origin);
    if(request.headers.has('Origin')&&!origin)return json({error:'Origin not allowed.'},403);
    if(request.method!=='OPTIONS'){
      const gate=await requestGate(request,env,'metrics',request.method!=='GET',now());
      if(gate!==200){const response=json({error:gate===429?'Too many requests. Please retry shortly.':'Request protection unavailable.'},gate,origin);if(gate===429)response.headers.set('Retry-After','60');return response;}
    }
    if(url.pathname==='/private/collect')return privateRequest(request,env,origin,options.privateOptions||{});
    if(url.pathname==='/private/visits'||url.pathname==='/daily'){
      if(request.method==='OPTIONS'){
        if(!origin)return json({error:'Origin not allowed.'},403);
        return new Response(null,{status:204,headers:{...headers(origin),'Access-Control-Allow-Methods':'GET, OPTIONS','Access-Control-Allow-Headers':'Authorization','Access-Control-Max-Age':'600'}});
      }
      if(request.method!=='GET')return json({error:'Method not allowed.'},405,origin);
      const auth=request.headers.get('Authorization')||'';
      if(!auth.startsWith('Bearer ')||auth.length>16000)return json({error:'Owner authentication required.'},401,origin);
      try{await verifyOwner(auth.slice(7),env,options.privateOptions||{});}catch{return json({error:'Owner authentication required.'},403,origin);}
      try{return json(url.pathname==='/daily'?await daily(env.DB,entries,now()):await summary(env.DB,entries,now()),200,origin);}
      catch{return json({error:'Aggregate metrics are temporarily unavailable.'},503,origin);}
    }
    if(!['/event','/summary','/weekly','/daily'].includes(url.pathname))return json({error:'Not found.'},404,origin);
    if(request.method==='OPTIONS'){
      if(!origin||url.pathname!=='/event')return json({error:'Origin not allowed.'},403);
      return new Response(null,{status:204,headers:{...headers(origin),
        'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type',
        'Access-Control-Max-Age':'3600'}});
    }
    const date=now();
    try{
      if(url.pathname==='/event'){
        if(request.method!=='POST')return json({error:'Method not allowed.'},405,origin);
        if(!origin)return json({error:'Origin not allowed.'},403);
        let body;
        try{body=await readSmallJson(request);}catch{return json({error:'Expected valid JSON of at most 1024 bytes.'},400,origin);}
        const event=validateEvent(body,entries);
        if(!event)return json({error:'Unknown page or invalid event.'},400,origin);
        const configured=Number(env.MAX_DAILY_EVENTS||MAX_EVENTS);
        const maximum=Number.isInteger(configured)&&configured>0?Math.min(MAX_EVENTS,configured):MAX_EVENTS;
        if(!await record(env.DB,event,date,maximum))return json({error:'Daily event limit reached.'},429,origin);
        return new Response(null,{status:204,headers:headers(origin)});
      }
      if(request.method!=='GET')return json({error:'Method not allowed.'},405,origin);
      const cache=options.cache??globalThis.caches?.default;
      // A new namespace cannot return previously cached public visit totals.
      const cacheKey=new Request(url.origin+'/__aggregate_cache/v2-tutorials-only'+url.pathname,{method:'GET'});
      const cached=cache?await cache.match(cacheKey):null;
      if(cached){
        const response=new Response(cached.body,cached);
        for(const [key,value] of Object.entries(headers(origin,true)))response.headers.set(key,value);
        return response;
      }
      let payload;
      if(url.pathname==='/summary'){
        const tutorials={};
        for(const entry of Object.values(entries))if(entry.type==='tutorial')tutorials[entry.canonicalPath]={views:0,copies:0};
        const result=await env.DB.prepare(SQL.pages).all();
        for(const row of result.results)if(Object.hasOwn(tutorials,row.path))tutorials[row.path]={views:count(row.views),copies:count(row.copies)};
        payload={tutorials};
      }else payload=await weekly(env.DB,entries,date);
      const response=json(payload,200,origin,true);
      if(cache){
        const stored=json(payload,200,null,true);
        if(url.pathname==='/weekly')stored.headers.set('Cache-Control','public, max-age=3600, s-maxage=3600');
        ctx.waitUntil(cache.put(cacheKey,stored));
      }
      return response;
    }catch{
      // Deliberately no request/body/error logging. Provider limits or outages
      // never become a fake zero-count response.
      return json({error:'Aggregate metrics are temporarily unavailable.'},503,origin);
    }
  }};
}

export default createWorker(registry);
