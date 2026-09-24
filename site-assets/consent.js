(() => {
 'use strict';
 const ID = 'G-TF7X8WSNGW', KEY = 'd9-analytics-consent-v1', TTL = 180 * 86400000;
 const en = document.documentElement.lang === 'en';
 const denied = {analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'};
 window.dataLayer = window.dataLayer || [];
 window.gtag = window.gtag || function(){window.dataLayer.push(arguments);};
 const gtag = window.gtag;
 gtag('consent','default',denied);
 gtag('set','ads_data_redaction',true);
 let choice = null, loaded = false, returnFocus = null;
 function read(){try{const s=JSON.parse(localStorage.getItem(KEY));return s && ['granted','denied'].includes(s.value) && s.expires>Date.now()?s.value:null;}catch{return null;}}
 function clearCookies(){
  document.cookie.split(';').forEach(part=>{const name=part.trim().split('=')[0];if(!/^_ga(?:_|$)/.test(name))return;
   ['',location.hostname,'.'+location.hostname,'.dra9oncinema.com'].forEach(domain=>{document.cookie=name+'=; Max-Age=0; Path=/; SameSite=Lax'+(domain?'; Domain='+domain:'');});
  });
 }
 function start(){
  if(loaded || choice!=='granted' || !['dra9oncinema.com','www.dra9oncinema.com'].includes(location.hostname))return;
  loaded=true;window['ga-disable-'+ID]=false;
  gtag('consent','update',{...denied,analytics_storage:'granted'});
  gtag('js',new Date());
  let ref='';try{ref=new URL(document.referrer).origin;}catch{}
  gtag('config',ID,{send_page_view:true,page_location:location.origin+location.pathname,page_referrer:ref,allow_google_signals:false,allow_ad_personalization_signals:false,cookie_expires:15552000,cookie_update:false});
  const script=document.createElement('script');script.async=true;script.src='https://www.googletagmanager.com/gtag/js?id='+ID;document.head.append(script);
 }
 const banner=document.createElement('section');banner.id='consent-banner';banner.setAttribute('role','region');banner.setAttribute('aria-labelledby','consent-title');banner.hidden=true;
 const text=en?{title:'Your privacy choices',body:'With your permission, Google Analytics measures visits and YouTube subscribe-button clicks. Advertising tracking stays off. You can decline and still watch everything, or change your choice below at any time.',accept:'Allow analytics',reject:'Decline analytics',policy:'Privacy policy',settings:'Cookie settings'}:{title:'방문 통계 수집 동의',body:'동의하시면 Google Analytics로 방문 통계와 YouTube 구독 버튼 클릭을 집계합니다. 광고 추적은 사용하지 않습니다. 거부해도 모든 작품을 볼 수 있으며, 아래 쿠키 설정에서 언제든 변경할 수 있습니다.',accept:'통계 수집 동의',reject:'통계 수집 거부',policy:'개인정보처리방침',settings:'쿠키 설정'};
 const title=document.createElement('h2');title.id='consent-title';title.textContent=text.title;
 const desc=document.createElement('p');desc.textContent=text.body;
 const policy=document.createElement('a');policy.href=(en?'/en':'')+'/privacy/';policy.textContent=text.policy;
 const actions=document.createElement('div');actions.className='consent-actions';
 const reject=document.createElement('button');reject.type='button';reject.textContent=text.reject;
 const accept=document.createElement('button');accept.type='button';accept.textContent=text.accept;
 actions.append(reject,accept);banner.append(title,desc,policy,actions);document.body.append(banner);
 function save(value){
  choice=value;try{localStorage.setItem(KEY,JSON.stringify({value,expires:Date.now()+TTL}));}catch{}
  banner.hidden=true;
  if(value==='granted')start();else{
   window['ga-disable-'+ID]=true;gtag('consent','update',denied);clearCookies();
   if(loaded){location.reload();return;}
  }
  if(returnFocus)returnFocus.focus();
 }
 reject.addEventListener('click',()=>save('denied'));accept.addEventListener('click',()=>save('granted'));
 document.addEventListener('click',event=>{
  const settings=event.target.closest('[data-cookie-settings]');
  if(settings){returnFocus=settings;banner.hidden=false;reject.focus();return;}
  const button=event.target.closest('a.subscribe-button');
  if(!button || choice!=='granted' || !loaded)return;
  const placement=button.closest('.hero')?'hero':button.closest('.player-footer')?'player':'watch';
  gtag('event','youtube_subscribe_click',{button_location:placement,page_language:en?'en':'ko',page_location:location.origin+location.pathname,link_url:button.href});
 });
 window.addEventListener('storage',event=>{if(event.key===KEY){window['ga-disable-'+ID]=true;location.reload();}});
 choice=read();if(choice==='granted')start();else{window['ga-disable-'+ID]=true;clearCookies();banner.hidden=choice==='denied';}
})();
