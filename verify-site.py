"""Check generated URLs and bilingual routes before publishing. No dependencies."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from site_config import CONTACT_EMAIL, OG_ALT
from image_dimensions import jpeg_size
from youtube_sync import load_snapshot, merge_portfolio_data, latest_episode, exact_count

parser = argparse.ArgumentParser()
parser.add_argument('--origin', required=True)
parser.add_argument('--base-path', default='')
parser.add_argument('--directory', default='dist')
args = parser.parse_args()
root = Path(args.directory).resolve()
base = '/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
origin = args.origin.rstrip('/')
site = origin + base
source_data = json.loads((Path(__file__).resolve().parent / 'portfolio-data.json').read_text(encoding='utf-8'))
source_data = merge_portfolio_data(source_data, load_snapshot())
expected_ids = {video['id'] for video in source_data['videos']}
video_count = len(expected_ids)
published_catalog=json.loads((root/'catalog.js').read_text(encoding='utf-8').split(' = ',1)[1].rstrip(';\n'))
published_by_id={work['id']:work for work in published_catalog}
latest_work=latest_episode(published_catalog)


def local_file(url):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc:
        if parts.scheme + '://' + parts.netloc != origin:
            return None
    elif not parts.path or not parts.path.startswith('/'):
        return None
    path = unquote(parts.path)
    assert path.startswith(base + '/'), f'URL escapes deployment path: {url}'
    relative = path[len(base):].lstrip('/')
    result = root / relative
    if path.endswith('/'):
        result /= 'index.html'
    assert result.is_relative_to(root) and result.is_file(), f'Missing local resource: {url}'
    return result


def hero_image_sources(markup):
    if 'data-work-hero' in markup:
        config=json.loads((Path(__file__).resolve().parent/'hero_rotation_config.json').read_text(encoding='utf-8'))
        return {base+'/assets/hero/'+config['clips'][0]['files']['poster']}
    sources={latest_work['image']}
    script=re.search(r'<script[^>]+src="([^" >]*/responsive-media\.[a-f0-9]+\.js)"',markup)
    if script:
        mapping=json.loads(local_file(script[1]).read_text(encoding='utf-8').split('=',1)[1].rstrip(';'))
        optimized=mapping.get(latest_work['id'],{}).get('src')
        if optimized:sources.add(optimized)
    return sources

def hero_feature_path(markup):
    data=re.search(r'<script type="application/json" data-work-hero-config>([\s\S]*?)</script>',markup)
    return json.loads(data[1])['slides'][0]['url'] if data else latest_work['path']


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.lang = ''
        self.canonical = ''
        self.alternates = {}
        self.switches = {}
        self.json_chunks = []
        self.in_json = False
        self.metas = {}
        self.anchors = []
        self.images = []
        self.iframes = []
        self.scripts = []
        self.video_id = ''
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'meta':
            key = attrs.get('property') or attrs.get('name')
            self.metas.setdefault(key, []).append(attrs.get('content'))
        if tag == 'a':
            self.anchors.append(attrs)
        if tag == 'img':
            assert attrs.get('src', '').strip(), f'Image has an empty source: {attrs}'
            self.images.append(attrs)
        if tag == 'iframe':
            self.iframes.append(attrs)
        if tag == 'body':
            self.video_id = attrs.get('data-id', '')
        for key in ['href', 'src', 'poster']:
            if attrs.get(key):
                local_file(attrs[key])
        if tag == 'html':
            self.lang = attrs['lang']
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs['href']
        if tag == 'link' and attrs.get('rel') == 'alternate' and 'hreflang' in attrs:
            self.alternates[attrs['hreflang']] = attrs['href']
        if 'data-language' in attrs:
            self.switches[attrs['data-language']] = attrs['href']
        if tag == 'script':
            self.scripts.append(attrs)
            self.in_json = attrs.get('type') == 'application/ld+json'

    def handle_data(self, data):
        if self.in_json and data.strip():
            self.json_chunks.append(json.loads(data))

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_json = False


library = root/'library/index.html'
assert library.is_file(), 'Private library shell missing'
library_source = library.read_text(encoding='utf-8')
assert 'noindex,nofollow,noarchive' in library_source
assert 'id="login"' in library_source and 'id="cards"' in library_source
assert not (root/'library/private-library.json').exists()
library_page=Page(library_source)
assert any('library.js' in script.get('data-service-src','') and 'src' not in script for script in library_page.scripts), 'Private library initializes tracking/service before permission'
html_files = [page for page in root.rglob('*.html') if page != library and page.parent != root/'pwa']
from tutorials import ROUTES as TUTORIAL_ROUTES
from questions import ROUTES as QUESTION_ROUTES
from presskit import ROUTES as PRESS_ROUTES
from international import ROUTES as SERIES_ROUTES, supported_routes
translated_routes=supported_routes([{**w,'path':w['path'][len(base):]} for w in published_catalog])
TUTORIAL_ROUTES = [*TUTORIAL_ROUTES, *QUESTION_ROUTES, *PRESS_ROUTES, *SERIES_ROUTES]
from importlib.util import find_spec
new_bilingual_routes=lambda:[]
if find_spec('notes_update') is not None:
 from notes_update import new_bilingual_routes
from lounge import extra_bilingual
from actors import routes as actor_routes
assert len(html_files) == 2 * (video_count + 10 + len(TUTORIAL_ROUTES)+len(new_bilingual_routes())+extra_bilingual()+len(actor_routes()))+2*len(translated_routes), len(html_files)
for path in html_files:
    source = path.read_text(encoding='utf-8')
    assert source.count('/consent.js?v=') == 1, path
    assert 'data-cookie-settings' in source, path
    assert 'googletagmanager.com/gtag/js' not in source, path
    page = Page(source)
    assert all(not frame.get('src') for frame in page.iframes), f'External iframe loads before permission: {path}'
    for script in page.scripts:
        active=script.get('src','')
        assert not re.search(r'/(?:community|library)\.js(?:\?|$)',active), f'Service module loads before permission: {path}'
    from lounge import enabled as lounge_enabled
    is_board_redirect=lounge_enabled() and '/questions/' in path.as_posix()
    if '/lounge/' in path.as_posix() or ('/questions/' in path.as_posix() and not is_board_redirect):
        assert any('community.js' in script.get('data-service-src','') for script in page.scripts), path
    if is_board_redirect:
        assert 'http-equiv="refresh"' in source and '/lounge/#board' in source
        assert not any('community.js' in script.get('data-service-src','') for script in page.scripts)
    relative = path.relative_to(root).as_posix()
    lang = relative.split('/',1)[0] if relative.startswith(('en/','ja/','es/')) else 'ko'
    assert page.lang == lang, path
    assert page.metas.get('twitter:card') == ['summary_large_image'], path
    assert len(page.metas.get('og:image', [])) == 1, path
    assert page.metas.get('twitter:image') == page.metas['og:image'], path
    og_file = local_file(page.metas['og:image'][0])
    assert og_file, path
    width, height = jpeg_size(og_file)
    assert page.metas['og:image:width'] == [str(width)], path
    assert page.metas['og:image:height'] == [str(height)], path
    assert page.metas['og:locale'] == [{'ko':'ko_KR','en':'en_US','ja':'ja_JP','es':'es_ES'}[lang]], path
    contacts = [a['href'] for a in page.anchors if a.get('href', '').startswith('mailto:')]
    assert contacts and {url.split('?', 1)[0] for url in contacts} == {'mailto:' + CONTACT_EMAIL}, path
    assert not any('TODO' in a.get('href', '') for a in page.anchors), path
    if relative in ('index.html', 'en/index.html'):
        assert (width, height) == (1200, 630) and og_file.stat().st_size <= 300_000
        assert page.metas['og:image:alt'] == [OG_ALT[lang]], path
        share_manifest=json.loads((root/'assets/og/pages/manifest.json').read_text(encoding='utf-8'))
        share=next(row for row in share_manifest if row['kind']=='home' and row['language']==lang)
        assert share['sources']==[f'assets/og/og-{lang}.jpg'], path
        assert page.metas['og:image']==[share['url']], path
        prefix = base + ('/en' if lang == 'en' else '')
        assert any('hero-casting-link' in a.get('class','') and '/actors/min-seoa/?casting=1' in a.get('href','') for a in page.anchors), path
        for route in ('/', '/#episodes', '/#originals', '/#collaboration', '/#about'):
            assert any(a.get('href') == prefix + route and 'nav-link' in a.get('class', '') for a in page.anchors), (path, route)
        assert source.index('id="latest-episodes"') < source.index('id="about"'), path
        assert 'id="binge-watch"' not in source and 'id="soundtracks"' not in source, path
        assert source.index('id="collaboration"') < source.index('id="about"'), path
        assert source.count('id="collaboration"') == 1, path
        hero=next(img for img in page.images if 'hero-image' in img.get('class','').split())
        assert hero['src'] in hero_image_sources(source), 'Homepage hero does not use the newest episode'
        assert any(a.get('href')==hero_feature_path(source) and 'hero-feature-link' in a.get('class','') for a in page.anchors), 'Featured work link is stale'
        assert 'id="latest-episodes"' in source
        for season in {video['season'] for video in published_catalog if re.fullmatch(r's[1-9][0-9]*',video['category'])}:
            assert f'data-category="s{season}"' in source, 'A published season has no filter'
        channel_count=exact_count(source_data.get('channel',{}).get('apiSubscriberCount'))
        if channel_count is not None:
            label='YouTube subscribers' if lang=='en' else 'YouTube 구독자'
            assert re.search(r'class="collaboration-stat" data-youtube-api-count[^>]*>[\s\S]*?<dd><strong>'+str(channel_count)+r'</strong>',source), 'Raw channel subscriber count was changed'
            stamp=source_data['channel']['apiStatisticsUpdatedAt']
            assert f'<time datetime="{stamp}">{stamp}</time>' in source, 'YouTube retrieval timestamp is absent'
    ko_relative = re.sub(r'^(?:en|ja|es)/','',relative)
    route = '/' + ko_relative.removesuffix('index.html')
    available=['ko','en','ja','es'] if route in translated_routes else ['ko','en']
    assert page.switches == {code:base+('' if code=='ko' else '/'+code)+(route if code in available else '/') for code in ('ko','en','ja','es')}, path
    assert page.alternates == {**{code:site+('' if code=='ko' else '/'+code)+route for code in available},'x-default':site+'/en'+route}, path
    if not relative.endswith('404.html'):
        expected = site + ('/'+lang if lang!='ko' else '') + ('/lounge/' if is_board_redirect else route)
        assert page.canonical == expected, (path, page.canonical)
        assert len(page.json_chunks) == 1, path
        schema = page.json_chunks[0]
        assert schema['url'] == expected, path
        for thumbnail in schema.get('thumbnailUrl', []):
            local_file(thumbnail)
        if route.startswith('/watch/'):
            assert schema['@type'] == 'VideoObject'
            assert page.video_id in expected_ids, path
            original = next(video for video in source_data['videos'] if video['id'] == page.video_id)
            assert schema['embedUrl'] == f'https://www.youtube-nocookie.com/embed/{page.video_id}', path
            assert schema['thumbnailUrl'] == [site + published_by_id[page.video_id]['image'][len(base):]], path
            assert all(isinstance(schema.get(field), str) and schema[field].strip() for field in ('name', 'description', 'uploadDate', 'duration')), path
            assert schema['uploadDate'] == original['uploadDate'], path
            assert datetime.fromisoformat(schema['uploadDate'].replace('Z', '+00:00')).utcoffset() is not None, path
            assert re.fullmatch(r'PT\d+(?:\.\d+)?S', schema['duration']), path
            assert float(schema['duration'][2:-1]) == float(original['seconds']) > 0, path
            assert 'contentUrl' not in schema, 'Use the actual embed URL, not a YouTube watch URL as a media file'
            api_views=exact_count(original.get('apiViewCount'))
            if api_views is not None:
                label={'ko':'YouTube 조회수','en':'YouTube views','ja':'YouTube再生回数','es':'Reproducciones de YouTube'}[lang]
                assert f'{label} <strong>{api_views}</strong>' in source, 'Raw episode view count was changed or missing'
    assert 'about-identity' not in source and 'avatar.jpg' not in source, path

# The Season 3 release must be reachable in both languages, with accessible
# public story cards and a cross-season route from the previous full movie.
if '0I75_YXhMSM' in expected_ids:
    episode_route = '/watch/fall-707-s3-ep1/'
    gallery_asset = base + '/assets/fall707-s3-ep1/'
    for lang, prefix in [('ko', ''), ('en', '/en')]:
        route_prefix = base + prefix
        homepage = (root/(prefix.lstrip('/') + '/index.html').lstrip('/')).read_text(encoding='utf-8')
        home = Page(homepage)
        hero = next(img for img in home.images if 'hero-image' in img.get('class', '').split())
        assert hero['src'] in hero_image_sources(homepage)
        assert any(a.get('href') == hero_feature_path(homepage) and 'hero-feature-link' in a.get('class', '') for a in home.anchors)
        assert 'data-category="s3"' in homepage
        assert homepage.index('id="episodes"') < homepage.index('id="season-two"')
        assert 'upcoming-episode' not in homepage
        links = Page((root/(prefix.lstrip('/') + '/links/index.html').lstrip('/')).read_text(encoding='utf-8'))
        assert any(a.get('href') == route_prefix + latest_work['path'][len(base):] and 'bio-feature' in a.get('class', '') for a in links.anchors)
        watch_path = root/(prefix.lstrip('/') + episode_route + 'index.html').lstrip('/')
        watch_source = watch_path.read_text(encoding='utf-8')
        watch = Page(watch_source)
        assert watch.json_chunks[0]['duration'] == 'PT1227.79S'
        assert watch.json_chunks[0]['embedUrl'].endswith('/0I75_YXhMSM')
        if lang == 'en':
            from html import unescape
            from localization import EN_SUMMARIES
            expected_summary = EN_SUMMARIES['0I75_YXhMSM']
            synopsis = re.search(r'<p class="watch-description">(.*?)</p>', watch_source, re.S)
            assert synopsis and unescape(synopsis.group(1)) == expected_summary, 'Season 3 English synopsis was truncated'
            assert watch.json_chunks[0]['description'] == expected_summary
        assert 'id="episode-captions-title"' in watch_source and 'CC' in watch_source
        assert 'id="episode-story-cards" tabindex="0"' in watch_source
        gallery = [img for img in watch.images if img.get('src', '').startswith(gallery_asset)]
        assert len(gallery) == 5
        for index, img in enumerate(gallery, 1):
            assert img['width'] == '1122' and img['height'] == '1402'
            assert img['loading'] == 'lazy' and img['decoding'] == 'async'
            assert img['alt'].startswith(f'카드 {index}/5.' if lang == 'ko' else f'Card {index} of 5.')
        assert any(a.get('href') == 'https://www.instagram.com/p/Degx3lXCeUp/' and a.get('rel') == 'noopener noreferrer' for a in watch.anchors)
        previous = Page((root/(prefix.lstrip('/') + '/watch/fall-707-season-2-full/index.html').lstrip('/')).read_text(encoding='utf-8'))
        assert any(a.get('href') == route_prefix + episode_route and a.get('class') == 'next-episode' for a in previous.anchors)

# The supplied Newtake manuscript must survive the shared localization pipeline
# intact; only the designated placeholder is replaced by the requested Reel.
from newtake_tutorial import PATH as NEWTAKE_PATH, EMBED as NEWTAKE_EMBED, SPONSOR as NEWTAKE_SPONSOR, START as NEWTAKE_START, END as NEWTAKE_END, article_html as newtake_article, read_source as newtake_source
for lang, prefix in [('ko',''),('en','/en')]:
    metadata, _ = newtake_source(lang)
    document = (root/(prefix+NEWTAKE_PATH+'index.html').lstrip('/')).read_text(encoding='utf-8')
    page = Page(document)
    article = document.split(NEWTAKE_START,1)[1].split(NEWTAKE_END,1)[0]
    assert article.replace(' data-external-src=', ' src=') == newtake_article(lang), 'Newtake body was changed by the shared page pipeline'
    assert page.metas['description'] == [metadata['description']]
    assert page.metas['og:title'] == [metadata['title']+' | 드래곤시네마 DRA9ON CINEMA']
    assert page.metas['og:description'] == [metadata['description']]
    assert page.metas['og:type'] == ['article']
    assert page.metas['article:published_time'] == [metadata['date']]
    assert page.metas['article:tag'] == metadata['tags']
    assert page.json_chunks[0]['headline'] == metadata['title']
    assert page.json_chunks[0]['datePublished'] == metadata['date']
    assert page.json_chunks[0]['keywords'] == metadata['tags']
    assert page.json_chunks[0]['inLanguage'] == lang
    assert len(page.iframes) == 1 and not page.iframes[0].get('src') and page.iframes[0].get('data-external-src') == NEWTAKE_EMBED
    sponsor = [anchor for anchor in page.anchors if anchor.get('href') == NEWTAKE_SPONSOR]
    assert len(sponsor) == 1 and sponsor[0]['target'] == '_blank'
    assert set(sponsor[0]['rel'].split()) == {'sponsored','noopener'}
    assert article.count('<table>') == 2 and article.count('<pre ') == 2
    assert 'embed.js' not in document
    for route in ['/', '/tutorials/']:
        listing = Page((root/(prefix+route+'index.html').lstrip('/')).read_text(encoding='utf-8'))
        latest = next(anchor for anchor in listing.anchors if 'tutorial-preview' in anchor.get('class','').split())
        from lighting_tutorial import PATH as LIGHTING_PATH
        assert latest['href'] == base+prefix+LIGHTING_PATH, 'New article is not the latest tutorial'
        assert any(a.get('href') == base+prefix+NEWTAKE_PATH for a in listing.anchors), 'Newtake tutorial must stay in the list'

catalogs = []
for filename in ['catalog.js', 'en/catalog.js']:
    data = json.loads((root / filename).read_text(encoding='utf-8').split(' = ', 1)[1].rstrip(';\n'))
    assert len(data) == video_count
    assert {work['id'] for work in data} == expected_ids
    for work in data:
        local_file(work['path'])
        local_file(work['image'])
        original=next(video for video in source_data['videos'] if video['id']==work['id'])
        assert work.get('apiViewCount') == original.get('apiViewCount'), 'API view counts changed in the public catalog'
    catalogs.append(data)
for ko, en in zip(*catalogs):
    assert ko['id'] == en['id']
    assert en['path'] == base + '/en' + ko['path'][len(base):]
    assert ko['name'] in en['searchText'] and en['name'] in ko['searchText']

sitemap = ET.parse(root / 'sitemap.xml').getroot()
from lounge import extra_bilingual
assert len(sitemap) == 2 * (video_count + 9 + len(TUTORIAL_ROUTES)+len(new_bilingual_routes())+extra_bilingual()+len(actor_routes()))+2*len(translated_routes)
for entry in sitemap:
    local_file(entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text)
assert (root / '.nojekyll').exists()
assert 'Sitemap: ' + site + '/sitemap.xml' in (root / 'robots.txt').read_text(encoding='utf-8')
from html import unescape
for page in html_files:
    document = page.read_text(encoding='utf-8')
    policies = re.findall(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)"', document)
    assert len(policies) == 1, f'Missing/duplicate CSP: {page}'
    policy = unescape(policies[0])
    if NEWTAKE_PATH.strip('/') in page.relative_to(root).as_posix():
        assert NEWTAKE_EMBED in policy
    else:
        assert 'https://www.instagram.com' not in policy, 'Instagram frame permission escaped the new article'
    for directive in ["object-src 'none'", "base-uri 'none'", "form-action 'none'", "script-src-attr 'none'"]:
        assert directive in policy, (page, directive)
    script_policy = next(part.strip() for part in policy.split(';') if part.strip().startswith('script-src '))
    assert "'unsafe-inline'" not in script_policy and "'unsafe-eval'" not in script_policy
    assert document.index('Content-Security-Policy') < document.index('<script'), page
    assert not re.search(r'\son\w+\s*=', document), f'Inline event handler blocked by CSP: {page}'
print(f'PASS: {len(html_files)} pages, {video_count} source videos, selected routes in four languages, local assets, language switches, canonical URLs, sitemap and CSP.')
