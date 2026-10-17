"""Public collaboration section; all figures are dated, platform-specific counts.

Integration: add ``render_collaboration(icon)`` before the home About section,
load /collaboration.css, and merge TRANSLATIONS into the English page map.
Keep a metric disabled until its current public figure has been verified.
"""

from html import escape
from urllib.parse import quote

from site_config import CONTACT_EMAIL


UPDATED_AT = '2026.10.17'
STATS = (
    {'platform': 'YouTube', 'value': '1.38만', 'unit': '구독자',
     'url': 'https://www.youtube.com/@dra9oncinema', 'enabled': True},
    {'platform': 'Instagram', 'value': '9.4만', 'unit': '팔로워',
     'url': 'https://www.instagram.com/dra9oncinema/', 'enabled': True},
    # Owner supplied this figure; expose only after confirming the correct page.
    {'platform': 'Facebook', 'value': '7.3만', 'unit': '팔로워',
     'url': '', 'enabled': False},
)

SERVICES = (
    ('AI 브랜드 필름', '브랜드의 메시지를 한 편의 이야기로 만듭니다.'),
    ('숏폼 콘텐츠', '인물과 장면, 짧고 강한 이야기로 시선을 이끕니다.'),
    ('영상 제작 협업', '기획·캐릭터·프리비즈부터 연출·편집까지 함께합니다.'),
)

CPP_PROGRAMS = ('Dreamina', 'Higgsfield', 'OpenArt')

CASES = (
    {
        'name': 'Newtake',
        'type': '브랜드 콘텐츠 · 광고',
        'title': 'Claude with Newtake',
        'description': 'Newtake를 활용한 AI 제작 과정을 담은 브랜드 콘텐츠.',
        'url': 'https://www.instagram.com/reel/DelRHYDunY-/',
    },
    {
        'name': 'Dreamina CPP',
        'type': '크리에이터 프로그램',
        'title': '스승을 잘못 만난 염력소녀',
        'description': '캐릭터와 초능력 액션을 결합한 짧은 장르 드라마.',
        'url': 'https://www.instagram.com/reel/Dcsxt2LRC1d/',
    },
    {
        'name': 'Higgsfield CPP',
        'type': '크리에이터 프로그램',
        'title': '지하철 참교육',
        'description': '지하철 공간을 배경으로 연출한 액션 숏필름.',
        'url': 'https://www.instagram.com/reel/DeAJ-h_SdDw/',
    },
    {
        'name': 'OpenArt CPP',
        'type': '크리에이터 프로그램',
        'title': '먹동이 공놀이',
        'description': '공놀이가 우주까지 이어지는 캐릭터 판타지 숏필름.',
        'url': 'https://www.instagram.com/reel/DcvvFWvJupa/',
    },
    {
        'name': 'bbanana AI',
        'type': '도구 활용 사례',
        'title': 'AI 에이전트로 만든 막장 드라마',
        'description': 'MCP를 연결해 이미지부터 영상까지 제작한 워크플로 실험.',
        'url': 'https://www.instagram.com/reel/Delgj0xuzcF/',
    },
)

MAIL_SUBJECT_KO = '[협업 문의] DRA9ON CINEMA'
MAIL_SUBJECT_EN = '[Collaboration inquiry] DRA9ON CINEMA'
MAIL_BODY_KO = ('안녕하세요, 드래곤시네마님.\n\n'
                '브랜드 / 프로젝트명:\n'
                '제작 목적:\n'
                '희망 형식 / 분량:\n'
                '희망 일정:\n'
                '예산 범위:\n'
                '참고 링크:\n'
                '담당자 / 연락처:\n')
MAIL_BODY_EN = ('Hello DRA9ON CINEMA,\n\n'
                'Brand / project:\n'
                'Project goal:\n'
                'Format / length:\n'
                'Preferred schedule:\n'
                'Budget range:\n'
                'Reference links:\n'
                'Name / contact details:\n')


