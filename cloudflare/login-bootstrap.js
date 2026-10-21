/* Preview only: make an unloaded/failed authentication module visible. */
(()=>{
 'use strict';
 if(location.hostname!=='dra9on-cinema.pages.dev')return;
 const login=document.getElementById('login'),redirect=document.getElementById('login-redirect');
 const feedback=document.createElement('p');feedback.id='login-feedback';feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');login.after(feedback);
 let ready=false,diagnostic=false,timer;
 const report=text=>{feedback.textContent=text;};
 const fail=()=>{clearTimeout(timer);login.disabled=false;redirect.disabled=false;report('로그인 연결을 준비하지 못했습니다. 네트워크·콘텐츠 차단을 확인하고 새로고침 후 다시 시도하세요. (library/module-not-ready)');};
 window.D9PreviewLibrary=Object.freeze({
  ready(){ready=true;clearTimeout(timer);login.disabled=false;redirect.disabled=false;login.textContent='Google 계정으로 로그인';if(!diagnostic)report('로그인 준비가 끝났습니다. Google 계정으로 로그인을 눌러주세요.');},
  error(text){diagnostic=true;clearTimeout(timer);login.disabled=false;redirect.disabled=false;report(text);},
 });
 document.addEventListener('click',event=>{
  const button=event.target.closest?.('#login,#login-redirect');if(!button||ready)return;
  event.preventDefault();event.stopImmediatePropagation();
  const connect=document.querySelector('.functional-service-gate button');
  if(!connect){fail();return;}
  report('Google 로그인에 필요한 보안 연결을 준비하고 있습니다… 준비가 끝나면 로그인 버튼을 다시 눌러주세요.');
  login.disabled=true;redirect.disabled=true;login.textContent='로그인 연결 준비 중…';
  clearTimeout(timer);timer=setTimeout(fail,25000);connect.click();
 },true);
 // This marker resumes only an explicitly started sign-in, never authorizes data.
 try{if(sessionStorage.getItem('d9-preview-login-pending-v1'))document.querySelector('.functional-service-gate button')?.click();}catch{}
})();
