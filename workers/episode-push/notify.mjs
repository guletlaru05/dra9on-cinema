import {buildPushPayload} from '@block65/webcrypto-web-push';
import {validEndpoint} from './src/index.mjs';
import {pathToFileURL} from 'node:url';
const ENDPOINT='https://dra9on-episode-push.tutorial-metrics.workers.dev',SITE='https://dra9oncinema.com';
const text={ko:(s,e)=>`FALL 707 시즌 ${s} ${e}화가 공개됐습니다.`,en:(s,e)=>`FALL 707 Season ${s}, Episode ${e} is now available.`,ja:(s,e)=>`FALL 707 シーズン${s}・第${e}話を公開しました。`,es:(s,e)=>`Ya está disponible FALL 707, temporada ${s}, episodio ${e}.`};
export function notification(row){const e=row.episode,lang=Object.hasOwn(text,row.lang)?row.lang:'en';return {id:e.id,title:e.locales[lang].title,body:text[lang](e.season,e.episode),url:e.locales[lang].url,image:e.image,lang};}
async function main(){
 const token=process.env.PUSH_DISPATCH_TOKEN?.trim(),publicKey=process.env.PUSH_VAPID_PUBLIC_KEY?.trim(),privateKey=process.env.PUSH_VAPID_PRIVATE_KEY?.trim();
 if(!token||!publicKey||!privateKey)throw Error('Push secrets are not configured.');
 const api=async(route,input)=>{const response=await fetch(ENDPOINT+route,{method:'POST',redirect:'error',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(input),signal:AbortSignal.timeout(25000)});if(!response.ok)throw Error('Dispatcher request failed: '+response.status);return response.json();};
 const feedResponse=await fetch(SITE+'/pwa/episodes.json?build='+encodeURIComponent(process.env.EXPECTED_REVISION||Date.now()),{cache:'no-store',redirect:'error',signal:AbortSignal.timeout(25000)});
 if(!feedResponse.ok)throw Error('Published episode feed unavailable.');const feed=await feedResponse.json();
 if(process.env.EXPECTED_REVISION&&feed.revision!==process.env.EXPECTED_REVISION)throw Error('The new site revision is not visible yet; scheduled retry will sync the published feed.');
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
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)main().catch(()=>{console.error('Episode notification dispatch failed. Check configuration or retry. No subscription data was logged.');process.exitCode=1;});
