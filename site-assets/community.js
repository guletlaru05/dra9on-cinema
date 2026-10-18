import {initializeApp} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js';
import {getAuth,signInAnonymously,GoogleAuthProvider,signInWithPopup,signInWithRedirect,getRedirectResult,signOut,onAuthStateChanged,browserLocalPersistence,setPersistence} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js';
import {initializeFirestore,memoryLocalCache,doc,collection,getDoc,getDocs,query,orderBy,limit,startAfter,writeBatch,serverTimestamp,updateDoc} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js';
import {initializeAppCheck,ReCaptchaEnterpriseProvider,getToken} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-app-check.js';
import {createBoardAlerts} from './board-alerts.js';
const $=id=>document.getElementById(id),lang=document.documentElement.lang,en=lang==='en',t=(ko,eng)=>lang==='ko'?ko:window.D9Locale?.translate(ko,eng)||eng;
const readOnlyPreview=document.body.dataset.loungePreview==='true';
const config=window.D9_ENGAGEMENT_CONFIG,app=initializeApp(config,'d9-community'),auth=getAuth(app);
const db=initializeFirestore(app,{localCache:memoryLocalCache(),experimentalForceLongPolling:true});
const protection=initializeAppCheck(app,{provider:new ReCaptchaEnterpriseProvider(config.appCheckSiteKey),isTokenAutoRefreshEnabled:true});
const owner=user=>user?.email==='guletlaru05@gmail.com'&&user.emailVerified&&user.providerData.some(p=>p.providerId==='google.com');
const alerts=createBoardAlerts({auth,owner,t,appCheckToken:()=>deadline(getToken(protection,false)),baseline:async send=>{let cursor;for(let page=0;page<100;page++){await secured();const parts=[orderBy('createdAt','desc'),limit(10)];if(cursor)parts.push(startAfter(cursor));const result=await deadline(getDocs(query(collection(db,'communityPosts'),...parts)));await send(result.docs.map(d=>d.id),result.size<10);if(result.size<10)return;cursor=result.docs.at(-1);}throw Error('baseline incomplete');}});
let posts=[],lastPost,lastArchive,loading=false,writing=false,generation=0;
function text(id,value){$(id).textContent=value;}
function element(tag,content='',className=''){const el=document.createElement(tag);el.textContent=content;if(className)el.className=className;return el;}
function deadline(p,ms=20000){let timer;return Promise.race([p,new Promise((_,reject)=>timer=setTimeout(()=>reject(Error(t('연결 시간이 초과됐습니다. 다시 시도하세요.','Connection timed out. Please retry.'))),ms))]).finally(()=>clearTimeout(timer));}
async function secured(){await deadline(getToken(protection,false));}
function failure(error){return error.code==='permission-denied'?t('서버가 허용하지 않은 요청입니다. 보안 확인 또는 글쓰기 간격을 확인하고 다시 시도하세요.','The server denied this request. Check security verification or the posting interval and retry.'):t('처리하지 못했습니다. ','Could not complete this request. ')+(error.code||error.message||'');}
function date(value){return value?.toDate?value.toDate().toLocaleString(({ko:'ko-KR',en:'en-US',ja:'ja-JP',es:'es-ES'})[lang]||'en-US',{dateStyle:'medium',timeStyle:'short'}):'';}
function topic(value){return ({story:t('이야기','Story'),making:t('제작','Filmmaking'),character:t('캐릭터','Character'),other:t('기타','Other')})[value]||'';}
function postRow(snapshot){
 const data=snapshot.data(),row=element('tr','','board-row'),title=element('td','','board-title-cell'),link=element('a',data.title,'board-title-link');
 link.href='#post-'+snapshot.id;title.append(link);row.append(title);
 const values=[topic(data.topic),data.official?'DRA9ON CINEMA':data.nickname,date(data.createdAt),data.answer?t('답변 완료','Answered'):t('답변 대기','Awaiting reply')];
 const names=['topic','author','date','state'];
 values.forEach((value,index)=>row.append(element('td',value,'board-'+names[index]+'-cell')));
 if(data.answer)row.classList.add('has-answer');
 return row;
}
function postCard(snapshot){
 const data=snapshot.data(),card=element('article','','board-post');
 card.id='post-'+snapshot.id;if(data.answer)card.classList.add('has-answer');
 const heading=element('h3',data.title),meta=element('p',[topic(data.topic),data.official?'DRA9ON CINEMA · '+t('제작자','Creator'):t('방문자','Visitor')+' · '+data.nickname,date(data.createdAt),data.answer?t('답변 완료','Answered'):t('답변 대기','Awaiting reply')].join(' · '),'board-meta');heading.tabIndex=-1;card.append(heading,meta);
 if(data.answer)card.prepend(element('span',t('운영자 답변','Creator replied'),'board-replied-badge'));
 card.append(element('p',data.body,'qna-body'));
 if(data.answer){card.append(element('p','DRA9ON CINEMA · '+t('제작자 답변','Creator reply'),'section-eyebrow'),element('p',data.answer,'qna-body'),element('p',date(data.answeredAt),'board-meta'));}
 if(owner(auth.currentUser)&&!readOnlyPreview){
  const field=element('textarea');field.value=data.answer;field.rows=5;field.maxLength=5000;field.setAttribute('aria-label',t('공개 답변 작성','Write a public reply'));card.append(field);
  const actions=element('div','','tutorial-actions'),save=element('button',t('답변 게시','Publish reply'),'button button-white'),hide=element('button',t('글 숨기기','Hide post'),'button button-glass'),status=element('p','','tutorial-notice');save.type=hide.type='button';status.setAttribute('role','status');actions.append(save,hide);card.append(actions,status);
  save.addEventListener('click',async()=>{const answer=field.value.trim();if(answer.length<2){status.textContent=t('답변을 2자 이상 적어주세요.','Write at least 2 characters.');return;}save.disabled=hide.disabled=true;try{await secured();await deadline(updateDoc(snapshot.ref,{answer,answeredAt:serverTimestamp(),updatedAt:serverTimestamp()}));await alerts.changed(snapshot.id);status.textContent=t('답변을 공개 게시했습니다.','Reply published.');await loadPosts();}catch(error){status.textContent=failure(error);}finally{save.disabled=hide.disabled=false;}});
  hide.addEventListener('click',async()=>{if(!window.confirm(t('글을 공개 게시판에서 숨길까요? 보관함에서 복원할 수 있습니다.','Hide this post from the public board? You can restore it from the archive.')))return;save.disabled=hide.disabled=true;try{await secured();const current=await deadline(getDoc(snapshot.ref));if(!current.exists())return;const batch=writeBatch(db);batch.set(doc(db,'communityArchive',snapshot.id),{post:current.data(),archivedAt:serverTimestamp(),state:'hidden'});batch.delete(snapshot.ref);await deadline(batch.commit());await alerts.removed(snapshot.id);location.hash='board';await loadPosts();text('board-owner-status',t('글을 숨겼습니다. 보관함에서 복원할 수 있습니다.','Post hidden. It can be restored from the archive.'));}catch(error){status.textContent=failure(error);}finally{save.disabled=hide.disabled=false;}});
 }
 return card;
}
function renderPosts(){
 const filter=$('board-filter').value,visible=posts.filter(p=>filter==='all'||p.data().topic===filter),focused=location.hash.match(/^#post-([A-Za-z0-9_-]{1,128})$/)?.[1];
 $('board-posts').replaceChildren(...visible.map(postRow));
 const selected=focused&&posts.find(p=>p.id===focused);
 $('board-detail-content').replaceChildren(...(selected?[postCard(selected)]:[]));
 if(focused){text('board-status',selected?'':loading?t('게시판을 불러오는 중…','Loading the board…'):t('글을 찾을 수 없습니다. 숨겨졌거나 삭제된 글일 수 있습니다.','Post unavailable. It may have been hidden or removed.'));return;}
 if(!visible.length)text('board-status',posts.length?t('불러온 글 중 이 분야의 글이 없습니다. 이전 글 더 보기를 눌러보세요.','No loaded posts match this topic. Try loading previous posts.'):t('아직 글이 없습니다. 첫 이야기를 남겨주세요.','No posts yet. Start the first conversation.'));else text('board-status','');
}
async function loadPosts(more=false){
 if(loading)return;loading=true;const ticket=generation;$('board-more').disabled=$('board-refresh').disabled=true;text('board-status',t('게시판을 불러오는 중…','Loading the board…'));
 try{await secured();const constraints=[orderBy('createdAt','desc'),limit(10)];if(more&&lastPost)constraints.push(startAfter(lastPost));const result=await deadline(getDocs(query(collection(db,'communityPosts'),...constraints)));if(ticket!==generation)return;posts=more?[...posts,...result.docs]:result.docs;lastPost=result.docs.at(-1);const focused=location.hash.match(/^#post-([A-Za-z0-9_-]{1,128})$/)?.[1];if(focused&&!posts.some(p=>p.id===focused)){const direct=await deadline(getDoc(doc(db,'communityPosts',focused)));if(direct.exists())posts.push(direct);}$('board-more').hidden=result.size<10;renderPosts();if(focused&&!posts.some(p=>p.id===focused))text('board-status',t('글을 찾을 수 없습니다. 숨겨졌거나 삭제된 글일 수 있습니다.','Post unavailable. It may have been hidden or removed.'));if(focused)requestAnimationFrame(()=>document.getElementById('post-'+focused)?.scrollIntoView({block:'start'}));}
 catch(error){if(ticket===generation)text('board-status',failure(error));}finally{loading=false;$('board-more').disabled=$('board-refresh').disabled=false;if(ticket!==generation)loadPosts();}
}
async function publish(event){
 event.preventDefault();if(readOnlyPreview)return;if(writing)return;if(!$('board-form').reportValidity())return;if($('board-website').value)return;
 const nickname=$('board-nickname').value.trim(),title=$('board-title').value.trim(),body=$('board-body').value.trim();
 if(nickname.length<2||title.length<2||body.length<10){text('board-write-status',t('닉네임·제목은 2자, 내용은 10자 이상 적어주세요.','Use at least 2 characters for nickname and title, and 10 for the post.'));return;}
 writing=true;$('board-submit').disabled=true;text('board-write-status',t('게시하는 중… 창을 닫지 마세요.','Publishing… Keep this page open.'));
 try{await secured();if(!auth.currentUser)await deadline(signInAnonymously(auth));const user=auth.currentUser,creator=owner(user),rateRef=doc(db,'communityLimits',user.uid);
 if(!creator){const rate=await deadline(getDoc(rateRef));if(rate.exists()&&Date.now()-rate.data().lastAt.toMillis()<600000)throw Error(t('도배 방지를 위해 이전 글 작성 후 10분 뒤에 게시할 수 있습니다.','To prevent spam, wait 10 minutes after your previous post.'));}
 const ref=doc(collection(db,'communityPosts')),batch=writeBatch(db);batch.set(ref,{nickname:creator?'DRA9ON CINEMA':nickname,title,body,topic:$('board-topic').value,authorUid:user.uid,official:creator,answer:'',answeredAt:null,createdAt:serverTimestamp(),updatedAt:serverTimestamp()});if(!creator)batch.set(rateRef,{lastAt:serverTimestamp(),lastPostId:ref.id});await deadline(batch.commit());await alerts.post(ref.id);$('board-form').reset();location.hash='post-'+ref.id;text('board-write-status',t('게시했습니다. 글과 제작자의 답변은 이 게시판에서 볼 수 있습니다.','Posted. Your post and the creator’s reply appear on this board.'));await loadPosts();}
 catch(error){text('board-write-status',failure(error));}finally{writing=false;$('board-submit').disabled=false;}
}
async function archive(more=false){
 if(!owner(auth.currentUser))return;const ticket=generation;$('board-archive-refresh').disabled=true;
 try{await secured();const constraints=[orderBy('archivedAt','desc'),limit(20)];if(more&&lastArchive)constraints.push(startAfter(lastArchive));const result=await deadline(getDocs(query(collection(db,'communityArchive'),...constraints)));if(ticket!==generation)return;if(!more)$('board-archive').replaceChildren();for(const snapshot of result.docs){const data=snapshot.data();if(data.state!=='hidden')continue;const card=element('article','','qna-card');card.append(element('h3',data.post.title),element('p',data.post.body,'qna-body'));const restore=element('button',t('복원하기','Restore'),'button button-glass'),status=element('p');restore.type='button';restore.disabled=readOnlyPreview;status.setAttribute('role','status');card.append(restore,status);restore.addEventListener('click',async()=>{restore.disabled=true;try{await secured();const publicRef=doc(db,'communityPosts',snapshot.id),current=await deadline(getDoc(publicRef));if(current.exists())throw Error(t('이미 공개된 글입니다. 게시판을 새로고침하세요.','This post is already public. Refresh the board.'));const batch=writeBatch(db);batch.set(publicRef,{...data.post,updatedAt:serverTimestamp()});batch.update(snapshot.ref,{state:'restored'});await deadline(batch.commit());await alerts.changed(snapshot.id);card.remove();await loadPosts();text('board-owner-status',t('게시글을 복원했습니다.','Post restored.'));}catch(error){status.textContent=failure(error);}finally{restore.disabled=false;}});$('board-archive').append(card);}lastArchive=result.docs.at(-1);$('board-archive-more').hidden=result.size<20;text('board-owner-status',result.empty?t('보관한 글이 없습니다.','No archived posts.'):'');}
 catch(error){if(ticket===generation)text('board-owner-status',failure(error));}finally{$('board-archive-refresh').disabled=false;}
}
async function boot(){
 await setPersistence(auth,browserLocalPersistence);
 $('board-form').addEventListener('submit',publish);$('board-filter').addEventListener('change',renderPosts);$('board-more').addEventListener('click',()=>loadPosts(true));$('board-refresh').addEventListener('click',()=>loadPosts());
 window.addEventListener('hashchange',()=>{const id=location.hash.match(/^#post-([A-Za-z0-9_-]{1,128})$/)?.[1];if(id&&!posts.some(p=>p.id===id))void loadPosts();else{renderPosts();if(id)$('board-detail-content').querySelector('h3')?.focus();}});
 $('board-owner-login').addEventListener('click',async()=>{const button=$('board-owner-login');button.disabled=true;text('board-owner-status',t('Google 로그인 창에서 계정을 선택하세요. 창이 열리지 않으면 현재 창에서 로그인을 이용하세요.','Choose your account in the Google window. If it does not open, use Sign in in this tab.'));try{const provider=new GoogleAuthProvider();provider.setCustomParameters({prompt:'select_account'});await deadline(signInWithPopup(auth,provider),30000);}catch(error){text('board-owner-status',failure(error)+t(' 현재 창에서 로그인을 이용하거나 Safari 또는 Chrome에서 열어주세요.',' Use Sign in in this tab, or open the page in Safari or Chrome.'));}finally{button.disabled=false;}});
 $('board-owner-redirect')?.addEventListener('click',async()=>{try{const provider=new GoogleAuthProvider();provider.setCustomParameters({prompt:'select_account'});text('board-owner-status',t('Google 로그인 화면으로 이동합니다.','Opening Google sign-in.'));await signInWithRedirect(auth,provider);}catch(error){text('board-owner-status',failure(error));}});
 getRedirectResult(auth).catch(error=>text('board-owner-status',failure(error)));
 $('board-owner-logout').addEventListener('click',()=>signOut(auth));$('board-archive-refresh').addEventListener('click',()=>archive());$('board-archive-more').addEventListener('click',()=>archive(true));
 onAuthStateChanged(auth,user=>{generation++;$('board-owner-panel').hidden=!owner(user);$('board-owner-login').hidden=owner(user);if($('board-owner-redirect'))$('board-owner-redirect').hidden=owner(user);$('board-owner-logout').hidden=!user||user.isAnonymous;$('board-nickname').readOnly=!!owner(user);if(owner(user))$('board-nickname').value='DRA9ON CINEMA';else if($('board-nickname').value==='DRA9ON CINEMA')$('board-nickname').value='';$('board-archive').replaceChildren();void alerts.session();text('board-owner-status',user&&!user.isAnonymous&&!owner(user)?t('이 계정에는 제작자 관리 권한이 없습니다. 닉네임 글쓰기는 가능합니다.','This account has no creator privileges. Nickname posting is still available.'):'');renderPosts();if(!loading)loadPosts();});
}
boot().catch(error=>text('board-status',failure(error)));

