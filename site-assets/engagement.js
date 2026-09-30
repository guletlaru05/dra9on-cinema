/* Public catalogue totals are lazy-loaded and cached; identity starts only in a player. */
(() => {
  const config=window.D9_ENGAGEMENT_CONFIG;
  if(!config)return;
  const en=document.documentElement.lang==='en', t=(ko,eng)=>en?eng:ko;
  const version='12.3.0', sdk='https://www.gstatic.com/firebasejs/'+version+'/';
  const cache=new Map();let servicePromise,applicationPromise;
  function protectedApplication(){
    if(!applicationPromise)applicationPromise=Promise.all([
      import(sdk+'firebase-app.js'),import(sdk+'firebase-app-check.js')
    ]).then(([app,check])=>{
      const application=app.getApps().find(item=>item.name==='d9-engagement')||app.initializeApp(config,'d9-engagement');
      if(!config.appCheckSiteKey)throw new Error('App Check configuration missing');
      const protection=check.initializeAppCheck(application,{
        provider:new check.ReCaptchaEnterpriseProvider(config.appCheckSiteKey),
        isTokenAutoRefreshEnabled:true
      });
      return {application,protection,check};
    });
    return applicationPromise;
  }
  function services(){
    if(!servicePromise)servicePromise=Promise.all([
      protectedApplication(),import(sdk+'firebase-auth.js'),import(sdk+'firebase-firestore.js')
    ]).then(async([{application,protection,check},auth,db])=>{
      await check.getToken(protection);
      const identity=auth.getAuth(application);
      await identity.authStateReady();
      if(!identity.currentUser)await auth.signInAnonymously(identity);
      return {db:db.getFirestore(application),api:db,uid:identity.currentUser.uid};
    }).catch(error=>{servicePromise=null;throw error;});
    return servicePromise;
  }
  function refs(s,id){return [s.api.doc(s.db,'filmStats',id),s.api.doc(s.db,'filmStats',id,'reactions',s.uid)];}
  async function read(id){
    const old=cache.get(id);if(old&&Date.now()-old.at<60000)return old;
    const s=await services(), [total,user]=refs(s,id);
    const [a,b]=await Promise.all([s.api.getDoc(total),s.api.getDoc(user)]);
    const value={views:a.data()?.views||0,likes:a.data()?.likes||0,liked:b.data()?.liked||false,at:Date.now()};
    cache.set(id,value);return value;
  }
  async function change(id,kind){
    const s=await services(),[total,user]=refs(s,id);
    const result=await s.api.runTransaction(s.db,async tx=>{
      const [a,b]=await Promise.all([tx.get(total),tx.get(user)]);
      const stats=a.data()||{views:0,likes:0};
      const before=b.data()||{liked:false,viewedAt:s.api.Timestamp.fromMillis(0)};
      if(kind==='view'&&Date.now()-before.viewedAt.toMillis()<86400000)
        return {...stats,liked:before.liked};
      const after={...before};
      if(kind==='like')after.liked=!before.liked;
      else after.viewedAt=s.api.serverTimestamp();
      const next={views:stats.views+(kind==='view'?1:0),likes:stats.likes+(kind==='like'?(after.liked?1:-1):0),updatedAt:s.api.serverTimestamp()};
      tx.set(user,after);tx.set(total,next);
      return {views:next.views,likes:next.likes,liked:after.liked};
    });
    const value={...result,at:Date.now()};cache.set(id,value);return value;
  }
  let youtubePromise;
  function youtube(){
    if(window.YT?.Player)return Promise.resolve(window.YT);
    if(!youtubePromise)youtubePromise=new Promise((resolve,reject)=>{
      const previous=window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady=()=>{previous?.();resolve(window.YT);};
      const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';
      script.onerror=()=>{youtubePromise=null;reject(new Error('player API unavailable'));};
      document.head.append(script);
    });
    return youtubePromise;
  }
  const totals=new Map(), pending=new Map();
  const totalKey=id=>'d9-film-totals-'+config.projectId+'-'+id;
  function showTotal(node,value){
    const format=n=>Number(n).toLocaleString(en?'en-US':'ko-KR');
    node.textContent=t('재생 ','Plays ')+format(value.views)+' · ♡ '+format(value.likes);
    node.setAttribute('aria-label',t('사이트 재생 ','Site plays ')+format(value.views)+t('회, 좋아요 ', ', likes ')+format(value.likes));
    node.title=t('사이트 내 재생 수 · 좋아요','Site plays · Likes');
  }
  function saveTotal(id,value){
    const total={views:value.views,likes:value.likes,at:Date.now()};totals.set(id,total);
    try{sessionStorage.setItem(totalKey(id),JSON.stringify(total));}catch{}
    document.querySelectorAll('[data-film-stats]').forEach(node=>{if(node.dataset.filmStats===id)showTotal(node,total);});
    return total;
  }
  function publicTotal(id){
    let value=totals.get(id);
    if(!value)try{value=JSON.parse(sessionStorage.getItem(totalKey(id)));}catch{}
    if(value&&Number.isFinite(value.views)&&Number.isFinite(value.likes)&&Date.now()-value.at<300000)return Promise.resolve(value);
    if(!pending.has(id))pending.set(id,protectedApplication()
      .then(({protection,check})=>check.getToken(protection))
      .then(({token})=>fetch('https://firestore.googleapis.com/v1/projects/'+encodeURIComponent(config.projectId)+'/databases/(default)/documents/filmStats/'+encodeURIComponent(id),{headers:{'X-Firebase-AppCheck':token}}))
      .then(async response=>{if(response.status===404)return {views:0,likes:0};if(!response.ok)throw new Error('counts unavailable');const body=await response.json();return {views:Number(body.fields?.views?.integerValue||0),likes:Number(body.fields?.likes?.integerValue||0)};})
      .then(value=>saveTotal(id,value)).finally(()=>pending.delete(id)));
    return pending.get(id);
  }
  const cards=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(!entry.isIntersecting)return;
    cards.unobserve(entry.target);
    publicTotal(entry.target.dataset.filmStats).then(value=>showTotal(entry.target,value)).catch(()=>{entry.target.title=t('집계를 잠시 불러올 수 없습니다.','Counts temporarily unavailable.');});
  }),{rootMargin:'120px'});
  window.D9Engagement={
    observeCard(node,id){node.dataset.filmStats=id;cards.observe(node);},
    attach(id,frame,container){
      container.querySelector('.film-engagement')?.remove();
      const row=document.createElement('div');row.className='film-engagement';
      const count=document.createElement('span'),like=document.createElement('button'),status=document.createElement('span');
      count.textContent=t('사이트 재생 —','Site plays —');
      like.type='button';like.disabled=true;like.textContent=t('♡ 좋아요 —','♡ Like —');like.setAttribute('aria-pressed','false');
      status.className='engagement-status';status.setAttribute('role','status');
      row.append(count,like,status);container.append(row);
      let disposed=false,player,viewed=false,busy=false;
      let queue=Promise.resolve();
      const serial=action=>{const next=queue.then(action);queue=next.catch(()=>{});return next;};
      const observer=new MutationObserver(()=>{if(!frame.isConnected){disposed=true;observer.disconnect();}});
      observer.observe(frame.parentNode,{childList:true});
      function paint(value){saveTotal(id,value);if(disposed)return;count.textContent=t('사이트 재생 ','Site plays ')+value.views.toLocaleString(en?'en-US':'ko-KR');like.textContent=(value.liked?'♥ ':'♡ ')+t('좋아요 ','Like ')+value.likes.toLocaleString(en?'en-US':'ko-KR');like.setAttribute('aria-pressed',String(value.liked));like.disabled=false;}
      function failed(error){console.warn('D9 engagement unavailable',error?.code||error?.message||'unknown');if(!disposed){status.textContent=t('집계를 잠시 불러올 수 없습니다. 영상은 계속 볼 수 있어요.','Counts are temporarily unavailable. You can still watch.');}}
      serial(()=>read(id).then(paint)).catch(failed);
      like.addEventListener('click',async()=>{if(busy)return;busy=true;like.disabled=true;status.textContent='';try{await serial(()=>change(id,'like').then(paint));}catch{failed();}finally{busy=false;if(!disposed)like.disabled=false;}});
      youtube().then(YT=>{
        if(disposed||!frame.isConnected)return;
        function playing(state){
          if(state!==YT.PlayerState.PLAYING||viewed||disposed)return;
          viewed=true;serial(()=>change(id,'view').then(paint)).catch(failed);
        }
        player=new YT.Player(frame,{events:{onReady:event=>playing(event.target.getPlayerState()),onStateChange:event=>playing(event.data)}});
      }).catch(failed);
    }
  };
  window.dispatchEvent(new Event('d9-engagement-ready'));
})();
