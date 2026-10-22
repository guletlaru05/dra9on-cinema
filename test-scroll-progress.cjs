const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const code=fs.readFileSync('site-assets/scroll-progress.js','utf8');
function run(native=false,height=2000,reduced=false){
 const callbacks={},queue=[],fill={style:{}},bar={dataset:{},firstElementChild:fill,hidden:true},root={scrollHeight:height,clientHeight:500,scrollTop:0};let resized;
 const motion={matches:reduced,addEventListener(k,fn){this.changed=fn;}};
 const window={CSS:{supports:()=>native},matchMedia:()=>motion,ResizeObserver:function(fn){resized=fn;this.observe=()=>{};}};
 const document={scrollingElement:root,documentElement:root,body:{},getElementById:()=>bar,addEventListener(k,fn){callbacks[k]=fn;}};
 const context={window,document,ResizeObserver:window.ResizeObserver,requestAnimationFrame:fn=>queue.push(fn),addEventListener(k,fn,options){callbacks[k]={fn,options};},removeEventListener(k){delete callbacks[k];}};
 vm.runInNewContext(code,context);
 return {bar,root,fill,callbacks,motion,flush(){while(queue.length)queue.shift()();},resize(){resized();},scroll(){callbacks.scroll.fn();},get pending(){return queue.length;}};
}
test('supported CSS path never adds a scroll listener',()=>{const s=run(true);s.flush();assert.equal(s.bar.dataset.driver,'css');assert.equal(s.bar.hidden,false);assert.equal(s.callbacks.scroll,undefined);assert.equal(s.fill.style.transform,undefined);});
test('fallback coalesces passive scrolls and clamps bounce at both ends',()=>{const s=run();s.flush();assert.equal(s.callbacks.scroll.options.passive,true);s.root.scrollTop=750;s.scroll();s.scroll();assert.equal(s.pending,1);s.flush();assert.equal(s.fill.style.transform,'scaleX(0.5)');s.root.scrollTop=-90;s.scroll();s.flush();assert.equal(s.fill.style.transform,'scaleX(0)');s.root.scrollTop=2500;s.scroll();s.flush();assert.equal(s.fill.style.transform,'scaleX(1)');});
test('short pages hide; dynamic login or board content restores and recalculates range',()=>{const s=run(false,500);s.flush();assert.equal(s.bar.hidden,true);s.root.scrollHeight=2500;s.root.scrollTop=1000;s.resize();s.flush();assert.equal(s.bar.hidden,false);assert.equal(s.fill.style.transform,'scaleX(0.5)');s.root.scrollHeight=500;s.resize();s.flush();assert.equal(s.bar.hidden,true);});
test('reduced-motion keeps functional progress when global CSS animations are disabled',()=>{const s=run(true,2000,true);s.flush();assert.equal(s.bar.dataset.driver,'js');s.root.scrollTop=750;s.scroll();s.flush();assert.equal(s.fill.style.transform,'scaleX(0.5)');s.motion.matches=false;s.motion.changed();s.flush();assert.equal(s.bar.dataset.driver,'css');assert.equal(s.callbacks.scroll,undefined);s.motion.matches=true;s.motion.changed();s.flush();assert.equal(s.bar.dataset.driver,'js');assert.equal(s.fill.style.transform,'scaleX(0.5)');});
