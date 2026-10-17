const pageLanguage=document.documentElement.lang,en=pageLanguage!=='ko',t=(ko,english)=>window.D9Locale?.translate(ko,english)??(en?english:ko);

// Keep the crawlable navigation links, moving the same nodes into a compact
// native disclosure on every public page that has the shared header.
(()=>{
 const header=document.querySelector('header.header'),nav=header?.querySelector('.nav'),actions=header?.querySelector('.header-actions');
 if(!nav||!actions)return;
 const menu=document.createElement('div');menu.className='site-menu';
 const toggle=document.createElement('button');toggle.type='button';toggle.className='site-menu-toggle';toggle.setAttribute('aria-label',t('사이트 메뉴','Site menu'));toggle.setAttribute('aria-haspopup','dialog');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls','site-navigation');
 const bars=document.createElement('span');bars.className='site-menu-bars';bars.setAttribute('aria-hidden','true');
 for(let i=0;i<3;i++)bars.append(document.createElement('i'));
 const label=document.createElement('span');label.className='site-menu-label';label.textContent=t('메뉴','Menu');toggle.append(bars,label);
 const panel=document.createElement('dialog');panel.id='site-navigation';panel.className='site-menu-panel';panel.setAttribute('aria-label',t('사이트 메뉴','Site menu'));
 const top=document.createElement('div');top.className='site-menu-heading';const brand=document.createElement('span');brand.textContent='DRA9ON CINEMA';
 const close=document.createElement('button');close.type='button';close.className='site-menu-close';close.textContent=t('닫기 ×','Close ×');top.append(brand,close);
 panel.append(top,nav);
 const social=document.createElement('div');social.className='site-menu-social';for(const link of [...actions.querySelectorAll('.channel-button')])social.append(link);
 if(social.childElementCount)panel.append(social);
 menu.append(toggle,panel);actions.append(menu);header.classList.add('compact-navigation');
 const shut=(focus=false)=>{panel.close();if(focus)toggle.focus();};
 toggle.addEventListener('click',()=>{panel.showModal();document.documentElement.classList.add('site-menu-open');toggle.setAttribute('aria-expanded','true');close.focus();});
 panel.addEventListener('close',()=>{document.documentElement.classList.remove('site-menu-open');toggle.setAttribute('aria-expanded','false');});
 close.addEventListener('click',()=>shut(true));
 menu.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();shut(true);}});
 nav.addEventListener('click',event=>{if(event.target.closest('a'))shut();});
 panel.addEventListener('click',event=>{if(event.target!==panel)return;const r=panel.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)shut(true);});
})();

const works=window.PORTFOLIO||[],byId=id=>works.find(v=>v.id===id),$=id=>document.getElementById(id);

const isReleased=v=>window.D9Release?.released(v)??true;

const statsAssetRoot=new URL('../../',document.currentScript.src);

let engagementLoad;

function loadEngagement(){

  if(!engagementLoad){

    const load=name=>new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=new URL(name+'?v=20261017-visitors1',statsAssetRoot);script.onload=resolve;script.onerror=reject;document.head.append(script);});

    engagementLoad=load('api-engagement.js').catch(()=>{engagementLoad=null;});

  }

  return engagementLoad;

}

// Exact read-only YouTube counts do not initialize any browser identity.
window.D9LoadEngagement=loadEngagement;

// Optional artwork and counters must not compete with the initial hero.
function afterMainPaint(task){
  const schedule=()=>{
    if('requestIdleCallback' in window)window.requestIdleCallback(task,{timeout:1500});
    else setTimeout(task,100);
  };
  if(document.readyState==='complete')schedule();
  else window.addEventListener('load',schedule,{once:true});
}
const cardStatsObserver='IntersectionObserver' in window?new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(!entry.isIntersecting)return;
    cardStatsObserver.unobserve(entry.target);
    afterMainPaint(()=>{if(entry.target.isConnected)loadEngagement().then(()=>{
      if(entry.target.isConnected)window.D9Engagement?.observeCard(entry.target,entry.target.dataset.filmStats);
    });});
  });
},{rootMargin:'120px'}):null;
function observeCardStats(node,id){
  node.dataset.filmStats=id;
  if(cardStatsObserver)cardStatsObserver.observe(node);
  else afterMainPaint(()=>{if(node.isConnected)loadEngagement().then(()=>window.D9Engagement?.observeCard(node,id));});
}

function mountEngagement(id,frame,container){

  if(!container)return;

  container.querySelector('.film-engagement')?.remove();

  loadEngagement().then(()=>{if(frame.isConnected)window.D9Engagement?.attach(id,frame,container);});

}

const paths={play:'<path d="m8 4 13 8-13 8z" fill="currentColor" stroke="none"/>',plus:'<path d="M12 5v14M5 12h14"/>',check:'<path d="m5 12 4 4L19 6"/>'};

