import {readFile} from 'node:fs/promises';
import {buildPushPayload} from '@block65/webcrypto-web-push';
import {validEndpoint,validEpisode} from './src/index.mjs';
import {pathToFileURL} from 'node:url';
const ENDPOINT='https://dra9on-episode-push.tutorial-metrics.workers.dev',SITE='https://dra9oncinema.com';
const text={ko:(s,e,p)=>`FALL 707 시즌 ${s} ${e}화${p?' Part '+p:''}가 공개됐습니다.`,en:(s,e,p)=>`FALL 707 Season ${s}, Episode ${e}${p?', Part '+p:''} is now available.`,ja:(s,e,p)=>`FALL 707 シーズン${s}・第${e}話${p?'・パート'+p:''}を公開しました。`,es:(s,e,p)=>`Ya está disponible FALL 707, temporada ${s}, episodio ${e}${p?', parte '+p:''}.`};
export function notification(row){const e=row.episode,lang=Object.hasOwn(text,row.lang)?row.lang:'en',part=e.locales.ko.url.match(/-part([1-9][0-9]{0,2})\/$/)?.[1];return {id:e.id,title:e.locales[lang].title,body:text[lang](e.season,e.episode,part),url:e.locales[lang].url,image:e.image,lang};}
export async function readNotificationFeed(env={},fetcher=fetch,readPublicFeed=()=>readFile(new URL('../../.cache/canonical-episodes.json',import.meta.url),'utf8')){
 const dry=env.PUSH_DRY_RUN==='true',site=env.PUSH_SITE_ORIGIN||SITE;
 if(site!==SITE)throw Error('Unapproved notification source.');
 let feed;
 if(env.PUSH_VERIFIED_FEED_FILE==='true'){
  if(!/^[a-f0-9]{40}$/.test(env.EXPECTED_REVISION||''))throw Error('A verified feed requires its expected revision.');
  const text=await readPublicFeed();if(text.length>1000000)throw Error('Invalid public episode feed.');feed=JSON.parse(text);
 }else{
 const response=await fetcher(site+'/pwa/episodes.json?build='+encodeURIComponent(env.EXPECTED_REVISION||Date.now()),{cache:'no-store',redirect:'error',headers:{'User-Agent':'DRA9ON-deploy-check/1.0','Accept':'application/json'},signal:AbortSignal.timeout(25000)});
 if(!response.ok)throw Error('Published episode feed unavailable (HTTP '+response.status+').');feed=await response.json();
 }
 if(!/^[a-f0-9]{40}$/.test(feed.revision||'')||!Array.isArray(feed.episodes)||feed.episodes.length>200||!feed.episodes.every(e=>validEpisode(e,new Date())))throw Error('Invalid public episode feed.');
 if(env.EXPECTED_REVISION&&feed.revision!==env.EXPECTED_REVISION)throw Error('The new site revision is not visible yet.');
 return feed;
}
export async function main(env=process.env,fetcher=fetch){
 const feed=await readNotificationFeed(env,fetcher);
 if(env.PUSH_DRY_RUN==='true'){
  console.log(JSON.stringify({dryRun:true,revision:feed.revision,episodes:feed.episodes.length,dispatched:false}));return;
 }
 const token=env.PUSH_DISPATCH_TOKEN?.trim(),publicKey=env.PUSH_VAPID_PUBLIC_KEY?.trim(),privateKey=env.PUSH_VAPID_PRIVATE_KEY?.trim();
 if(!token||!publicKey||!privateKey)throw Error('Push secrets are not configured.');
 const api=async(route,input)=>{const response=await fetch(ENDPOINT+route,{method:'POST',redirect:'error',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(input),signal:AbortSignal.timeout(25000)});if(!response.ok)throw Error('Dispatcher request failed: '+response.status);return response.json();};
 const synced=await api('/sync',feed);let sent=0,expired=0,retry=0;
 // At most 1000 deliveries/run, using only the existing public-repository runner.
 for(let page=0;page<50;page++){
  const {deliveries}=await api('/batch',{});if(!deliveries.length)break;
  const results=[];
  for(let offset=0;offset<deliveries.length;offset+=4){await Promise.all(deliveries.slice(offset,offset+4).map(async row=>{
   let status=0;
   try{
    if(!validEndpoint(row.endpoint))status=400;
    else{const message={data:JSON.stringify(notification(row)),options:{ttl:86400}};const payload=await buildPushPayload(message,{endpoint:row.endpoint,keys:{p256dh:row.p256dh,auth:row.auth}},{subject:'https://dra9oncinema.com/',publicKey,privateKey});const response=await fetch(row.endpoint,{...payload,redirect:'error',signal:AbortSignal.timeout(15000)});status=response.status;await response.body?.cancel();}
   }catch{/* Never log endpoints, keys, payloads or provider responses. */}
   if(status>=200&&status<300)sent++;else if(status===404||status===410)expired++;else retry++;
   results.push({event_id:row.event_id,sub_id:row.sub_id,lease:row.lease,status});
  }));}
  await api('/ack',{results});
 }
 console.log(JSON.stringify({initialized:synced.initialized,newEpisodes:synced.newEpisodes,sent,expired,retry}));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(error=>{const reason=/^(Published episode feed unavailable \(HTTP \d{3}\)\.|The new site revision is not visible yet\.|Invalid public episode feed\.|fetch failed)$/.test(error.message)?error.message:'Check configuration or retry.';console.error('Episode notification dispatch failed. '+reason+' No subscription data was logged.');process.exitCode=1;});
