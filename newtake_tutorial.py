"""Publish the supplied Newtake article without rewriting its Korean body.

Markdown and audited HTML fragments live together in tutorial-content/. The
stdlib-only site build checks both hashes; the optional preparation script uses
markdown-it-py only when an author edits a Markdown source.
"""
from datetime import date
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

PATH = '/tutorials/claude-mcp-newtake/'
ART = '/assets/notes/claude-mcp-newtake-cover-v1.svg'
SHARE_ART = '/assets/notes/claude-mcp-newtake-share-v1.jpg'
REEL = 'https://www.instagram.com/reel/DelRHYDunY-/'
EMBED = REEL + 'embed/'
SPONSOR = 'https://www.newtake.com/?sourceId=NT920205'
CONTENT = Path(__file__).resolve().parent / 'tutorial-content'
START = '<!-- newtake-source:start -->'
END = '<!-- newtake-source:end -->'
ALT_KO = 'Claude에서 MCP를 거쳐 Newtake로 이어지는 4컷 영상 제작 흐름 도식'
ALT_EN = 'Diagram of a four-shot video workflow from Claude through MCP to Newtake'


def read_source(lang):
    """Read the small, explicit frontmatter format used by these two sources."""
    source = (CONTENT/f'claude-mcp-newtake.{lang}.md').read_text(encoding='utf-8')
    match = re.fullmatch(r'---\n(.*?)\n---\n(.*)', source, re.S)
    if not match:
        raise ValueError('Missing Newtake frontmatter')
    metadata = {}
    for line in match[1].splitlines():
        key, value = line.split(':', 1)
        value = value.strip()
        if value.startswith('"'):
            value = json.loads(value)
        elif value.startswith('[') and value.endswith(']'):
            value = [item.strip() for item in value[1:-1].split(',')]
        metadata[key] = value
    assert metadata['slug'] == 'claude-mcp-newtake'
    date.fromisoformat(metadata['date'])
    assert all(metadata.get(key) for key in ('title', 'description', 'date', 'tags'))
    return metadata, match[2]


KO, _ = read_source('ko')
EN, _ = read_source('en')
TRANSLATIONS = {
    KO['title']: EN['title'],
    KO['title']+' | DRA9ON CINEMA': EN['title']+' | DRA9ON CINEMA',
    KO['description']: EN['description'],
    ', '.join(KO['tags']): ', '.join(EN['tags']),
    ALT_KO: ALT_EN,
    **dict(zip(KO['tags'], EN['tags'])),
}


def load_fragment(lang):
    _, body = read_source(lang)
    fragment = (CONTENT/f'claude-mcp-newtake.{lang}.html').read_text(encoding='utf-8')
    manifest = json.loads((CONTENT/'claude-mcp-newtake.manifest.json').read_text(encoding='utf-8'))
    assert sha256(body.encode('utf-8')).hexdigest() == manifest[lang]['body_sha256'], 'Regenerate the Markdown fragments after editing the body'
    assert sha256(fragment.encode('utf-8')).hexdigest() == manifest[lang]['html_sha256'], 'Newtake HTML fragment changed independently of its source'
    return fragment


def article_html(lang):
    metadata, _ = read_source(lang)
    text = load_fragment(lang)
    placeholder = '(여기에 결과 영상 또는 릴스 임베드)' if lang == 'ko' else '(Embed the finished video or Reel here)'
    target = '<blockquote>\n<p>'+placeholder+'</p>\n</blockquote>'
    assert text.count(target) == 1
    title = 'Claude × Newtake 제작 결과 릴스' if lang == 'ko' else 'Claude × Newtake finished Reel'
    fallback = 'Instagram에서 릴스 보기' if lang == 'ko' else 'Watch the Reel on Instagram'
    embed = f'''<figure class="newtake-result"><iframe src="{EMBED}" title="{escape(title)}" width="540" height="740" loading="lazy" allow="encrypted-media; fullscreen; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe><figcaption><a href="{REEL}" target="_blank" rel="noopener noreferrer">{fallback} ↗</a></figcaption></figure>'''
    text = text.replace(target, embed, 1)
    tags = ''.join('<li>'+escape(tag)+'</li>' for tag in metadata['tags'])
    meta = f'<p class="tutorial-date"><time datetime="{metadata["date"]}">{metadata["date"].replace("-", ".")}</time> · {escape(metadata["category"])}</p><ul class="newtake-tags" aria-label="Tags">{tags}</ul>'
    text = text.replace('</h1>', '</h1>'+meta, 1)
    return '<article class="newtake-article">'+text+'</article>'


def teaser(t):
    title = t(KO['title'], EN['title'])
    return f'''<a class="tutorial-preview" href="{PATH}"><img src="{ART}" width="1600" height="900" loading="lazy" decoding="async" alt="{t(ALT_KO,ALT_EN)}"><div><p class="section-eyebrow">CLAUDE / MCP / NEWTAKE</p><h3>{title}</h3><p class="tutorial-card-date"><time datetime="{KO['date']}">{KO['date'].replace('-','.')}</time> · {t('문장 한 줄 · 컷 설계 · SF 영상','One sentence · Shot planning · Sci-fi video')}</p><span>{t('실제 제작 과정 · 강좌 열기','Actual production process · Open lesson')} →</span></div></a>'''


def build(out, origin, head, header, footer, t):
    schema = {'@context':'https://schema.org','@type':'Article',
              'headline':KO['title'],'name':KO['title'],'description':KO['description'],
              'url':origin+PATH,'image':origin+SHARE_ART,'inLanguage':'ko',
              'datePublished':KO['date'],'dateModified':KO['date'],'keywords':KO['tags'],
              'author':{'@type':'Organization','name':'DRA9ON CINEMA'}}
    document_head = head(KO['title']+' | DRA9ON CINEMA',KO['description'],PATH,schema)
    document_head = document_head.replace('property="og:type" content="video.episode"','property="og:type" content="article"')
    values = {'og:image':origin+SHARE_ART,'twitter:image':origin+SHARE_ART,
              'og:image:width':'1600','og:image:height':'900',
              'og:image:alt':ALT_KO,'twitter:image:alt':ALT_KO}
    def social_meta(match):
        tag = match[0]
        key = re.search(r'\b(?:name|property)="([^"]+)"', tag)
        return re.sub(r'\bcontent="[^"]*"', 'content="'+escape(values[key[1]],quote=True)+'"',tag, count=1) if key and key[1] in values else tag
    document_head = re.sub(r'<meta\b[^>]*>',social_meta,document_head)
    extra = '<meta name="keywords" content="'+escape(', '.join(KO['tags']),quote=True)+'">'
    extra += '<meta property="article:published_time" content="'+KO['date']+'">'
    extra += ''.join('<meta property="article:tag" content="'+escape(tag,quote=True)+'">' for tag in KO['tags'])
    extra += '<link rel="stylesheet" href="/newtake-tutorial.css">'
    document_head = document_head.replace('</head>',extra+'</head>',1)
    body = f'<body class="watch-page">{header()}<main class="tutorial-main newtake-main" id="main"><a class="note-back" href="/tutorials/">← {t("튜토리얼 목록","All tutorials")}</a><p class="section-eyebrow">CLAUDE / MCP / NEWTAKE</p>{START}{article_html("ko")}{END}</main>{footer()}</body></html>'
    target = out/PATH.strip('/')
    target.mkdir(parents=True,exist_ok=True)
    (target/'index.html').write_text(document_head+body,encoding='utf-8')