const icon=n=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[n]||''}</svg>`;

const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let saved=new Set();try{const s=JSON.parse(localStorage.getItem('dra9on-portfolio-saved')||'[]');if(Array.isArray(s))saved=new Set(s.filter(id=>byId(id)))}catch{}

let selected=null,category='all',view='all',query='',toastTimer,restoreFocus=null;

function notify(text){if(!$('toast'))return;clearTimeout(toastTimer);$('toast').textContent=text;$('toast').classList.add('visible');toastTimer=setTimeout(()=>$('toast').classList.remove('visible'),2600)}

function syncSaved(){document.querySelectorAll('[data-save]').forEach(b=>{const v=byId(b.dataset.save);if(!v)return;const yes=saved.has(v.id);b.classList.toggle('is-saved',yes);b.setAttribute('aria-pressed',String(yes));b.setAttribute('aria-label',`${v.name} ${yes?t('찜 해제','Remove from list'):t('찜하기','Save')}`);b.innerHTML=icon(yes?'check':'plus')+(b.classList.contains('save-button')?(yes?t('찜한 작품','My list'):t('찜하기','Save')):'')});if(selected&&$('detail-save')){$('detail-save').innerHTML=icon(saved.has(selected.id)?'check':'plus')+(saved.has(selected.id)?t('찜한 작품','My list'):t('찜하기','Save'));$('detail-save').setAttribute('aria-pressed',String(saved.has(selected.id)))}}

function setSaved(id,value){if(!byId(id))throw new Error(t('올바른 작품 ID가 필요합니다.','A valid film ID is required.'));const next=new Set(saved);value?next.add(id):next.delete(id);try{localStorage.setItem('dra9on-portfolio-saved',JSON.stringify([...next]))}catch{notify(t('이 브라우저에서는 찜 목록을 저장할 수 없습니다.','Your list cannot be saved in this browser.'));throw new Error(t('브라우저 저장소 사용 불가','Browser storage is unavailable'))}saved=next;syncSaved();if(category==='saved')render();notify(value?t('찜한 작품에 담았어요','Added to your list'):t('찜한 작품에서 삭제했어요','Removed from your list'))}

function card(v){return `<article class="card"><a class="card-open" href="${v.path}" data-detail="${v.id}" aria-label="${escapeHTML(v.label+' '+v.name)} ${t('상세 보기','View details')}"><div class="card-image"><img src="${v.image}" alt="${escapeHTML(v.name)} ${t('공식 썸네일','official thumbnail')}" width="720" height="405" loading="lazy" decoding="async"><span class="duration">${v.duration||''}</span><span class="card-hover-play"><span>${icon('play')}</span></span></div><p class="card-label">${v.label}</p><h3 class="card-name">${escapeHTML(v.name)}</h3></a><button class="card-save" data-save="${v.id}" aria-label="${escapeHTML(v.name)} ${t('찜하기','Save')}" aria-pressed="false">${icon('plus')}</button></article>`}

function filtered(){return works.filter(v=>(view==='all'||(view==='fall'?!!v.season:v.category==='original'))&&(category==='all'||(category==='saved'?saved.has(v.id):v.category===category))&&(!query||`${v.name} ${v.title} ${v.label} ${v.searchText||''} ${v.season?'FALL 707 낙하707 낙하 707':''}`.toLowerCase().includes(query.toLowerCase())))}

function render(){if(!$('browse-results'))return;const home=category==='all'&&view==='all'&&!query;document.body.classList.toggle('browse-mode',!home);$('hero').hidden=!home;$('home-rows').hidden=!home;$('browse-results').hidden=home;document.querySelectorAll('[data-category]').forEach(b=>{const yes=b.dataset.category===category;b.classList.toggle('active',yes);b.setAttribute('aria-pressed',String(yes))});document.querySelectorAll('[data-view]').forEach(b=>{const yes=b.dataset.view===view;b.classList.toggle('active',yes);yes?b.setAttribute('aria-current','page'):b.removeAttribute('aria-current')});if(!home){const result=filtered();if(/^s[1-9][0-9]*$/.test(category))result.sort((a,b)=>a.episode-b.episode);const labels={ost:'FALL 707 · OST',all:t('모든 작품','All films'),s1:t('FALL 707 · 시즌 1','FALL 707 · Season 1'),s2:t('FALL 707 · 시즌 2','FALL 707 · Season 2'),s3:t('FALL 707 · 시즌 3','FALL 707 · Season 3'),full:t('몰아보기','Full movies'),original:t('오리지널 작품','Original films'),saved:t('찜한 작품','My list')};$('browse-title').textContent=query?t(`“${query}” 검색 결과`,`Results for “${query}”`):category!=='all'?(labels[category]||t('FALL 707 · 시즌 '+category.slice(1),'FALL 707 · Season '+category.slice(1))):view==='fall'?'FALL 707: REBOOT':view==='original'?t('오리지널 작품','Original films'):t('모든 작품','All films');$('result-count').textContent=`${result.length}${t('편',result.length===1?' film':' films')}${category==='saved'?t(' · 이 브라우저에 저장된 목록',' · Saved in this browser'):''}`;$('results-grid').innerHTML=result.map(card).join('');decorateCards($('results-grid')); $('empty-state').hidden=result.length>0}syncSaved();document.querySelectorAll('.shelf-track').forEach(updateArrows)}

function updateArrows(track){const prev=document.querySelector(`[data-scroll="${track.id}"][data-direction="-1"]`),next=document.querySelector(`[data-scroll="${track.id}"][data-direction="1"]`);if(prev)prev.disabled=track.scrollLeft<=2;if(next)next.disabled=track.scrollLeft+track.clientWidth>=track.scrollWidth-3}

function showDetail(id){const v=byId(id);if(!v||!$('detail-dialog'))return;restoreFocus=document.activeElement;selected=v;$('detail-title').textContent=v.name;$('detail-label').textContent=v.label;$('detail-image').src=v.image;$('detail-image').alt=v.name+t(' 공식 썸네일',' official thumbnail');$('detail-description').textContent=v.summary;$('detail-meta').textContent=`DRA9ON CINEMA · ${v.duration||''}`;$('detail-page').href=v.path;syncSaved();$('detail-dialog').showModal()}

function createPlayer(id){const v=byId(id);if(!v)throw new Error(t('알 수 없는 영상입니다.','Unknown film.'));const frame=document.createElement('iframe');frame.dataset.externalSrc=`https://www.youtube-nocookie.com/embed/${v.id}?rel=0&playsinline=1&autoplay=0&enablejsapi=1&origin=${encodeURIComponent(location.origin)}&hl=${en?'en':'ko'}${en?'&cc_lang_pref=en':''}`;frame.title=v.title;frame.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';frame.referrerPolicy='strict-origin-when-cross-origin';frame.allowFullscreen=true;return frame}

