export const PENDING='d9-preview-login-pending-v1';
export function errorText(error){
 const code=/^[a-z][a-z0-9/-]{1,70}$/i.test(error?.code||'')?error.code:'auth/unknown';
 const reasons={
  'auth/popup-blocked':'로그인 팝업이 차단됐습니다. 아래 현재 창 로그인 버튼을 이용하세요.',
  'auth/popup-closed-by-user':'Google 로그인 창이 닫혔습니다. 다시 누르거나 현재 창으로 로그인하세요.',
  'auth/cancelled-popup-request':'다른 로그인 요청이 진행 중입니다. 잠시 후 다시 시도하세요.',
  'auth/unauthorized-domain':'이 사이트 주소가 Firebase 로그인 허용 목록에 없습니다. 운영자에게 알려주세요.',
  'auth/network-request-failed':'Google 로그인에 연결하지 못했습니다. 네트워크·콘텐츠 차단을 확인하세요.',
  'auth/web-storage-unsupported':'이 브라우저에서 로그인 저장소를 사용할 수 없습니다. 일반 Safari 또는 Chrome 창에서 다시 시도하세요.',
  'auth/redirect-empty':'Google 로그인 후 인증 결과가 돌아오지 않았습니다. 브라우저 저장소 제한 또는 로그인 취소 때문일 수 있습니다. 다시 시도하거나 PC의 팝업 로그인을 이용하세요.',
  'library/timeout':'로그인 응답이 지연되고 있습니다. 팝업 차단을 확인하거나 현재 창으로 로그인하세요.',
 };
 return (reasons[code]||'로그인하지 못했습니다. 새로고침 후 다시 시도하고 계속되면 아래 오류 코드를 알려주세요.')+' ('+code+')';
}
export function mobileBrowser(nav){return /iPhone|iPad|iPod|Android/.test(nav.userAgent||'')||(nav.platform==='MacIntel'&&nav.maxTouchPoints>1);}
export function installPreviewLogin({auth,GoogleAuthProvider,signInWithPopup,signInWithRedirect,getRedirectResult,deadline,document:doc=document,window:win=window,navigator:nav=navigator,storage,clock=Date.now}){
 const popup=doc.getElementById('login'),redirect=doc.getElementById('login-redirect');let busy=false;
 const status=text=>{win.D9PreviewLibrary?.error(text);doc.getElementById('status').textContent=text;};
 const provider=()=>{const p=new GoogleAuthProvider();p.setCustomParameters({prompt:'select_account'});return p;};
 function clearPending(){try{storage?.removeItem(PENDING);}catch{}}
 async function start(useRedirect){
  if(busy)return;busy=true;popup.disabled=true;redirect.disabled=true;
  status(useRedirect?'현재 창에서 Google 로그인으로 이동합니다…':'Google 로그인 창에서 계정을 선택하세요.');
  // error() may enable controls; keep both disabled until this attempt settles.
  popup.disabled=true;redirect.disabled=true;
  try{
   if(useRedirect){
    try{if(!storage)throw Error();storage.setItem(PENDING,String(clock()));if(!storage.getItem(PENDING))throw Error();}
    catch{throw {code:'auth/web-storage-unsupported'};}
    await deadline(signInWithRedirect(auth,provider()),'Google 로그인 이동',15000);
   }else await deadline(signInWithPopup(auth,provider()),'Google 로그인',45000);
  }catch(error){clearPending();status(errorText(error));}
  finally{busy=false;popup.disabled=false;redirect.disabled=false;}
 }
 popup.addEventListener('click',()=>start(mobileBrowser(nav)));
 redirect.addEventListener('click',()=>start(true));
 return {async restore(){
  let pending=0;try{pending=Number(storage?.getItem(PENDING));}catch{}
  try{
   const result=await deadline(getRedirectResult(auth),'로그인 결과 확인',15000);
   await deadline(auth.authStateReady(),'로그인 상태 확인',15000);
   if(pending&&clock()-pending<600000&&!result&&!auth.currentUser)status(errorText({code:'auth/redirect-empty'}));
  }catch(error){status(errorText(error));}
  finally{clearPending();}
 }};
}
