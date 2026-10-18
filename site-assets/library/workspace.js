import {createLinkPreview} from './link-preview.js?v=20261018-preview1';
import {recommendSettings,incompatibleModel} from './scene-assist.js?v=20261018-assist1';
import {TAGS,validateWorkspace,archiveReferences,searchReferences,compileDraft,exportWorkspace} from './workspace-core.js?v=20261018-workspace2';
const $=id=>document.getElementById(id);
const element=(tag,text,className)=>{const node=document.createElement(tag);if(text!=null)node.textContent=text;if(className)node.className=className;return node;};
const now=()=>new Date().toISOString();
function download(value,name){const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));const a=element('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),5000);}
export function createWorkspace({save,collect,getGeneration}){
 let state=validateWorkspace(),documents=[],tutorials=[],referenceError='',draftId='',draftDate='',draftCreated='',selectedRefs=[],active='compose',session=0,busy=false;
 const root=$('workspace');
 let sceneTimer=null,previewTimer=null,lastAutoPrompt='',lastAutoTitle='',sceneDirty=false;
 const modelInput=$('ws-model'),sceneInput=$('ws-scene'),autoInput=$('ws-auto');
 const status=message=>$('ws-status').textContent=message;
 const route=name=>{active=name;for(const panel of root.querySelectorAll('[data-ws-panel]'))panel.hidden=panel.dataset.wsPanel!==name;for(const button of root.querySelectorAll('[data-ws-tab]'))button.setAttribute('aria-pressed',String(button.dataset.wsTab===name));};
 root.querySelectorAll('[data-ws-tab]').forEach(button=>button.addEventListener('click',()=>route(button.dataset.wsTab)));
 function showWorkspace(){root.hidden=false;$('library').hidden=true;$('workspace-nav').hidden=false;$('open-workspace').setAttribute('aria-pressed','true');$('open-archive').setAttribute('aria-pressed','false');}
 function showArchive(){root.hidden=true;$('library').hidden=false;$('open-workspace').setAttribute('aria-pressed','false');$('open-archive').setAttribute('aria-pressed','true');}
 $('open-workspace').addEventListener('click',showWorkspace);$('open-archive').addEventListener('click',showArchive);
 for(const name of ['tutorial','threads','guidebook','platform'])$('collection-'+name).addEventListener('click',showArchive);
 function sourceCard(doc){
  const article=element('article',null,'ws-source');article.append(element('small',doc.source_type),element('h3',doc.title));
  if(doc.author)article.append(element('p','게시자: '+doc.author,'ws-author'));
  if(doc.models?.length)article.append(element('p','모델: '+doc.models.join(' / '),'muted'));
  if(doc.tags?.length)article.append(element('p','기법: '+doc.tags.join(' · '),'muted'));
  if(doc.url){const link=element('a','출처 열기 ↗');link.href=doc.url;link.target='_blank';link.rel='noopener noreferrer';article.append(link);}
  if(doc.prompts?.length){const detail=element('details');detail.append(element('summary','원문 프롬프트 전체 보기 · '+doc.prompts.length+'개'));for(const prompt of doc.prompts){detail.append(element('pre',prompt));const copy=element('button','이 원문 전체 복사');copy.type='button';copy.addEventListener('click',()=>copyText(prompt));detail.append(copy);}article.append(detail);}
  const body=element('details');body.append(element('summary','설명·본문 보기'),element('pre',doc.body||'별도 본문 없음'));article.append(body);return article;
 }
 async function copyText(text){try{await navigator.clipboard.writeText(text);status('전체 내용을 복사했습니다.');}catch{status('자동 복사가 차단됐습니다. 입력칸이나 원문을 길게 눌러 전체 선택 후 복사하세요.');}}
 async function mutate(action,success){
  if(busy){status('저장 중입니다. 잠시 뒤 다시 눌러주세요.');return false;}busy=true;const ticket=session;
  try{status('소유자 전용 저장소에 저장 중…');const payload=await save(action);if(ticket!==session)return false;state=validateWorkspace(payload.workspace);documents=[...tutorials,...archiveReferences(payload),...state.collected];render();status(success);return true;}
  catch(error){if(ticket===session)status('저장하지 못했습니다. '+error.message);return false;}
  finally{busy=false;}
 }
 function render(){
  $('ws-counts').textContent=`내 튜토리얼 ${tutorials.length}편 · 개인 참고 자료 ${documents.length-tutorials.length}개 · 저장한 프롬프트 ${state.drafts.length}개 · 수집 대기 ${state.inbox.filter(r=>r.status==='pending').length}개`;
  $('ws-reference-status').textContent=referenceError;
  const list=$('ws-saved');list.replaceChildren();
  for(const record of state.drafts){const card=element('article',null,'ws-card');card.append(element('span',record.kind+' / '+record.model+' / '+record.ratio,'badge'),element('h3',record.title),element('p',new Date(record.updatedAt).toLocaleString('ko-KR'),'muted'));const open=element('button','열어서 수정'),remove=element('button','삭제');open.type=remove.type='button';open.addEventListener('click',()=>{draftId=record.id;draftDate=record.updatedAt;draftCreated=record.createdAt;sceneDirty=true;modelInput.dataset.manual='true';$('ws-ratio').dataset.manual='true';clearTimeout(sceneTimer);$('ws-scene').value=record.scene;$('ws-kind').value=record.kind;$('ws-model').value=record.model;$('ws-ratio').value=record.ratio;$('ws-title').value=record.title;$('ws-prompt').value=record.prompt;selectedRefs=record.references;$('ws-references').replaceChildren(...record.references.map(ref=>sourceCard(documents.find(d=>d.id===ref.id)||ref)));$('ws-prompt-note').textContent='저장된 프롬프트입니다. 수정 후 저장하면 이 버전을 업데이트합니다.';route('compose');root.scrollIntoView({block:'start'});});remove.addEventListener('click',()=>{if(confirm('이 프롬프트를 삭제할까요?'))mutate({type:'delete-draft',id:record.id},'삭제했습니다.');});card.append(open,document.createTextNode(' '),remove);list.append(card);}
  if(!state.drafts.length)list.append(element('p','아직 저장한 프롬프트가 없습니다. 장면 설명으로 첫 초안을 만들어보세요.','muted'));
  const inbox=$('ws-inbox-list');inbox.replaceChildren();
  for(const row of state.inbox){const card=element('article',null,'ws-card');card.append(element('span',({pending:'PC 처리 대기',saved:'자료 저장 완료',failed:'읽기 실패'})[row.status]+(row.category?' · '+row.category:''),'badge'),element('h3',row.title||row.url));const link=element('a',row.url);link.href=row.url;link.target='_blank';link.rel='noopener noreferrer';card.append(link);if(row.note)card.append(element('p',row.note));if(row.reason)card.append(element('p',row.reason,'ws-note'));const doc=state.collected.find(d=>d.id==='collected:'+row.id);if(doc)card.append(sourceCard(doc));if(row.status==='failed'){const retry=element('button','PC에서 다시 확인하도록 대기');retry.addEventListener('click',()=>mutate({type:'retry-link',id:row.id,at:now()},'다시 대기시켰습니다.'));card.append(retry);}const remove=element('button','수집함에서 삭제');remove.addEventListener('click',()=>{if(confirm('수집함의 링크와 연결된 사이트 자료를 삭제할까요?'))mutate({type:'delete-link',id:row.id},'사이트 수집함에서 삭제했습니다.');});card.append(remove);inbox.append(card);}
  if(!state.inbox.length)inbox.append(element('p','모바일에서 공유 링크를 복사한 뒤 위에 붙여넣으세요.','muted'));
  $('ws-learn-progress').textContent=`학습 완료 ${tutorials.filter(d=>state.completed.includes(d.id)).length} / ${tutorials.length}편`;
  const learning=$('ws-learning');learning.replaceChildren();for(const doc of tutorials){const card=element('article',null,'ws-card');card.append(element('h3',doc.title));const link=element('a','튜토리얼 읽기 ↗');link.href=doc.url;link.target='_blank';link.rel='noopener';card.append(link);const label=element('label',null,'ws-check'),checkbox=element('input');checkbox.type='checkbox';checkbox.checked=state.completed.includes(doc.id);checkbox.addEventListener('change',async()=>{checkbox.disabled=true;const ok=await mutate({type:'progress',id:doc.id,done:checkbox.checked},'학습 기록을 저장했습니다.');if(!ok){checkbox.checked=!checkbox.checked;checkbox.disabled=false;}});label.append(checkbox,document.createTextNode('실습까지 완료'));card.append(label);learning.append(card);}
 }
 function compose(automatic=false){try{if(automatic&&sceneDirty){$('ws-assist-note').textContent='직접 수정한 초안은 유지했습니다. 다시 만들려면 아래 버튼을 누르세요.';return;}const scene=$('ws-scene').value,filter=$('ws-tag').value;if(incompatibleModel($('ws-kind').value,modelInput.value))throw Error('결과물 종류에 맞는 모델을 선택하세요. 영상에는 Midjourney 같은 이미지 모델을 사용할 수 없습니다.');const found=searchReferences(scene,documents,{tags:filter?[filter]:[],model:$('ws-model').value});const result=compileDraft({scene,kind:$('ws-kind').value,model:$('ws-model').value,ratio:$('ws-ratio').value,camera:$('ws-camera').value,light:$('ws-light').value,character:$('ws-character').value,dialogue:$('ws-dialogue').value},found);selectedRefs=result.references;sceneDirty=false;$('ws-prompt').value=result.prompt;$('ws-prompt-note').textContent=result.mode+'. '+result.note;if(!$('ws-title').value||$('ws-title').value===lastAutoTitle){$('ws-title').value=scene.trim().slice(0,70);lastAutoTitle=$('ws-title').value;}lastAutoPrompt=result.prompt;$('ws-references').replaceChildren(...found.map(sourceCard));if(!found.length)$('ws-references').append(element('p','일치하는 참고 자료를 찾지 못했습니다. 검색할 장면·기법을 더 구체적으로 입력하세요.','muted'));status(automatic?'장면에 맞춰 참고 자료와 초안을 자동으로 준비했습니다. 검토 후 비공개 저장하세요.':'초안을 만들었습니다. 아래에서 직접 수정하고 저장하세요.');}catch(error){status(error.message);}}

 function assist(){
  const suggested=recommendSettings(sceneInput.value,$('ws-kind').value);
  if(modelInput.dataset.manual!=='true'||incompatibleModel($('ws-kind').value,modelInput.value)){modelInput.value=suggested.model;delete modelInput.dataset.manual;}
  if($('ws-ratio').dataset.manual!=='true')$('ws-ratio').value=suggested.ratio;
  $('ws-assist-note').textContent=suggested.reason+(suggested.tags.length?' 감지한 기법: '+suggested.tags.join(' · '):'')+' 실제 모델 제공 여부·가격은 생성 전에 확인하세요.';
 }
 function scheduleScene(){clearTimeout(sceneTimer);if(!autoInput.checked||!sceneInput.value.trim())return;sceneTimer=setTimeout(()=>{assist();compose(true);},900);}
 sceneInput.addEventListener('input',scheduleScene);
 for(const name of ['camera','light','character','dialogue'])$('ws-'+name).addEventListener('input',scheduleScene);
 $('ws-kind').addEventListener('change',()=>{assist();scheduleScene();});
 modelInput.addEventListener('input',()=>{modelInput.dataset.manual='true';scheduleScene();});
 $('ws-ratio').addEventListener('change',()=>{$('ws-ratio').dataset.manual='true';scheduleScene();});
 $('ws-tag').addEventListener('change',scheduleScene);
 autoInput.addEventListener('change',()=>{clearTimeout(sceneTimer);if(autoInput.checked)scheduleScene();});
 $('ws-prompt').addEventListener('input',()=>{sceneDirty=$('ws-prompt').value!==lastAutoPrompt;});
 $('ws-compose').addEventListener('click',()=>{clearTimeout(sceneTimer);assist();compose(false);});
 $('ws-copy').addEventListener('click',()=>copyText($('ws-prompt').value));
 $('ws-save').addEventListener('click',async()=>{if(!$('ws-prompt').value.trim()){status('먼저 프롬프트를 작성하세요.');return;}const at=now(),record={id:draftId||'draft:'+crypto.randomUUID(),title:$('ws-title').value.trim()||'제목 없는 장면',scene:$('ws-scene').value,prompt:$('ws-prompt').value,kind:$('ws-kind').value,model:$('ws-model').value,ratio:$('ws-ratio').value,references:selectedRefs,createdAt:draftCreated||at,updatedAt:at};if(await mutate({type:'save-draft',record,expectedUpdatedAt:draftDate},'전체 프롬프트와 참고 출처를 저장했습니다.')){draftId=record.id;draftDate=at;draftCreated=record.createdAt;}});
 $('ws-new').addEventListener('click',()=>{clearTimeout(sceneTimer);sceneDirty=false;lastAutoPrompt=lastAutoTitle='';delete modelInput.dataset.manual;delete $('ws-ratio').dataset.manual;$('ws-assist-note').textContent='';draftId=draftDate=draftCreated='';selectedRefs=[];for(const name of ['scene','title','prompt','camera','light','character','dialogue'])$('ws-'+name).value='';$('ws-references').replaceChildren();$('ws-prompt-note').textContent='규칙 기반 초안 · AI API 미사용';status('새 장면을 입력하세요.');});

 const preview=createLinkPreview({read:collect,onUpdate:value=>{
  const box=$('ws-link-preview'),info=$('ws-link-preview-status'),content=$('ws-link-preview-content');
  box.hidden=value.phase==='idle';content.replaceChildren();
  if(value.phase==='idle'){info.textContent='';return;}
  if(value.phase==='loading'){info.textContent='게시자와 공개 원문을 불러오는 중…';return;}
  if(value.phase==='ready'){
   info.textContent='공개 원문을 불러왔습니다. 아직 저장하지 않았습니다.';
   const card=sourceCard(value.record);const details=card.querySelector('details');if(details)details.open=true;
   content.append(card);
  }else info.textContent=(value.reason||'원문을 읽지 못했습니다.')+' 링크를 수집함에 넣으면 PC 확인 대기로 보관할 수 있습니다.';
 }});
 const linkInput=$('ws-link');
 function schedulePreview(){clearTimeout(previewTimer);preview.select(linkInput.value);previewTimer=setTimeout(()=>{if(linkInput.value.trim())void preview.load(linkInput.value);},650);}
 linkInput.addEventListener('input',()=>{clearTimeout(previewTimer);preview.select(linkInput.value);});
 for(const event of ['paste','change','blur'])linkInput.addEventListener(event,schedulePreview);
 $('ws-read-link').addEventListener('click',()=>{clearTimeout(previewTimer);void preview.load(linkInput.value,{force:true});});
 $('ws-add-link').addEventListener('click',async()=>{
  if(busy)return;const ticket=session,url=linkInput.value.trim(),note=$('ws-link-note').value;
  $('ws-add-link').disabled=true;clearTimeout(previewTimer);
  try{
   const result=await preview.load(url);if(ticket!==session||!result||linkInput.value.trim()!==url)return;
   const at=now(),row={id:'link:'+crypto.randomUUID(),url,note,status:'pending',title:'',category:'',reason:'',createdAt:at,updatedAt:at};
   if(!await mutate({type:'add-link',record:row},'수집함에 등록했습니다.'))return;
   if(result.deferred)status(result.reason+' PC 처리 대기로 보관했습니다.');
   else await mutate({type:'sync-results',at:now(),report:{schema:'dra9on-site-results-v1',results:[{...result,id:row.id,url:row.url}]}},result.status==='saved'?'게시자·출처와 공개 원문 전체를 내 메모에 저장했습니다.':'원문은 저장하지 않았습니다. 수집함에서 실패 이유를 확인하세요.');
   if(ticket===session&&linkInput.value.trim()===url){linkInput.value='';$('ws-link-note').value='';preview.clear();}
  }catch(error){if(ticket===session)status(error.message);}
  finally{$('ws-add-link').disabled=false;}
 });
 $('ws-export').addEventListener('click',()=>download(exportWorkspace(state),'dra9on-site-workspace.json'));
 $('ws-import-results').addEventListener('change',async event=>{const file=event.target.files[0];event.target.value='';if(!file)return;try{if(file.size>2500000)throw Error('결과 파일은 2.5MB 이하여야 합니다.');await mutate({type:'sync-results',report:JSON.parse(await file.text()),at:now()},'PC 처리 결과를 반영했습니다.');}catch(error){status(error.message);}});
 $('ws-refresh').addEventListener('click',()=>location.reload());
 return {
  async load(payload){const ticket=++session;state=validateWorkspace(payload.workspace);documents=[...archiveReferences(payload),...state.collected];showWorkspace();render();try{const response=await fetch('../tutorial-reference-index.json',{cache:'no-cache',credentials:'omit'});if(!response.ok)throw Error();const index=await response.json();if(ticket!==session)return;tutorials=index.documents.filter(d=>d.language==='ko');documents=[...tutorials,...archiveReferences(payload),...state.collected];referenceError='';render();}catch{if(ticket===session){referenceError='공개 튜토리얼 색인을 불러오지 못했습니다. 기존 개인 자료로 검색합니다. 새로고침으로 다시 시도하세요.';render();}}},
  clear(){session++;clearTimeout(sceneTimer);clearTimeout(previewTimer);preview.clear();sceneDirty=false;lastAutoPrompt=lastAutoTitle='';delete modelInput.dataset.manual;delete $('ws-ratio').dataset.manual;root.hidden=true;$('workspace-nav').hidden=true;state=validateWorkspace();documents=[];tutorials=[];referenceError='';selectedRefs=[];draftId=draftDate=draftCreated='';for(const input of root.querySelectorAll('textarea,input:not([type=file])'))input.value='';$('ws-model').value='Midjourney (ZCRE)';$('ws-kind').value='이미지';$('ws-ratio').value='16:9';for(const name of ['references','saved','inbox-list','learning'])$('ws-'+name).replaceChildren();$('ws-assist-note').textContent='';status('');}
 };
}