function nextVideo(v){if(v.id==='sFw17ZPE42A')return works.find(w=>w.category==='s3'&&w.episode===1&&isReleased(w))||null;let seq=works.filter(w=>w.category===v.category&&isReleased(w));if(/^s[1-9][0-9]*$/.test(v.category))seq.sort((a,b)=>a.episode-b.episode);return seq[seq.findIndex(w=>w.id===v.id)+1]||(/^s[1-9][0-9]*$/.test(v.category)?works.find(w=>w.category===`s${v.season+1}`&&w.episode===1&&isReleased(w)):null)}

function play(id){const v=byId(id);if(v)location.href=v.path;}

async function share(id){const v=byId(id);if(!v)return;const url=new URL(v.path,location.origin).href;try{await navigator.clipboard.writeText(url);notify(t('작품 링크를 복사했어요','Film link copied'))}catch{notify(t('링크 복사가 제한되어 작품 페이지를 엽니다.','Copy unavailable. Opening the film page.'));location.href=v.path}}

document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.play)play(b.dataset.play);if(b.dataset.save){try{setSaved(b.dataset.save,!saved.has(b.dataset.save))}catch{}}if(b.dataset.share)share(b.dataset.share);if(b.dataset.view){view=b.dataset.view;category='all';query='';$('search').value='';render();window.scrollTo({top:0,behavior:'instant'})}if(b.dataset.category){category=b.dataset.category;view='all';render();window.scrollTo({top:0,behavior:'instant'})}if(b.dataset.scroll){const t=$(b.dataset.scroll);t.scrollBy({left:Number(b.dataset.direction)*t.clientWidth*.85,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'})}});

if($('search-toggle')){$('search-toggle').addEventListener('click',()=>{const opening=$('search').hidden;$('search').hidden=!opening;$('search-wrap').classList.toggle('expanded',opening);$('search-toggle').setAttribute('aria-expanded',String(opening));if(opening)$('search').focus();else{query='';$('search').value='';render()}});$('search').addEventListener('input',e=>{query=e.target.value.trim().slice(0,100);render()});$('search').addEventListener('keydown',e=>{if(e.key==='Escape'){$('search-toggle').click();$('search-toggle').focus()}})}

if($('reset-browse'))$('reset-browse').addEventListener('click',()=>{view='all';category='all';query='';$('search').value='';render();window.scrollTo({top:0,behavior:'instant'})});

if($('detail-dialog')){$('detail-close').addEventListener('click',()=>$('detail-dialog').close());$('detail-play').addEventListener('click',()=>play(selected.id));$('detail-save').addEventListener('click',()=>{try{setSaved(selected.id,!saved.has(selected.id))}catch{}});$('detail-share').addEventListener('click',()=>share(selected.id));$('player-close').addEventListener('click',()=>$('player-dialog').close());$('player-dialog').addEventListener('close',()=>{$('player-mount').replaceChildren();if(restoreFocus?.isConnected)restoreFocus.focus()});document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target!==d)return;const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}))}

