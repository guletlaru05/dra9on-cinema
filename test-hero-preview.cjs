const {test}=require('node:test'),assert=require('node:assert/strict');
const {createWorkHero}=require('./site-assets/work-hero.js');
function fixture({reduced=false,saveData=false,effectiveType='4g',downlink=5,mobile=false,rejectPlay=false}={}){
 const requests=[],videos=[],queue=new Map(),events={},observers=[];let id=0;
 const element=()=>{const handlers={},attrs={},classes=new Set();return {dataset:{},style:{},paused:true,currentTime:0,duration:8,ended:false,textContent:'',classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x)},addEventListener(k,f){(handlers[k]??=[]).push(f);},emit(k,arg={}){for(const f of handlers[k]||[])f(arg);},setAttribute(k,v){attrs[k]=v;},getAttribute(k){return attrs[k]??null;},removeAttribute(k){delete attrs[k];},focus(){},scrollIntoView(){},canPlayType:()=>true,load(){this.currentTime=0;this.ended=false;},pause(){this.paused=true;},play(){if(rejectPlay)return Promise.reject({name:'NotAllowedError'});this.paused=false;this.emit('playing');return Promise.resolve();},set src(v){attrs.src=v;requests.push(v);},get src(){return attrs.src;}};};
 const slides=Array.from({length:5},(_,i)=>({id:'clip-'+i,title:'Title '+i,description:'Description '+i,label:'Label '+i,tab:'Work '+i,url:'/work-'+i+'/',poster:'poster-'+i+'.jpg',webm:'clip-'+i+'.webm',mp4:'clip-'+i+'.mp4',mobile:'clip-'+i+'-mobile.mp4',duration:8}));
 const tabs=slides.map(()=>{const x=element(),line=element();x.querySelector=()=>line;return x;});
 const config={textContent:JSON.stringify({slides,pause:'Pause',resume:'Resume'})},poster=element(),heading=element(),label=element(),description=element(),view=element(),panel=element(),pause=element();
 Object.defineProperty(poster,'src',{value:'',writable:true});
 const media={querySelector(){return {};},insertBefore(v){videos.push(v);}};
 const nodes={'[data-work-hero-config]':config,'.hero-media':media,'.hero-image':poster,'#hero-title':heading,'.d9-work-label':label,'.d9-work-description':description,'.hero-feature-link':view,'[role=tabpanel]':panel,'.d9-work-pause':pause};
 const root={dataset:{},hidden:false,querySelector:s=>nodes[s],querySelectorAll:()=>tabs};
 const doc={readyState:'loading',hidden:false,body:{},createElement:element,querySelector:()=>null,addEventListener(k,f){events[k]=f;}};
 const motion={matches:reduced,addEventListener(k,f){this.change=f;}},viewport={matches:mobile,addEventListener(k,f){this.change=f;}};
 const env={document:doc,navigator:{connection:{saveData,effectiveType,downlink}},matchMedia:s=>s.includes('max-width')?viewport:motion,addEventListener(k,f){events[k]=f;},requestAnimationFrame(f){queue.set(++id,f);return id;},cancelAnimationFrame(i){queue.delete(i);},IntersectionObserver:class{constructor(cb){observers.push(cb);}observe(){}},MutationObserver:class{observe(){}}};
 const controller=createWorkHero(root,env);
 const step=now=>{const tasks=[...queue.values()];queue.clear();tasks.forEach(f=>f(now));};
 return {requests,videos,root,doc,tabs,heading,view,panel,pause,controller,step,ready(){observers[0]([{isIntersecting:true}]);events.load();step(0);step(0);},visible(value){observers[0]([{isIntersecting:value}]);},hidden(value){doc.hidden=value;events.visibilitychange();}};
}
test('no media request before load and two paints; the single active video is muted and inline',()=>{
 const f=fixture();assert.equal(f.requests.length,0);f.ready();assert.deepEqual(f.requests,['clip-0.webm']);assert.equal(f.videos[0].muted,true);assert.equal(f.videos[0].playsInline,true);assert.equal(f.videos[1].getAttribute('src'),null);
});
test('prefetch only the next clip in the last second and reuse it on transition',()=>{
 const f=fixture();f.ready();f.videos[0].currentTime=6.8;f.step(100);assert.equal(f.requests.length,1);f.videos[0].currentTime=7.1;f.step(200);assert.deepEqual(f.requests,['clip-0.webm','clip-1.webm']);assert.equal(f.videos[1].paused,true);
 f.videos[0].emit('ended');assert.equal(f.root.dataset.activeWork,'clip-1');assert.equal(f.requests.length,2);assert.equal(f.videos[0].getAttribute('src'),null);assert.equal(f.videos[1].paused,false);
});
test('manual jump discards unrelated prefetch and updates copy, links, selected tab and progress',()=>{
 const f=fixture();f.ready();f.videos[0].currentTime=7.5;f.step(100);f.tabs[3].emit('click');assert.equal(f.root.dataset.activeWork,'clip-3');assert.equal(f.heading.textContent,'Title 3');assert.equal(f.view.href,'/work-3/');assert.equal(f.tabs[3].getAttribute('aria-selected'),'true');assert.equal(f.panel.getAttribute('aria-labelledby'),'work-tab-3');assert.equal(f.videos[1].getAttribute('src'),null);assert.equal(f.requests.at(-1),'clip-3.webm');
});
test('mobile selects the separate 640px MP4',()=>{const f=fixture({mobile:true});f.ready();assert.deepEqual(f.requests,['clip-0-mobile.mp4']);});
test('reduced motion, save-data, slow 3G and low bandwidth rotate only posters',()=>{
 for(const settings of [{reduced:true},{saveData:true},{effectiveType:'3g'},{downlink:.5}]){const f=fixture(settings);f.ready();for(let t=0;t<=8500;t+=250)f.step(t);assert.equal(f.requests.length,0);assert.equal(f.root.dataset.activeWork,'clip-1');}
});
test('offscreen and hidden pages pause, then resume without downloading another source',async()=>{
 const f=fixture();f.ready();await Promise.resolve();await Promise.resolve();f.visible(false);assert.equal(f.videos[0].paused,true);f.visible(true);assert.equal(f.videos[0].paused,false);await Promise.resolve();await Promise.resolve();f.hidden(true);assert.equal(f.videos[0].paused,true);f.hidden(false);assert.equal(f.videos[0].paused,false);assert.equal(f.requests.length,1);
});
test('pause freezes poster time and keyboard arrows wrap with one tab stop',()=>{
 const f=fixture({saveData:true});f.ready();f.step(0);f.step(250);f.pause.emit('click');for(let t=500;t<10000;t+=250)f.step(t);assert.equal(f.root.dataset.activeWork,'clip-0');assert.equal(f.pause.getAttribute('aria-pressed'),'true');f.tabs[0].emit('keydown',{key:'ArrowLeft',preventDefault(){}});assert.equal(f.root.dataset.activeWork,'clip-4');assert.equal(f.tabs[4].getAttribute('tabindex'),'0');assert.equal(f.tabs[0].getAttribute('tabindex'),'-1');assert.equal(f.requests.length,0);
});
test('autoplay rejection keeps the poster and releases the failed video',async()=>{
 const f=fixture({rejectPlay:true});f.ready();await Promise.resolve();await Promise.resolve();assert.equal(f.videos[0].getAttribute('src'),null);assert.equal(f.videos[0].classList.contains('is-playing'),false);assert.equal(f.root.dataset.activeWork,'clip-0');
});
test('failed prefetch is not retried every animation frame',()=>{
 const f=fixture();f.ready();f.videos[0].currentTime=7.2;f.step(100);f.videos[1].emit('error');for(let t=200;t<2000;t+=100)f.step(t);assert.equal(f.requests.length,2);
});
