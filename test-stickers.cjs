const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const code=fs.readFileSync('site-assets/min-stickers.js','utf8');
function setup({width=390,coarse=true,reduced=false}={}){
 const document={activeElement:null};
 function node(){const classes=new Set();return {dataset:{},hidden:false,attrs:{},children:{},events:{},classList:{add:x=>classes.add(x),remove:x=>classes.delete(x),contains:x=>classes.has(x),toggle(x){classes.has(x)?classes.delete(x):classes.add(x);}},querySelector(s){return this.children[s];},addEventListener(k,fn){this.events[k]=fn;},fire(k,e={}){this.events[k]?.(e);},setAttribute(k,v){this.attrs[k]=v;},getAttribute(k){return this.attrs[k];},focus(){document.activeElement=this;}};}
 const section=node(),dialog=node(),expand=node(),art=node(),caption=node(),position=node(),stage=node();
 const cards=Array.from({length:12},(_,i)=>{const x=node();x.dataset={full:`/assets/stickers/min-${i+1}-full.webp`,motion:'salute'};x.attrs['aria-label']='Sticker '+i;return x;});
 section.children={'.sticker-grid':node(),'.sticker-expand':expand,'.sticker-dialog':dialog};
 section.querySelectorAll=s=>s==='[data-sticker]'?cards:[...cards,dialog].filter(n=>n.classList.contains('sticker-moving'));
 dialog.children={'.sticker-large':art,'h3':caption,'.sticker-position':position,'.sticker-prev':node(),'.sticker-next':node(),'.sticker-close':node(),'.sticker-stage':stage};
 dialog.showModal=()=>{dialog.open=true;};dialog.close=()=>{dialog.open=false;dialog.fire('close');};
 expand.children={'.sticker-more':node(),'.sticker-less':node(),'[aria-hidden]':node()};
 const media={};function matchMedia(q){const m={matches:q.includes('reduced')?reduced:q.includes('hover')?coarse:q.includes('600')?width<=600:width<=1000,addEventListener(k,fn){this.change=fn;}};media[q]=m;return m;}
 let intersect;const observer={observe(){},unobserve(){}};
 document.querySelectorAll=()=>[section];
 vm.runInNewContext(code,{document,matchMedia,window:{IntersectionObserver:true},IntersectionObserver:function(fn){intersect=fn;return observer;},setTimeout:()=>1,clearTimeout(){}});
 return {cards,dialog,expand,art,caption,position,stage,document,media,intersect,get visible(){return cards.filter(x=>!x.hidden).length;}};
}
test('two responsive rows, disclosure and resize preserve access to all twelve',()=>{
 const s=setup();assert.equal(s.visible,6);s.expand.fire('click');assert.equal(s.visible,12);assert.equal(s.expand.attrs['aria-expanded'],'true');s.expand.fire('click');assert.equal(s.visible,6);
 const t=setup({width:800});assert.equal(t.visible,8);const pc=setup({width:1440});assert.equal(pc.visible,12);assert.equal(pc.expand.hidden,true);
});
test('lightbox navigates every tile, wraps, supports keys/swipe and returns focus',()=>{
 const s=setup();assert.equal(s.art.src,undefined);s.cards[0].fire('click');assert.equal(s.dialog.open,true);s.dialog.children['.sticker-prev'].fire('click');assert.equal(s.position.textContent,'12 / 12');
 s.dialog.fire('keydown',{key:'ArrowRight',preventDefault(){}});assert.equal(s.position.textContent,'1 / 12');
 s.stage.fire('touchstart',{touches:[{clientX:200,clientY:100}]});s.stage.fire('touchend',{changedTouches:[{clientX:100,clientY:105}]});assert.equal(s.position.textContent,'2 / 12');
 s.dialog.children['.sticker-close'].fire('click');assert.equal(s.document.activeElement,s.cards[0]);
});
test('touch entrance plays once and reduced motion blocks both entry and tap',()=>{
 const s=setup();const entry=[{target:s.cards[0],isIntersecting:true}];s.intersect(entry);assert.ok(s.cards[0].classList.contains('sticker-moving'));s.cards[0].classList.remove('sticker-moving');s.intersect(entry);assert.ok(!s.cards[0].classList.contains('sticker-moving'));
 s.cards[0].fire('click');assert.ok(s.cards[0].classList.contains('sticker-moving'));
 const r=setup({reduced:true});r.intersect([{target:r.cards[0],isIntersecting:true}]);r.cards[0].fire('click');assert.ok(!r.cards[0].classList.contains('sticker-moving'));assert.ok(!r.dialog.classList.contains('sticker-moving'));assert.equal(r.dialog.open,true);
});
