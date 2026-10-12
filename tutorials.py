"""Original public exercises; never reads the owner's private library."""
from html import escape
from site_config import CONTACT_EMAIL
from tutorial_scenes import render as render_scenes
from tutorial_comparisons import render as render_comparison
from seedance_tutorial import build as build_seedance, PATH as SEEDANCE_PATH, ART as SEEDANCE_ART, TITLE_KO as SEEDANCE_TITLE_KO, TITLE_EN as SEEDANCE_TITLE_EN
from platform_tutorial import build as build_platform, teaser as platform_teaser, PATH as PLATFORM_PATH
from seedance_languages import build as build_languages, teaser as languages_teaser, PATH as LANGUAGES_PATH
from camera_tutorial import build as build_camera, teaser as camera_teaser, PATH as CAMERA_PATH

ROUTES = ['/tutorials/', '/tutorials/character-sheet/', SEEDANCE_PATH, PLATFORM_PATH, LANGUAGES_PATH, CAMERA_PATH]
TRANSLATIONS = {}
ART = '/assets/notes/character-sheet-duchess20-v3-center-soft-wm.webp'

def t(ko, en):
    TRANSLATIONS[ko] = en
    return escape(ko)

LABEL = t('튜토리얼', 'Tutorials')
TITLE = t('같은 인물로, 다음 장면까지.', 'The same character. The next scene.')
DESC = t('로판 AI 캐릭터 시트 입문: 외모와 의상을 먼저 정하고, 여러 각도에서 같은 인물을 확인하는 실습.', 'A beginner romantic-fantasy character-sheet exercise: define the face and outfit, then check the same person across multiple views.')
ALT = t('로판 드레스를 입은 여성의 정면·측면 전신과 세 가지 얼굴 각도를 비교하는 캐릭터 시트 실습 예시', 'Practice character sheet comparing front and side full-body views and three portrait angles of a woman in a romantic-fantasy gown')
PROMPT_KO = '''새로운 가상 로판 여주인공의 영화 제작용 캐릭터 레퍼런스 시트를 만들어 주세요.

인물: 20세 성인인 가상의 한국 여성. 한국 아이돌처럼 세련되고 아름다운 외모, 이전 예시와 구분되는 새로운 얼굴, 앳되고 부드러운 타원형 얼굴선, 큰 아몬드형 눈매와 작고 섬세한 코. 긴 짙은 갈색 머리, 반묶음 스타일, 자연스러운 피부 결, 차분한 표정. 실존 인물이나 유명인의 얼굴을 따라 하지 않습니다.
고정 의상: 공작영애의 화려한 아이보리·파우더 블루 실크 드레스, 은빛 자수 보디스와 레이스 긴소매, 진주 장식, 보석 목걸이와 작은 은빛 티아라, 드레스에 맞춘 우아한 구두. 모든 컷에서 같은 의상과 같은 헤어스타일을 유지합니다.
구성: 가로 3:2 캔버스. 왼쪽에 정면 전신과 측면 전신, 오른쪽에 정면 얼굴·45도 얼굴·측면 얼굴. 전신 컷에는 머리부터 신발까지 모두 보이게 합니다.
환경: 단색 짙은 회색 스튜디오 배경, 부드럽고 중립적인 조명. 과한 채도, 강한 역광, 필터 같은 피부 보정은 피합니다.
일관성: 눈매, 코, 턱선, 얼굴 비율, 머리 길이, 드레스의 네크라인과 소매 형태가 각도에 따라 바뀌지 않도록 합니다. 인물의 포즈는 힘을 뺀 자연스러운 자세입니다.
표기: 이미지 가운데에 반투명 DRA9ON CINEMA 워터마크만 넣고, 다른 글씨나 장식은 넣지 않습니다.'''
PROMPT_EN = '''Create a cinematic reference sheet for a new fictional character.

Character: a fictional Korean adult woman aged 20 with refined Korean idol-level beauty, a newly designed identity, a youthful soft oval face, large almond-shaped eyes and a small refined nose. Long dark-brown hair in a half-up style, natural skin texture and a calm expression. Do not imitate a real person or celebrity.
Fixed outfit: a duke’s daughter’s lavish ivory and powder-blue silk gown, silver-embroidered bodice, lace long sleeves, pearl trim, jeweled necklace, delicate silver tiara and matching elegant shoes. Keep the same outfit and hairstyle in every view.
Layout: landscape 3:2 canvas. Front and side full-body views on the left; front, three-quarter and side portraits on the right. Show the entire body, including shoes, in full-body views.
Environment: plain charcoal-gray studio background and soft neutral lighting. Avoid oversaturation, strong backlight and heavily retouched skin.
Consistency: preserve the eye shape, nose, jawline, facial proportions, hair length, gown neckline and sleeve silhouette across views. Use relaxed natural poses.
Text: only a semi-transparent DRA9ON CINEMA watermark across the center; no other text or decoration.'''
TRANSLATIONS[PROMPT_KO] = PROMPT_EN
LESSONS=[{'path':ROUTES[1],'date':'2026-10-11','art':ART,'title':TITLE,'alt':ALT}]
LESSONS.append({'path':SEEDANCE_PATH,'date':'2026-10-11','art':SEEDANCE_ART,'title':t(SEEDANCE_TITLE_KO,SEEDANCE_TITLE_EN),'alt':t('로판 씬을 영상화하기 위한 세 구간 스토리보드','Three-frame storyboard for turning a romantic-fantasy scene into video'),'video':True})

