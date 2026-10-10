"""Creator-directed questions, received privately by email; curated public answers."""
from html import escape
from urllib.parse import quote
from site_config import CONTACT_EMAIL

ROUTES = ['/questions/']
TRANSLATIONS = {}

def t(ko, en):
    TRANSLATIONS[ko] = en
    return escape(ko)

LABEL = t('질문과 답변', 'Q&A')
TITLE = t('궁금한 장면, 만드는 사람에게.', 'Ask the person behind the frame.')
DESC = t('작품과 세계관, AI 제작 과정에 대해 드래곤시네마에 질문하세요.', 'Ask DRA9ON CINEMA about the stories, their worlds and the AI filmmaking process.')
TRANSLATIONS[TITLE + ' | DRA9ON CINEMA'] = 'Ask the person behind the frame. | DRA9ON CINEMA'

# Add creator-reviewed public answers here. These are introductory answers,
# not fabricated visitor submissions.
ANSWERS = [
    ('story', '작품·세계관', 'Stories & worlds', '낙하 707은 어떤 이야기인가요?', 'What is FALL 707 about?',
     '현대 특수부대원이 조선으로 떨어지는 밀리터리 판타지 오컬트 스릴러입니다. 리부트에서 민 대위가 맞서는 주된 적은 무당 빌런과 좀비들입니다. 시즌별 변화와 이야기의 출발점은 제작 비하인드에서 더 자세히 읽을 수 있습니다.',
     'A military fantasy occult thriller about a modern special forces officer who falls into Joseon. In the reboot, Captain Min’s main enemies are a shaman villain and zombies. The production notes explain the origins of the story and the changes between seasons.', '/notes/', '제작 비하인드 읽기', 'Read the production notes'),
    ('making', 'AI 제작·튜토리얼', 'AI filmmaking & tutorials', '캐릭터 얼굴을 같은 사람으로 유지하려면?', 'How do I keep the same character face?',
     '먼저 기준 얼굴을 고르고, 캐릭터 시트로 얼굴·의상·헤어스타일을 고정합니다. 다음 장면을 만들 때 그 시트를 참고 이미지로 첨부하고, 결과의 눈매·코·턱선과 의상을 직접 비교하세요. 첫 공개 튜토리얼에 시트와 씬 예시, 전체 실습 프롬프트를 넣었습니다.',
     'Choose a reference face first, then lock the face, clothes and hairstyle with a character sheet. Attach that sheet as a reference for the next scene and compare the eyes, nose, jawline and outfit. The first public tutorial includes sheet and scene examples with complete practice prompts.', '/tutorials/character-sheet/', '튜토리얼 보기', 'Open the tutorial'),
    ('other', '기타', 'Other', '질문을 보내면 바로 사이트에 공개되나요?', 'Will my question appear publicly right away?',
     '질문은 제작자 이메일로 전달되며 자동 공개되지 않습니다. 여러 사람에게 도움이 되는 내용은 질문자의 이름·이메일 등 개인정보를 제외하고 답변으로 정리할 수 있습니다. 공개를 원하지 않으면 메일에 “비공개 답변 요청”이라고 적어주세요.',
     'Questions go to the creator by email and are not published automatically. Helpful topics may become curated answers without the sender’s name, email or other personal details. Write “private reply requested” if you do not want your question used in a public answer.', None, None, None),
]

def question_link(ko, en):
    href = 'mailto:' + CONTACT_EMAIL + '?subject=' + quote('DRA9ON CINEMA | ' + ko)
    TRANSLATIONS[href] = 'mailto:' + CONTACT_EMAIL + '?subject=' + quote('DRA9ON CINEMA | ' + en)
    return href

def build_questions(out, origin, head, header, footer):
    groups = [('story','작품·세계관','Stories & worlds'), ('making','AI 제작·튜토리얼','AI filmmaking & tutorials'), ('other','기타','Other')]
    cards = []
    for number, (key, ko, en) in enumerate(groups, 1):
        cards.append(f'<a class="question-topic" href="{question_link(ko,en)}"><span class="question-number">0{number}</span><h2>{t(ko,en)}</h2><span>{t("질문 보내기", "Send a question")} ↗</span></a>')
    answers = []
    for key, cat_ko, cat_en, q_ko, q_en, a_ko, a_en, link, link_ko, link_en in ANSWERS:
        related = f'<a class="text-button" href="{link}">{t(link_ko,link_en)} →</a>' if link else ''
        answers.append(f'<details class="question-answer"><summary><span class="section-eyebrow">{t(cat_ko,cat_en)}</span><span>{t(q_ko,q_en)}</span></summary><div><p>{t(a_ko,a_en)}</p>{related}</div></details>')
    body = f'''<body class="watch-page">{header()}<main class="tutorial-main questions-main" id="main"><a class="note-back" href="/">← {t('사이트로 돌아가기','Back to the site')}</a><header class="tutorial-heading"><p class="section-eyebrow">DRA9ON CINEMA / QUESTIONS & ANSWERS</p><h1>{TITLE}</h1><p class="tutorial-intro">{DESC}</p><p class="question-intro">{t('보고 싶은 이야기부터, 만들다 막힌 장면까지. 질문을 보내주시면 제작자가 확인하고 답변합니다.','From stories you want to see to scenes you are struggling to create. Send a question for the creator to review and answer.')}</p></header><section aria-label="{t('질문 주제 선택','Choose a question topic')}"><div class="question-topics">{''.join(cards)}</div><p class="tutorial-notice">{t('버튼을 누르면 이메일 앱이 열립니다. 질문 내용과 참고할 영상·튜토리얼 링크를 함께 적어주세요. 답변에는 시간이 걸릴 수 있습니다.','Each button opens your email app. Include your question and a relevant video or tutorial link. Replies may take time.')}</p><a class="text-button" href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></section><section class="question-answers"><p class="section-eyebrow">START HERE</p><h2>{t('먼저 읽어보세요.','Start with these answers.')}</h2><p class="tutorial-notice">{t('처음 방문한 분들을 위해 제작자가 정리한 기본 안내입니다.','Introductory answers prepared by the creator for first-time visitors.')}</p>{''.join(answers)}</section></main>{footer()}</body></html>'''
    schema = {'@context':'https://schema.org','@type':'WebPage','name':TITLE,'description':DESC,'url':origin+ROUTES[0]}
    page = out / 'questions'
    page.mkdir(parents=True, exist_ok=True)
    html = head(TITLE+' | DRA9ON CINEMA',DESC,ROUTES[0],schema).replace('property="og:type" content="video.episode"','property="og:type" content="website"') + body
    (page/'index.html').write_text(html, encoding='utf-8')
