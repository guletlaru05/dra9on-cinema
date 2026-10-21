// Firebase's documented same-origin sign-in helper proxy. Preview host only.
// No application data, credentials, sessions or request bodies are logged/stored.
const HOST='dra9on-cinema.pages.dev';
const UPSTREAM='https://dra9on-cinema-stats.firebaseapp.com';
function protectedResponse(response){
 const headers=new Headers(response.headers);
 headers.set('Cache-Control','no-store, max-age=0');
 headers.set('Strict-Transport-Security','max-age=31536000');
 headers.set('X-Content-Type-Options','nosniff');
 headers.set('Referrer-Policy','strict-origin-when-cross-origin');
 headers.set('Permissions-Policy','camera=(), microphone=(), geolocation=(), payment=(), usb=()');
 // Firebase's helper iframe must remain embeddable by this same-origin app.
 headers.set('X-Frame-Options','SAMEORIGIN');
 const csp=headers.get('Content-Security-Policy');
 headers.set('Content-Security-Policy',(csp?csp+'; ':'')+"frame-ancestors 'self'");
 return new Response(response.body,{status:response.status,headers});
}
export async function handle(request,env,fetcher=fetch){
 const url=new URL(request.url);
 if(url.hostname!==HOST)return new Response('Preview host required',{status:403});
 const helper=url.pathname.startsWith('/__/auth/')||url.pathname==='/__/firebase/init.json';
 if(!helper)return env.ASSETS.fetch(request);
 if(!['GET','POST','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405});
 if(url.pathname==='/__/firebase/init.json'){
  if(request.method==='POST')return new Response('Method not allowed',{status:405});
  const response=await env.ASSETS.fetch(request),out=new Headers(response.headers);
  out.set('Cache-Control','no-store, max-age=0');return protectedResponse(new Response(response.body,{status:response.status,headers:out}));
 }
 const target=new URL(url.pathname+url.search,UPSTREAM),headers=new Headers();
 for(const key of ['accept','content-type','user-agent','referer'])if(request.headers.has(key))headers.set(key,request.headers.get(key));
 // Do not forward the site's Cookie or Authorization headers to Firebase.
 try{
  const response=await fetcher(target.href,{method:request.method,headers,body:request.method==='POST'?request.body:undefined,redirect:'manual'});
  const out=new Headers(response.headers);out.set('Cache-Control','no-store, max-age=0');
  out.delete('Set-Cookie');
  return protectedResponse(new Response(response.body,{status:response.status,headers:out}));
 }catch{return new Response('Firebase sign-in helper is unavailable. Retry sign-in.',{status:502,headers:{'Cache-Control':'no-store'}});}
}
// Pages passes ExecutionContext as the third argument; it is not our fetch seam.
export default {fetch(request,env){return handle(request,env);}};