document.querySelectorAll('.shelf-track').forEach(t=>{t.addEventListener('scroll',()=>updateArrows(t),{passive:true});updateArrows(t)});window.addEventListener('resize',()=>document.querySelectorAll('.shelf-track').forEach(updateArrows));syncSaved();

if(document.modelContext?.registerTool&&$('browse-results')){const lifecycle=new AbortController();const register=t=>{try{Promise.resolve(document.modelContext.registerTool(t,{signal:lifecycle.signal})).catch(()=>{})}catch{}};register({name:'browse_portfolio',title:t('포트폴리오 검색','Search portfolio'),description:t('검색어로 DRA9ON CINEMA의 작품을 찾아 화면에 표시합니다.','Find and display DRA9ON CINEMA films by search term.'),inputSchema:{type:'object',properties:{query:{type:'string',maxLength:100}},required:['query'],additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:false},execute(input){if(!input||typeof input.query!=='string'||input.query.length>100||Object.keys(input).some(k=>k!=='query'))throw new Error(t('100자 이하의 검색어를 입력해 주세요.','Enter a search term of up to 100 characters.'));view='all';category='all';query=input.query.trim();$('search').value=query;render();return {works:filtered().map(v=>({id:v.id,title:v.name,url:v.path}))}}});register({name:'set_saved_work',title:t('작품 찜하기','Save film'),description:t('이 브라우저의 찜 목록에 작품을 저장하거나 제거합니다.','Add or remove a film from the list saved in this browser.'),inputSchema:{type:'object',properties:{id:{type:'string'},saved:{type:'boolean'}},required:['id','saved'],additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:false},execute(input){if(!input||typeof input.id!=='string'||!byId(input.id)||typeof input.saved!=='boolean'||Object.keys(input).some(k=>!['id','saved'].includes(k)))throw new Error(t('올바른 작품 ID와 저장 여부를 입력해 주세요.','Enter a valid film ID and saved state.'));setSaved(input.id,input.saved);return {id:input.id,saved:saved.has(input.id)}}});window.addEventListener('pagehide',()=>lifecycle.abort(),{once:true})}



// Carry the current section when switching between the static language routes.

// Short, silent local previews are separate from the click-to-play YouTube film.

function createHeroPreview(hero){

  const previewRoot=new URL('../previews/',hero.querySelector('.hero-image').src);

  const video=document.createElement('video'), button=document.createElement('button');

  const motion=matchMedia('(prefers-reduced-motion: reduce)');

  video.className='hero-preview';video.muted=true;video.defaultMuted=true;

  video.playsInline=true;video.preload='none';video.setAttribute('aria-hidden','true');video.tabIndex=-1;

  button.type='button';button.className='hero-preview-toggle';

  hero.querySelector('.hero-image').after(video);hero.append(button);

  let source='',seen=false,ended=false,blocked=false,stopped=false,manual=false,loading=false,userStopped=false,generation=0;

  function label(){button.textContent=ended||blocked?t('↻ 무음 미리보기','↻ Silent preview'):stopped||(!previewReady&&!manual)?t('▶ 미리보기 재생','▶ Play preview'):t('Ⅱ 미리보기 정지','Ⅱ Pause preview');}

  let previewReady=false;
  const constrained=()=>!!navigator.connection?.saveData||['slow-2g','2g'].includes(navigator.connection?.effectiveType);
  afterMainPaint(()=>{previewReady=true;sync();});

  function allowed(){return (manual||previewReady)&&seen&&!hero.hidden&&!document.hidden&&!document.querySelector('dialog[open]')&&!stopped&&(manual||(!motion.matches&&!constrained()));}

  function sync(){

    if(!allowed()){video.pause();return;}

    if(ended||blocked||loading||!source||!video.paused)return;

    if(video.getAttribute('src')!==source){video.src=source;video.load();}

    loading=true;const attempt=generation;

    video.play().catch(error=>{if(attempt!==generation||error.name==='AbortError')return;blocked=true;video.classList.remove('is-playing');label();}).finally(()=>{if(attempt===generation)loading=false;});

  }

  video.addEventListener('playing',()=>{if(allowed())video.classList.add('is-playing');else video.pause();});

  video.addEventListener('ended',()=>{ended=true;video.classList.remove('is-playing');label();});

  video.addEventListener('error',()=>{blocked=true;video.classList.remove('is-playing');label();});

  button.addEventListener('click',()=>{

    manual=true;

    if(ended||blocked||(video.paused&&!stopped)){ended=false;blocked=false;stopped=false;video.currentTime=0;}

    else stopped=!stopped;

    userStopped=stopped;label();sync();

  });

  new IntersectionObserver(entries=>{seen=entries[0].isIntersecting;sync();},{threshold:0.15}).observe(hero);

  new MutationObserver(sync).observe(hero,{attributes:true,attributeFilter:['hidden']});

  document.querySelectorAll('dialog').forEach(dialog=>new MutationObserver(sync).observe(dialog,{attributes:true,attributeFilter:['open']}));

  document.addEventListener('visibilitychange',sync);

  motion.addEventListener('change',()=>{manual=false;stopped=motion.matches;label();sync();});

  return {select(v){

    generation++;

    video.pause();video.classList.remove('is-playing');video.removeAttribute('src');video.load();

    button.hidden=v.preview===false;

    if(v.preview===false){source='';return;}

    const name=v.category==='full'?'s1-full':`s${v.season}-${v.episode}`;

    source=new URL(name+'.mp4',previewRoot).href;ended=false;blocked=false;loading=false;

    stopped=userStopped||motion.matches||constrained();manual=false;label();sync();

  }};

}

