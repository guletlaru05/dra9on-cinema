// Reference data is never executable. This module makes no network or AI calls.
export const TAGS=['카메라','조명','캐릭터 일관성','액션','분위기'];
export const CATEGORIES=['프롬프트','툴·플랫폼','사람','기타'];
const LIMITS={drafts:50,inbox:100,collected:50,completed:100};
const words=s=>String(s||'').toLowerCase().match(/[\p{L}\p{N}]+/gu)||[];
const text=(value,max,label)=>{if(typeof value!=='string'||value.length>max)throw Error(label+' 형식을 확인하세요.');return value;};
const id=value=>{if(typeof value!=='string'||!/^[a-zA-Z0-9:_-]{1,160}$/.test(value))throw Error('자료 ID를 확인하세요.');return value;};
const date=value=>{if(typeof value!=='string'||!/^\d{4}-\d\d-\d\dT/.test(value)||!Number.isFinite(Date.parse(value)))throw Error('저장 시각을 확인하세요.');return value;};
export function publicUrl(value){
 const url=new URL(text(value,3000,'링크'));
 if(url.protocol!=='https:'||url.username||url.password||url.port&&url.port!=='443')throw Error('로그인 정보 없는 공개 HTTPS 링크를 넣으세요.');
 const host=url.hostname.toLowerCase();
 if(host==='localhost'||host.endsWith('.localhost')||host.endsWith('.local')||host.includes(':')||/^(0\.|10\.|127\.|169\.254\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/.test(host))throw Error('PC 내부·사설 네트워크 주소는 수집할 수 없습니다.');
 url.hash='';return url.href;
}
function refs(value){
 if(!Array.isArray(value)||value.length>5)throw Error('참고 자료는 최대 5개입니다.');
 return value.map(r=>({id:id(r.id),title:text(r.title,400,'출처 제목'),url:r.url?publicUrl(r.url):'',source_type:text(r.source_type,40,'자료 구분')}));
}
export function emptyWorkspace(){return {version:1,drafts:[],inbox:[],collected:[],completed:[]};}
export function validateWorkspace(value){
 if(value==null)return emptyWorkspace();
 if(value.version!==1)throw Error('지원하지 않는 작업실 버전입니다.');
 for(const [key,max] of Object.entries(LIMITS))if(!Array.isArray(value[key])||value[key].length>max)throw Error('작업실 '+key+' 저장 한도를 확인하세요.');
 const result={version:1,drafts:value.drafts.map(d=>({id:id(d.id),title:text(d.title,240,'제목'),scene:text(d.scene,8000,'장면'),prompt:text(d.prompt,30000,'프롬프트'),kind:text(d.kind,20,'결과물'),model:text(d.model,100,'모델'),ratio:text(d.ratio,10,'비율'),references:refs(d.references),createdAt:date(d.createdAt),updatedAt:date(d.updatedAt)})),
 inbox:value.inbox.map(d=>{if(!['pending','saved','failed'].includes(d.status))throw Error('수집 상태를 확인하세요.');return {id:id(d.id),url:publicUrl(d.url),note:text(d.note||'',3000,'수집 메모'),status:d.status,title:text(d.title||'',400,'수집 제목'),category:text(d.category||'',40,'자료 종류'),reason:text(d.reason||'',2000,'처리 결과'),createdAt:date(d.createdAt),updatedAt:date(d.updatedAt)};}),
 collected:value.collected.map(d=>{if(!CATEGORIES.includes(d.category)||!Array.isArray(d.prompts)||d.prompts.length>30||!Array.isArray(d.tags)||d.tags.length>15)throw Error('수집 자료를 확인하세요.');return {id:id(d.id),title:text(d.title,400,'자료 제목'),url:publicUrl(d.url),author:text(d.author||'',200,'공개 작성자'),category:d.category,source_type:'내 메모',prompts:d.prompts.map(p=>text(p,100000,'원문 프롬프트')),body:text(d.body||'',150000,'자료 본문'),tags:d.tags.map(t=>text(t,50,'기법')),models:(d.models||[]).map(m=>text(m,100,'사용 모델')),updatedAt:date(d.updatedAt)};}),completed:value.completed.map(id)};
 for(const key of ['drafts','inbox','collected','completed']){const ids=result[key].map(d=>typeof d==='string'?d:d.id);if(new Set(ids).size!==ids.length)throw Error('중복된 작업실 ID가 있습니다.');}
 return result;
}
export function archiveReferences(payload){
 return (payload.items||[]).map((r,index)=>({id:'archive:'+index,title:r.title,body:[r.body,...(r.sections||[]).map(s=>s.text)].join('\n'),prompts:r.prompt?[r.prompt]:[],url:r.links?.[0]?.url||'',source_type:'개인 자료실',tags:r.categories||[],models:r.tools||[]}));
}
const THEMES=[['카메라',/구도|앵글|카메라|원경|중경|근경|lens|camera|framing/i],['조명',/조명|빛|명암|역광|light|shadow/i],['캐릭터 일관성',/인물|얼굴|캐릭터|일관|시트|character|face|identity/i],['액션',/액션|추격|전투|싸움|뛰|달리|fight|chase|action/i],['분위기',/분위기|미감|색|질감|시네마틱|영화|cinematic|mood|texture/i]];
export function searchReferences(scene,documents,{tags=[],model='',limit=5}={}){
 const query=words(scene).filter(x=>x.length>1),themes=THEMES.filter(([,rx])=>rx.test(scene)).map(([tag])=>tag);
 return documents.filter(d=>d.language!=='en').map(d=>{
  const title=String(d.title||'').toLowerCase(),body=[d.body,...d.prompts||[],...d.tags||[]].join(' ').toLowerCase();
  let score=query.reduce((sum,w)=>sum+(title.includes(w)?8:0)+(body.includes(w)?1:0),0);
  score+=themes.filter(t=>(d.tags||[]).includes(t)).length*2;
  if(tags.length&&!tags.every(t=>(d.tags||[]).includes(t)))score=0;
  if(score>0&&model&&body.includes(model.toLowerCase()))score+=2;
  return {...d,score};
 }).filter(d=>d.score>0).sort((a,b)=>Number(b.source_type==='내 튜토리얼')-Number(a.source_type==='내 튜토리얼')||b.score-a.score).slice(0,limit);
}
export function compileDraft({scene,kind='이미지',model='Midjourney (ZCRE)',ratio='16:9',camera='',light='',character='',dialogue=''},references=[]){
 if(typeof scene!=='string'||!scene.trim()||scene.length>8000)throw Error('장면 설명을 1~8,000자로 입력하세요.');
 const lines=[`결과물: ${kind}. 사용할 도구·모델: ${model}. 요청 비율: ${ratio}.`,`장면: ${scene.trim()}`];
 lines.push('인물·공간: '+(character.trim()||'지정한 인물의 얼굴·헤어·의상·소품과 공간 배치를 유지합니다. 지정하지 않은 고유 인물·작품 설정은 추가하지 않습니다.'));
 lines.push('구도: '+(camera.trim()||'인물 위치와 시선 대상이 읽히는 눈높이 구도. 얼굴·손·중요 소품이 필요한 범위 안에 들어가며 전경·중경·후경을 구분합니다.'));
 lines.push('조명·무드: '+(light.trim()||'공간에서 설명할 수 있는 광원, 절제된 채도와 어두운 영화 무드. 그림자 속 눈과 윤곽은 읽히게 하고 피부·옷감·금속의 재질을 자연스럽게 유지합니다. 과한 선명도와 플라스틱 피부는 피합니다.'));
 if(kind==='영상'){
  lines.push('연기·동선: 핵심 행동 하나를 준비 → 행동 → 반응으로 나눕니다. 인물의 이동과 카메라의 움직임을 별도 문장으로 정하고, 시작·끝 상태를 이어갑니다.');
  lines.push('참조 입력: 실제 도구에서 첨부한 파일의 멘션을 선택하고 얼굴·의상·공간·동작의 역할을 지정합니다. 멘션 글자만 쓰는 것으로 파일 첨부를 대신하지 않습니다.');
  lines.push(dialogue.trim()?'대사 원문:\n'+dialogue.trim()+'\n호흡·멈춤을 구분하고 임의의 대사·번역·자막은 추가하지 않습니다.':'소리: 지정하지 않은 대사·음악·자막을 추가하지 않습니다.');
 }else lines.push('정지 이미지: 한 장의 장면입니다. 연속 컷·콜라주·검은 여백·불필요한 글자와 로고는 넣지 않습니다.');
 const techniques=[...new Set(references.flatMap(d=>d.tags||[]).filter(t=>TAGS.includes(t)))];
 if(techniques.length)lines.push('참고 자료에서 확인할 기법: '+techniques.join(' / ')+'. 생성 후 원문 예시와 결과를 나란히 비교합니다.');
 lines.push('검수: 얼굴·손·소품·공간·빛을 기준 이미지와 비교하고 문제가 있는 한 항목씩 수정합니다.');
 return {prompt:lines.join('\n\n'),mode:'규칙 기반 초안 · AI API 미사용',references:references.map(d=>({id:d.id,title:d.title,url:d.url||'',source_type:d.source_type})),note:references.length?'참고 자료를 찾고 입력 조건을 조합한 초안입니다. 원문 프롬프트와 작성된 초안을 구분합니다.':'일치하는 참고 자료가 없어 일반 구성 초안으로 작성했습니다. 출처에 근거한 답변으로 표시하지 않습니다.'};
}
export function applyAction(workspace,action){
 const state=validateWorkspace(structuredClone(workspace));
 if(action.type==='save-draft'){
  const index=state.drafts.findIndex(d=>d.id===action.record.id);
  if(index>=0&&state.drafts[index].updatedAt!==action.expectedUpdatedAt)throw Error('다른 기기에서 수정됐습니다. 목록에서 다시 불러오세요.');
  if(index<0)state.drafts.unshift(action.record);else state.drafts[index]=action.record;
 }else if(action.type==='add-link'){
  const url=publicUrl(action.record.url);if(state.inbox.some(d=>d.url===url))throw Error('이미 수집함에 있는 링크입니다.');state.inbox.unshift({...action.record,url});
 }else if(action.type==='retry-link'){
  const row=state.inbox.find(r=>r.id===action.id);if(!row||row.status!=='failed')throw Error('실패한 링크만 다시 대기시킬 수 있습니다.');row.status='pending';row.reason='';row.updatedAt=action.at;
 }else if(action.type==='progress'){
  state.completed=state.completed.filter(v=>v!==action.id);if(action.done)state.completed.push(action.id);
 }else if(action.type==='sync-results'){
  if(action.report?.schema!=='dra9on-site-results-v1'||!Array.isArray(action.report.results)||action.report.results.length>100)throw Error('PC 동기화 결과 파일을 확인하세요.');
  for(const result of action.report.results){
   const row=state.inbox.find(r=>r.id===result.id);
   if(!row||row.url!==publicUrl(result.url)||row.status!=='pending')continue;
   if(!['saved','failed'].includes(result.status))throw Error('확인되지 않은 처리 결과입니다.');
   row.status=result.status;row.reason=result.reason||'';row.title=result.record?.title||row.title;row.category=result.record?.category||'';row.updatedAt=action.at;
   if(result.status==='saved'&&result.record){const doc={...result.record,id:'collected:'+row.id,url:result.record.url||row.url,updatedAt:action.at};const index=state.collected.findIndex(d=>d.id===doc.id);if(index<0)state.collected.push(doc);else state.collected[index]=doc;}
  }
 }else if(action.type==='delete-draft'){
  state.drafts=state.drafts.filter(d=>d.id!==action.id);
 }else if(action.type==='delete-link'){
  state.inbox=state.inbox.filter(d=>d.id!==action.id);
  state.collected=state.collected.filter(d=>d.id!=='collected:'+action.id);
 }else throw Error('지원하지 않는 작업입니다.');
 return validateWorkspace(state);
}
export function exportWorkspace(state){return {schema:'dra9on-site-workspace-v1',exportedAt:new Date().toISOString(),workspace:validateWorkspace(state)};}
