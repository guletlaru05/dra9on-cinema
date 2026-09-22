"""Check generated URLs and bilingual routes before publishing. No dependencies."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument('--origin', required=True)
parser.add_argument('--base-path', default='')
parser.add_argument('--directory', default='dist')
args = parser.parse_args()
root = Path(args.directory).resolve()
base = '/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
origin = args.origin.rstrip('/')
site = origin + base


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
        self.feed(source)

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        for key in ['href', 'src', 'poster']:
            if attrs.get(key):
                local_file(attrs[key])
        if tag == 'html':
            self.lang = attrs['lang']
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs['href']
        if tag == 'link' and attrs.get('rel') == 'alternate':
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
assert len(html_files) == 46, len(html_files)
for path in html_files:
    source = path.read_text(encoding='utf-8')
    page = Page(source)
    relative = path.relative_to(root).as_posix()
    lang = 'en' if relative.startswith('en/') else 'ko'
    assert page.lang == lang, path
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
    assert len(data) == 21
    for work in data:
        local_file(work['path'])
        local_file(work['image'])
    catalogs.append(data)
for ko, en in zip(*catalogs):
    assert ko['id'] == en['id']
    assert en['path'] == base + '/en' + ko['path'][len(base):]
    assert ko['name'] in en['searchText'] and en['name'] in ko['searchText']

sitemap = ET.parse(root / 'sitemap.xml').getroot()
assert len(sitemap) == 44
for entry in sitemap:
    local_file(entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text)
assert (root / '.nojekyll').exists()
assert 'Sitemap: ' + site + '/sitemap.xml' in (root / 'robots.txt').read_text(encoding='utf-8')
print('PASS: 46 pages, 21 videos per language, local assets, language switches, canonical URLs and sitemap.')