if ($('hero')) {

  const hero=$('hero'), motion=matchMedia('(prefers-reduced-motion: reduce)');

  // The home uses its film still; no third preview CTA or background download.
  const preview={select(){}};

  const start=works.find(v=>v.category==='s1'&&v.episode===1);

  if(start)hero.querySelector('.hero-start').dataset.detail=start.id;

  // Both primary actions keep their destinations while the artwork rotates.
  const newest=works.filter(v=>/^s[1-9][0-9]*$/.test(v.category)&&isReleased(v)).sort((a,b)=>b.season-a.season||b.episode-a.episode)[0];
  const latestLink=hero.querySelector('.hero-feature-link');
  if(newest){latestLink.href=newest.path;latestLink.dataset.detail=newest.id;}
  latestLink.textContent=t('최신 에피소드','LATEST EPISODE');

  const season=Math.max(...works.filter(v=>/^s[1-9][0-9]*$/.test(v.category)&&isReleased(v)).map(v=>v.season));

  const seasonTwoFull=works.find(v=>v.id==='sFw17ZPE42A');
  const featuredSlides=()=>[
    ...works.filter(v=>v.category===`s${season}`&&isReleased(v)).sort((a,b)=>b.episode-a.episode),
    ...(seasonTwoFull&&isReleased(seasonTwoFull)?[seasonTwoFull]:[]),
    ...works.filter(v=>v.category==='s2'&&v.season!==season&&isReleased(v)).sort((a,b)=>b.episode-a.episode)
  ];
  const slides=featuredSlides();
  const seasonOneFull=works.find(v=>v.id==='4f6Zguf7c2M');

  if(seasonOneFull)slides.push(seasonOneFull);

  if (slides.length>1) {

    let index=0, paused=motion.matches, hovered=false, focused=false, visible=true;

    const controls=document.createElement('div');

    controls.className='hero-carousel-controls';

    controls.setAttribute('role','group');

    controls.setAttribute('aria-label',t('추천 작품 배너','Featured episode carousel'));

    controls.innerHTML=`<button type="button" data-hero-prev aria-label="${t('이전 배너','Previous banner')}">←</button><span class="hero-position"></span><button type="button" data-hero-next aria-label="${t('다음 배너','Next banner')}">→</button><button type="button" data-hero-pause></button>`;

    hero.append(controls);

    const pause=controls.querySelector('[data-hero-pause]');

    function updatePause(){pause.textContent=paused?t('자동 전환 시작','Start rotation'):t('자동 전환 정지','Pause rotation');}

    function showSlide(next){

      index=(next+slides.length)%slides.length;

      const v=slides[index], image=hero.querySelector('.hero-image');

      image.src=v.image; image.alt=v.name;

      hero.querySelector('.hero-kicker').textContent=v.category==='full'?t(`FALL 707 · 시즌 ${v.season} 풀버전`,`FALL 707 · SEASON ${v.season} FULL MOVIE`):`FALL 707 · S${v.season} EP.${String(v.episode).padStart(2,'0')}`;
      hero.querySelector('.hero-tagline').textContent=v.name;

      hero.querySelector('.hero-description').textContent=v.summary;

      const playButton=hero.querySelector('.hero-feature-link');

      // This is always the latest episode, never the carousel's current item.
      if(newest){playButton.href=newest.path;playButton.dataset.detail=newest.id;}
      playButton.textContent=t('최신 에피소드','LATEST EPISODE');
      hero.querySelector('.hero-meta').textContent=`2026 · ${v.category==='full'?`SEASON ${v.season} · FULL MOVIE`:`S${v.season} EP.${v.episode}`} · ${v.duration||''}`;
      const badge=hero.querySelector('.new-episode:not(.upcoming-episode)');
      if(badge){badge.hidden=v.category==='full'||v.season!==season;if(!badge.hidden)badge.querySelector('strong').textContent=`S${v.season} EP.${String(v.episode).padStart(2,'0')}`;}
      controls.querySelector('.hero-position').textContent=`${String(index+1).padStart(2,'0')} / ${String(slides.length).padStart(2,'0')}`;

      preview.select(v);

    }

    document.addEventListener('d9:released',()=>{slides.splice(0,slides.length,...featuredSlides());if(seasonOneFull)slides.push(seasonOneFull);showSlide(0);});
    let timer;

    function schedule(){clearInterval(timer);timer=setInterval(()=>{

      if(!hero.hasAttribute("data-swiping")&&!paused&&!hovered&&!focused&&visible&&!document.hidden&&!hero.hidden&&!document.querySelector('dialog[open]'))showSlide(index+1);

    },12000);}

    controls.querySelector('[data-hero-prev]').addEventListener('click',()=>{showSlide(index-1);schedule();});

    controls.querySelector('[data-hero-next]').addEventListener('click',()=>{showSlide(index+1);schedule();});

    pause.addEventListener('click',()=>{paused=!paused;updatePause();schedule();});

    hero.addEventListener('mouseenter',()=>{hovered=true;});

    hero.addEventListener('mouseleave',()=>{hovered=false;schedule();});

    hero.addEventListener('focusin',()=>{focused=true;});

    hero.addEventListener('focusout',e=>{focused=hero.contains(e.relatedTarget);schedule();});

    motion.addEventListener('change',()=>{if(motion.matches){paused=true;updatePause();}});

    new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;},{threshold:0.15}).observe(hero);

    controls.querySelectorAll('[data-hero-prev],[data-hero-next]').forEach(button=>{button.classList.add('hero-side-arrow');hero.append(button)});hero.classList.add('hero-carousel');showSlide(0);updatePause();schedule();

  }

}





