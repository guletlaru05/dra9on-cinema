const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('site-assets/community.js','utf8');
class Node{
 constructor(tag='div'){this.tagName=tag;this.children=[];this.textContent='';const classes=new Set();this.classList={add:x=>classes.add(x),contains:x=>classes.has(x)};}
 append(...nodes){this.children.push(...nodes);}prepend(...nodes){this.children.unshift(...nodes);}replaceChildren(...nodes){this.children=nodes;}setAttribute(k,v){this[k]=v;}
}
function fixture(hash=''){
 const nodes=Object.fromEntries(['board-posts','board-detail-content','board-status','board-filter'].map(id=>[id,new Node()]));nodes['board-filter'].value='all';
 const context={document:{createElement:tag=>new Node(tag)},$:id=>nodes[id],location:{hash},t:(ko,en)=>en,topic:v=>v,date:()=> 'Oct 19, 2026',owner:()=>false,auth:{currentUser:null},readOnlyPreview:true,loading:false,posts:[]};
 vm.createContext(context);vm.runInContext(source.slice(source.indexOf('function text('),source.indexOf('function deadline('))+source.slice(source.indexOf('function postRow('),source.indexOf('async function loadPosts(')),context);
 return {context,nodes};
}
const snapshot=(id,answer='')=>({id,data:()=>({title:'<img src=x onerror=alert(1)>',nickname:'A viewer',topic:'character',body:'Actual question text',answer})});
test('list contains five columns and text-only title links, without exposing post bodies',()=>{const f=fixture();f.context.posts=[snapshot('one')];f.context.renderPosts();const row=f.nodes['board-posts'].children[0];assert.equal(row.tagName,'tr');assert.equal(row.children.length,5);assert.equal(row.children[0].children[0].textContent,'<img src=x onerror=alert(1)>');assert.equal(row.children[0].children[0].href,'#post-one');assert.equal(f.nodes['board-detail-content'].children.length,0);});
test('a direct post link shows exactly one full question and creator reply',()=>{const f=fixture('#post-two');f.context.posts=[snapshot('one'),snapshot('two','Creator answer')];f.context.renderPosts();const card=f.nodes['board-detail-content'].children[0];assert.equal(card.tagName,'article');assert.equal(card.id,'post-two');assert.ok(card.children.some(n=>n.textContent==='Actual question text'));assert.ok(card.children.some(n=>n.textContent==='Creator answer'));assert.equal(f.nodes['board-posts'].children[1].classList.contains('has-answer'),true);f.context.location.hash='#board';f.context.renderPosts();assert.equal(f.nodes['board-detail-content'].children.length,0);assert.equal(f.nodes['board-posts'].children.length,2);});
test('topic filtering never loses the selected direct post or original loaded posts',()=>{const f=fixture('#post-one');f.context.posts=[snapshot('one')];f.nodes['board-filter'].value='making';f.context.renderPosts();assert.equal(f.nodes['board-posts'].children.length,0);assert.equal(f.nodes['board-detail-content'].children.length,1);assert.equal(f.context.posts.length,1);});
test('unavailable direct links report failure instead of pretending the post loaded',()=>{const f=fixture('#post-missing');f.context.renderPosts();assert.match(f.nodes['board-status'].textContent,/Post unavailable/);});