def teaser():
    cards=''.join(f'''<a class="tutorial-preview" href="{lesson['path']}"><img src="{lesson['art']}" width="1536" height="1024" loading="lazy" decoding="async" alt="{lesson['alt']}"><div><p class="section-eyebrow">{'SEEDANCE 2.5 / IMAGE TO VIDEO' if lesson.get('video') else 'CHARACTER / SCENE / LIGHT'}</p><h3>{lesson['title']}</h3><p class="tutorial-card-date"><time datetime="{lesson['date']}">{lesson['date'].replace('-','.')}</time> · {t("이미지 · 영상 · 편집", "Image · Video · Edit") if lesson.get('video') else t("캐릭터 · 씬 · 조명", "Character · Scene · Light")}</p><span>{t('시댄스 2.5 영상화 · 강좌 열기','Seedance 2.5 image to video · Open lesson') if lesson.get('video') else t('로판 캐릭터 시트 기초 · 강좌 열기', 'Romantic-fantasy character basics · Open lesson')} →</span></div></a>''' for lesson in sorted(LESSONS,key=lambda item:item['date'],reverse=True))
    cards+=platform_teaser(t)
    cards+=languages_teaser(t)
    cards=camera_teaser(t)+cards
    return f'''<section class="tutorial-teaser" id="tutorials"><div><p class="section-eyebrow">FILMMAKING / FIELD NOTES</p><h2>{t('장면을 만드는 첫걸음.', 'Your first step into a scene.')}</h2><p>{t('작품을 보다가 제작 과정이 궁금해졌다면. 직접 따라 해보는 작은 실습부터 시작하세요.', 'Curious about how the films are made? Start with a small hands-on exercise.')}</p></div><div class="tutorial-lesson-list">{cards}</div></section>'''