def render_collaboration(icon):
    """Render Korean source markup for the existing bilingual build pipeline."""
    esc = lambda text: escape(text, quote=True)
    stats = ''.join(
        '<div class="collaboration-stat">'
        f'<dt><a href="{esc(item["url"])}" target="_blank" '
        f'rel="noopener noreferrer">{esc(item["platform"])} {icon("external")}</a></dt>'
        f'<dd><strong>{esc(item["value"])}</strong><span>{esc(item["unit"])}</span></dd>'
        '</div>'
        for item in STATS if item['enabled'] and item['url']
    )
    services = ''.join(
        f'<div><h3>{esc(title)}</h3><p>{esc(description)}</p></div>'
        for title, description in SERVICES
    )
    programs = ''.join(f'<li>{esc(name)} <span>CPP</span></li>' for name in CPP_PROGRAMS)
    cases = ''.join(
        '<li><a class="collaboration-case" '
        f'href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">'
        f'<span class="collaboration-case-number" aria-hidden="true">{number:02}</span>'
        '<div class="collaboration-case-brand">'
        f'<p>{esc(item["type"])}</p><h4>{esc(item["name"])}</h4></div>'
        '<div class="collaboration-case-copy">'
        f'<h5>{esc(item["title"])}</h5><p>{esc(item["description"])}</p></div>'
        f'<span class="collaboration-case-link">사례 보기 {icon("external")}</span>'
        '</a></li>'
        for number, item in enumerate(CASES, 1)
    )
    mailto = (f'mailto:{CONTACT_EMAIL}?subject={quote(MAIL_SUBJECT_KO)}'
              f'&body={quote(MAIL_BODY_KO)}')
    return f'''<section class="collaboration-section" id="collaboration" aria-labelledby="collaboration-title">
<div class="collaboration-intro">
  <div class="collaboration-heading">
    <p class="collaboration-eyebrow">COLLABORATION / BUSINESS</p>
    <h2 id="collaboration-title">다음 장면을,<br><span>함께 만듭니다.</span></h2>
    <p class="collaboration-lede">브랜드의 이야기에도, 영화의 감각을.<br>기획부터 완성까지 드래곤시네마와 함께하세요.</p>
  </div>
  <div class="collaboration-contact">
    <p class="collaboration-contact-label">새로운 프로젝트를 기다립니다.</p>
    <a class="collaboration-cta" href="{esc(mailto)}">협업 제안 보내기 {icon('arrow')}</a>
    <p class="collaboration-email">{esc(CONTACT_EMAIL)}</p>
    <p class="collaboration-brief">브랜드·제작 목적·희망 형식·일정·예산 범위를 알려주시면 제안을 검토하는 데 도움이 됩니다.</p>
  </div>
</div>
<div class="collaboration-programs" aria-labelledby="collaboration-programs-title">
  <h3 id="collaboration-programs-title">참여 크리에이터 프로그램 · CPP</h3>
  <ul>{programs}</ul>
</div>
<div class="collaboration-audience">
  <p class="collaboration-small-label">이야기가 만나는 관객</p>
  <dl class="collaboration-stats">{stats}</dl>
  <p class="collaboration-count-note">{UPDATED_AT} 공개 프로필 기준 · 플랫폼별 구독자·팔로워 수이며 중복 이용자를 포함합니다.</p>
</div>
<div class="collaboration-services">{services}</div>
<div class="collaboration-work">
  <div class="collaboration-work-heading"><p class="collaboration-eyebrow">SELECTED CONTENT</p><h3>브랜드 콘텐츠부터 제작 실험까지.</h3></div>
  <ol class="collaboration-cases">{cases}</ol>
</div>
</section>'''


TRANSLATIONS = {
    '다음 장면을,': 'The next scene.',
    '함께 만듭니다.': 'Made together.',
    '브랜드의 이야기에도, 영화의 감각을.': 'A cinematic eye for your brand’s story.',
    '기획부터 완성까지 드래곤시네마와 함께하세요.': 'Work with DRA9ON CINEMA, from the first idea to the final cut.',
    '새로운 프로젝트를 기다립니다.': 'Let’s talk about your next project.',
    '협업 제안 보내기': 'Discuss a project',
    '브랜드·제작 목적·희망 형식·일정·예산 범위를 알려주시면 제안을 검토하는 데 도움이 됩니다.': 'Please include your brand, project goal, format, schedule and budget range so we can review your proposal.',
    '이야기가 만나는 관객': 'THE AUDIENCE BEHIND THE STORIES',
    '참여 크리에이터 프로그램 · CPP': 'CREATOR PROGRAM PARTICIPATION · CPP',
    '1.38만': '13.8K',
    '9.4만': '94K',
    '7.3만': '73K',
    '구독자': 'subscribers',
    '팔로워': 'followers',
    '공개 프로필 기준 · 플랫폼별 구독자·팔로워 수이며 중복 이용자를 포함합니다.': '· Platform-specific subscriber and follower counts; audiences may overlap.',
    'AI 브랜드 필름': 'AI brand films',
    '브랜드의 메시지를 한 편의 이야기로 만듭니다.': 'Turn your brand’s message into a cinematic story.',
    '숏폼 콘텐츠': 'Short-form content',
    '인물과 장면, 짧고 강한 이야기로 시선을 이끕니다.': 'Characters, striking scenes and stories that hold attention.',
    '영상 제작 협업': 'Production collaboration',
    '기획·캐릭터·프리비즈부터 연출·편집까지 함께합니다.': 'Concept, character design and previs through direction and editing.',
    '브랜드 콘텐츠부터 제작 실험까지.': 'Brand stories. Creative experiments.',
    '브랜드 콘텐츠 · 광고': 'Brand content · Advertisement',
    'Newtake를 활용한 AI 제작 과정을 담은 브랜드 콘텐츠.': 'Brand content exploring an AI production workflow with Newtake.',
    '크리에이터 프로그램': 'Creator program',
    '스승을 잘못 만난 염력소녀': 'The Telekinetic Girl with the Wrong Master',
    '캐릭터와 초능력 액션을 결합한 짧은 장르 드라마.': 'A short genre drama combining character storytelling and supernatural action.',
    '지하철 참교육': 'Subway Showdown',
    '지하철 공간을 배경으로 연출한 액션 숏필름.': 'An action short film staged in a subway setting.',
    '먹동이 공놀이': 'Mukdong’s Ball Game',
    '공놀이가 우주까지 이어지는 캐릭터 판타지 숏필름.': 'A character-led fantasy short that takes a ball game into outer space.',
    '도구 활용 사례': 'Tool workflow showcase',
    'AI 에이전트로 만든 막장 드라마': 'A Wild Drama Made with an AI Agent',
    'MCP를 연결해 이미지부터 영상까지 제작한 워크플로 실험.': 'An MCP workflow experiment, from generated images to the finished video.',
    '사례 보기': 'View project',
    quote(MAIL_SUBJECT_KO): quote(MAIL_SUBJECT_EN),
    quote(MAIL_BODY_KO): quote(MAIL_BODY_EN),
}
