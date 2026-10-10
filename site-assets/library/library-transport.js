export function deadline(promise, label, ms=15000){
 let timer;const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>{const error=Error(label+" 시간이 초과됐습니다.");error.code="library/timeout";reject(error);},ms);});
 return Promise.race([promise,timeout]).finally(()=>clearTimeout(timer));
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
  if(typeof payload!=="string")throw Error("자료 본문을 확인할 수 없습니다.");return payload;
 }catch(error){if(timedOut){const timeout=Error("자료 수신 시간이 초과됐습니다.");timeout.code="library/timeout";throw timeout;}throw error;}
 finally{clearTimeout(timer);signal?.removeEventListener("abort",abort);}
}