def build_tutorials(out, origin, head, header, footer):
    intro = f'''<p class="tutorial-intro">{t('처음 만드는 사람도 한 단계씩. 완성된 작품 뒤의 제작 방법을 공개 실습으로 풀어봅니다.', 'One step at a time, even for first-time creators. Explore the process behind the films through original public exercises.')}</p>'''
    index_title = t('작품 뒤의 방법, 직접 해보세요.', 'Behind the films. Try the process.')
    topics = '<nav class="tutorial-topics" aria-label="' + t('강좌 주제','Lesson topics') + '">' + ''.join('<a href="/tutorials/character-sheet/' + anchor + '">' + t(ko,en) + '</a>' for anchor,ko,en in [('#step-1','캐릭터','Character'),('#scene-examples','씬 이미지','Scene images'),('#lighting','조명·무드','Light and mood')]) + '<a href="'+SEEDANCE_PATH+'">'+t('시댄스 2.5 · 영상화','Seedance 2.5 · Video')+'</a></nav>'
    body = f'<body class="watch-page">{header()}<main class="tutorial-main" id="main"><a class="note-back" href="/">← {t("사이트로 돌아가기", "Back to the site")}</a><p class="section-eyebrow">DRA9ON CINEMA / TUTORIALS</p><h1>{index_title}</h1>{intro}{topics}{teaser()}<p class="tutorial-notice">{t("직접 구성한 공개 실습을 제작일과 주제별로 차곡차곡 모읍니다.", "Original public exercises, collected over time by publication date and topic.")}</p></main>{footer()}</body></html>'
    schema = {'@context':'https://schema.org','@type':'CollectionPage','name':index_title,'url':origin+ROUTES[0]}
    write(out, ROUTES[0], page_head(head, index_title, DESC, ROUTES[0], schema)+body)
    sections = []
    steps = [
      ('먼저, 바뀌면 안 되는 것을 적습니다.', 'First, write down what must stay fixed.',
       '바로 이미지부터 뽑기보다 인물의 나이대, 머리 길이, 의상과 신발을 네 줄로 적으세요. 이번 실습은 긴 반묶음 머리·작은 은빛 티아라·아이보리와 파우더 블루 드레스·은빛 자수와 진주·우아한 구두로 고정합니다. 성격과 이야기 설정은 별도 메모에 두고, 시트에는 눈으로 비교할 수 있는 특징을 우선합니다.',
       'Before generating images, write four lines covering age range, hair length, outfit and shoes. This exercise fixes long half-up hair, a delicate silver tiara, an ivory and powder-blue gown, silver embroidery and pearls, and elegant shoes. Keep personality and story notes separate; prioritize visible features on the sheet.'),
      ('기준 얼굴을 하나 고릅니다.', 'Choose one reference face.',
       '이미지 생성 도구에서 정면 또는 45도 얼굴 한 장을 먼저 만드세요. 얼굴과 머리가 잘 보이고 조명이 고른 컷이 좋습니다. 마음에 드는 얼굴을 기준으로 저장한 뒤, 도구가 참고 이미지 입력을 지원한다면 그 이미지를 첨부해 다음 시트를 요청하세요. 텍스트만 반복하면 같은 인물이 보장되지 않습니다.',
       'Generate a front or three-quarter portrait first. Choose one with a clear face, visible hair and even lighting. Save your preferred portrait. If your tool supports reference images, attach it when requesting the sheet. Repeating text alone does not guarantee the same identity.'),
      ('다섯 가지 시점으로 확인합니다.', 'Check five useful views.',
       '정면 전신과 측면 전신으로 체형·의상·신발을 보고, 정면·45도·측면 얼굴로 눈매·코·턱선을 확인합니다. 얼굴이 너무 작게 나오면 한 장에 더 많은 포즈를 욱여넣지 말고 얼굴 시트를 별도로 요청하세요. 아래 예시는 이 강좌용으로 새로 만든 AI 이미지이며, 낙하 707의 실제 제작 시트가 아닙니다.',
       'Use front and side full-body views to check silhouette, clothes and shoes. Use front, three-quarter and side portraits to compare eyes, nose and jawline. If faces become too small, request a separate portrait sheet instead of adding more poses. The example below is newly generated for this lesson, not an actual FALL 707 production sheet.'),
      ('틀린 부분만 다시 수정합니다.', 'Repair one mismatch at a time.',
       '전신은 마음에 드는데 측면 얼굴이 다른 사람이라면 전체 설정을 다시 바꾸지 마세요. 기준 얼굴을 다시 첨부하고 “측면 컷의 코와 턱선을 기준 이미지에 맞춰 수정, 나머지 의상 유지”처럼 범위를 좁혀 요청하세요. 편집 기능이 있는 도구라면 수정할 컷을 지정하고, 결과는 원본과 나란히 비교합니다.',
       'If the body looks right but the side portrait looks like someone else, keep the original design. Attach the reference again and narrow the request: “Match the nose and jawline in the side portrait to the reference; keep the outfit unchanged.” If editing is supported, target that view and compare the result with the original.'),
      ('장면 한 컷으로 검증합니다.', 'Validate it in one scene.',
       '시트를 참고로 첨부하고 “같은 인물이 흐린 날 성 안의 창가에 서 있는 중간 거리 컷, 의상과 머리 유지”를 요청해 보세요. 배경이 바뀌어도 얼굴과 의상이 이어지는지 확인합니다. 한 번에 액션·표정·조명·카메라를 모두 바꾸기보다 배경 하나만 바꿔야 문제 원인을 찾기 쉽습니다.',
       'Attach the sheet and request a medium shot of the same character standing beside a window inside a castle on an overcast day, keeping the outfit and hair unchanged. Check whether identity survives the new setting. Change only the background first; changing action, expression, light and camera together makes errors harder to diagnose.'),
    ]
    summaries=[('외모·머리·의상·신발을 먼저 고정하세요.','Fix appearance, hair, outfit and shoes first.'),('잘 보이는 얼굴 한 장을 기준으로 저장하세요.','Save one clearly visible face as your reference.'),('전신 두 컷과 얼굴 세 컷을 비교하세요.','Compare two full-body views and three portraits.'),('다른 얼굴이나 의상만 좁혀서 수정하세요.','Target only the mismatched face or outfit.'),('같은 인물을 새로운 공간에서 확인하세요.','Check the same character in a new setting.')]
    for i, (ko,en,body_ko,body_en) in enumerate(steps,1):
        example=render_comparison(['identity','reference','views','crop','scene'][i-1],t)
        sections.append(f'<section class="tutorial-step" id="step-{i}"><span class="tutorial-number">{i:02}</span><div><h2>{t(ko,en)}</h2><p>{t(*summaries[i-1])}</p>{example}<details class="tutorial-explain"><summary>{t("방법 자세히 보기", "Read the detailed method")}</summary><p>{t(body_ko,body_en)}</p></details></div></section>')
    comparison = [('얼굴이 달라짐','The face changes','기준 얼굴을 다시 첨부하고 눈매·코·턱선부터 비교','Reattach the reference; compare eyes, nose and jawline first'),('의상이 바뀜','The outfit changes','드레스 색·네크라인·소매·자수·티아라·신발을 고정 문장에 명시','Specify gown color, neckline, sleeves, embroidery, tiara and shoes in the fixed description'),('신발이나 머리가 잘림','Shoes or hair are cropped','전신 컷에 머리부터 신발까지 보이도록 요청','Request full-body views including the head and shoes'),('조명이 너무 강함','Lighting is too harsh','단색 배경과 중립 조명으로 기준 시트를 다시 확인','Check the reference under neutral lighting against a plain background')]
    fixes=''.join(f'<div><dt>{t(a,b)}</dt><dd>{t(c,d)}</dd></div>' for a,b,c,d in comparison)
    prompt_html=escape(PROMPT_KO)
    article=f'''<body class="watch-page">{header()}<main class="tutorial-main" id="main"><a class="note-back" href="/tutorials/">← {t('튜토리얼 목록', 'All tutorials')}</a><header class="tutorial-heading"><p class="section-eyebrow">01 / CHARACTER DESIGN / BEGINNER</p><h1>{TITLE}</h1><p class="tutorial-intro">{DESC}</p><div class="tutorial-meta"><span>{t('목표: 다음 장면에 재사용할 기준 시트 1장', 'Goal: one reusable reference sheet')}</span><span>{t('준비물: 이미지 생성 도구 · 기준 얼굴 이미지', 'You need: an image tool and a reference portrait')}</span></div></header><figure class="tutorial-figure"><a href="{ART}" target="_blank" rel="noopener"><img src="{ART}" width="1536" height="1024" alt="{ALT}" decoding="async" fetchpriority="high"></a><figcaption>{t('20세 성인 공작영애 · 새 얼굴과 화려한 궁정 의상 · AI 실습 예시. 이미지를 누르면 크게 볼 수 있습니다.', 'Adult duke’s daughter, age 20 · New face and lavish court costume · AI practice example. Select to view larger.')}</figcaption></figure><nav class="tutorial-toc" aria-label="{t('강좌 목차', 'Lesson contents')}"><a href="#step-1">{t('제작 순서', 'Workflow')}</a><a href="#practice-prompt">{t('실습 프롬프트', 'Practice prompt')}</a><a href="#checklist">{t('오류 점검', 'Troubleshooting')}</a></nav>{''.join(sections)}<section class="tutorial-prompt" id="practice-prompt"><p class="section-eyebrow">TRY IT YOURSELF</p><h2>{t('복사해서 시작하는 실습 프롬프트', 'A complete prompt to start with')}</h2><p>{t('드래곤시네마가 이 강좌를 위해 작성한 예시입니다. 원하는 인물로 네 줄의 고정 설정을 바꿔서 사용하세요. 도구에 따라 참고 이미지·비율 설정 방식과 결과가 다릅니다.', 'An original exercise written by DRA9ON CINEMA. Adapt the fixed character details to your own design. Reference-image controls, aspect-ratio settings and results vary by tool.')}</p><a class="text-button" href="/assets/tutorials/character-sheet-prompt-ko.txt" download>{t('프롬프트 TXT 다운로드', 'Download prompt TXT')} ↓</a><pre tabindex="0"><code>{prompt_html}</code></pre></section><section id="checklist"><p class="section-eyebrow">BEFORE THE NEXT SCENE</p><h2>{t('마음에 안 드는 결과라면?', 'What if the result feels wrong?')}</h2><dl class="tutorial-fixes">{fixes}</dl><p class="tutorial-notice">{t('한 장에 여러 각도가 있어도 인물이 완벽히 일치한다는 보장은 없습니다. 얼굴과 의상을 직접 비교한 뒤 기준 이미지를 선택하세요.', 'Multiple views on one sheet do not guarantee perfect identity consistency. Compare the face and clothes yourself before choosing your reference.')}</p></section><aside class="tutorial-ending"><p class="section-eyebrow">FROM STUDY TO SCREEN</p><h2>{t('이렇게 만든 인물이 이야기 속으로.', 'From a character to a story.')}</h2><p>{t('캐릭터를 다시 설계하며 시작한 낙하 707. 제작 비하인드와 실제 작품을 함께 살펴보세요.', 'FALL 707 began again with redesigned characters. Explore the production notes and the finished film.')}</p><div class="tutorial-actions"><a class="button button-glass" href="/questions/">{t("제작자에게 질문하기", "Ask the creator")} →</a><a class="button button-white" href="/notes/">{t('제작 비하인드', 'Behind the Scenes')} →</a><a class="button button-glass" href="/watch/fall-707-s1-ep1/">{t('낙하 707 1화 보기', 'Watch FALL 707 episode one')} →</a><a class="text-button" href="mailto:{CONTACT_EMAIL}">{t('문의하기', 'Get in touch')} ↗</a></div></aside></main>{footer()}</body></html>'''
    lighting_rows = [
      ('빛의 방향','Light direction','A: 넓고 부드러운 정면 빛. B: 화면 왼쪽 45도에서 들어오는 창빛. 방향을 먼저 정하면 얼굴의 어느 쪽이 밝고 어두울지 비교할 수 있습니다.','A: broad soft front light. B: window light from frame left at roughly 45 degrees. Establish direction first so you can compare the bright and dark sides of the face.'),
      ('명암과 보조광','Contrast and fill','A는 반대쪽 얼굴도 밝게 보여 기준 얼굴을 확인하기 좋습니다. B는 반대쪽 보조광을 줄여 긴장감을 만듭니다. 검은 그림자에 눈과 턱이 사라지면 보조광을 조금 추가하도록 요청하세요.','A keeps both cheeks readable for checking identity. B reduces fill on the opposite side for tension. If eyes and jaw disappear into black, request slightly more fill.'),
      ('색온도와 무드','Color temperature and mood','창빛은 차갑게, 배경 촛불은 따뜻하게 설정하면 인물과 공간이 분리됩니다. 화면 전체를 주황색으로 칠하기보다 빛의 출처를 각각 적으세요. 차분한 색감과 낮은 채도는 별도로 지정합니다.','Cool window light and a warm background candle separate the character from the room. Describe each source instead of turning everything orange. Specify restrained color and low saturation separately.'),
      ('구도와 비교 방법','Framing and comparison','두 컷의 인물·의상·포즈·카메라 위치를 고정하고 조명만 바꿉니다. 머리부터 허리까지 보이는 중간 거리, 눈높이 카메라로 시작하세요. AI가 각도까지 바꾸면 같은 구도로 다시 요청해야 조명 차이를 판단하기 쉽습니다.','Keep character, clothes, pose and camera position fixed; change only lighting. Start with an eye-level medium shot. If AI changes the angle too, request matching framing before comparing the light.'),
    ]
    light_summaries=[('창빛의 방향부터 정합니다.','Choose the window-light direction first.'),('그림자 속 얼굴도 읽히게 합니다.','Keep the face readable in shadow.'),('차가운 창빛과 따뜻한 촛불을 나눕니다.','Separate cool window light from warm candlelight.'),('같은 구도로 조명만 비교합니다.','Compare lighting with the framing held fixed.')]
    lighting_grid=''.join(f'<div><dt>{t(a,b)}</dt><dd>{t(*light_summaries[i])}{render_comparison(["direction","contrast","temperature","framing"][i],t)}<details class="tutorial-explain"><summary>{t("설명 펼치기", "Read the explanation")}</summary><p>{t(c,d)}</p></details></dd></div>' for i,(a,b,c,d) in enumerate(lighting_rows))
    scene_ko='''첨부한 기준 시트와 같은 가상의 로판 여주인공입니다. 얼굴, 긴 반묶음 머리, 아이보리·파우더 블루 실크 드레스, 은빛 자수와 레이스 긴소매, 진주 장식과 작은 은빛 티아라를 유지합니다. 성 안의 돌벽과 큰 창문 옆에 차분하게 서 있습니다. 눈높이 카메라, 머리부터 허리까지 보이는 중간 거리 컷, 16:9. 화면 왼쪽 45도에서 부드러운 흐린 날 창빛이 들어옵니다. 반대쪽 얼굴은 보조광을 약하게 하되 눈과 턱의 형태는 읽히게 합니다. 배경의 작은 촛불만 따뜻하고 창빛은 차가운 색입니다. 낮은 채도와 절제된 명암, 자연스러운 피부 결, 실사 시대극 영화 무드. 과한 피부 보정, 네온색, 빛나는 마법 효과는 없습니다. 이미지 가운데 반투명 DRA9ON CINEMA 워터마크.'''
    scene_en='''Use the same fictional romantic-fantasy heroine as the attached reference sheet. Preserve her face, long half-up hair, ivory and powder-blue silk gown, silver embroidery, lace long sleeves, pearl trim and delicate silver tiara. She stands calmly beside a large window and stone wall inside a castle. Eye-level camera, medium shot from head to waist, 16:9. Soft overcast window light enters from frame left at roughly 45 degrees. Keep fill on the opposite cheek low, but preserve readable eyes and jaw shape. Only a small background candle is warm; the window light is cool. Low saturation, restrained contrast, natural skin texture, live-action period-film mood. No heavy skin retouching, neon colors or glowing magic. Semi-transparent DRA9ON CINEMA watermark across the center.'''
    TRANSLATIONS[scene_ko]=scene_en
    lighting=f'''<section id="lighting" class="tutorial-lighting"><p class="section-eyebrow">LIGHT / CONTRAST / MOOD</p><h2>{t('같은 얼굴, 빛이 바꾸는 분위기.', 'Same face. A different mood through light.')}</h2><p>{t('A는 얼굴 확인용 중립 조명, B는 성 안의 긴장감을 만드는 측면 조명입니다. 아래 이미지는 조명 차이를 설명하기 위한 AI 생성 예시로, 완벽히 통제된 촬영 실험은 아닙니다.', 'A uses neutral light to check identity; B uses side light for tension inside the castle. These are AI-generated illustrations of lighting choices, not a perfectly controlled photographic experiment.')}</p><figure class="tutorial-figure"><a href="/assets/notes/character-lighting-duchess20-v3-center-soft-wm.webp" target="_blank" rel="noopener"><img src="/assets/notes/character-lighting-duchess20-v3-center-soft-wm.webp" width="1536" height="1024" loading="lazy" decoding="async" alt="{t('같은 로판 여주인공을 중립 조명 A와 측면 조명 B로 비교한 실습 이미지', 'Practice comparison of the same romantic-fantasy heroine under neutral light A and side light B')}"></a><figcaption>{t('A · 중립 조명 / B · 영화 무드 조명', 'A · Neutral light / B · Cinematic mood')}</figcaption></figure><dl class="tutorial-fixes">{lighting_grid}</dl><details class="tutorial-prompt"><summary>{t('성 안의 장면 실습 프롬프트 · 전체 보기', 'Castle scene practice prompt · Read in full')}</summary><pre tabindex="0"><code>{escape(scene_ko)}</code></pre><p>{t('더 밝게 바꾸려면 보조광만 늘리고, 더 쓸쓸하게 바꾸려면 배경 촛불만 빼보세요. 한 번에 한 항목씩 수정하고 결과를 비교합니다.', 'For a brighter version, increase fill only. For a lonelier mood, remove only the background candle. Change one setting at a time and compare the results.')}</p></details></section>'''
    article=article.replace('<section class="tutorial-prompt" id="practice-prompt">',lighting+'<section class="tutorial-prompt" id="practice-prompt">').replace('/assets/tutorials/character-sheet-prompt-ko.txt','/assets/notes/character-sheet-prompt-ko.txt')
    article=article.replace('<a href="#checklist">','<a href="#lighting">'+t('조명·무드·명암','Light, mood and contrast')+'</a><a href="#checklist">')
    article=article.replace('<nav class="tutorial-toc"',render_scenes(t)+'<nav class="tutorial-toc"',1)
    article=article.replace(''.join(sections), '<p class="tutorial-notice">'+t('아래 비교 이미지는 항목별 차이를 보여주려고 새로 만든 AI 실습 예시입니다. 특정 도구의 실제 전후 결과나 완전히 통제된 촬영 실험은 아닙니다. A·B 설명을 읽고, 이미지에서 바뀐 부분을 직접 찾아보세요.','The comparisons below are newly generated AI teaching examples, not before-and-after captures from a specific tool or controlled photographic experiments. Read the A/B labels and find the illustrated differences.')+'</p>'+''.join(sections),1)
    article=article.replace('<a href="#step-1">','<a href="#scene-examples">'+t('씬 예시','Scene examples')+'</a><a href="#step-1">',1)
    article=article.replace('<pre tabindex="0"><code>'+prompt_html,'<details class="tutorial-full-prompt"><summary>'+t('캐릭터 시트 전체 프롬프트 펼치기','Read the complete character-sheet prompt')+'</summary><pre tabindex="0"><code>'+prompt_html,1)
    article=article.replace('</code></pre></section>','</code></pre></details></section>',1)
    article=article.replace('<div class="tutorial-meta">','<p class="tutorial-date"><time datetime="2026-10-11">2026.10.11</time> · '+t('캐릭터 · 씬 · 조명','Character · Scene · Light')+'</p><div class="tutorial-meta">',1)
    TRANSLATIONS[escape(TITLE)+' | DRA9ON CINEMA'] = TRANSLATIONS[TITLE]+' | DRA9ON CINEMA'
    TRANSLATIONS[index_title+' | DRA9ON CINEMA'] = TRANSLATIONS[index_title]+' | DRA9ON CINEMA'
    schema={'@context':'https://schema.org','@type':'Article','headline':TITLE,'description':DESC,'image':origin+ART,'url':origin+ROUTES[1],'inLanguage':'ko','datePublished':'2026-10-11','dateModified':'2026-10-11','author':{'@type':'Organization','name':'DRA9ON CINEMA'}}
    from tutorial_workbench import enhance
    article, workbench_style = enhance(article, out, t)
    article_head = page_head(head,TITLE,DESC,ROUTES[1],schema).replace('</head>',workbench_style+'</head>')
    write(out,ROUTES[1],article_head+article)
    build_seedance(out,origin,head,header,footer,t)
    build_platform(out,origin,head,header,footer,t)
    build_languages(out,origin,head,header,footer,t)
    build_camera(out,origin,head,header,footer,t)

def page_head(head,title,description,path,schema):
    return head(title+' | DRA9ON CINEMA',description,path,schema).replace('property="og:type" content="video.episode"','property="og:type" content="article"' if path==ROUTES[1] else 'property="og:type" content="website"')

def write(out,path,html):
    target=out/path.strip('/');target.mkdir(parents=True,exist_ok=True)
    (target/'index.html').write_text(html,encoding='utf-8')
