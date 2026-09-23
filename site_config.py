"""Public site settings. TODO entries stay hidden until real URLs/assets are supplied."""

# TODO: Verify forwarding and receipt before switching CONTACT_EMAIL to the domain address.
CONTACT_EMAIL = 'guletlaru05@gmail.com'
PENDING_CONTACT_EMAIL = 'contact@dra9oncinema.com'

SOCIAL_LINKS = [
    {'name': 'YouTube', 'url': 'https://www.youtube.com/@dra9oncinema'},
    {'name': 'Instagram', 'url': 'https://www.instagram.com/dra9oncinema/'},
]

# TODO: Confirm permission to publish, then fill in project, thumbnail, video_url and year.
# project accepts either a single name or {'ko': '...', 'en': '...'}.
COMMERCIAL_WORKS = [
    {'client': 'Seegene', 'project': 'TODO', 'thumbnail': 'TODO', 'video_url': 'TODO', 'year': 'TODO'},
    {'client': 'ICAK', 'project': 'TODO', 'thumbnail': 'TODO', 'video_url': 'TODO', 'year': 'TODO'},
]

ABOUT_PARAGRAPHS = {
    'ko': [
        '드래곤시네마(DRA9ON CINEMA)는 AI로 장르 영화를 만드는 1인 시네마 스튜디오입니다.',
        '모션그래픽 디자이너로 쌓아온 영상 감각 위에 AI 제작 파이프라인을 더해, 기획·시나리오·캐릭터 설계부터 스토리보드, 영상 연출, 편집까지 한 사람의 시선으로 완성합니다.',
        '대표작 〈낙하 707: 리부트〉는 현대 특수부대원이 조선에 떨어지며 시작되는 밀리터리 판타지 사극입니다. 이 밖에도 오컬트, 판타지, 액션을 넘나드는 오리지널 IP를 꾸준히 확장하고 있습니다.',
        '오리지널 시리즈와 함께 브랜드 필름, 광고 영상 등 커머셜 프로젝트도 제작합니다.',
    ],
    'en': [
        'DRA9ON CINEMA is a solo AI cinema studio creating original Korean genre films and series.',
        'Built on a background in motion graphics design, every project, from concept, screenplay and character design to storyboard, direction and edit, is shaped by a single creative vision.',
        'Our flagship series, FALL 707: REBOOT, follows a modern special forces captain who falls into the Joseon Dynasty. Military, fantasy, historical and occult: the universe keeps expanding through new original IP.',
        'Alongside original series, DRA9ON CINEMA produces brand films and commercial content.',
    ],
}

OG_ALT = {
    'ko': 'DRA9ON CINEMA 〈낙하 707: 리부트〉 FALL 707 키비주얼',
    'en': 'DRA9ON CINEMA — FALL 707: REBOOT key visual',
}

def ready(value):
    return isinstance(value, str) and bool(value.strip()) and not value.startswith('TODO')

def web_url(value):
    from urllib.parse import urlsplit
    return ready(value) and urlsplit(value).scheme == 'https' and bool(urlsplit(value).netloc)
