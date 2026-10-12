"""Original public orientation. Never imports the owner's private archive."""
PATH='/tutorials/platform-start/'
ART='/assets/notes/platform-sf-workflow-v3.webp'
from domestic_platforms import render as render_domestic

def teaser(t):
    return f'''<a class="tutorial-preview" href="{PATH}"><img src="{ART}" width="1672" height="941" loading="lazy" decoding="async" alt="{t('SF 엔지니어의 인물 기준·정비 복도 씬·음향 편집을 보여주는 제작 흐름 예시','Original science-fiction workflow example: character reference, corridor scene and sound edit')}"><div><p class="section-eyebrow">TOOLS / OFFICIAL LESSONS</p><h3>{t('어떤 도구로, 어디서 시작할까?','Which tool? Where do I begin?')}</h3><p class="tutorial-card-date"><time datetime="2026-10-11">2026.10.11</time> · {t('SF 제작 흐름 · 영상 · 음악','SF workflow · Video · Music')}</p><span>{t('플랫폼별 입문 안내 · 강좌 열기','Platform starter guide · Open lesson')} →</span></div></a>'''

def build(out,origin,head,header,footer,t):
    title=t('어떤 도구로, 어디서 시작할까?','Which tool? Where do I begin?')
    desc=t('AI 영상·OST 제작 입문: Seedance, Runway, Suno, ZCRE, BBANANA의 입력 역할과 첫 실습, 공식 강좌 링크.','A beginner guide to AI video and soundtracks: input roles, first exercises and official lessons for Seedance, Runway, Suno, ZCRE and BBANANA.')
    t('어떤 도구로, 어디서 시작할까? | DRA9ON CINEMA','Which tool? Where do I begin? | DRA9ON CINEMA')
    entries=[
      ('Seedance / Dreamina','참고 이미지의 역할부터','Start with reference roles',
       '시트는 얼굴·의상, 씬은 공간·빛·시작 구도로 나눕니다. 업로드한 자료를 입력창의 실제 멘션으로 연결하세요. 지원 모드와 태그 표기는 현재 화면을 따릅니다.',
       'Assign the sheet to identity and clothes, and the scene to space, light and the opening composition. Insert actual uploaded-reference mentions in the prompt field. Use the modes and tags your interface offers.',
       '인물 한 명이 문 쪽으로 눈을 움직이는 컷부터. 인물 동작과 카메라 움직임을 따로 적고, 첫·중간·끝 프레임을 비교하세요.',
       'Start with one person looking toward a doorway. Write acting separately from camera motion, then compare the first, middle and final frames.',
       '/tutorials/seedance-2-5/','이 사이트에서 따라 하기','Practice on this site',
       'https://dreamina.capcut.com/seedance/how-to-use-seedance-2-5'),
      ('Runway','이미지는 시작, 텍스트는 움직임','Image for the start. Text for motion.',
       '입력 이미지를 영상의 시작 화면으로 두고, 프롬프트에는 이어질 행동과 카메라 움직임을 적습니다. 얼굴·손이 깨진 시작 이미지는 먼저 고치세요.',
       'Use the input image as the opening frame and describe the following action and camera motion in the prompt. Repair unclear faces or hands before animating the image.',
       '같은 이미지로 고정 카메라와 느린 전진을 각각 시험하세요. 얼굴과 배경이 어디서 달라지는지 기록하고 한 번에 설정 하나만 바꿉니다.',
       'Test a locked camera and a slow push using the same image. Record changes to the face and background; change one setting at a time.',
       'https://academy.runwayml.com/guides/prompting-guide','공식 입문 강좌','Official starter lesson',
       'https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide'),
      ('Suno','가사와 음악 스타일을 나누기','Separate lyrics from musical style',
       'Custom mode에서 직접 쓴 가사와 장르·악기·보컬의 스타일 설명을 각 입력칸에 나눕니다. 영상 연출 지시는 음악 입력과 별도로 관리하세요.',
       'In Custom mode, separate your original lyrics from descriptions of genre, instruments and vocal style. Keep video direction in a separate production brief.',
       '직접 쓴 네 줄로 시작합니다. 발음과 호흡, 후렴의 감정 크기를 듣고 가사 또는 스타일 하나만 수정해 비교하세요. 공개·수익화 전에는 생성 당시 요금제와 약관을 확인합니다.',
       'Start with four original lines. Listen for pronunciation, breathing and chorus intensity; change either lyrics or style for the next comparison. Check the plan and terms applicable when the song was generated before publication or monetization.',
       'https://help.suno.com/en/articles/2415873','직접 쓴 가사 입력 안내','Guide to using your own lyrics',
       'https://help.suno.com/en/articles/2417409'),
    ]
    cards=[]
    for i,(name,ko,en,bko,ben,eko,een,url,lko,len_,source) in enumerate(entries,1):
        rel='' if url.startswith('/') else ' target="_blank" rel="noopener noreferrer"'
        cards.append(f'''<section class="tutorial-step" id="tool-{i}"><span class="tutorial-number">{i:02}</span><div><p class="section-eyebrow">{name}</p><h2>{t(ko,en)}</h2><p>{t(bko,ben)}</p><details class="tutorial-explain"><summary>{t('첫 실습 펼치기','Try a first exercise')}</summary><p>{t(eko,een)}</p></details><div class="tutorial-actions"><a class="button secondary" href="{url}"{rel}>{t(lko,len_) } ↗</a><a href="{source}" target="_blank" rel="noopener noreferrer">{t('공식 참고 자료','Official reference')} ↗</a></div></div></section>''')
    body=f'''<body class="watch-page">{header()}<main class="tutorial-main" id="main"><a class="note-back" href="/tutorials/">← {t('튜토리얼 목록','All tutorials')}</a><p class="section-eyebrow">DRA9ON CINEMA / TOOLS</p><h1>{title}</h1><p class="tutorial-intro">{t('새 도구를 전부 배우기보다, 만들고 싶은 한 컷부터 정하세요. 입력과 움직임의 역할을 구분하면 첫 실습이 쉬워집니다.','Start with the one shot you want to make. Understanding the roles of inputs and motion makes your first exercise easier.')}</p><p class="tutorial-date"><time datetime="2026-10-11">2026.10.11</time> · {t('입문 · 영상 · 음악','Beginner · Video · Music')}</p><nav class="tutorial-topics" aria-label="{t('플랫폼 선택','Choose a platform')}">{''.join(f'<a href="#tool-{i}">{name}</a>' for i,(name,*_) in enumerate(entries,1))}</nav><figure class="tutorial-comparison"><img src="{ART}" width="1672" height="941" loading="lazy" decoding="async" alt="{t('SF 인물 기준 → 정비 복도 씬 → 음향 편집의 세 단계 예시','Three-panel SF workflow: character reference, corridor scene and audio edit')}"><figcaption><p>{t('인물 기준 → SF 씬 → 음향 편집. 이 강좌용으로 만든 AI 제작 흐름 예시이며, 플랫폼별 실제 출력이나 편집기 화면을 뜻하지 않습니다.','Reference → SF scene → sound edit. An original AI workflow illustration, not actual provider outputs or an editor screenshot.')}</p></figcaption></figure>{''.join(cards)}<section class="tutorial-step"><span class="tutorial-number">04</span><div><h2>{t('더 깊이: 힉스필드 공식 강좌','Go deeper: official Higgsfield lessons')}</h2><p>{t('첫 컷을 만들었다면 카메라 움직임을 배우고, 액션은 준비·접촉·반응으로 나눠 연습해보세요. 아래는 공식 학습 자료로 연결됩니다.','After making your first shot, study camera movement and practice action through preparation, contact and reaction. These links lead to official learning resources.')}</p><div class="tutorial-actions"><a class="button secondary" href="https://higgsfield.ai/camera-controls" target="_blank" rel="noopener noreferrer">{t('카메라 움직임 보기','Explore camera movement')} ↗</a><a href="https://higgsfield.ai/academy/courses/direct-ai-fight-scenes" target="_blank" rel="noopener noreferrer">{t('액션 연출 강좌','Action direction course')} ↗</a></div></div></section><p class="tutorial-notice">{t('공식 안내를 참고해 직접 작성한 공개 입문 실습입니다. 강의 전체 영상이나 원문 프롬프트를 재배포하지 않습니다. 기능·사용량·비용은 플랫폼과 모델, 계정에 따라 다르므로 생성 전에 현재 화면을 확인하세요.','These original public exercises reference official documentation. Full course videos and source prompts are not redistributed. Features, usage and costs vary by platform, model and account; check the current interface before generating.')}</p><div class="tutorial-actions"><a class="button primary" href="/tutorials/character-sheet/">{t('캐릭터 시트부터 시작하기','Start with a character sheet')} →</a><a href="/tutorials/seedance-2-5/">{t('씬 이미지 영상화 실습','Animate a scene image')} →</a></div></main>{footer()}</body></html>'''
    schema={'@context':'https://schema.org','@type':'Article','headline':title,'description':desc,'url':origin+PATH,'image':origin+ART,'datePublished':'2026-10-11','dateModified':'2026-10-13','author':{'@type':'Organization','name':'DRA9ON CINEMA'}}
    body=body.replace('<nav class="tutorial-topics"', '<div class="tutorial-actions"><a href="#korean-platforms">'+t('국내 플랫폼 안내','Korean services')+' ↓</a></div><nav class="tutorial-topics"',1)
    body=body.replace('<p class="tutorial-notice">',render_domestic(t)+'<p class="tutorial-notice">',1)
    dst=out/PATH.strip('/');dst.mkdir(parents=True,exist_ok=True)
    (dst/'index.html').write_text(head(title+' | DRA9ON CINEMA',desc,PATH,schema).replace('property="og:type" content="video.episode"','property="og:type" content="article"')+body,encoding='utf-8')
