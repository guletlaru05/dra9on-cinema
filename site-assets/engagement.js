/* Public totals are lazy-loaded; identity starts in a player or after analytics consent. */
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
  function services(allowed=()=>true){
    if(!allowed())return Promise.reject(new Error('visits/consent-required'));
    if(!servicePromise)servicePromise=Promise.all([
      protectedApplication(),import(sdk+'firebase-auth.js'),import(sdk+'firebase-firestore.js')
    ]).then(async([{application,protection,check},auth,db])=>{
      await check.getToken(protection);
      if(!allowed())throw new Error('visits/consent-required');
      const identity=auth.getAuth(application);
      await identity.authStateReady();
      if(!allowed())throw new Error('visits/consent-required');
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
  const visitDay=()=>Math.floor((Date.now()+32400000)/86400000);
  const visitCacheKey='d9-site-visits-v1-'+config.projectId;
  const visitMarkerKey='d9-site-visit-day-v1-'+config.projectId;
  let visitCache,visitRead,visitRecord;
  const mayRecordVisit=()=>['dra9oncinema.com','www.dra9oncinema.com'].includes(location.hostname)
    && !/^\/(?:en\/)?library(?:\/|$)/.test(location.pathname)
    && window.D9AnalyticsConsent?.get()==='granted';
  function validVisitTotals(value){
    return value&&Number.isSafeInteger(value.total)&&value.total>=0
      &&Number.isSafeInteger(value.today)&&value.today>=0&&value.today<=value.total
      &&value.day===visitDay()&&typeof value.startedAt==='string'
      &&Number.isFinite(Date.parse(value.startedAt))&&Number.isFinite(value.at);
  }
  function saveVisitTotals(value){
    if(!validVisitTotals(value))throw new Error('visits/invalid-totals');
    visitCache=value;
    try{sessionStorage.setItem(visitCacheKey,JSON.stringify(value));}catch{}
    return value;
  }
  async function visitTotals({force=false}={}){
    if(!visitCache)try{visitCache=JSON.parse(sessionStorage.getItem(visitCacheKey));}catch{}
    if(!force&&validVisitTotals(visitCache)&&Date.now()-visitCache.at>=0&&Date.now()-visitCache.at<300000)return visitCache;
    if(!visitRead)visitRead=(async()=>{
      const day=visitDay(),{protection,check}=await protectedApplication();
      const {token}=await check.getToken(protection);
      const readDocument=async path=>{
        const response=await fetch('https://firestore.googleapis.com/v1/projects/'+encodeURIComponent(config.projectId)+'/databases/(default)/documents/'+path,{headers:{'X-Firebase-AppCheck':token}});
        if(response.status===404)return null;
        if(!response.ok)throw new Error('visits/unavailable');
        return (await response.json()).fields;
      };
      // Read the daily count first: a concurrent visit may then raise the total,
      // but cannot leave us comparing a newer daily count to an older total.
      const daily=await readDocument('siteVisitDays/'+day);
      const summary=await readDocument('siteVisits/summary');
      // A missing summary is not a fabricated zero; the first consenting visit starts it.
      if(!summary)throw new Error('visits/not-started');
      if(visitDay()!==day)throw new Error('visits/day-changed');
      return saveVisitTotals({total:Number(summary.total?.integerValue),today:daily?Number(daily.visits?.integerValue):0,
        startedAt:summary.startedAt?.timestampValue,day,at:Date.now()});
    })().finally(()=>{visitRead=null;});
    return visitRead;
  }
  async function recordSiteVisit(){
    if(!mayRecordVisit())return null;
    let marked;try{marked=localStorage.getItem(visitMarkerKey);}catch{}
    if(marked===String(visitDay()))return visitTotals();
    if(!visitRecord)visitRecord=(async()=>{
      const s=await services(mayRecordVisit);
      if(!mayRecordVisit())return null;
      // One bounded retry covers crossing KST midnight while Firestore is committing.
      for(let attempt=0;attempt<2;attempt++){
        const day=visitDay(),summary=s.api.doc(s.db,'siteVisits','summary'),daily=s.api.doc(s.db,'siteVisitDays',String(day)),browser=s.api.doc(s.db,'siteVisitBrowsers',s.uid);
        try{
          const result=await s.api.runTransaction(s.db,async tx=>{
            if(!mayRecordVisit())return null;
            const [a,b,c]=await Promise.all([tx.get(summary),tx.get(daily),tx.get(browser)]);
            if(!mayRecordVisit())return null;
            if(day!==visitDay())throw new Error('visits/day-changed');
            const total=a.data(),today=b.data(),previous=c.data();
            if(previous?.day===day)return {day};
            if(previous&&(!Number.isSafeInteger(previous.day)||previous.day>day))throw new Error('visits/invalid-browser-day');
            if(total&&(!Number.isSafeInteger(total.total)||total.total<0||!total.startedAt?.toDate))throw new Error('visits/invalid-total');
            if(today&&(!Number.isSafeInteger(today.visits)||today.visits<0||today.day!==day))throw new Error('visits/invalid-day');
            const stamp=s.api.serverTimestamp();
            tx.set(summary,{total:(total?.total||0)+1,startedAt:total?.startedAt||stamp,updatedAt:stamp});
            tx.set(daily,{day,visits:(today?.visits||0)+1,updatedAt:stamp});
            tx.set(browser,{day,visitedAt:stamp});
            return {day};
          });
          if(!result)return null;
          if(mayRecordVisit())try{localStorage.setItem(visitMarkerKey,String(result.day));}catch{}
          // Read committed server timestamps, including the genuine initial start date.
          await visitRead?.catch(()=>{});
          return visitTotals({force:true});
        }catch(error){
          if(attempt===0&&day!==visitDay()&&mayRecordVisit())continue;
          throw error;
        }
      }
    })().catch(error=>{if(!mayRecordVisit())return null;throw error;}).finally(()=>{visitRecord=null;});
    return visitRecord;
  }
  const cards=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(!entry.isIntersecting)return;
    cards.unobserve(entry.target);
    publicTotal(entry.target.dataset.filmStats).then(value=>showTotal(entry.target,value)).catch(()=>{entry.target.title=t('집계를 잠시 불러올 수 없습니다.','Counts temporarily unavailable.');});
  }),{rootMargin:'120px'});
  window.D9Engagement={
    visitTotals,
    recordSiteVisit,
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
