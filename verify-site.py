"""Check generated URLs and bilingual routes before publishing. No dependencies."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET
from site_config import CONTACT_EMAIL, OG_ALT
from image_dimensions import jpeg_size

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
expected_ids = {video['id'] for video in source_data['videos']}
video_count = len(expected_ids)


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
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag == 'meta':
            key = attrs.get('property') or attrs.get('name')
            self.metas.setdefault(key, []).append(attrs.get('content'))
        if tag == 'a':
            self.anchors.append(attrs)
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
            self.in_json = attrs.get('type') == 'application/ld+json'

    def handle_data(self, data):
        if self.in_json and data.strip():
            self.json_chunks.append(json.loads(data))

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_json = False


html_files = list(root.rglob('*.html'))
assert len(html_files) == 2 * (video_count + 4), len(html_files)
for path in html_files:
    source = path.read_text(encoding='utf-8')
    assert source.count('/consent.js?v=') == 1, path
    assert 'data-cookie-settings' in source, path
    assert 'googletagmanager.com/gtag/js' not in source, path
    page = Page(source)
    relative = path.relative_to(root).as_posix()
    lang = 'en' if relative.startswith('en/') else 'ko'
    assert page.lang == lang, path
    assert page.metas.get('twitter:card') == ['summary_large_image'], path
    assert len(page.metas.get('og:image', [])) == 1, path
    assert page.metas.get('twitter:image') == page.metas['og:image'], path
    og_file = local_file(page.metas['og:image'][0])
    assert og_file, path
    width, height = jpeg_size(og_file)
    assert page.metas['og:image:width'] == [str(width)], path
    assert page.metas['og:image:height'] == [str(height)], path
    assert page.metas['og:locale'] == ['en_US' if lang == 'en' else 'ko_KR'], path
    contacts = [a['href'] for a in page.anchors if a.get('href', '').startswith('mailto:')]
    assert contacts and set(contacts) == {'mailto:' + CONTACT_EMAIL}, path
    assert not any('TODO' in a.get('href', '') for a in page.anchors), path
    if relative in ('index.html', 'en/index.html'):
        assert (width, height) == (1200, 630) and og_file.stat().st_size <= 300_000
        assert page.metas['og:image:alt'] == [OG_ALT[lang]], path
        assert page.metas['og:image'] == [site + f'/assets/og/og-{lang}.jpg?v=20260924-fall707'], path
        prefix = base + ('/en' if lang == 'en' else '')
        assert any(a.get('href') == prefix + '/watch/fall-707-s1-ep1/' and 'hero-start' in a.get('class', '') for a in page.anchors), path
        for route in ('/', '/#episodes', '/#originals', '/#about'):
            assert any(a.get('href') == prefix + route and 'nav-link' in a.get('class', '') for a in page.anchors), (path, route)
        assert source.index('id="more-cuts"') < source.index('id="about"'), path
    ko_relative = relative.removeprefix('en/')
    route = '/' + ko_relative.removesuffix('index.html')
    assert page.switches == {'ko': base + route, 'en': base + '/en' + route}, path
    assert page.alternates == {'ko': site + route, 'en': site + '/en' + route, 'x-default': site + '/en' + route}, path
    if not relative.endswith('404.html'):
        expected = site + ('/en' if lang == 'en' else '') + route
        assert page.canonical == expected, (path, page.canonical)
        assert len(page.json_chunks) == 1, path
        schema = page.json_chunks[0]
        assert schema['url'] == expected, path
        for thumbnail in schema.get('thumbnailUrl', []):
            local_file(thumbnail)
        if route.startswith('/watch/'):
            assert schema['@type'] == 'VideoObject'
            assert schema['embedUrl'].startswith('https://www.youtube-nocookie.com/embed/')
    assert 'about-identity' not in source and 'avatar.jpg' not in source, path

catalogs = []
for filename in ['catalog.js', 'en/catalog.js']:
    data = json.loads((root / filename).read_text(encoding='utf-8').split(' = ', 1)[1].rstrip(';\n'))
    assert len(data) == video_count
    assert {work['id'] for work in data} == expected_ids
    for work in data:
        local_file(work['path'])
        local_file(work['image'])
    catalogs.append(data)
for ko, en in zip(*catalogs):
    assert ko['id'] == en['id']
    assert en['path'] == base + '/en' + ko['path'][len(base):]
    assert ko['name'] in en['searchText'] and en['name'] in ko['searchText']

sitemap = ET.parse(root / 'sitemap.xml').getroot()
assert len(sitemap) == 2 * (video_count + 3)
for entry in sitemap:
    local_file(entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text)
assert (root / '.nojekyll').exists()
assert 'Sitemap: ' + site + '/sitemap.xml' in (root / 'robots.txt').read_text(encoding='utf-8')
print(f'PASS: {len(html_files)} pages, {video_count} videos per language, local assets, language switches, canonical URLs and sitemap.')
