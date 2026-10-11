export function deadline(promise, label, ms=15000){
 let timer;const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>{const error=Error(label+" 시간이 초과됐습니다.");error.code="library/timeout";reject(error);},ms);});
 return Promise.race([promise,timeout]).finally(()=>clearTimeout(timer));
}
const PACK_PREFIX='D9GZ1:';
const MAX_EXPANDED=2500000;
export async function unpackPrivatePayload(payload){
 if(typeof payload!=='string')throw Error('자료 본문 형식이 올바르지 않습니다.');
 if(!payload.startsWith(PACK_PREFIX)){if(new TextEncoder().encode(payload).length>MAX_EXPANDED)throw Error('자료 크기를 확인하세요.');return payload;}
 if(typeof DecompressionStream!=='function')throw Error('압축 자료를 열려면 Safari 또는 Chrome을 최신 버전으로 업데이트하세요.');
 const encoded=payload.slice(PACK_PREFIX.length);if(encoded.length>750000||! /^[A-Za-z0-9+/]+={0,2}$/.test(encoded))throw Error('압축 자료 형식을 확인하세요.');
 const bytes=Uint8Array.from(atob(encoded),x=>x.charCodeAt(0));const reader=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')).getReader();const chunks=[];let length=0;
 try{while(true){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>MAX_EXPANDED){await reader.cancel();throw Error('자료 압축 해제 크기를 초과했습니다.');}chunks.push(value);}}finally{reader.releaseLock();}
 return new TextDecoder('utf-8',{fatal:true}).decode(await new Blob(chunks).arrayBuffer());
}
export async function packPrivatePayload(payload){
 if(new TextEncoder().encode(payload).length>MAX_EXPANDED)throw Error('자료는 2.5MB 이하로 준비하세요.');
 if(typeof CompressionStream!=='function')return payload;
 const bytes=new Uint8Array(await new Response(new Blob([payload]).stream().pipeThrough(new CompressionStream('gzip'))).arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));return PACK_PREFIX+btoa(binary);
}
export async function loadPrivatePayload({projectId,idToken,appCheckToken,signal,fetchImpl=fetch,timeoutMs=20000}){
 if(!idToken)throw Error("로그인 인증이 필요합니다.");
 const controller=new AbortController();let timedOut=false;
 const abort=()=>controller.abort();if(signal?.aborted)abort();signal?.addEventListener("abort",abort,{once:true});
 const timer=setTimeout(()=>{timedOut=true;controller.abort();},timeoutMs);
 try{
  const headers={Authorization:"Bearer "+idToken};if(appCheckToken)headers["X-Firebase-AppCheck"]=appCheckToken;
  const response=await fetchImpl("https://firestore.googleapis.com/v1/projects/"+encodeURIComponent(projectId)+"/databases/(default)/documents/privateLibrary/main",{headers,signal:controller.signal,cache:"no-store",credentials:"omit"});
  if(!response.ok){const error=Error("서버 응답 "+response.status);error.code=response.status===403?"permission-denied":response.status===401?"unauthenticated":"library/http-"+response.status;throw error;}
  const document=await response.json(),payload=document.fields?.payload?.stringValue;
  if(typeof payload!=="string")throw Error("자료 본문을 확인할 수 없습니다.");return await unpackPrivatePayload(payload);
 }catch(error){if(timedOut){const timeout=Error("자료 수신 시간이 초과됐습니다.");timeout.code="library/timeout";throw timeout;}throw error;}
 finally{clearTimeout(timer);signal?.removeEventListener("abort",abort);}
}
