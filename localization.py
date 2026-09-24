"""Generate crawlable English pages alongside the Korean portfolio."""
from copy import deepcopy
from site_config import ABOUT_PARAGRAPHS, OG_ALT
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
import re

EN_NAMES = {
    '6Wdj9n3Pq9Q': 'When Captain Min Falls',
    'bDqEJXYr2dY': 'You Knew Everything',
    'vrVGZ_HMxQs': "The Enemy I Can't Shoot",
    'dGnjxL64HHY': 'A Night in Mokpojin — Season 2 EP.1–2',
    'WZ0ozLABZwE': 'The Assault on Mokpojin',
    'l2G5ITnriFQ': 'A Bond on the Snowy Road',
    '4f6Zguf7c2M': 'FALL 707 Season 1 — Full Movie',
    'BY0ZT5SK8qY': 'The Palace’s Last Night',
    'hoFQL2ON9m4': 'The Palace’s Last Night',
    '6CCZA8el6Mk': 'Gunfire in the Palace',
    'gTdqOtFvcDM': 'The Black Bell',
    'HP-B3jZLs3w': 'Those Who Rise Again',
    'NV9PeKvKv7c': '707 Captain Awakens in Joseon',
    'y4t5NDVqPyU': '707 Captain Lost in Explosion',
    'pBti3GK2nkc': 'Joseon Ghost Special Operations',
    'j95SyBMQiNI': 'The Janitor of the Black Tower',
    'VCd4T8sLFjg': 'TARGET: NO ANSWER',
    'OLSjUGODAeE': 'She Opened Her Eyes Again',
    'L53hio-gtv0': 'The Immortal Crazy X and the n-th Grim Reaper 2',
    'Byh-aCKSDgo': 'Exorcist Agent of the Occult Suppression Bureau',
    'UxrkaAvtsNI': 'Iron Revenant',
    'iVwqj1gUPDY': 'The Immortal Crazy X and the n-th Grim Reaper',
}
SERIES_SUMMARY = 'An AI-created Korean military fantasy drama. A modern special forces soldier finds himself in Joseon-era Korea.'
EN_SUMMARIES = {
    '6Wdj9n3Pq9Q': 'An endless horde. A wounded captain, left to fight alone. A new force is about to enter the battle. Season 2, Episode 5.',
    'bDqEJXYr2dY': SERIES_SUMMARY + ' A masked prince arrives to rescue Yeonhwa, but Min’s comrades are taken again. Captain Min turns his gun on the person who saved him. Season 2, Episode 4.',
    'vrVGZ_HMxQs': SERIES_SUMMARY + ' Yeonhwa has been abducted, and former comrades have become enemies. Season 2, Episode 3.',
    'dGnjxL64HHY': SERIES_SUMMARY + ' Watch Season 2, Episodes 1–2 in one continuous cut.',
    '4f6Zguf7c2M': SERIES_SUMMARY + ' The complete first season in one film.',
    'hoFQL2ON9m4': 'Following the mystery of the Black Bell, Iseo confronts a young shaman. Dark smoke engulfs the palace, leaving her gravely wounded. Captain Min rushes to her defense as modern gunfire meets an occult force. The trailer for the Season 1 finale.',
    'pBti3GK2nkc': 'Meet Yerin, a cursed member of an exorcist special operations unit. A teaser from DRA9ON CINEMA.',
    'j95SyBMQiNI': 'A black magic tower appears in the heart of Seoul. After the battle, a janitor enters its labyrinth. A dark fantasy concept film.',
    'VCd4T8sLFjg': 'A call to her mother goes unanswered. An AI crime action thriller from DRA9ON CINEMA.',
    'OLSjUGODAeE': 'An AI romance fantasy teaser from DRA9ON CINEMA. Discover She Opened Her Eyes Again.',
    'L53hio-gtv0': 'The second installment of The Immortal Crazy X and the n-th Grim Reaper. An original film created with AI.',
    'Byh-aCKSDgo': 'Exorcist Agent of the Occult Suppression Bureau. An original film created with AI by DRA9ON CINEMA.',
    'UxrkaAvtsNI': 'Iron Revenant: a Korean live-action mecha concept created with AI by DRA9ON CINEMA.',
    'iVwqj1gUPDY': 'The Immortal Crazy X and the n-th Grim Reaper. An original film created with AI by DRA9ON CINEMA.',
}
UI = {
    'YouTube 구독': 'Subscribe on YouTube',
    '낙하707': 'FALL707',
    '낙하 707': 'FALL 707',
    '밀리터리': 'Military',
    '판타지': 'Fantasy',
    '사극': 'Historical drama',
    '오컬트': 'Occult',
    '현대 특수부대와 조선 시대가 만나는 밀리터리 판타지·사극 AI 영화.': 'An AI military fantasy film series where modern special forces encounter Joseon-era Korea.',
    '드래곤시네마': 'DRA9ON CINEMA',
    '드래곤 시네마': 'DRA9ON CINEMA',
    'DRA9ON CINEMA | 공식 링크': 'DRA9ON CINEMA | Official Links',
    'FALL 707 최신화, 시즌 1 풀버전, 공식 유튜브와 협업 문의를 한곳에서.': 'Watch the latest FALL 707 episode and Season 1 full movie. Find the official YouTube channel and collaboration contact.',
    'FALL 707과 오리지널 영화들을 만나보세요.': 'Discover FALL 707 and original films.',
    '공식 링크': 'Official links',
    '최신화 보기': 'Watch the latest episode',
    '시즌 1 풀버전': 'Watch Season 1',
    '전체 작품 둘러보기': 'Explore all films',
    '작품·이미지·텍스트의 무단 복제, 재업로드 및 상업적 이용을 금합니다. 이용 문의는 이메일로 연락해 주세요.': 'Unauthorized copying, re-uploading, or commercial use of the films, images, and text is prohibited. Please email us for usage inquiries.',
    '낙하 707 리부트 · FALL 707 ': 'FALL 707 ',
    '낙하707: 리부트. ': 'FALL 707: REBOOT. ',
    '드래곤시네마 DRA9ON CINEMA | 낙하 707 · FALL 707': 'DRA9ON CINEMA | FALL 707 REBOOT · Korean AI Films',
    '드래곤시네마의 〈낙하 707: 리부트〉(낙하707, FALL707, FALL 707). 현대 특수부대와 조선 시대가 만나는 밀리터리 판타지·사극 AI 영화. 시즌 1·2와 풀버전을 감상하세요.': 'Watch FALL 707: REBOOT, a Korean military fantasy series set in Joseon, and explore original AI films by DRA9ON CINEMA. Browse episodes, full movies and the filmmaker’s portfolio.',
    'DRA9ON CINEMA — 낙하 707 · FALL 707 영상 포트폴리오': 'DRA9ON CINEMA — FALL 707 and Original AI Films',
    'AI로 세계관을 실사화하는 크리에이터. 낙하707: 리부트(FALL 707: REBOOT)와 오리지널 AI 영화 제작.': 'Independent AI filmmaker bringing imagined worlds to life. Creator of FALL 707: REBOOT and original AI films.',
    'AI로 세계관을 실사화하는 크리에이터.': 'Bringing imagined worlds to life through AI film.',
    '드래곤시네마(DRA9ON CINEMA)는 AI로 세계관을 실사화하는 크리에이터입니다. 현대 특수부대와 조선 시대가 만나는 〈낙하 707: 리부트〉(낙하707, FALL707, FALL 707: REBOOT)를 비롯해, 밀리터리·판타지·사극·오컬트를 결합한 장르 영화를 만듭니다.': 'DRA9ON CINEMA brings imagined worlds to life through AI filmmaking. From the military fantasy and occult thriller FALL 707: REBOOT to original genre films, each project explores a new cinematic possibility.',
    'FALL 707 REBOOT 시즌 2 — 민 대위': 'FALL 707 REBOOT Season 2 — Captain Min',
    '낯선 시대에 떨어졌다.': 'A soldier out of time.',
    '살아남는 방식은, 변하지 않았다.': 'Survival is still the mission.',
    '현대의 특수부대원이 조선에 떨어진다.': 'A modern special forces soldier lands in Joseon-era Korea.',
    '두 시대가 충돌하는 오리지널 시리즈, 〈낙하 707: 리부트〉.': 'Two eras collide in an original series by DRA9ON CINEMA.',
    '밀리터리 × 판타지 × 오컬트': 'MILITARY × FANTASY × OCCULT',
    '모든 이야기의 시작, 시즌 1': 'Where it all begins · Season 1',
    '세계관은 계속 넓어진다': 'More worlds to discover',
    '한 번 더, 깊이 빠져들다': 'Full movies & trailers',
    '한 편의 영화처럼.': 'The whole story. One sitting.',
    '에피소드 사이의 기다림 없이, FALL 707을 연속으로.': 'Experience FALL 707 in one continuous cut.',
    '상상을, 장면으로.': 'From imagination to cinema.',
    '이야기를, 세계관으로.': 'From stories to worlds.',
    '채널 문의': 'Contact',
    '채널에서 더 보기': 'Explore the channel',
    '시즌 1 몰아보기': 'Watch Season 1',
    'FALL 707 시즌 1 풀무비': 'FALL 707 Season 1 full movie',
    '1화부터 보기': 'Start Episode 1',
    '에피소드 보기': 'Browse episodes',
    '최신 에피소드': 'LATEST EPISODE',
    '시즌 1–2': 'Seasons 1–2',
    '시즌 1': 'Season 1',
    '시즌 2': 'Season 2',
    '전체 작품 보기': 'Browse all films',
    '전체 작품': 'All films',
    '오리지널 작품': 'Original films',
    '오리지널': 'Originals',
    '몰아보기': 'Full movies',
    '찜한 작품': 'My list',
    '찜하기': 'Save',
    '작품집': 'Films',
    '협업 문의': 'Collaborate',
    '홈': 'Home',
    '콘텐츠로 바로 가기': 'Skip to content',
    '주 메뉴': 'Main navigation',
    '작품 분류': 'Browse categories',
    '작품, 에피소드 검색': 'Search films or episodes',
    '작품 또는 에피소드 검색': 'Search films or episodes',
    '작품 검색': 'Search films',
    '상세 보기': 'View details',
    '공식 썸네일': 'official thumbnail',
    '이전 보기': 'Previous films',
    '다음 보기': 'Next films',
    '상세 정보 닫기': 'Close details',
    '지금 재생': 'Play now',
    '작품 전용 페이지 열기': 'Open film page',
    '링크 복사': 'Copy link',
    '영상 닫기': 'Close player',
    'YouTube에서 보기': 'Watch on YouTube',
    '다음 작품': 'Next film',
    '다음 이야기': 'Up next',
    '이 작품 공유하기': 'Share this film',
    '관련 작품': 'Related films',
    '다른 작품': 'More films',
    '에피소드': 'Episodes',
    '경로': 'Breadcrumb',
    '아직 작품이 없어요.': 'No films found.',
    '다른 검색어를 입력하거나 보고 싶은 작품의 + 버튼을 눌러주세요.': 'Try another search, or use the + button to save a film to your list.',
    '플레이어에서 재생이 제한되면 ‘YouTube에서 보기’를 눌러주세요.': 'If playback is unavailable here, select “Watch on YouTube”. For subtitles, use the player’s CC and language settings where available.',
    '페이지를 찾을 수 없습니다 | DRA9ON CINEMA': 'Page not found | DRA9ON CINEMA',
    '홈에서 다른 작품을 만나보세요.': 'Find more films on the homepage.',
    '이 장면은 찾을 수 없어요.': 'This scene could not be found.',
    '작품 둘러보기': 'Explore the films',
}


