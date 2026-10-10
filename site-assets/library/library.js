import {initializeApp} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import {getAuth,GoogleAuthProvider,signInWithPopup,signOut,onAuthStateChanged,setPersistence,browserSessionPersistence} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import {initializeFirestore,memoryLocalCache,doc,getDocFromServer,setDoc,serverTimestamp} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import {initializeAppCheck,ReCaptchaEnterpriseProvider} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app-check.js";
const $=id=>document.getElementById(id);
let entries=[],groups=[],generation=0,ready=false;
const message=t=>$("status").textContent=t;
function clear(){entries=[];groups=[];$("cards").replaceChildren();$("categories").replaceChildren();$("category").replaceChildren(new Option("전체 분야",""));$("kind").replaceChildren(new Option("전체 종류",""));$("search").value="";$("overview").textContent="";$("result").textContent="";$("library").hidden=true;}
function validate(value){
 if(!value||value.version!==1||!Array.isArray(value.categories)||!Array.isArray(value.items)||value.items.length>500)throw Error("지원하지 않는 자료 형식입니다.");
 const categories=value.categories;
 if(categories.some(x=>typeof x!=="string"||x.length>80)||new Set(categories).size!==categories.length)throw Error("카테고리를 확인하세요.");
 for(const item of value.items){
  if(!item||typeof item.title!=="string"||typeof item.body!=="string"||typeof item.kind!=="string"||!Array.isArray(item.categories)||!item.categories.every(x=>categories.includes(x)))throw Error("자료 항목을 확인하세요.");
  if(!Array.isArray(item.links)||item.links.some(x=>{try{return typeof x.label!=="string"||new URL(x.url).protocol!=="https:";}catch{return true;}}))throw Error("출처 링크는 HTTPS 주소여야 합니다.");
  if(item.prompt!=null&&typeof item.prompt!=="string")throw Error("프롬프트 형식을 확인하세요.");
 }
 return value;
}
function el(tag,text,className){const node=document.createElement(tag);if(text!=null)node.textContent=text;if(className)node.className=className;return node;}
function render(){
 const query=$("search").value.trim().toLocaleLowerCase(),category=$("category").value,kind=$("kind").value;
 const shown=entries.filter(x=>(!category||x.categories.includes(category))&&(!kind||x.kind===kind)&&(!query||[x.title,x.body,x.prompt||"",...(x.tags||[])].join(" ").toLocaleLowerCase().includes(query)));
 $("cards").replaceChildren();
 for(const item of shown){
  const card=el("article",null,"card");card.append(el("div",item.kind+" / "+item.categories.join(" · "),"meta"),el("h2",item.title),el("p",item.body));
  if(item.prompt){const details=el("details"),pre=el("pre",item.prompt),copy=el("button","프롬프트 복사");copy.type="button";copy.addEventListener("click",async()=>{try{await navigator.clipboard.writeText(item.prompt);copy.textContent="복사 완료";}catch{message("프롬프트 텍스트를 길게 눌러 복사하세요.");}});details.append(el("summary","응용 프롬프트 펼치기"),pre,copy);card.append(details);}
  if(item.tags?.length)card.append(el("p",item.tags.map(x=>"#"+x).join(" "),"tags"));
  for(const source of item.links){const a=el("a",source.label+" ↗");a.href=source.url;a.target="_blank";a.rel="noopener noreferrer";card.append(a);}
  $("cards").append(card);
 }
 $("result").textContent=shown.length+" / "+entries.length+"개 자료";
 for(const b of $("categories").children)b.setAttribute("aria-pressed",String(b.dataset.category===category));
}
function display(value){
 entries=value.items;groups=value.categories;$("category").replaceChildren(new Option("전체 분야",""));groups.forEach(x=>$("category").add(new Option(x,x)));
 $("kind").replaceChildren(new Option("전체 종류",""));[...new Set(entries.map(x=>x.kind))].forEach(x=>$("kind").add(new Option(x,x)));
 $("categories").replaceChildren();for(const x of ["",...groups]){const b=el("button",x||"전체");b.type="button";b.dataset.category=x;b.addEventListener("click",()=>{$("category").value=x;render();});$("categories").append(b);}
 $("overview").textContent=entries.length+"개 자료 · "+groups.length+"개 분야 · "+(value.updated||"")+" · 출처 요약 / 직접 작성한 학습 예시";
 $("library").hidden=false;render();
}
async function boot(){
 if(!window.D9_ENGAGEMENT_CONFIG){message("연결 설정을 불러오지 못했습니다. 새로고침하세요.");return;}
 const config=window.D9_ENGAGEMENT_CONFIG,app=initializeApp(config,"d9-private-library"),auth=getAuth(app),db=initializeFirestore(app,{localCache:memoryLocalCache()});
 if(config.appCheckSiteKey)initializeAppCheck(app,{provider:new ReCaptchaEnterpriseProvider(config.appCheckSiteKey),isTokenAutoRefreshEnabled:true});
 await setPersistence(auth,browserSessionPersistence);
 const ref=doc(db,"privateLibrary","main");
 $("login").addEventListener("click",async()=>{if(!ready)return;$("login").disabled=true;message("Google 로그인 창에서 계정을 선택하세요.");try{const provider=new GoogleAuthProvider();provider.setCustomParameters({prompt:"select_account"});await signInWithPopup(auth,provider);}catch(error){message(error.code==="auth/popup-blocked"?"팝업을 허용하고 다시 로그인하세요. 인앱 브라우저에서는 Safari 또는 Chrome으로 열어주세요.":"로그인하지 못했습니다. "+(error.code||"네트워크 연결을 확인하세요."));}finally{$("login").disabled=false;}});
 $("logout").addEventListener("click",async()=>{generation++;clear();await signOut(auth);});
 onAuthStateChanged(auth,async user=>{
  const ticket=++generation;clear();$("logout").hidden=!user;$("gate").hidden=false;
  if(!user){message("");return;}
  if(!user.emailVerified||!user.providerData.some(x=>x.providerId==="google.com")){message("확인된 Google 계정으로 로그인하세요.");return;}
  message("서버에서 자료실 권한을 확인하고 있습니다.");
  try{const snapshot=await getDocFromServer(ref);if(ticket!==generation)return;$("gate").hidden=true;$("library").hidden=false;
   if(!snapshot.exists()){message("자료실 권한이 확인되었습니다. 자료 업데이트에서 준비된 JSON 파일을 선택하세요.");return;}
   display(validate(JSON.parse(snapshot.data().payload)));message("");
  }catch(error){if(ticket!==generation)return;clear();message(error.code==="permission-denied"?"이 계정에는 자료실 접근 권한이 없습니다. 소유자 계정으로 다시 로그인하세요.":"자료를 불러오지 못했습니다. "+(error.code||error.message));}
 });
 $("import").addEventListener("change",async event=>{
  const file=event.target.files[0];event.target.value="";if(!file)return;if(!auth.currentUser){message("먼저 로그인하세요.");return;}
  const ticket=generation;
  try{if(file.size>750000)throw Error("자료 파일은 750KB 이하로 준비하세요.");const value=validate(JSON.parse(await file.text())),payload=JSON.stringify(value);message("비공개 자료를 저장하고 있습니다.");await setDoc(ref,{payload,updatedAt:serverTimestamp()});if(ticket!==generation)return;display(value);message("비공개 자료 업데이트 완료.");}
  catch(error){message("저장하지 못했습니다. "+(error.code||error.message));}
 });
 ["search","category","kind"].forEach(x=>$(x).addEventListener(x==="search"?"input":"change",render));
 ready=true;
}
boot().catch(error=>message("자료실을 시작하지 못했습니다. "+(error.code||error.message)));

