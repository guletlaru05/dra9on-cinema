import {initializeApp} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js';
import {getAuth,signInAnonymously,GoogleAuthProvider,signInWithPopup,signOut,onAuthStateChanged,browserLocalPersistence,setPersistence} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js';
import {initializeFirestore,memoryLocalCache,doc,getDoc,getDocs,collection,query,orderBy,limit,startAfter,setDoc,writeBatch,serverTimestamp} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js';
import {initializeAppCheck,ReCaptchaEnterpriseProvider,getToken} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-app-check.js';
const $=id=>document.getElementById(id), en=document.documentElement.lang==='en', t=(ko,eng)=>en?eng:ko;
const config=window.D9_ENGAGEMENT_CONFIG;
const app=initializeApp(config,'d9-questions'),auth=getAuth(app);
const db=initializeFirestore(app,{localCache:memoryLocalCache(),experimentalForceLongPolling:true});
const protection=initializeAppCheck(app,{provider:new ReCaptchaEnterpriseProvider(config.appCheckSiteKey),isTokenAutoRefreshEnabled:true});
const owner=user=>user?.email==='guletlaru05@gmail.com'&&user.emailVerified&&user.providerData.some(p=>p.providerId==='google.com');
let lastPublic,lastInbox,version=0,busy=false;
const message=(id,text)=>$(id).textContent=text;
function deadline(p,ms=20000){let timer;return Promise.race([p,new Promise((_,reject)=>timer=setTimeout(()=>reject(Error(t('연결 시간이 초과됐습니다. 다시 시도하세요.','Connection timed out. Please try again.'))),ms))]).finally(()=>clearTimeout(timer));}
function failure(error){return (error.code||'')==='permission-denied'?t('서버가 요청을 허용하지 않았습니다. 계정과 보안 확인 상태를 확인하고 다시 시도하세요.','The server denied this request. Check your account and browser security verification, then retry.'):t('처리하지 못했습니다. 연결을 확인하고 다시 시도하세요. ','Could not complete this request. Check your connection and retry. ')+(error.code||error.message||'');}
async function secured(){await deadline(getToken(protection,false));}
function element(tag,text,className){const node=document.createElement(tag);node.textContent=text;if(className)node.className=className;return node;}
function answerCard(data){const card=element('article','','question-answer qna-card');card.append(element('h3',data.title),element('p',data.question,'qna-body'),element('p',t('DRA9ON CINEMA의 답변','Answer from DRA9ON CINEMA'),'section-eyebrow'),element('p',data.answer,'qna-body'));return card;}
async function publicAnswers(more=false){
 $('qna-public-more').disabled=true;message('qna-public-status',t('공개 답변을 불러오는 중…','Loading public answers…'));
 try{await secured();const constraints=[orderBy('updatedAt','desc'),limit(10)];if(more&&lastPublic)constraints.push(startAfter(lastPublic));const result=await deadline(getDocs(query(collection(db,'questionAnswers'),...constraints)));if(!more)$('qna-public').replaceChildren();result.docs.forEach(d=>$('qna-public').append(answerCard(d.data())));lastPublic=result.docs.at(-1);$('qna-public-more').hidden=result.size<10;message('qna-public-status',result.empty&&!more?t('아직 공개된 방문자 답변이 없습니다. 아래 기본 안내를 먼저 읽어보세요.','No visitor answers have been published yet. Start with the introductory answers below.'):'');}
 catch(error){message('qna-public-status',failure(error));}finally{$('qna-public-more').disabled=false;}
}
async function ownQuestion(user,ticket){
 $('qna-mine').replaceChildren();$('qna-new').hidden=true;$('qna-form').hidden=false;
 if(!user||owner(user))return;
 try{await secured();const result=await deadline(getDoc(doc(db,'questionInbox',user.uid)));if(ticket!==version)return;
 if(result.exists()){const data=result.data();const card=element('article','','qna-card');card.append(element('h3',data.title),element('p',data.body,'qna-body'),element('p',data.status==='pending'?t('답변 대기 중','Awaiting a reply'):t('DRA9ON CINEMA의 답변','Answer from DRA9ON CINEMA'),'section-eyebrow'));if(data.answer)card.append(element('p',data.answer,'qna-body'));$('qna-mine').append(card);$('qna-form').hidden=true;$('qna-new').hidden=data.status==='pending';}}
 catch(error){if(ticket===version)message('qna-status',failure(error));}
}
function inboxCard(snapshot){
 const data=snapshot.data(),card=element('article','','qna-card qna-owner-card');
 card.append(element('p',data.status==='pending'?t('답변 대기','Pending'):t('답변 완료','Answered'),'section-eyebrow'),element('h3',data.title),element('p',data.body,'qna-body'),element('p',data.allowPublic?t('질문자가 익명 공개에 동의했습니다. 개인정보를 지운 공개 문구를 작성하세요.','The sender allows anonymous publication. Remove personal details from the public version.'):t('비공개 답변만 요청한 질문입니다. 공개할 수 없습니다.','Private reply requested. This question cannot be published.')));
 const response=element('textarea','');response.value=data.answer;response.maxLength=5000;response.rows=5;response.setAttribute('aria-label',t('답변 작성','Write an answer'));card.append(response);
 const publication=element('details','');publication.append(element('summary',t('공개 답변 문구 편집','Edit the public answer')));
 const publicTitle=element('input','');publicTitle.value=data.title;publicTitle.maxLength=120;publicTitle.setAttribute('aria-label',t('공개 제목','Public title'));
 const publicBody=element('textarea','');publicBody.value=data.body;publicBody.maxLength=3000;publicBody.rows=4;publicBody.setAttribute('aria-label',t('개인정보를 뺀 공개 질문','Public question without personal details'));
 publication.append(publicTitle,publicBody);if(data.allowPublic)card.append(publication);
 const status=element('p','','tutorial-notice');status.setAttribute('role','status');
 const actions=element('div','','tutorial-actions');const save=element('button',t('비공개 답변 저장','Save private reply'),'button button-glass'),publish=element('button',t('답변 저장·공개','Save and publish'),'button button-white'),hide=element('button',t('공개 답변 내리기','Unpublish answer'),'button button-glass'),archive=element('button',t('보관하기','Archive'),'button button-glass');
 [save,publish,hide,archive].forEach(b=>b.type='button');publish.disabled=!data.allowPublic;
 actions.append(save);if(data.allowPublic)actions.append(publish,hide);actions.append(archive);card.append(actions,status);
 async function update(mode){
  const value=response.value.trim();if(mode!=='archive'&&value.length<2){status.textContent=t('답변을 2자 이상 작성하세요.','Write at least 2 characters.');return;}
  if(mode==='publish'&&(!publicTitle.value.trim()||publicBody.value.trim().length<10)){status.textContent=t('공개 제목과 질문 내용을 확인하세요.','Check the public title and question.');return;}
  [save,publish,hide,archive].forEach(b=>b.disabled=true);
  try{await secured();const batch=writeBatch(db);batch.update(snapshot.ref,{answer:value,status:mode==='archive'?'archived':'answered',updatedAt:serverTimestamp()});
   const ref=doc(db,'questionAnswers',snapshot.id);
   if(mode==='publish')batch.set(ref,{title:publicTitle.value.trim(),question:publicBody.value.trim(),answer:value,topic:data.topic,updatedAt:serverTimestamp()});else batch.delete(ref);
   await deadline(batch.commit());status.textContent=mode==='publish'?t('답변을 저장하고 공개했습니다.','Answer saved and published.'):t('비공개로 저장했습니다. 기존 공개 답변도 내려갔습니다.','Saved privately. Any previous public answer was unpublished.');if(mode==='archive')card.remove();await publicAnswers();
  }catch(error){status.textContent=failure(error);}finally{[save,hide,archive].forEach(b=>b.disabled=false);publish.disabled=!data.allowPublic;}
 }
 save.addEventListener('click',()=>update('save'));publish.addEventListener('click',()=>update('publish'));hide.addEventListener('click',()=>update('hide'));archive.addEventListener('click',()=>update('archive'));return card;
}
async function inbox(more=false){
 if(!owner(auth.currentUser))return;const ticket=version;$('qna-inbox-more').disabled=true;message('qna-owner-status',t('비공개 질문함을 불러오는 중…','Loading the private inbox…'));
 try{await secured();const constraints=[orderBy('createdAt','desc'),limit(20)];if(more&&lastInbox)constraints.push(startAfter(lastInbox));const result=await deadline(getDocs(query(collection(db,'questionInbox'),...constraints)));if(ticket!==version)return;if(!more)$('qna-inbox').replaceChildren();result.docs.filter(d=>d.data().status!=='archived').forEach(d=>$('qna-inbox').append(inboxCard(d)));lastInbox=result.docs.at(-1);$('qna-inbox-more').hidden=result.size<20;message('qna-owner-status',result.empty?t('아직 받은 질문이 없습니다.','No questions received yet.'):t('질문은 비공개입니다. 공개 버튼을 누르기 전 문구를 확인하세요.','Questions are private. Review the wording before publishing.'));}
 catch(error){if(ticket===version)message('qna-owner-status',failure(error));}finally{$('qna-inbox-more').disabled=false;}
}
async function submit(event){
 event.preventDefault();if(busy)return;const form=$('qna-form');if(!form.reportValidity())return;
 const title=$('qna-title').value.trim(),body=$('qna-body').value.trim();if(title.length<2||body.length<10){message('qna-status',t('제목 2자, 질문 10자 이상 적어주세요.','Use at least 2 characters for the title and 10 for the question.'));return;}
 if($('qna-website').value)return;
 busy=true;$('qna-submit').disabled=true;message('qna-status',t('질문을 저장하는 중… 창을 닫지 마세요.','Saving your question… Keep this page open.'));
 try{await secured();if(!auth.currentUser)await deadline(signInAnonymously(auth));if(owner(auth.currentUser))throw Error(t('제작자 계정은 관리 화면에서 답변하세요.','Use the owner panel to answer questions.'));
 const ref=doc(db,'questionInbox',auth.currentUser.uid),existing=await deadline(getDoc(ref));if(existing.exists())throw Error(t('이 브라우저에 남긴 질문이 있습니다. 답변 후 새 질문을 작성하세요.','This browser already has a question. Wait for a reply before starting a new question.'));
 await deadline(setDoc(ref,{title,body,topic:$('qna-topic').value,allowPublic:$('qna-public-consent').checked,createdAt:serverTimestamp(),updatedAt:serverTimestamp(),answer:'',status:'pending'}));form.reset();message('qna-status',t('질문을 비공개로 접수했습니다. 같은 브라우저에서 ‘내 질문·답변 확인’을 눌러 답변을 확인하세요.','Your question was received privately. Return in this browser and use “Check my question and reply”.'));await ownQuestion(auth.currentUser,version);
 }catch(error){message('qna-status',failure(error));}finally{busy=false;$('qna-submit').disabled=false;}
}
async function boot(){
 await setPersistence(auth,browserLocalPersistence);
 $('qna-form').addEventListener('submit',submit);
 $('qna-login').addEventListener('click',async()=>{try{const provider=new GoogleAuthProvider();provider.setCustomParameters({prompt:'select_account'});await signInWithPopup(auth,provider);}catch(error){message('qna-status',failure(error)+t(' 인앱 브라우저라면 Safari 또는 Chrome에서 열어주세요.',' Open in Safari or Chrome if using an in-app browser.'));}});
 $('qna-logout').addEventListener('click',()=>signOut(auth));
 $('qna-mine-refresh').addEventListener('click',()=>ownQuestion(auth.currentUser,version));
 $('qna-public-refresh').addEventListener('click',()=>publicAnswers());$('qna-public-more').addEventListener('click',()=>publicAnswers(true));
 $('qna-inbox-refresh').addEventListener('click',()=>inbox());$('qna-inbox-more').addEventListener('click',()=>inbox(true));
 $('qna-new').addEventListener('click',async()=>{if(!window.confirm(t('이전 비공개 질문과 답변을 영구 삭제하고 새 질문을 작성할까요? 공개된 답변은 유지됩니다.','Permanently delete the previous private question and reply to start another? Published answers remain.')))return;try{await secured();const result=await deadline(getDoc(doc(db,'questionInbox',auth.currentUser.uid)));if(!result.exists()||result.data().status==='pending')return;if(Date.now()-result.data().createdAt.toMillis()<3600000)throw Error(t('접수로부터 1시간 뒤 새 질문을 작성할 수 있습니다.','You can start another question one hour after submission.'));const batch=writeBatch(db);batch.delete(result.ref);await deadline(batch.commit());$('qna-mine').replaceChildren();$('qna-form').hidden=false;$('qna-new').hidden=true;message('qna-status',t('새 질문을 작성할 수 있습니다. 이전 비공개 질문·답변은 삭제됐습니다.','You can write a new question. The previous private question and reply were deleted.'));}catch(error){message('qna-status',failure(error));}});
 onAuthStateChanged(auth,user=>{const ticket=++version;$('qna-owner').hidden=!owner(user);$('qna-logout').hidden=!user||user.isAnonymous;$('qna-login').hidden=owner(user);$('qna-inbox').replaceChildren();message('qna-status','');ownQuestion(user,ticket);if(owner(user))inbox();else if(user&&!user.isAnonymous)message('qna-status',t('질문 작성은 가능하지만 제작자 관리 권한은 없습니다.','You can ask a question, but this account has no owner privileges.'));});
 await publicAnswers();
}
boot().catch(error=>message('qna-status',failure(error)));