def english_work(work):
    result = deepcopy(work)
    result['name'] = EN_NAMES[work['id']]
    result['summary'] = EN_SUMMARIES.get(work['id'], SERIES_SUMMARY)
    result['title'] = (f"FALL 707: REBOOT · {work['label']} | " if work['season'] else '') + result['name']
    result['path'] = '/en' + work['path']
    result['searchText'] = ' '.join([work['name'], work['title'], result['name'], result['title']])
    return result


class EnglishPage(HTMLParser):
    """Translate text and accessible labels without altering markup or image assets."""
    def __init__(self, translations, origin):
        super().__init__(convert_charrefs=False)
        self.translations = sorted(translations.items(), key=lambda pair: len(pair[0]), reverse=True)
        self.origin = origin
        self.parts = []
        self.in_json = False

    def translate(self, text):
        for original, translated in self.translations:
            text = text.replace(original, translated)
        return text

    def handle_decl(self, decl): self.parts.append('<!' + decl + '>')
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html': attrs['lang'] = 'en'
        if tag == 'script': self.in_json = attrs.get('type') == 'application/ld+json'
        for key in ['alt', 'aria-label', 'placeholder', 'title', 'content']:
            if key in attrs: attrs[key] = self.translate(attrs[key])
        if tag == 'a' and attrs.get('href', '').startswith('/'):
            attrs['href'] = '/en' + attrs['href']
        if tag == 'link' and attrs.get('rel') == 'canonical':
            attrs['href'] = attrs['href'].replace(self.origin + '/', self.origin + '/en/', 1)
        if tag == 'meta' and attrs.get('property') == 'og:url':
            attrs['content'] = attrs['content'].replace(self.origin + '/', self.origin + '/en/', 1)
        if tag == 'meta' and (attrs.get('property') == 'og:image' or attrs.get('name') == 'twitter:image'):
            attrs['content'] = attrs['content'].replace('/assets/og/og-ko.jpg', '/assets/og/og-en.jpg')
        if tag == 'meta' and attrs.get('property') == 'og:locale': attrs['content'] = 'en_US'
        if tag == 'script' and attrs.get('src') == '/catalog.js': attrs['src'] = '/en/catalog.js'
        if tag == 'iframe': attrs['src'] += '&hl=en&cc_lang_pref=en'
        self.parts.append('<' + tag + ''.join(' ' + k + ('="' + escape(v, quote=True) + '"' if v is not None else '') for k, v in attrs.items()) + '>')

    def handle_endtag(self, tag):
        self.parts.append('</' + tag + '>')
        if tag == 'script': self.in_json = False

    def handle_data(self, text):
        if self.in_json:
            def translated(value):
                if isinstance(value, dict):
                    result = {k: translated(v) for k, v in value.items()}
                    if 'url' in result: result['url'] = result['url'].replace(self.origin + '/', self.origin + '/en/', 1)
                    if result.get('@type') == 'ProfilePage': result['inLanguage'] = 'en'
                    return result
                if isinstance(value, list): return [translated(v) for v in value]
                return self.translate(value) if isinstance(value, str) else value
            self.parts.append(json.dumps(translated(json.loads(text)), ensure_ascii=False).replace('</', '<\\/'))
        else:
            self.parts.append(escape(self.translate(text), quote=False))

    def handle_entityref(self, name): self.parts.append('&' + name + ';')
    def handle_charref(self, name): self.parts.append('&#' + name + ';')


