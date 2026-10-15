"""Public context and story cards for the Season 3 premiere."""
from html import escape

EPISODE_ID = '0I75_YXhMSM'
INSTAGRAM_URL = 'https://www.instagram.com/p/Degx3lXCeUp/'
ASSET_PATH = '/assets/fall707-s3-ep1/'

CARDS = [
    ('01_cover.webp', '그 문을 열지 마라', 'Do not open that door',
     '카드 1/5. 헬멧을 쓴 민대위의 얼굴 옆으로 손전등 빛이 번진다. 문구: 그 문을 열지 마라.',
     'Card 1 of 5. Helmeted Captain Min beside a flashlight beam. Text: Do not open that door. A forbidden door. A comrade she cannot abandon.'),
    ('02_missing_han.webp', '돌아오지 못한 한 사람', 'The one who has not returned',
     '카드 2/5. 얼굴에 검은 문양이 남은 한중사. 문구: 돌아오지 못한 한 사람. 반년이 지나도 한중사는 돌아오지 못했다.',
     'Card 2 of 5. Sergeant Han with dark markings across his face. Text: The one who has not returned. Sergeant Han is still missing. Six months have passed.'),
    ('03_kim_tremor.webp', '김중사의 손이 떨리기 시작했다', 'Sergeant Kim’s hand starts trembling',
     '카드 3/5. 한복을 입은 김중사의 물그릇과 손. 문구: 김중사의 손이 떨리기 시작했다.',
     'Card 3 of 5. Sergeant Kim in hanbok, holding a water bowl. Text: Sergeant Kim’s hand starts trembling. The nightmare may not be over.'),
    ('04_forbidden_door.webp', '동료를 위해 그 문을 열 것인가?', 'Will she open that door for her comrade?',
     '카드 4/5. 어두운 공간에서 빛을 받은 민대위의 옆얼굴. 문구: 동료를 위해 그 문을 열 것인가?',
     'Card 4 of 5. Captain Min’s profile in a dark space. Text: Will she open that door for her comrade? Warned never to open it. A comrade she cannot abandon.'),
    ('05_watch_now.webp', '시즌 3 1화, 지금 공개', 'Season 3, Episode 1 — out now',
     '카드 5/5. 밤의 조선 마당에 선 민대위. 낙하707: 리부트 시즌3 1화 공개와 YouTube 시청 안내.',
     'Card 5 of 5. Captain Min in a lantern-lit Joseon courtyard at night. Text: FALL 707: REBOOT, Season 3, Episode 1, out now. Watch on YouTube. Link in bio.'),
]

TRANSLATIONS = {
    '7개 언어 자막': 'Subtitles in 7 languages',
    'YouTube 플레이어의 CC와 설정에서 원하는 자막 언어를 선택하세요.': 'Choose your subtitle language using CC and Settings in the YouTube player.',
    '한국어 · English · 日本語 · 繁體中文 · Español (Latinoamérica) · Bahasa Indonesia · Tiếng Việt': 'Korean · English · Japanese · Traditional Chinese · Spanish (Latin America) · Indonesian · Vietnamese',
    '다섯 장으로 만나는 시즌 3 1화': 'Five cards from the Season 3 premiere',
    '돌아오지 못한 동료, 다시 나타난 이상 징후, 그리고 열지 말라는 경고. 다섯 장의 카드로 1화의 시작을 만나보세요.': 'A missing comrade, troubling symptoms, and a warning about a door. Explore the premise of Episode 1 in five story cards.',
    '카드를 옆으로 넘기거나 화살표를 누르세요. 카드를 선택하면 큰 이미지가 새 탭에서 열립니다.': 'Swipe sideways or use the arrows. Select a card to open the full image in a new tab.',
    '시즌 3 1화 카드뉴스': 'Season 3, Episode 1 story cards',
    '이전 카드': 'Previous card',
    '다음 카드': 'Next card',
    'Instagram에서 원본 보기': 'View the original on Instagram',
    'AI로 제작된 픽션입니다.': 'AI-generated fiction.',
}
for index, (_, title_ko, title_en, alt_ko, alt_en) in enumerate(CARDS, 1):
    TRANSLATIONS[title_ko] = title_en
    TRANSLATIONS[alt_ko] = alt_en
    TRANSLATIONS[f'카드 {index}/5 크게 보기 (새 탭)'] = f'Open card {index} of 5, full image (new tab)'


def episode_extras(work, icon):
    if work['id'] != EPISODE_ID:
        return ''
    cards = []
    for index, (filename, title, _, alt, _) in enumerate(CARDS, 1):
        image = ASSET_PATH + filename
        cards.append(
            f'<li><figure><a href="{image}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="카드 {index}/5 크게 보기 (새 탭)">'
            f'<img src="{image}" width="1122" height="1402" loading="lazy" decoding="async" alt="{escape(alt, quote=True)}">'
            f'</a><figcaption><span>{index:02} / 05</span>{escape(title)}</figcaption></figure></li>'
        )
    return (
        '<section class="episode-captions" aria-labelledby="episode-captions-title">'
        '<h2 id="episode-captions-title">7개 언어 자막</h2>'
        '<p>YouTube 플레이어의 CC와 설정에서 원하는 자막 언어를 선택하세요.</p>'
        '<p class="episode-caption-languages">한국어 · English · 日本語 · 繁體中文 · Español (Latinoamérica) · Bahasa Indonesia · Tiếng Việt</p>'
        '</section>'
        '<section class="episode-promo" aria-labelledby="episode-promo-title">'
        '<div class="episode-promo-heading"><div><p class="section-eyebrow">EPISODE STORY CARDS</p>'
        '<h2 id="episode-promo-title">다섯 장으로 만나는 시즌 3 1화</h2></div>'
        '<div class="shelf-controls">'
        f'<button type="button" data-scroll="episode-story-cards" data-direction="-1" aria-label="이전 카드">{icon("left")}</button>'
        f'<button type="button" data-scroll="episode-story-cards" data-direction="1" aria-label="다음 카드">{icon("right")}</button></div></div>'
        '<p class="episode-promo-intro">돌아오지 못한 동료, 다시 나타난 이상 징후, 그리고 열지 말라는 경고. 다섯 장의 카드로 1화의 시작을 만나보세요.</p>'
        '<p class="episode-promo-help" id="episode-story-help">카드를 옆으로 넘기거나 화살표를 누르세요. 카드를 선택하면 큰 이미지가 새 탭에서 열립니다.</p>'
        '<ol class="episode-card-track shelf-track" id="episode-story-cards" tabindex="0" aria-label="시즌 3 1화 카드뉴스" aria-describedby="episode-story-help">'
        + ''.join(cards)
        + '</ol>'
        f'<a class="text-button" href="{INSTAGRAM_URL}" target="_blank" rel="noopener noreferrer">Instagram에서 원본 보기 {icon("external")}</a>'
        '<p class="episode-fiction-note">AI로 제작된 픽션입니다.</p></section>'
    )