// Horizontal gestures change artwork; vertical scrolling and pinch zoom stay native.

(() => {

  const hero = document.getElementById('hero');

  if (!hero || !hero.querySelector('[data-hero-next]')) return;

  hero.style.touchAction = 'pan-y pinch-zoom';

  const image = hero.querySelector('.hero-image');

  if (image) image.draggable = false;

  let gesture = null;

  function reset() { gesture = null; hero.removeAttribute('data-swiping'); }

  hero.addEventListener('pointerdown', event => {

    if (!event.isPrimary) { reset(); return; }

    if (event.button !== 0 || event.target.closest('a,button,input,select,textarea')) return;

    gesture = {id:event.pointerId, x:event.clientX, y:event.clientY};

    hero.setAttribute('data-swiping', '');

    hero.setPointerCapture(event.pointerId);

  });

  hero.addEventListener('pointermove', event => {

    if (!gesture || gesture.id !== event.pointerId) return;

    const dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;

    if (Math.abs(dy) > 12 && Math.abs(dy) > Math.abs(dx)) reset();

  });

  hero.addEventListener('pointerup', event => {

    if (!gesture || gesture.id !== event.pointerId) return;

    const dx = event.clientX - gesture.x, dy = event.clientY - gesture.y;

    reset();

    if (Math.abs(dx) < 48 || Math.abs(dx) < Math.abs(dy) * 1.5) return;

    hero.querySelector(dx < 0 ? '[data-hero-next]' : '[data-hero-prev]').click();

  });

  hero.addEventListener('pointercancel', reset);

  hero.addEventListener('lostpointercapture', reset);

})();



// A homepage refresh starts at the hero; normal section links and Back keep working.

(() => {

  const navigationType = performance.getEntriesByType('navigation')[0]?.type;

  if (!document.getElementById('hero') || navigationType === 'back_forward' || (navigationType !== 'reload' && location.hash)) return;

  history.scrollRestoration = 'manual';

  if (location.hash) history.replaceState(history.state, '', location.pathname + location.search);

  const resetScroll = () => {

    window.scrollTo({top:0, left:0, behavior:'instant'});

    requestAnimationFrame(() => window.scrollTo({top:0, left:0, behavior:'instant'}));

  };

  window.addEventListener('pageshow', resetScroll, {once:true});

  window.addEventListener('pagehide', () => { history.scrollRestoration = 'auto'; }, {once:true});

})();



// Keep collaboration contact usable even without a configured mail app.

