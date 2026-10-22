/* No request bodies, tokens, email addresses or IPs are logged or persisted. */
export const ORIGIN = 'https://dra9oncinema.com';
export const DESTINATION = 'guletlaru05@gmail.com';
const ACTORS = {'min-seoa':'민서아 대위','yeonhwa':'연화','yuna':'유나 (염력소녀)','haseul':'하슬 (혈맥선생)'};
const PURPOSES = {advertising:'광고', 'music-video':'뮤직비디오', other:'기타'};
const forbidden = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/;
function text(value,min,max,single=false) {
 if(typeof value!=='string')return null;
 const result=value.trim();
 return result.length>=min && result.length<=max && !forbidden.test(result) && (!single || !/[\r\n]/.test(result)) ? result : null;
}
export function validate(data) {
 if(!data || typeof data!=='object' || Array.isArray(data) || data.website || data.consent!==true)return null;
 const company=text(data.company,1,120,true),contact=text(data.contact,1,80,true),email=text(data.email,3,254,true),message=text(data.message,10,4000);
 if(!company||!contact||!email||!message||!/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)||!Object.hasOwn(ACTORS,data.actor)||!Object.hasOwn(PURPOSES,data.purpose))return null;
 return {company,contact,email,message,actor:data.actor,purpose:data.purpose};
}
function b64(value){return btoa(String.fromCharCode(...new TextEncoder().encode(value)));}
export function compose(data,id) {
 const subject='[AI 배우 섭외] '+ACTORS[data.actor]+' / '+PURPOSES[data.purpose];
 const body=['DRA9ON CINEMA 섭외·협업 문의','접수 ID: '+id,'회사명: '+data.company,'담당자: '+data.contact,'이메일: '+data.email,'배우: '+ACTORS[data.actor],'용도: '+PURPOSES[data.purpose],'','내용:',data.message,'','※ 방문자가 작성한 문의입니다. 링크·첨부 요청은 별도로 확인하세요.'].join('\r\n');
 return ['From: DRA9ON CINEMA <casting@dra9oncinema.com>','To: '+DESTINATION,'Reply-To: '+data.email,'Subject: =?UTF-8?B?'+b64(subject)+'?=','MIME-Version: 1.0','Content-Type: text/plain; charset=UTF-8','Content-Transfer-Encoding: base64','Message-ID: <'+id+'@dra9oncinema.com>','Date: '+new Date().toUTCString(),'',''+b64(body).match(/.{1,76}/g).join('\r\n')].join('\r\n');
}
export async function handle(request,env,deps) {
 const cors=request.headers.get('Origin')===ORIGIN;
 const headers={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Vary':'Origin'};
 if(cors)Object.assign(headers,{'Access-Control-Allow-Origin':ORIGIN,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type','Access-Control-Max-Age':'600'});
 const respond=(status,error,id)=>new Response(JSON.stringify(error?{ok:false,error}:{ok:true,id}),{status,headers});
 if(new URL(request.url).pathname!=='/inquiry')return respond(404,'not-found');
 if(!cors)return respond(403,'origin');
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers});
 if(request.method!=='POST')return respond(405,'method');
 if(!env.TURNSTILE_SECRET || !env.CASTING_EMAIL || !env.INQUIRY_LIMITER)return respond(503,'unavailable');
 if(!/^application\/json(?:\s*;|$)/i.test(request.headers.get('Content-Type')||''))return respond(415,'content-type');
 if(Number(request.headers.get('Content-Length'))>20000)return respond(413,'too-large');
 try {
  // A rotating digest is used only as an approximate per-location rate-limit key.
  const ip=request.headers.get('CF-Connecting-IP')||'unknown';
  const hour=Math.floor(Date.now()/3600000);
  const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(hour+':'+ip));
  const key=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
  if(!(await env.INQUIRY_LIMITER.limit({key})).success)return respond(429,'rate');
  const reader=request.body?.getReader();let size=0,chunks=[];
  if(!reader)return respond(400,'invalid');
  while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>20000){await reader.cancel();return respond(413,'too-large');}chunks.push(value);}
  const raw=new Uint8Array(size);let offset=0;for(const chunk of chunks){raw.set(chunk,offset);offset+=chunk.length;}
  let data;try{data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));}catch{return respond(400,'invalid');}
  const valid=validate(data);if(!valid || !text(data.token,1,2048,true))return respond(400,'invalid');
  let verification;
  try{verification=await deps.verify(env.TURNSTILE_SECRET,data.token);}catch{return respond(503,'security-unavailable');}
  if(!verification?.success || verification.hostname!=='dra9oncinema.com' || verification.action!=='casting')return respond(403,'challenge');
  const id=crypto.randomUUID();
  try{await deps.send(compose(valid,id));}catch{return respond(502,'delivery');}
  return respond(200,null,id);
 }catch{return respond(503,'unavailable');}
}
