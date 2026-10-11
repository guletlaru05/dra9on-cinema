import {deadline,loadPrivatePayload} from "./library-transport.js?v=20261011-platforms9";
import {createLibraryUI} from "./library-ui.js?v=20261011-platforms9";
import {initializeApp} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import {getAuth,GoogleAuthProvider,signInWithPopup,signInWithRedirect,getRedirectResult,signOut,onAuthStateChanged,setPersistence,browserSessionPersistence,getIdToken} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import {initializeFirestore,memoryLocalCache,doc,setDoc,serverTimestamp} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import {initializeAppCheck,ReCaptchaEnterpriseProvider,getToken} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app-check.js";
const $=id=>document.getElementById(id);
let entries=[],groups=[],generation=0,ready=false;
const message=t=>$("status").textContent=t;
function clear(){clearUI();}
function validate(value){
 if(!value||value.version!==1||!Array.isArray(value.categories)||!Array.isArray(value.items)||value.items.length>500)throw Error("지원하지 않는 자료 형식입니다.");
 const categories=value.categories;
 if(categories.some(x=>typeof x!=="string"||x.length>80)||new Set(categories).size!==categories.length)throw Error("카테고리를 확인하세요.");
 if(value.imageSources!=null&&(typeof value.imageSources!=="object"||Array.isArray(value.imageSources)||Object.keys(value.imageSources).length>20||Object.values(value.imageSources).some(x=>typeof x!=="string"||x.length>150000||!/^data:image\/(?:jpeg|webp);base64,[A-Za-z0-9+/]+={0,2}$/.test(x))))throw Error("씬 예시 이미지 형식을 확인하세요.");
 for(const item of value.items){
  if(!item||typeof item.title!=="string"||typeof item.body!=="string"||typeof item.kind!=="string"||!Array.isArray(item.categories)||!item.categories.every(x=>categories.includes(x)))throw Error("자료 항목을 확인하세요.");
  if(!Array.isArray(item.links)||item.links.some(x=>{try{return typeof x.label!=="string"||new URL(x.url).protocol!=="https:";}catch{return true;}}))throw Error("출처 링크는 HTTPS 주소여야 합니다.");
  if(item.prompt!=null&&typeof item.prompt!=="string")throw Error("프롬프트 형식을 확인하세요.");
  if(item.summary!=null&&typeof item.summary!=="string")throw Error("요약 형식을 확인하세요.");
  if(item.tools!=null&&(!Array.isArray(item.tools)||item.tools.some(x=>typeof x!=="string")))throw Error("툴 분류를 확인하세요.");
  if(item.sections!=null&&(!Array.isArray(item.sections)||item.sections.some(x=>typeof x.title!=="string"||typeof x.text!=="string")))throw Error("설명 형식을 확인하세요.");
  if(item.image!=null&&(!/^data:image\/jpeg;base64,[A-Za-z0-9+/]+={0,2}$/.test(item.image.data)||item.image.data.length>150000||typeof item.image.alt!=="string"||typeof item.image.caption!=="string"))throw Error("예시 이미지는 작은 JPEG 파일이어야 합니다.");
  if(item.imageRef?.aspect!=null&&(!Number.isFinite(item.imageRef.aspect)||item.imageRef.aspect<0.5||item.imageRef.aspect>3))throw Error("이미지 비율을 확인하세요.");
  if(item.imageRef!=null&&(!value.imageSources?.[item.imageRef.key]||!Number.isInteger(item.imageRef.row)||!Number.isInteger(item.imageRef.col)||item.imageRef.row<0||item.imageRef.row>3||item.imageRef.col<0||item.imageRef.col>2||typeof item.imageRef.alt!=="string"))throw Error("씬 예시 위치를 확인하세요.");
  if(item.checks!=null&&(!Array.isArray(item.checks)||item.checks.length>20||item.checks.some(x=>typeof x!=="string")))throw Error("체크리스트 형식을 확인하세요.");
  if(item.examples!=null){if(!Array.isArray(item.examples)||item.examples.length>8)throw Error("비교 예시 형식을 확인하세요.");for(const example of item.examples){if(!example||typeof example.title!=="string"||typeof example.caption!=="string"||!example.imageRef)throw Error("비교 예시 설명을 확인하세요.");
   if(example.imageRef.aspect!=null&&(!Number.isFinite(example.imageRef.aspect)||example.imageRef.aspect<0.5||example.imageRef.aspect>3))throw Error("예시 비율을 확인하세요.");
   if(example.imageRef!=null&&(!value.imageSources?.[example.imageRef.key]||!Number.isInteger(example.imageRef.row)||!Number.isInteger(example.imageRef.col)||example.imageRef.row<0||example.imageRef.row>3||example.imageRef.col<0||example.imageRef.col>2||typeof example.imageRef.alt!=="string"))throw Error("씬 예시 위치를 확인하세요.");
  }}
 }
 if(value.learningPath!=null&&(!Array.isArray(value.learningPath)||value.learningPath.some(x=>typeof x.title!=="string"||typeof x.text!=="string"||!categories.includes(x.category))))throw Error("학습 순서를 확인하세요.");
 return value;
}
const {display,clear:clearUI}=createLibraryUI();
async function boot(){
 if(!window.D9_ENGAGEMENT_CONFIG){message("연결 설정을 불러오지 못했습니다. 새로고침하세요.");return;}
 const config=window.D9_ENGAGEMENT_CONFIG,app=initializeApp(config,"d9-private-library"),auth=getAuth(app),db=initializeFirestore(app,{localCache:memoryLocalCache(),experimentalForceLongPolling:true});
 const appCheck=config.appCheckSiteKey?initializeAppCheck(app,{provider:new ReCaptchaEnterpriseProvider(config.appCheckSiteKey),isTokenAutoRefreshEnabled:true}):null;
 let loadController=null;
 await setPersistence(auth,browserSessionPersistence);
 getRedirectResult(auth).catch(error=>message("로그인 결과를 확인하지 못했습니다. "+(error.code||error.message)));
 $("login-redirect").addEventListener("click",async()=>{const provider=new GoogleAuthProvider();provider.setCustomParameters({prompt:"select_account"});try{await signInWithRedirect(auth,provider);}catch(error){message("로그인하지 못했습니다. "+(error.code||error.message));}});
 const ref=doc(db,"privateLibrary","main");
 $("login").addEventListener("click",async()=>{if(!ready)return;$("login").disabled=true;message("Google 로그인 창에서 계정을 선택하세요.");try{const provider=new GoogleAuthProvider();provider.setCustomParameters({prompt:"select_account"});await signInWithPopup(auth,provider);}catch(error){message(error.code==="auth/popup-blocked"?"팝업을 허용하고 다시 로그인하세요. 인앱 브라우저에서는 Safari 또는 Chrome으로 열어주세요.":"로그인하지 못했습니다. "+(error.code||"네트워크 연결을 확인하세요."));}finally{$("login").disabled=false;}});
 $("logout").addEventListener("click",async()=>{generation++;loadController?.abort();clear();await signOut(auth);});
 async function load(user){
  const ticket=++generation;loadController?.abort();loadController=new AbortController();const signal=loadController.signal;clear();$("gate").hidden=false;$("retry-load").hidden=true;$("load-panel").hidden=!user;$("login").hidden=!!user;
  if(!user)return;
  if(!user.emailVerified||!user.providerData.some(x=>x.providerId==="google.com")){message("확인된 Google 계정으로 로그인하세요.");return;}
  $("load-progress").textContent="1/3 로그인 인증 확인 중…";message("");
  try{
   const idToken=await deadline(getIdToken(user),"로그인 인증");if(ticket!==generation)return;
   $("load-progress").textContent="2/3 브라우저 보안 확인 중…";
   const appCheckToken=appCheck?(await deadline(getToken(appCheck,false),"브라우저 보안 확인")).token:null;if(ticket!==generation)return;
   $("load-progress").textContent="3/3 비공개 자료 불러오는 중…";
   const payload=await loadPrivatePayload({projectId:config.projectId,idToken,appCheckToken,signal});if(ticket!==generation)return;
   const value=validate(JSON.parse(payload));display(value);$("gate").hidden=true;$("load-panel").hidden=true;message("");
  }catch(error){if(ticket!==generation)return;clear();$("retry-load").hidden=false;
   const text=error.code==="permission-denied"?"서버가 접근을 허용하지 않았습니다. 등록된 소유자 계정인지 확인하세요. 보안 확인 문제일 수도 있습니다.":error.code==="unauthenticated"?"로그인 인증이 만료됐습니다. 로그아웃 후 다시 로그인하세요.":error.code==="library/timeout"?error.message+" 아래 버튼으로 다시 불러올 수 있습니다.":"자료를 불러오지 못했습니다. 네트워크 또는 콘텐츠 차단을 확인하고 다시 시도하세요. ("+(error.code||"연결 오류")+")";
   $("load-progress").textContent=text;message("");
  }
 }
 $("retry-load").addEventListener("click",()=>load(auth.currentUser));
 onAuthStateChanged(auth,user=>{$("logout").hidden=!user;if(!user){generation++;loadController?.abort();clear();$("gate").hidden=false;$("load-panel").hidden=true;$("login").hidden=false;message("");return;}load(user);});
 $("import").addEventListener("change",async event=>{
  const file=event.target.files[0];event.target.value="";if(!file)return;if(!auth.currentUser){message("먼저 로그인하세요.");return;}
  const ticket=generation;
  try{if(file.size>750000)throw Error("자료 파일은 750KB 이하로 준비하세요.");const value=validate(JSON.parse(await file.text())),payload=JSON.stringify(value);message("비공개 자료를 저장하고 있습니다.");await setDoc(ref,{payload,updatedAt:serverTimestamp()});if(ticket!==generation)return;display(value);message("비공개 자료 업데이트 완료.");}
  catch(error){message("저장하지 못했습니다. "+(error.code||error.message));}
 });

 ready=true;
}
boot().catch(error=>message("자료실을 시작하지 못했습니다. "+(error.code||error.message)));
