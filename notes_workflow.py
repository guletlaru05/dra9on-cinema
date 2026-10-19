"""Publish the owner's reviewed workflow and early-experiment afterword in four languages.

Article fragments are the reviewed editorial source. Shared site chrome, media
preferences, CSP, language links and the image viewer stay in the normal build.
"""
from pathlib import Path
from hashlib import sha256
from html import escape
import json
import re

ROOT = Path(__file__).parent
CONTENT = ROOT / 'notes-content/production-workflow'
ART = '/assets/notes/production-workflow/'


def routes():
    return {'/notes/workflow/', '/notes/fall-707-beginnings/'}


def build(out, origin, base_path=''):
    from international import PageLanguage, dictionary, supported_routes

    base_docs = {
        lang: (out / ('' if lang == 'ko' else 'en') / 'notes/fall-707-beginnings/index.html').read_text(encoding='utf-8')
        for lang in ('ko', 'en', 'ja', 'es')
    }
    css = (out / 'notes-workflow.css').read_bytes()
    css_name = 'notes-workflow.' + sha256(css).hexdigest()[:12] + '.css'
    (out / 'assets/build' / css_name).write_bytes(css)
    images = {r['file']: r for r in json.loads((out / ART.lstrip('/') / 'manifest.json').read_text(encoding='utf-8'))}

    def replace_meta(doc, selector, value):
        return re.sub(r'(<meta ' + selector + r' content=")[^"]*', lambda m: m[1] + escape(value, quote=True), doc)

    for article in json.loads((CONTENT / 'pages.json').read_text(encoding='utf-8')):
        lang, route = article['language'], article['path']
        prefix = '' if lang == 'ko' else '/' + lang
        doc = re.sub(r'<main\b[\s\S]*?</main>', '<main id="main"></main>', base_docs[lang], count=1)
        if lang in ('ja', 'es'):
            asset_versions = {kind + '-version': sha256((out / lang / (kind + '.js')).read_bytes()).hexdigest()[:12] for kind in ('catalog', 'locale')}
            parser = PageLanguage(lang, dictionary(lang, out), origin, base_path, supported_routes([]), asset_versions)
            parser.feed(doc)
            doc = ''.join(parser.parts)

        main = (CONTENT / article['fragment']).read_text(encoding='utf-8')
        if base_path:
            main = re.sub(r'((?:href|src)=")(/(?!/)[^"]*)', lambda m: m[1] + base_path + m[2], main)
        doc = doc.replace('<main id="main"></main>', main, 1)
        title, description = article['title'], article['description']
        url = origin + prefix + route
        picture = 'workflow-hero.webp' if route.endswith('/workflow/') else 'pilot-10.webp'
        image = images[picture]
        share_image = origin + ART + picture.replace('.webp', '-share.jpg')
        doc = re.sub(r'<title>[\s\S]*?</title>', lambda _: '<title>' + escape(title) + ' | DRA9ON CINEMA</title>', doc, count=1)
        doc = replace_meta(doc, 'name="description"', description)
        for name, value in [('og:title', title), ('og:description', description), ('og:url', url), ('og:type', 'article'), ('og:image', share_image), ('og:image:width', str(image['width'])), ('og:image:height', str(image['height'])), ('og:image:alt', title)]:
            doc = replace_meta(doc, 'property="' + name + '"', value)
        for name, value in [('twitter:title', title), ('twitter:description', description), ('twitter:image', share_image), ('twitter:image:alt', title)]:
            doc = replace_meta(doc, 'name="' + name + '"', value)
        doc = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m[1] + url, doc, count=1)
        schema = {'@context': 'https://schema.org', '@type': 'Article', 'headline': title, 'description': description,
                  'url': url, 'inLanguage': lang, 'image': origin + ART + picture,
                  'author': {'@type': 'Organization', 'name': 'DRA9ON CINEMA'}, 'dateModified': '2026-10-19'}
        payload = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
        doc = re.sub(r'(<script type="application/ld\+json">)[\s\S]*?</script>', lambda m: m[1] + payload + '</script>', doc, count=1)
        doc = doc.replace('</head>', '<link rel="stylesheet" href="' + base_path + '/assets/build/' + css_name + '"></head>', 1)
        target = out / prefix.strip('/') / route.strip('/') / 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(doc, encoding='utf-8')
