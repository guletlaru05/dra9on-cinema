import {createRemoteJWKSet,jwtVerify} from 'jose';
import {parse} from 'parse5';
const PROJECT='dra9on-cinema-stats';
const KEYS=createRemoteJWKSet(new URL('https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com'),{timeoutDuration:6000,cooldownDuration:30000});
const HOSTS=new Set(['dra9oncinema.com','www.dra9oncinema.com','higgsfield.ai','www.higgsfield.ai','klingai.com','www.klingai.com','app.klingai.com','kling.ai','www.kling.ai','docs.byteplus.com','seed.bytedance.com','www.seed.bytedance.com','dreamina.capcut.com','zcre.co.kr','www.zcre.co.kr','bbanana.ai','www.bbanana.ai','threads.com','www.threads.com','threads.net','www.threads.net','x.com','www.x.com','twitter.com','www.twitter.com','instagram.com','www.instagram.com','openart.ai','www.openart.ai']);
export const PRIVATE_BUDGET_SQL='INSERT INTO private_read_budget(day,reads) VALUES(?,1) ON CONFLICT(day) DO UPDATE SET reads=reads+1 WHERE reads<50 RETURNING reads';
function answer(body,status,origin){return new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Vary':'Origin','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',...(origin?{'Access-Control-Allow-Origin':origin}:{})}});}
export async function verifyOwner(token,env,options={}){
 const {payload}=await jwtVerify(token,options.keys||KEYS,{algorithms:['RS256'],issuer:'https://securetoken.google.com/'+PROJECT,audience:PROJECT,currentDate:options.date||new Date(),requiredClaims:['sub','exp','iat','auth_time','email','email_verified']});
 const time=Math.floor((options.date||new Date()).getTime()/1000);
 if(!payload.sub||payload.sub.length>128||!Number.isFinite(payload.iat)||payload.iat>time||!Number.isFinite(payload.auth_time)||payload.auth_time>time||payload.email_verified!==true||payload.firebase?.sign_in_provider!=='google.com')throw Error('owner');
 const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(String(payload.email))))).map(n=>n.toString(16).padStart(2,'0')).join('');
 if(!env.OWNER_EMAIL_SHA256||digest!==env.OWNER_EMAIL_SHA256)throw Error('owner');return payload.sub;
}
export function trustedUrl(input){
 const url=new URL(input);if(url.protocol!=='https:'||url.username||url.password||url.port&&url.port!=='443'||!HOSTS.has(url.hostname))throw Error('unsupported');url.hash='';return url;
}
const attr=(node,name)=>node.attrs?.find(a=>a.name===name)?.value||'';
const children=node=>node.childNodes||[];
const text=node=>node.nodeName==='#text'?node.value:children(node).map(text).join('');
function walk(node,fn){fn(node);children(node).forEach(child=>walk(child,fn));}
const stripContacts=value=>value.replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g,'[연락처 제외]').replace(/(?:\+\d{1,3}[ .-]?)?\(?\d{2,4}\)?[ .-]\d{3,4}[ .-]\d{4}/g,'[연락처 제외]');
export function extractSource(html,url,mime='text/html'){
 let title='',author='',body='',prompts=[];
 if(mime==='text/plain'){body=html;title=new URL(url).pathname;}
 else{
  const tree=parse(html);let main=null,article=null,bodyNode=null;
  walk(tree,node=>{if(node.tagName==='main'&&!main)main=node;if(node.tagName==='article'&&!article)article=node;if(node.tagName==='body')bodyNode=node;if(node.tagName==='title')title=text(node);if(node.tagName==='meta'){const name=attr(node,'name')||attr(node,'property');if(name==='og:title')title=attr(node,'content');if(name==='author'||name==='article:author')author=attr(node,'content');}});
  const chunks=[];function read(node){if(['script','style','noscript','nav','footer','header','form','button','svg'].includes(node.tagName))return;if(node.nodeName==='#text'){chunks.push(node.value);return;}if(node.tagName==='pre'){const original=text(node);if(original.trim())prompts.push(original);chunks.push(original,'\n');return;}children(node).forEach(read);if(['p','div','li','section','h1','h2','h3','h4','br','tr'].includes(node.tagName))chunks.push('\n');}read(main||article||bodyNode||tree);body=chunks.join('').replace(/\n[ \t]*\n[ \t]*\n/g,'\n\n').trim();
 }
 if(body.length<180||/verify you are human|just a moment\.\.\.|enable javascript and cookies|log in to continue|captcha/i.test(body.slice(0,2500)))throw Error('로그인·봇 차단·본문 부족으로 원문을 확인하지 못했습니다.');
 if(!prompts.length){prompts=[...body.matchAll(/```[^\n]*\n([\s\S]*?)```/g)].map(m=>m[1]);if(!prompts.length){const match=body.match(/(?:^|\n)(?:prompt|프롬프트)\s*[:：]\s*([^\n]+(?:\n(?!\n).+)*)/i);if(match)prompts=[match[1]];}}
 if(/(?:threads\.(?:com|net)|instagram\.com|x\.com|twitter\.com)$/.test(new URL(url).hostname)&&!prompts.length&&body.length<1500)throw Error('SNS 미리보기만으로 프롬프트 원문을 확인할 수 없습니다.');
 const low=(title+'\n'+body).toLowerCase(),models=['Seedance 2.5','Seedance 2.0','Higgsfield','Kling','Midjourney','GPT Image','Seedream','Nano Banana','Suno'].filter(m=>low.includes(m.toLowerCase()));
 let category=prompts.length?'프롬프트':models.length||/platform|update|release|tutorial|creator program|플랫폼|업데이트|모집|캠페인/i.test(low)?'툴·플랫폼':'기타';
 const professional=/creator|크리에이터|marketer|마케터|brand|브랜드|director|감독|portfolio|포트폴리오|작품|studio|스튜디오|project|프로젝트|소속|official|공식/i;
 if(!prompts.length&&/(?:^|\/)(?:@[^/]+|about|profile)(?:\/|$)/.test(new URL(url).pathname)&&professional.test(low))category='사람';
 if(category==='사람'){body=stripContacts(body.split('\n').filter(line=>professional.test(line)&&!/집 주소|자택|거주지|생년|생일|가족|배우자|home address|birthday|birthdate|spouse|family/i.test(line)).join('\n'));title=stripContacts(title);author=stripContacts(author);prompts=[];}
 prompts=[...new Set(prompts)];
 if(body.length>150000||prompts.length>30||prompts.some(p=>p.length>100000)||title.length>400||author.length>200)throw Error('원문이 저장 한도보다 큽니다. 요약 저장하지 않았습니다. PC에서 원문을 확인하세요.');
 const tags=[['카메라',/camera|framing|카메라|구도|앵글/i],['조명',/light|shadow|조명|명암|역광/i],['캐릭터 일관성',/identity|character|캐릭터|일관성|시트/i],['액션',/action|chase|fight|액션|추격|전투/i],['분위기',/mood|cinematic|texture|미감|분위기|질감/i]].filter(([,rx])=>rx.test(low)).map(([name])=>name);
 return {title:title.trim()||'공개 자료',url,author,category,source_type:'내 메모',prompts,body,tags,models};
}
async function readLimited(response){const reader=response.body?.getReader();if(!reader)throw Error('본문이 없습니다.');let bytes=0;const chunks=[];try{while(true){const part=await reader.read();if(part.done)break;bytes+=part.value.byteLength;if(bytes>2000000){await reader.cancel();throw Error('원문이 2MB를 넘습니다. 요약 저장하지 않았습니다.');}chunks.push(part.value);}}finally{reader.releaseLock();}return new TextDecoder('utf-8',{fatal:true}).decode(await new Blob(chunks).arrayBuffer());}
export async function readPublic(url,fetcher=fetch){
 let target=trustedUrl(url);
 for(let redirect=0;redirect<5;redirect++){
  const response=await fetcher(target.href,{redirect:'manual',credentials:'omit',headers:{Accept:'text/html, text/plain;q=0.9'},signal:AbortSignal.timeout(12000)});
  if([301,302,303,307,308].includes(response.status)){const location=response.headers.get('location');await response.body?.cancel();if(!location)throw Error('이동 주소가 없습니다.');target=trustedUrl(new URL(location,target).href);continue;}
  if(!response.ok)throw Error('원문 서버 응답 '+response.status);
  const mime=(response.headers.get('content-type')||'').split(';')[0].trim();if(!['text/html','application/xhtml+xml','text/plain'].includes(mime)){await response.body?.cancel();throw Error('HTML 또는 텍스트 원문만 읽을 수 있습니다.');}
  return extractSource(await readLimited(response),target.href,mime);
 }throw Error('주소 이동이 너무 많습니다.');
}
export async function privateRequest(request,env,origin,options={}){
 if(!origin)return answer({error:'Origin not allowed.'},403);
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers:{'Access-Control-Allow-Origin':origin,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type, Authorization','Vary':'Origin','Cache-Control':'no-store','Access-Control-Max-Age':'600'}});
 if(request.method!=='POST')return answer({error:'Method not allowed.'},405,origin);
 const auth=request.headers.get('Authorization')||'';if(!auth.startsWith('Bearer ')||auth.length>16000)return answer({error:'Owner authentication required.'},401,origin);
 try{await verifyOwner(auth.slice(7),env,options);}catch{return answer({error:'Owner authentication required.'},403,origin);}
 let url;
 try{if(!/^application\/json(?:;|$)/i.test(request.headers.get('Content-Type')||''))throw Error();const raw=await readLimited(request);if(raw.length>4000)throw Error();const input=JSON.parse(raw);if(Object.keys(input).length!==1||typeof input.url!=='string'||input.url.length>3000)throw Error();url=new URL(input.url);if(url.protocol!=='https:'||url.username||url.password)throw Error();}catch{return answer({error:'One public HTTPS URL is required.'},400,origin);}
 try{trustedUrl(url.href);}catch{return answer({deferred:true,reason:'이 주소는 서버의 지원 목록에 없습니다.'},200,origin);}
 try{
  const budget=await env.DB.prepare(PRIVATE_BUDGET_SQL).bind((options.date||new Date()).toISOString().slice(0,10)).all();
  if(!budget.results?.length)return answer({deferred:true,reason:'하루 원문 확인 한도 50회에 도달했습니다.'},200,origin);
  const record=await readPublic(url.href,options.fetcher||fetch);return answer({status:'saved',reason:'공개 원문 확인 · 규칙 기반 분류',record},200,origin);
 }catch(error){return answer({status:'failed',reason:error.message==='unsupported'?'지원되지 않는 주소로 이동해 원문을 읽지 않았습니다.':String(error.message||'원문 확인 실패').slice(0,2000)},200,origin);}
}
