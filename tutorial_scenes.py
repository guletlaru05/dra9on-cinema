"""Original public scene exercises, independent of protected study material."""
from html import escape

def render(t):
    scenes=[
      ('01 / ESTABLISHING SHOT','character-scene-wide-duchess20-v3.webp',
       '공간을 먼저 보여주기','Show the space first',
       '넓은 성 안에 인물을 작게 배치하면, 인물이 어디에 있는지 한 컷으로 전달됩니다.',
       'A small figure inside a wide castle hall tells us where the character is in one shot.',
       '눈높이 · 와이드 · 창빛 · 공간 소개','Eye level · Wide · Window light · Setting',
       '기준 시트를 첨부합니다. 같은 20세 성인인 가상의 로판 여주인공, 긴 갈색 반묶음 머리와 아이보리·파우더 블루 실크 드레스, 은빛 자수와 진주 장식, 레이스 긴소매와 작은 은빛 티아라를 그대로 유지합니다. 오래된 성의 넓은 돌벽 홀, 높은 아치 창문, 멀리 열린 문이 보입니다. 여주인공은 화면 오른쪽 1/3 지점의 창가에 전신으로 작게 서서 빈 문을 바라봅니다. 카메라는 눈높이, 35mm 렌즈 느낌의 와이드 숏, 16:9. 앞쪽 기둥·중간의 인물·뒤쪽 문으로 깊이를 나눕니다. 흐린 오후의 부드럽고 차가운 창빛, 배경의 작은 따뜻한 촛불. 차분한 색과 자연스러운 피부, 실사 시대극 영화 무드. 네온색과 마법 효과 없이 오른쪽 아래 작은 DRA9ON CINEMA 워터마크.',
       'Attach the reference sheet. Preserve the same fictional adult romantic-fantasy heroine aged 20, long brown half-up hair, ivory and powder-blue silk gown, silver embroidery, pearl trim, lace long sleeves and delicate silver tiara. Show a wide old stone castle hall with tall arched windows and an open distant doorway. The heroine stands full-body near the window in the right third, looking toward the empty doorway. Eye-level camera, a 35mm-style wide shot, 16:9. Layer a foreground column, the character in the middle and the doorway in the distance. Soft cool window light on an overcast afternoon with a small warm background candle. Restrained colors, natural skin and a live-action period-film mood. No neon or magic effects. Small DRA9ON CINEMA watermark at bottom right.'),
      ('02 / REACTION SHOT','character-scene-close-duchess20-v3.webp',
       '표정으로 다음 이야기를 만들기','Let expression carry the next beat',
       '같은 인물을 가까이 보여주고, 눈빛과 입술의 작은 변화로 긴장감을 만듭니다.',
       'Move closer to the same character; small changes in the eyes and lips create tension.',
       '눈높이 · 클로즈업 · 측면광 · 반응','Eye level · Close-up · Side light · Reaction',
       '기준 시트와 같은 20세 성인 로판 여주인공의 얼굴과 긴 반묶음 머리, 공작영애의 아이보리·파우더 블루 실크 드레스와 은빛 자수, 진주 장식과 작은 은빛 티아라를 유지합니다. 성의 복도에서 불안한 소식을 막 들은 순간입니다. 화면 왼쪽의 보이지 않는 상대를 바라보며, 눈매와 입술만 조금 긴장합니다. 과장된 울음이나 놀란 표정은 없습니다. 눈높이 카메라, 얼굴의 45도 방향 클로즈업, 85mm 렌즈 느낌, 16:9. 왼쪽 창문에서 들어오는 부드럽고 차가운 측면광, 반대쪽 볼은 어둡지만 눈과 턱은 보이도록 약한 보조광. 뒤쪽 촛불은 작고 따뜻하게 흐립니다. 자연스러운 피부 결과 절제된 명암, 낮은 채도의 실사 영화 톤. 오른쪽 아래 작은 DRA9ON CINEMA 워터마크.',
       'Preserve the adult reference heroine’s youthful face (age 20), long half-up hair and a duke’s daughter’s ivory and powder-blue silk gown with silver embroidery, pearl trim and delicate silver tiara. She has just heard unsettling news in a castle corridor. She looks toward an unseen person at frame left, with only slight tension in the eyes and lips. No exaggerated crying or surprise. Eye-level camera, three-quarter close-up, an 85mm-style perspective, 16:9. Soft cool side light from a window left; the opposite cheek is darker but gentle fill keeps eyes and jaw readable. A small warm candle is softly blurred behind her. Natural skin texture, restrained contrast and muted live-action film colors. Small DRA9ON CINEMA watermark bottom right.'),
    ]
    cards=[]
    for label,image,ko,en,desc_ko,desc_en,tags_ko,tags_en,prompt_ko,prompt_en in scenes:
        cards.append(f'''<article class="tutorial-scene"><a href="/assets/notes/{image}" target="_blank" rel="noopener"><img src="/assets/notes/{image}" width="1536" height="864" loading="lazy" decoding="async" alt="{t(ko,en)}"></a><div class="tutorial-scene-copy"><p class="section-eyebrow">{label}</p><h3>{t(ko,en)}</h3><p>{t(desc_ko,desc_en)}</p><p class="scene-settings">{t(tags_ko,tags_en)}</p><details class="scene-prompt"><summary>{t('이 장면 프롬프트 펼치기','Read this scene’s full prompt')}</summary><pre tabindex="0"><code>{t(prompt_ko,prompt_en)}</code></pre></details></div></article>''')
    return f'''<section class="tutorial-scenes" id="scene-examples"><p class="section-eyebrow">SHEET → SCENE → EMOTION</p><h2>{t('시트에서, 이야기 속 한 장면으로.','From the sheet to a scene in the story.')}</h2><p>{t('같은 인물로 공간 소개와 감정 반응을 만들어봅니다. AI로 새로 만든 실습 예시입니다.','Create an establishing shot and an emotional reaction with the same character. These are newly generated AI practice examples.')}</p><div class="tutorial-scene-grid">{''.join(cards)}</div></section>'''