(() => {

  const contacts = document.querySelectorAll('a[href^="mailto:"]:not(.question-topic)');

  if (!contacts.length) return;

  const style = document.createElement('style');

  style.textContent = '.contact-block{min-width:0;display:flex;flex-direction:column;gap:10px}.contact-details{display:flex;align-items:center;flex-wrap:wrap;gap:8px 12px}.contact-address{font-size:14px;color:#ddd;overflow-wrap:anywhere;user-select:text}.contact-copy{font:inherit;font-size:12px;color:#eee;background:#252529;border:1px solid #555;border-radius:5px;min-height:44px;padding:8px 12px;cursor:pointer}.contact-copy:focus-visible{outline:2px solid #fff;outline-offset:3px}.contact-status{flex-basis:100%;font-size:12px;color:#bbb}.contact-status:empty{display:none}.bio-links .contact-details{padding:0 18px 12px}';

  document.head.append(style);

  contacts.forEach(link => {

    const block = document.createElement('div');

    block.className = 'contact-block';

    link.before(block);

    block.append(link);

    const details = document.createElement('div');

    details.className = 'contact-details';

    const address = document.createElement('span');

    address.className = 'contact-address';

    address.textContent = decodeURIComponent(link.getAttribute('href').slice(7).split('?')[0]);

    const copy = document.createElement('button');

    copy.type = 'button';

    copy.className = 'contact-copy';

    copy.textContent = t('이메일 복사', 'Copy email');

    const status = document.createElement('span');

    status.className = 'contact-status';

    status.setAttribute('role', 'status');

    copy.addEventListener('click', async () => {

      try {

        await navigator.clipboard.writeText(address.textContent);

        status.textContent = t('이메일 주소를 복사했어요.', 'Email address copied.');

      } catch {

        status.textContent = t('위 이메일 주소를 길게 누르거나 선택해서 복사해 주세요.', 'Select the email address above to copy it.');

      }

    });

    details.append(address, copy, status);

    block.append(details);

  });

})();



document.querySelectorAll('.nav a[href*="#"]').forEach(link => {

  link.addEventListener('click', () => {

    if (!$('hero')) return;

    view='all'; category='all'; query='';

    if ($('search')) $('search').value='';

    render();

  });

});



// The film shelf becomes a spacious screening catalogue when a collection is selected.

function decorateCards(root=document){

 root.querySelectorAll('.card').forEach((cardEl,index)=>{

  const link=cardEl.querySelector('[data-detail]'),v=link&&byId(link.dataset.detail);if(!v||cardEl.querySelector('.card-direct'))return;

  if(/^s[1-9][0-9]*$/.test(v.category)){const number=document.createElement('span');number.className='episode-number';number.setAttribute('aria-hidden','true');number.textContent=String(v.episode).padStart(2,'0');link.append(number);cardEl.classList.add('numbered-card')}

  link.setAttribute('aria-label',v.label+' '+v.name+' '+t('재생 페이지 열기','Open watch page'));

  const summary=document.createElement('p');summary.className='card-synopsis';summary.textContent=v.summary;

  const actions=document.createElement('div');actions.className='card-direct';

  const watch=document.createElement('a');watch.href=v.path;watch.dataset.detail=v.id;watch.textContent=t('사이트에서 보기','Watch here');watch.className='card-watch';

  const youtube=document.createElement('a');youtube.href='https://www.youtube.com/watch?v='+encodeURIComponent(v.id);youtube.target='_blank';youtube.rel='noopener noreferrer';youtube.textContent=t('YouTube에서 보기 ↗','Watch on YouTube ↗');

  if(!isReleased(v)){watch.textContent=window.D9Release.label;youtube.hidden=true;const duration=cardEl.querySelector('.duration');if(duration)duration.textContent=t('공개 예정','COMING SOON');}

  actions.append(watch);if(document.body.dataset.page!=='home')actions.append(youtube);cardEl.append(summary,actions);

  const title=cardEl.querySelector('.card-name'),line=document.createElement('div'),stats=cardEl.querySelector('[data-youtube-api-count]')||document.createElement('span');

  line.className='card-title-line';stats.classList.add('card-counts');stats.dataset.filmStats=v.id;

  const raw=v.apiViewCount,valid=typeof raw==='string'&&/^(?:0|[1-9][0-9]*)$/.test(raw);stats.hidden=!valid;
  stats.textContent=valid?t('YouTube 조회수 ','YouTube views ')+raw:'';

  title.before(line);line.append(title,stats);

  if(!isReleased(v))stats.hidden=true;

 });

}

decorateCards();



if(document.body.dataset.page==='watch'){const frame=document.querySelector('.watch-screen iframe');if(frame&&isReleased(byId(document.body.dataset.id)))mountEngagement(document.body.dataset.id,frame,document.querySelector('.watch-actions'));}



// Keep hero media slightly behind the normal scroll pace on desktop only.