def localize_site(out, works, origin, base_path=''):
    en_works = [english_work(work) for work in works]
    # Keep searching across both languages and keep saved video IDs shared.
    for ko, en in zip(works, en_works): ko['searchText'] = en['searchText']
    (out/'en').mkdir(exist_ok=True)
    for path, records in [('catalog.js', works), ('en/catalog.js', en_works)]:
        published_records = [{**record, 'path': base_path + record['path'], 'image': base_path + record['image']} for record in records]
        (out/path).write_text('window.PORTFOLIO = ' + json.dumps(published_records, ensure_ascii=False).replace('</', '<\\/') + ';\n', encoding='utf-8')
    base_translations = dict(UI)
    from privacy_page import TRANSLATIONS
    base_translations.update(TRANSLATIONS)
    base_translations.update(zip(ABOUT_PARAGRAPHS['ko'], ABOUT_PARAGRAPHS['en']))
    base_translations.update({OG_ALT['ko']: OG_ALT['en'],
        '상상을, 장면으로.': 'From imagination to frame.',
        '이야기를, 세계관으로.': 'From story to world.'})
    for ko, en in zip(works, en_works):
        base_translations[ko['name']] = en['name']
        base_translations[ko['title']] = en['title']
        base_translations[ko['summary']] = en['summary']
    pages = [out/'index.html', out/'404.html', out/'links/index.html', out/'privacy/index.html', *sorted((out/'watch').rglob('index.html'))]
    by_path = {v['path']: (v, e) for v, e in zip(works, en_works)}
    for source in pages:
        relative = source.relative_to(out)
        path = '/' + relative.as_posix().removesuffix('index.html')
        translations = dict(base_translations)
        if path in by_path:
            ko, en = by_path[path]
            # Several videos share a Korean synopsis; metadata must match this film.
            translations[ko['summary']] = en['summary']
            translations[ko['summary'][:170]] = en['summary'][:170]
        korean = source.read_text(encoding='utf-8')
        parser = EnglishPage(translations, origin)
        parser.feed(korean)
        english = ''.join(parser.parts)
        # Fail the build instead of silently publishing untranslated content.
        if re.search('[가-힣]', english):
            residual = re.findall(r'[^<>]*[가-힣][^<>]*', english)
            raise ValueError(f'Untranslated copy in {relative}: {residual[:4]}')
        for lang, document in [('ko', korean), ('en', english)]:
            english_path = '/en' + path
            alternates = ''.join(f'<link rel="alternate" hreflang="{code}" href="{origin}{url}">' for code, url in [('ko', path), ('en', english_path), ('x-default', english_path)])
            document = document.replace('</head>', alternates + '</head>')
            switch = '<nav class="language-switch" aria-label="Language">' + ''.join(f'<a href="{url}" lang="{code}" hreflang="{code}" data-language="{code}" aria-label="{label}"' + (' aria-current="page"' if code == lang else '') + f'>{display}</a>' for code, url, display, label in [('ko', path, 'KO', '한국어'), ('en', english_path, 'EN', 'English')]) + '</nav>'
            document = document.replace('<div class="header-actions">', '<div class="header-actions">' + switch)
            target = source if lang == 'ko' else out/'en'/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(document, encoding='utf-8')

    # Content-addressed resources make each published design update unambiguous.
    asset_dir = out/'assets'/'build'
    asset_dir.mkdir(parents=True, exist_ok=True)
    assets = {}
    for name in ['styles.css', 'portfolio.css', 'portfolio.js', 'catalog.js', 'en/catalog.js']:
        content = (out/name).read_bytes()
        stem, ext = name.replace('/', '-').rsplit('.', 1)
        destination = f'{stem}.{sha256(content).hexdigest()[:12]}.{ext}'
        (asset_dir/destination).write_bytes(content)
        assets['/' + name] = '/assets/build/' + destination
    for page in out.rglob('*.html'):
        content = page.read_text(encoding='utf-8')
        for old, new in assets.items(): content = content.replace('"' + old + '"', '"' + new + '"')
        if base_path:
            # Prefix only local URL attributes; canonical/schema URLs already use the full origin.
            content = re.sub(r'(\b(?:href|src|poster)=")(/(?!/))', lambda m: m[1] + base_path + m[2], content)
        page.write_text(content, encoding='utf-8')
    for asset in asset_dir.iterdir():
        if asset.is_file() and '/assets/build/' + asset.name not in assets.values(): asset.unlink()
    paths = ['/', '/links/', '/privacy/', *by_path]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    for path in paths:
        for prefix in ['', '/en']:
            sitemap += '<url><loc>' + origin + prefix + path + '</loc>'
            for lang, url in [('ko', path), ('en', '/en' + path), ('x-default', '/en' + path)]:
                sitemap += f'<xhtml:link rel="alternate" hreflang="{lang}" href="{origin}{url}"/>'
            sitemap += '</url>'
    (out/'sitemap.xml').write_text(sitemap + '</urlset>', encoding='utf-8')
