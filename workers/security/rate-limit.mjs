// Security counters only: never write client addresses/keys to D1, analytics or logs.
// Limits are approximate and local to each Cloudflare location, not a global DDoS gate.
export async function requestGate(request,env,group,writing=false,date=new Date()) {
 try {
  if(!env.REQUEST_LIMITER?.limit || (writing&&!env.WRITE_LIMITER?.limit))return 503;
  // Cloudflare supplies this header; ignore client-controlled Forwarded/X-Forwarded-For.
  const address=request.headers.get('CF-Connecting-IP')||'unavailable';
  const hour=Math.floor(date.getTime()/3600000);
  const bytes=new TextEncoder().encode(`${group}|${hour}|${address}`);
  const key=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if(!(await env.REQUEST_LIMITER.limit({key})).success)return 429;
  if(writing&&!(await env.WRITE_LIMITER.limit({key})).success)return 429;
  return 200;
 }catch{return 503;}
}