(() => {

 const hero = document.querySelector('body[data-page="home"] #hero');

 if (!hero) return;

 const enabled = matchMedia('(min-width: 801px) and (pointer: fine) and (prefers-reduced-motion: no-preference)');

 let pending = 0, inView = true;

 function paint() {

  pending = 0;

  const rect = hero.getBoundingClientRect();

  const shift = enabled.matches ? Math.min(260, Math.max(0, -rect.top * .35)) : 0;

  hero.style.setProperty('--hero-parallax', `${shift.toFixed(2)}px`);

 }

 function schedule() { if (!pending) pending = requestAnimationFrame(paint); }

 function sync() {

  window.removeEventListener('scroll', schedule);

  if (enabled.matches && inView) window.addEventListener('scroll', schedule, {passive:true});

  schedule();

 }

 if('IntersectionObserver' in window)new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;sync();}).observe(hero);
 enabled.addEventListener('change', sync);

 window.addEventListener('resize', schedule, {passive:true});

 window.addEventListener('pageshow', schedule);

 sync();

})();



// Reveal shelves once as they enter the viewport; content stays visible without JS.

(() => {

 const shelves = [...document.querySelectorAll('body[data-page="home"] #home-rows > .shelf')];

 const motion = matchMedia('(prefers-reduced-motion: reduce)');

 if (!shelves.length || !('IntersectionObserver' in window)) return;

 let observer;

 function setup() {

  observer?.disconnect();

  shelves.forEach(shelf => shelf.classList.remove('shelf-reveal-pending'));

  if (motion.matches) return;

  observer = new IntersectionObserver(entries => {

   entries.forEach(entry => {

    if (!entry.isIntersecting) return;

    entry.target.classList.remove('shelf-reveal-pending');

    entry.target.dataset.revealed = 'true';

    observer.unobserve(entry.target);

   });

  }, {threshold:0, rootMargin:'0px 0px -45px 0px'});

  shelves.forEach(shelf => {

   shelf.classList.add('shelf-reveal');

   shelf.querySelectorAll('.card').forEach((card,index) => card.style.setProperty('--reveal-delay', `${Math.min(index,5)*65}ms`));

   if (shelf.dataset.revealed || shelf.getBoundingClientRect().top < innerHeight - 45) return;

   shelf.classList.add('shelf-reveal-pending');

   observer.observe(shelf);

  });

 }

 motion.addEventListener('change', setup);

 document.addEventListener('focusin', event => {

  const shelf = event.target.closest('.shelf-reveal-pending');

  if (shelf) { shelf.classList.remove('shelf-reveal-pending'); shelf.dataset.revealed='true'; observer?.unobserve(shelf); }

 });

 setup();

})();



// Unlock without a reload, so a visitor watching another episode is not interrupted.

document.addEventListener('d9:released',({detail})=>{

 const v=byId(detail.id);

 document.querySelectorAll('.card').forEach(cardEl=>{

  if(cardEl.querySelector('[data-detail]')?.dataset.detail!==v.id)return;

  const watch=cardEl.querySelector('.card-watch');if(watch)watch.textContent=t('사이트에서 보기','Watch here');

  cardEl.querySelectorAll('.card-direct a').forEach(a=>a.hidden=false);

  const duration=cardEl.querySelector('.duration');if(duration)duration.textContent=v.duration||'';

  const stats=cardEl.querySelector('.card-counts');if(stats)observeCardStats(stats,v.id);

 });

 if(document.body.dataset.id===v.id){const frame=document.querySelector('.watch-screen iframe');if(frame)mountEngagement(v.id,frame,document.querySelector('.watch-actions'));}

 const next=$('player-next');if(next&&$('player-dialog')?.open){const current=works.find(w=>$('player-title').textContent===`${w.label} · ${w.name}`);if(current&&nextVideo(current)?.id===v.id){next.hidden=false;next.href=v.path;next.dataset.detail=v.id;next.textContent=t('다음 화 보기','Next episode')+' →';}}

});



// Clear exits from every dedicated watch page, including direct/shared links.

if(document.body.dataset.page==='watch'){

 const home=new URL(pageLanguage==='ko'?'':pageLanguage+'/',statsAssetRoot).pathname;

 const nav=document.createElement('nav');nav.className='watch-return';nav.setAttribute('aria-label',t('재생 화면 나가기','Leave watch page'));

 const back=document.createElement('a');back.href=home;back.textContent=t('← 이전 화면','← Back');

 back.addEventListener('click',event=>{

  if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button!==0)return;

  let internal=false;try{internal=new URL(document.referrer).origin===location.origin}catch{}

  if(internal&&history.length>1){event.preventDefault();history.back();}

 });

 const close=document.createElement('a');close.href=home;close.textContent=t('홈으로 닫기 ×','Close to home ×');

 nav.append(back,close);document.querySelector('.watch-main').prepend(nav);

}

