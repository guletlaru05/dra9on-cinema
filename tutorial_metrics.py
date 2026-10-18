"""Add numeric-only tutorial/site analytics after localization.

Provider setup is explicit: no demo token, synthetic counts or fallback tracking.
"""
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent


class Info(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.heading = False
        self.title = ''
        self.canonical = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1': self.heading = True
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a['href']

    def handle_endtag(self, tag):
        if tag == 'h1': self.heading = False

    def handle_data(self, text):
        if self.heading: self.title += text


def configuration():
    path = ROOT/'analytics-config.json'
    config = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    token = os.environ.get('CF_WEB_ANALYTICS_TOKEN', config.get('cloudflareWebAnalyticsToken', '')).strip()
    if token and not re.fullmatch(r'[a-fA-F0-9]{32}', token):
        raise ValueError('Invalid Cloudflare public beacon token')
    endpoint = os.environ.get('D9_METRICS_ENDPOINT', config.get('metricsEndpoint', '')).strip().rstrip('/')
    if endpoint:
        url = urlsplit(endpoint)
        if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ('','/'):
            raise ValueError('Metrics endpoint must be an HTTPS origin')
    return token, endpoint


def inject_metrics(out, base_path=''):
    token, endpoint = configuration()
    versioned = {}
    for name in ('tutorial-metrics.js', 'tutorial-metrics.css'):
        content = (out/name).read_bytes()
        stem, ext = name.rsplit('.', 1)
        filename = f'{stem}.{sha256(content).hexdigest()[:12]}.{ext}'
        (out/'assets/build'/filename).write_bytes(content)
        versioned[ext] = base_path+'/assets/build/'+filename
    registry = {}
    tutorials = {}
    for page in out.rglob('*.html'):
        rel = page.relative_to(out).as_posix()
        if rel.startswith(('library/','en/library/')) or rel in ('404.html','en/404.html'): continue
        path = '/' + rel.removesuffix('index.html')
        if path.endswith('.html'): continue
        doc = page.read_text(encoding='utf-8')
        info = Info(doc)
        if not info.canonical: continue
        public_path = base_path + path
        canonical_path = re.sub(r'^/(?:en|ja|es)(?=/)','',path)
        is_tutorial = canonical_path.startswith('/tutorials/') and canonical_path != '/tutorials/'
        registry[public_path] = {'canonicalPath': canonical_path, 'type': 'tutorial' if is_tutorial else 'page'}
        en = path.startswith('/en/')
        if is_tutorial:
            language = path.split('/')[1] if path.startswith(('/en/','/ja/','/es/')) else 'ko'
            tutorials.setdefault(canonical_path, {})[language] = info.title
        meta = '<meta name="d9-metrics-path" content="'+escape(public_path,quote=True)+'">'
        meta += '<meta name="d9-metrics-canonical" content="'+escape(canonical_path,quote=True)+'">'
        if endpoint:
            meta += '<meta name="d9-metrics-endpoint" content="'+escape(endpoint,quote=True)+'">'
        if is_tutorial:
            meta += '<meta name="d9-tutorial" content="true">'
        resources = meta+f'<link rel="stylesheet" href="{versioned["css"]}"><script src="{versioned["js"]}" defer></script>'
        if token:
            settings = escape(json.dumps({'token':token, 'spa':False}),quote=True)
            resources += f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon="{settings}"></script>'
        doc = doc.replace('</head>',resources+'</head>',1)
        if canonical_path == '/tutorials/':
            language = path.split('/')[1] if path.startswith(('/en/','/ja/','/es/')) else 'ko'
            label, newest, popular = {'ko':('튜토리얼 정렬','최신순','인기순'), 'en':('Sort tutorials','Newest','Most viewed'), 'ja':('記事の並び順','新しい順','人気順'), 'es':('Ordenar tutoriales','Más recientes','Más vistos')}[language]
            controls = f'<div class="tutorial-sort" role="group" aria-label="{label}"><button type="button" data-tutorial-sort="latest" aria-pressed="true">{newest}</button><button type="button" data-tutorial-sort="popular" aria-pressed="false">{popular}</button><span data-tutorial-sort-status role="status"></span></div>'
            doc = doc.replace('<div class="tutorial-lesson-list">',controls+'<div class="tutorial-lesson-list" data-tutorial-list>',1)
            if 'data-tutorial-catalog' in doc:
                doc = doc.replace('<div class="tutorial-lesson-list" data-tutorial-list>',controls+'<div class="tutorial-lesson-list" data-tutorial-list>',1)
        page.write_text(doc,encoding='utf-8')
    # Deployment allowlist: separate from public output, no personal data.
    worker = ROOT/'workers/tutorial-metrics'
    worker.mkdir(parents=True,exist_ok=True)
    (worker/'registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'tutorial-registry.json').write_text(json.dumps(tutorials,ensure_ascii=False)+'\n',encoding='utf-8')
    return {'cloudflareEnabled':bool(token), 'metricsEndpoint':endpoint, 'pages':len(registry)}
