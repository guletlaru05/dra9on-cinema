// Public official product notes only. Private prompts remain in the protected payload.
export const platforms = [
 {name:'Dreamina · Seedance',tool:'Seedance 2.5',focus:'참고 자료의 역할을 나눠 드라마 한 컷 만들기',
  input:'시작 씬, 캐릭터 시트, 지원 모드의 영상·오디오 참고. 단일 이미지 모드와 여러 참고 자료 모드를 먼저 구분합니다.',
  reference:'자료 업로드 → 입력창에서 해당 첨부 멘션 삽입 → 역할 문장 작성. 공식 예시의 @Image1은 시작 씬, @Image2는 외모 기준처럼 연결합니다. 번호·철자는 실제 화면을 따르며 일반 글자로 “이미지 1”만 적지 않습니다.',
  edit:'공식 가이드는 부분 영상 수정을 소개합니다. 실제 계정에 Video edit가 보일 때만 입력 영상·수정 구간·유지할 조건을 지정하세요. 참고 영상 사용과 이미 만든 영상의 편집은 서로 다른 작업입니다.',
  exercise:['글씨 없는 창가 씬과 인물 시트를 준비합니다.','지원 참고 모드를 고르고 업로드 목록의 멘션을 삽입합니다.','씬은 공간·빛·시작 구도, 시트는 얼굴·머리·의상으로 지정합니다.','인물은 제자리, 카메라는 느린 직선 접근처럼 한 컷을 지시합니다.','길이·비율·해상도·크레딧을 확인하고 첫·중간·끝 프레임을 비교합니다.'],
  caution:'30초나 720p는 화면에서 선택 가능할 때 사용합니다. 멘션이 연결됐는지, 참고 시트의 분할 화면이 영상에 들어가지 않았는지 확인하세요.',
  source:'https://dreamina.capcut.com/seedance/how-to-use-seedance-2-5',lesson:'/tutorials/seedance-2-5/'},
 {name:'Higgsfield',tool:'Higgsfield',focus:'카메라 움직임을 보고 선택하며 연출 공부하기',
  input:'카메라 프리셋 예시와 자신의 시작 이미지를 준비합니다. 서비스 안에서 선택한 모델과 기능 이름을 함께 기록하세요.',
  reference:'시댄스의 멘션 문법을 모든 기능에 그대로 쓰지 않습니다. 선택한 모델의 업로드 슬롯·참고 방식과 실제 입력 화면을 확인하세요.',
  edit:'Camera Controls는 움직임을 고르는 기능입니다. 기존 영상 수정이 필요하면 별도 Edit 화면에서 지원되는 기능과 모델을 확인합니다. 카메라 프리셋과 영상 편집을 같은 기능으로 취급하지 않습니다.',
  exercise:['공식 Camera Controls에서 Static과 Dolly In 예시를 나란히 봅니다.','인물 한 명이 있는 동일한 시작 이미지를 준비합니다.','첫 테스트는 한 프리셋만 고르고 인물 동작은 작게 유지합니다.','같은 이미지로 다른 프리셋을 시험하며 이동 방향과 끝 구도를 기록합니다.','얼굴·손의 안정성과 화면 가장자리 변형도 함께 확인합니다.'],
  caution:'제안한 실습이며 품질을 보장하는 비교 결과는 아닙니다. 움직임을 여러 개 겹치기보다 하나씩 비교하세요.',
  source:'https://higgsfield.ai/camera-controls'},
 {name:'Kling AI',tool:'Kling',focus:'여러 참고 이미지로 인물·의상·공간 연결하기',
  input:'인물, 의상, 배경처럼 역할이 다른 참고 자료를 준비합니다. 다중 이미지 참고의 지원 여부는 선택 모델에서 확인합니다.',
  reference:'Kuaishou 공식 발표는 여러 이미지의 피사체를 함께 참고하는 기능을 설명합니다. 이 자료는 1.6 출시 당시 문서입니다. 최신 모델의 슬롯·멘션 문법은 현재 화면 기준으로 확인하며 4.0 지원 여부를 이 문서로 단정하지 않습니다.',
  edit:'다중 이미지 참고는 새 영상을 만드는 입력 방식입니다. 기존 영상 수정은 별도 기능이 있는지 확인해야 하며 이 발표만으로 지원 여부를 확정할 수 없습니다.',
  exercise:['인물 한 명의 깨끗한 참고 이미지와 단순한 배경을 준비합니다.','현재 모델에 다중 참고 기능이 표시되는지 확인합니다.','각 이미지가 인물·의상·배경 중 무엇을 담당하는지 적습니다.','문으로 고개를 돌리는 정도의 작은 행동으로 먼저 시험합니다.','두 인물로 확장하기 전에 얼굴과 의상 유지가 되는지 검수합니다.'],
  caution:'옛 공식 발표의 기능과 최신 계정의 기능을 구분하세요. 정확한 모델명·사용 모드·입력 개수를 결과와 함께 기록합니다.',
  source:'https://ir.kuaishou.com/node/10401/pdf'},
 {name:'Runway',tool:'Runway',focus:'참고 자료를 이름으로 연결하고 반복 작업에 재사용하기',
  input:'선택 모델이 지원하는 이미지·영상·오디오를 업로드합니다. 허용 미디어 종류는 모델에 따라 다릅니다.',
  reference:'공식 안내: 입력창에서 @를 입력하고 목록에서 업로드한 참고를 선택합니다. 표시 예시는 @[Image 1]입니다. Seedance의 @Image1 표기를 그대로 옮기지 말고 실제 삽입된 태그를 유지합니다.',
  edit:'참고 미디어 연결과 기존 영상 편집은 별개입니다. 원하는 영상 편집 도구의 공식 도움말과 현재 모델의 입력 조건을 따로 확인하세요.',
  exercise:['모델을 선택하고 지원 미디어 종류를 확인합니다.','참고 이미지를 업로드한 뒤 @ 목록에서 해당 항목을 선택합니다.','인물과 공간의 역할을 분리해 작은 동작을 요청합니다.','반복해서 쓸 자료는 이름을 지정해 저장합니다.','원본과 결과를 나란히 비교하고 다음 테스트에서 같은 기준을 유지합니다.'],
  caution:'임시 업로드는 세션 간 유지되지 않을 수 있습니다. 저장 참고를 팀과 공유하는 설정은 개인 자료의 공유 범위를 확인한 뒤 선택하세요.',
  source:'https://help.runwayml.com/hc/en-us/articles/52963720640275-Using-reference-media-to-guide-your-generations'}
];
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!=null)n.textContent=text;if(cls)n.className=cls;return n;};
export function renderPlatforms(target,onStudy){
 target.replaceChildren();
 const intro=el('section',null,'platform-notice');intro.append(el('p','OFFICIAL SOURCES / CHECKED 2026.10.11','eyebrow'),el('h3','플랫폼은 작업실, 모델은 영상 생성 엔진'),el('p','같은 모델도 서비스·계정·모드에 따라 입력 방식과 기능이 다릅니다. 아래는 공식 공개 자료를 정리한 안내이며, 실습 순서는 드래곤시네마의 제안입니다. 링크를 열어 최신 지원 조건을 확인하세요.'));
 target.append(intro);
 const flow=el('ol',null,'platform-flow');for(const text of ['목적 고르기','모델·모드 확인','첨부 역할 지정','짧게 테스트','비교·수정'])flow.append(el('li',text));target.append(flow);
 const grid=el('div',null,'platform-grid');
 for(const p of platforms){const card=el('article',null,'platform-card');card.append(el('p',p.tool,'eyebrow'),el('h3',p.name),el('p',p.focus,'platform-focus'));
 const dl=el('dl');for(const [label,key] of [['입력 자료','input'],['멘션·참고 연결','reference'],['영상 수정','edit']])dl.append(el('dt',label),el('dd',p[key]));card.append(dl);
 const details=el('details');details.append(el('summary','처음 해보는 실습 · 5단계'));const steps=el('ol');p.exercise.forEach(x=>steps.append(el('li',x)));details.append(steps,el('p',p.caution,'muted'));card.append(details);
 const links=el('div',null,'platform-links');const source=el('a','공식 기능 안내 ↗');source.href=p.source;source.target='_blank';source.rel='noopener noreferrer';links.append(source);
 if(p.lesson){const a=el('a','시댄스 전체 튜토리얼 ↗');a.href=p.lesson;a.target='_blank';a.rel='noopener noreferrer';links.append(a);}
 const study=el('button','자료실의 관련 자료 보기');study.type='button';study.addEventListener('click',()=>onStudy(p.tool));links.append(study);card.append(links);grid.append(card);}
 target.append(grid);
 const cost=el('section',null,'platform-notice');cost.append(el('h3','무료 안내와 영상 생성 비용은 별개입니다.'),el('p','이 안내를 읽는 것만으로 외부 플랫폼의 크레딧이 차감되지는 않습니다. 영상 생성·영상 수정·업스케일은 각 서비스의 이용 조건을 따릅니다. 생성 버튼을 누르기 전에 표시된 예상 크레딧, 길이, 해상도, 무료 잔여량을 확인하세요. 고정 가격표는 두지 않습니다.'),el('p','WendVega는 정확한 서비스 주소가 확인되지 않아 기능 설명을 보류했습니다. 이름이 비슷한 서비스를 임의로 연결하지 않습니다.','muted'));target.append(cost);
}
