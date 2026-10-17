/* Exercise the shipped scripts through DOM events and network/clipboard effects. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const metricCode=fs.readFileSync('site-assets/tutorial-metrics.js','utf8');
const youtubeCode=fs.readFileSync('site-assets/api-engagement.js','utf8');
const ENDPOINT='https://metrics.example.workers.dev';
const slugs=['newest','middle','older','oldest'];
const path=slug=>'/tutorials/'+slug+'/';
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const settle=async()=>{await new Promise(resolve=>setImmediate(resolve));};

class Element {
 constructor(tag,document){this.tagName=tag.toLowerCase();this.document=document;this.children=[];this.parentElement=null;this.attributes=new Map();this.dataset={};this.events={};this.hidden=false;this._text='';}
 get className(){return this.attributes.get('class')||'';}
 set className(value){this.attributes.set('class',value);}
 get textContent(){return this._text+this.children.map(child=>child.textContent).join('');}
 set textContent(value){this._text=String(value);for(const child of this.children)child.parentElement=null;this.children=[];}
 setAttribute(name,value){this.attributes.set(name,String(value));if(name.startsWith('data-'))this.dataset[dataName(name)]=String(value);}
 getAttribute(name){if(name.startsWith('data-'))return this.dataset[dataName(name)]??null;return this.attributes.get(name)??null;}
 remove(){if(!this.parentElement)return;const siblings=this.parentElement.children;siblings.splice(siblings.indexOf(this),1);this.parentElement=null;}
 append(...nodes){for(const node of nodes){node.remove();node.parentElement=this;this.children.push(node);}}
 after(...nodes){const parent=this.parentElement;let index=parent.children.indexOf(this)+1;for(const node of nodes){node.remove();node.parentElement=parent;parent.children.splice(index++,0,node);}}
 addEventListener(type,callback){(this.events[type]??=[]).push(callback);}
 async click(){await Promise.all((this.events.click||[]).map(callback=>callback({target:this})));}
 matches(selector){
  if(selector.startsWith('.'))return this.className.split(/\s+/).includes(selector.slice(1));
  const attribute=selector.match(/^([a-z0-9-]+)?\[([a-z0-9-]+)(?:=["']?([^"'\]]+)["']?)?\]$/i);
  if(attribute){const [,tag,name,value]=attribute;return (!tag||tag===this.tagName)&&this.getAttribute(name)!==null&&(value===undefined||this.getAttribute(name)===value);}
  return selector===this.tagName;
 }
 querySelectorAll(selector){
  const parts=selector.trim().split(/\s+/),result=[];
  const matches=node=>{if(!node.matches(parts.at(-1)))return false;let ancestor=node.parentElement;for(let index=parts.length-2;index>=0;index--){while(ancestor&&!ancestor.matches(parts[index]))ancestor=ancestor.parentElement;if(!ancestor)return false;ancestor=ancestor.parentElement;}return true;};
  const visit=node=>{for(const child of node.children){if(matches(child))result.push(child);visit(child);}};visit(this);return result;
 }
 querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 cloneNode(deep=false){const copy=new Element(this.tagName,this.document);copy.attributes=new Map(this.attributes);copy.dataset={...this.dataset};copy._text=this._text;copy.hidden=this.hidden;copy.href=this.href;if(deep)copy.append(...this.children.map(child=>child.cloneNode(true)));return copy;}
}
function dataName(name){return name.slice(5).replace(/-([a-z])/g,(_,letter)=>letter.toUpperCase());}

function setup({kind='index',lang='en',host='dra9oncinema.com',endpoint=ENDPOINT,referrer='https://www.google.com/search?q=private-scene&email=secret@example.com',clipboard=async()=>{},dnt=false,gpc=false}={}){
 const requests=[],privacyAccess=[],clipboardWrites=[],response=deferred();
 const document={documentElement:{lang},referrer};
 document.createElement=tag=>new Element(tag,document);
 const body=document.createElement('body'),head=document.createElement('head');document.body=body;document.head=head;
 document.querySelectorAll=selector=>[...head.querySelectorAll(selector),...body.querySelectorAll(selector)];document.querySelector=selector=>document.querySelectorAll(selector)[0]||null;
 Object.defineProperty(document,'cookie',{get(){privacyAccess.push('cookie read');throw Error('Cookie access is forbidden for metrics');},set(){privacyAccess.push('cookie write');throw Error('Cookie access is forbidden for metrics');}});
 const main=document.createElement('main');body.append(main);
 const publicPath=kind==='article'?path('newest'):kind==='home'?'/':'/tutorials/';
 const meta=(name,content)=>{const node=document.createElement('meta');node.setAttribute('name',name);node.content=content;head.append(node);};
 meta('d9-metrics-endpoint',endpoint);meta('d9-metrics-path',(lang==='en'?'/en':'')+publicPath);meta('d9-metrics-canonical',publicPath);if(kind==='article')meta('d9-tutorial','true');
 const field=attribute=>{const node=document.createElement('span');node.setAttribute(attribute,'');node.textContent='—';body.append(node);return node;};
 const today=field('data-visits-today'),total=field('data-visits-total'),status=field('data-visits-status'),since=field('data-visits-since');
 const list=document.createElement('div');list.className='tutorial-lesson-list';if(kind==='index')list.setAttribute('data-tutorial-list','');main.append(list);
 const cards=kind==='article'?[]:slugs.map(slug=>{const node=document.createElement('a');node.className='tutorial-preview';node.href=(lang==='en'?'/en':'')+path(slug);const content=document.createElement('div'),heading=document.createElement('h3');heading.textContent=slug;content.append(heading);node.append(content);list.append(node);return node;});
 const sortStatus=field('data-tutorial-sort-status');sortStatus.textContent='';
 const sorts={};if(kind==='index')for(const value of ['latest','popular']){const node=document.createElement('button');node.setAttribute('data-tutorial-sort',value);node.setAttribute('aria-pressed',String(value==='latest'));main.append(node);sorts[value]=node;}
 const popular=document.createElement('section');popular.setAttribute('data-popular-tutorials','');popular.hidden=true;const popularList=document.createElement('div');popularList.setAttribute('data-popular-list','');const popularStatus=document.createElement('p');popularStatus.setAttribute('data-popular-status','');popular.append(popularStatus,popularList);if(kind==='home')main.append(popular);
 const promptTexts=['An original empty rain-soaked station.\nCamera: slow lateral tracking.\nLighting: dim practical lamps.','A quiet workshop, a locked camera.\nKeep the character and costume unchanged.'];
 if(kind==='article')for(const value of promptTexts){const pre=document.createElement('pre'),code=document.createElement('code');code.textContent=value;pre.append(code);main.append(pre);}
 const navigator={doNotTrack:dnt?'1':'0',globalPrivacyControl:gpc,clipboard:{async writeText(value){clipboardWrites.push(value);await clipboard(value);}}};
 Object.defineProperty(navigator,'userAgent',{get(){privacyAccess.push('user agent');throw Error('Fingerprinting is forbidden');}});
 const window={};
 const context={document,window,navigator,URL,location:{hostname:host,origin:'https://'+host,href:'https://'+host+publicPath+'?email=secret@example.com#private'},fetch(url,options={}){requests.push({url,options,body:options.body?JSON.parse(options.body):null});return url===endpoint+'/summary'?response.promise:Promise.resolve({ok:true,status:204});}};
 for(const name of ['localStorage','sessionStorage'])Object.defineProperty(context,name,{get(){privacyAccess.push(name);throw Error('Persistent metrics storage is forbidden');}});
 vm.runInNewContext(metricCode,context);
 return {context,document,requests,privacyAccess,clipboardWrites,promptTexts,today,total,status,since,list,cards,sorts,sortStatus,popular,popularList,
  copies:()=>document.querySelectorAll('.prompt-copy'),copyRequests:()=>requests.filter(request=>request.body?.kind==='copy'),
  async respond(value,ok=true){response.resolve({ok,json:async()=>value});await settle();},
  async fail(){response.reject(Error('Offline'));await settle();}};
}
const order=list=>list.children.map(node=>node.querySelector('h3')?.textContent);
const example=()=>({startedAt:'2026-10-17T00:00:00.000Z',updatedAt:'2026-10-17T01:00:00.000Z',timezone:'Asia/Seoul',day:'2026-10-17',today:{pageviews:8,entries:3},total:{pageviews:200,entries:50},tutorials:{[path('newest')]:{views:4,copies:1},[path('middle')]:{views:30,copies:0},[path('older')]:{views:20,copies:2},[path('oldest')]:{views:1,copies:999}}});

test('latest is the default; popular uses actual views and latest restores the original order',async()=>{
 const a=setup();assert.deepEqual(order(a.list),slugs);assert.equal(a.sorts.latest.getAttribute('aria-pressed'),'true');
 await a.respond(example());assert.deepEqual(order(a.list),slugs);assert.equal(a.today.textContent,'—');assert.equal(a.total.textContent,'—');
 assert.equal(a.cards[1].querySelector('.tutorial-metric').textContent,'Views 30 · Prompt copies 0');
 await a.sorts.popular.click();assert.deepEqual(order(a.list),['middle','older','newest','oldest']);assert.equal(a.sorts.popular.getAttribute('aria-pressed'),'true');
 await a.sorts.latest.click();assert.deepEqual(order(a.list),slugs);assert.equal(a.sorts.latest.getAttribute('aria-pressed'),'true');assert.deepEqual(a.privacyAccess,[]);
});

test('popular selected while summary is pending remains selected when data arrives',async()=>{
 const a=setup();await a.sorts.popular.click();assert.deepEqual(order(a.list),slugs);assert.notEqual(a.sortStatus.textContent,'');
 await a.respond(example());assert.deepEqual(order(a.list),['middle','older','newest','oldest']);assert.equal(a.sorts.popular.getAttribute('aria-pressed'),'true');assert.equal(a.sorts.latest.getAttribute('aria-pressed'),'false');assert.equal(a.sortStatus.textContent,'');
});

test('home shows three genuinely most-viewed tutorials, regardless of copy popularity',async()=>{
 const a=setup({kind:'home'});assert.equal(a.popular.hidden,true);await a.respond(example());
 assert.equal(a.popular.hidden,false);assert.deepEqual(order(a.popularList),['middle','older','newest']);assert.equal(a.popularList.children.length,3);
 assert.notEqual(a.popularList.children[0],a.cards[1]);assert.equal(a.cards[1].parentElement,a.list);
});

test('empty real aggregates display zero without inventing popular tutorials or a start date',async()=>{
 const a=setup({kind:'home'}),value=example();value.startedAt=null;value.updatedAt=null;value.today={pageviews:0,entries:0};value.total={pageviews:0,entries:0};for(const count of Object.values(value.tutorials)){count.views=0;count.copies=0;}
 await a.respond(value);assert.equal(a.today.textContent,'—');assert.equal(a.total.textContent,'—');assert.equal(a.since.textContent,'—');assert.equal(a.popular.hidden,true);assert.equal(a.popularList.children.length,0);assert.equal(a.cards[0].querySelector('.tutorial-metric').textContent,'Views 0 · Prompt copies 0');
});

test('malformed summaries and unavailable service never paint fabricated counts',async t=>{
 const cases=[['negative',v=>{v.tutorials[path('newest')].views=-1;}],['string number',v=>{v.tutorials[path('newest')].views='200';}],['unsafe integer',v=>{v.tutorials[path('newest')].views=Number.MAX_SAFE_INTEGER+1;}],['private path',v=>{v.tutorials['/library/']={views:1,copies:0};}],['missing tutorials',v=>{delete v.tutorials;}]];
 for(const [name,mutate] of cases)await t.test(name,async()=>{const a=setup({kind:'home'}),value=example();mutate(value);await a.respond(value);assert.equal(a.today.textContent,'—');assert.equal(a.total.textContent,'—');assert.equal(a.cards[0].querySelector('.tutorial-metric'),null);assert.equal(a.popular.hidden,true);assert.equal(a.status.textContent,'Counts are temporarily unavailable.');});
 for(const failure of ['http','network'])await t.test(failure,async()=>{const a=setup();if(failure==='http')await a.respond({},false);else await a.fail();assert.equal(a.today.textContent,'—');assert.equal(a.status.textContent,'Counts are temporarily unavailable.');});
});

test('events contain only numeric-aggregate inputs, not cookies, IDs, URLs or prompt text',async()=>{
 const a=setup({kind:'article'});const pageview=a.requests.find(request=>request.body?.kind==='pageview');
 assert.deepEqual(pageview.body,{kind:'pageview',path:'/en/tutorials/newest/',entry:true,referrer:'google'});
 assert.equal(pageview.options.credentials,'omit');assert.equal(pageview.options.referrerPolicy,'no-referrer');assert.deepEqual(Object.keys(pageview.options.headers),['Content-Type']);
 await a.copies()[0].click();const copy=a.copyRequests()[0];assert.deepEqual(copy.body,{kind:'copy',path:'/en/tutorials/newest/',entry:false,referrer:'google',card:'prompt-1'});assert.equal(copy.options.credentials,'omit');assert.equal(copy.options.referrerPolicy,'no-referrer');
 const transmitted=JSON.stringify(a.requests);for(const forbidden of ['secret@example.com','private-scene','An original empty','browserId','fingerprint','Authorization','Cookie'])assert.equal(transmitted.includes(forbidden),false,forbidden);assert.deepEqual(a.privacyAccess,[]);
 const internal=setup({referrer:'https://dra9oncinema.com/tutorials/?private=not-collected'});assert.equal(internal.requests.find(request=>request.body)?.body.entry,false);assert.equal(internal.requests.find(request=>request.body)?.body.referrer,'direct');
});

test('a prompt copy is recorded only after clipboard success, with distinct card IDs',async()=>{
 const gate=deferred();let first=true;const a=setup({kind:'article',clipboard:()=>{if(first){first=false;return gate.promise;}}});
 const clicked=a.copies()[0].click();await settle();assert.deepEqual(a.clipboardWrites,[a.promptTexts[0]]);assert.equal(a.copyRequests().length,0);assert.equal(a.document.querySelector('.prompt-copy-status').textContent,'');
 gate.resolve();await clicked;assert.equal(a.copyRequests().length,1);assert.equal(a.copyRequests()[0].body.card,'prompt-1');assert.equal(a.document.querySelector('.prompt-copy-status').textContent,'Copied.');
 await a.copies()[1].click();assert.equal(a.copyRequests().length,2);assert.equal(a.copyRequests()[1].body.card,'prompt-2');assert.equal(a.clipboardWrites[1],a.promptTexts[1]);assert.deepEqual(a.privacyAccess,[]);
});

test('clipboard rejection is visible and never becomes a counted copy',async()=>{
 const a=setup({kind:'article',clipboard:async()=>{throw Error('Permission denied');}});await a.copies()[0].click();
 assert.equal(a.copyRequests().length,0);assert.equal(a.document.querySelector('.prompt-copy-status').textContent,'Copy failed. Select the text and copy it.');
});

test('unconfigured and preview pages make no requests; privacy opt-outs only read public totals',async t=>{
 for(const options of [{endpoint:''},{host:'127.0.0.1'},{dnt:true},{gpc:true}])await t.test(JSON.stringify(options),async()=>{
  const a=setup({kind:'article',...options});const reads=options.dnt||options.gpc?1:0;assert.equal(a.requests.length,reads);await a.copies()[0].click();assert.equal(a.requests.length,reads);assert.equal(a.requests.some(request=>request.body),false);if(reads){await a.respond(example());assert.equal(a.today.textContent,'—');assert.equal(a.total.textContent,'—');}assert.deepEqual(a.clipboardWrites,[a.promptTexts[0]]);assert.deepEqual(a.privacyAccess,[]);
 });
});

test('YouTube display preserves exact API integer strings and hides unavailable values',()=>{
 const document={createElement:tag=>new Element(tag,document),documentElement:{lang:'en'}};
 const works=[{id:'huge',apiViewCount:'900719925474099312345'},{id:'zero',apiViewCount:'0'},{id:'missing'},{id:'wrong-type',apiViewCount:123},{id:'negative',apiViewCount:'-1'}];
 const notices=[],window={PORTFOLIO:works,dispatchEvent:event=>notices.push(event),D9ExternalConsent:{prepare(){}}};
 const context={window,document,Event:class{constructor(type){this.type=type;}}};
 for(const name of ['localStorage','sessionStorage'])Object.defineProperty(context,name,{get(){throw Error('API display must not store browser identity');}});
 vm.runInNewContext(youtubeCode,context);
 const huge=document.createElement('span');window.D9Engagement.observeCard(huge,'huge');assert.equal(huge.textContent,'YouTube views 900719925474099312345');assert.equal(huge.hidden,false);
 const zero=document.createElement('span');window.D9Engagement.observeCard(zero,'zero');assert.equal(zero.textContent,'YouTube views 0');assert.equal(zero.hidden,false);
 for(const id of ['missing','wrong-type','negative']){const node=document.createElement('span');window.D9Engagement.observeCard(node,id);assert.equal(node.hidden,true);}
 assert.equal(notices[0].type,'d9-engagement-ready');
});
