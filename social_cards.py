"""Deterministic social title cards using approved, existing site artwork.

No image generation, new stills, retouching, or remote requests. Run after all
localized pages exist so new tutorials inherit their own translated title/art.
"""
from hashlib import sha256
from functools import lru_cache
import warnings
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
LANGS = ('ko', 'en', 'ja', 'es')
SIZE = (1200, 630)
LAYOUT = 'page-cards-3-center-watermark-all-routes'
BG = '#101011'
WHITE = '#f4f3ef'
MUTED = '#b3b1b7'
RED = '#ed233a'

def tr(*values):
    return dict(zip(LANGS, values))

LABELS = {
    'actors': tr('AI 배우 에이전시', 'AI Actor Agency', 'AI俳優エージェンシー', 'Agencia de actores de IA'),
    'actor': tr('DRA9ON CINEMA AI 배우', 'DRA9ON CINEMA AI Actor', 'DRA9ON CINEMA AI俳優', 'DRA9ON CINEMA · Actor de IA'),
    'original': tr('오리지널 AI 캐릭터', 'Original AI characters', 'オリジナルAIキャラクター', 'Personajes originales de IA'),
    'notes': tr('제작 비하인드', 'Behind the Scenes', '制作の舞台裏', 'Detrás de cámaras'),
    'tutorials': tr('튜토리얼', 'Tutorials', 'チュートリアル', 'Tutoriales'),
    'lounge': tr('팬 라운지', 'Fan Lounge', 'ファンラウンジ', 'Espacio de fans'),
    'world': tr('세계관', 'The World', '世界観', 'El universo'),
    'characters': tr('캐릭터', 'Characters', '登場人物', 'Personajes'),
    'character': tr('FALL 707 · 캐릭터', 'FALL 707 · Character', 'FALL 707・登場人物', 'FALL 707 · Personaje'),
}
TUTORIAL_INTRO = tr(
    '캐릭터·구도·조명·미감부터 AI 영상 제작까지. DRA9ON CINEMA의 실습 튜토리얼과 전체 프롬프트를 만나보세요.',
    'Explore DRA9ON CINEMA tutorials and complete prompts for characters, framing, lighting, visual style and AI filmmaking.',
    'キャラクター・構図・照明・美的表現からAI映像制作まで。DRA9ON CINEMAの実践チュートリアルと全文プロンプトをご覧ください。',
    'Tutoriales y prompts completos de DRA9ON CINEMA sobre personajes, encuadre, iluminación, estilo visual y cine con IA.')

class Page(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.meta = {}; self.images = []; self.h1 = []; self.in_h1 = False; self.in_main = False
        self.feed(document)

    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        if tag == 'meta':
            self.meta[a.get('property', a.get('name'))] = a.get('content', '')
        if tag == 'main': self.in_main = True
        if tag == 'img' and a.get('src') and self.in_main:
            self.images.append(a['src'])
        if tag == 'h1': self.in_h1 = True

    def handle_endtag(self, tag):
        if tag == 'h1': self.in_h1 = False
        if tag == 'main': self.in_main = False

    def handle_data(self, data):
        if self.in_h1: self.h1.append(data)

    @property
    def heading(self):
        return re.sub(r'\s+', ' ', ''.join(self.h1)).strip()

def route_info(relative):
    parts = Path(relative).parts
    lang = parts[0] if parts[0] in LANGS[1:] else 'ko'
    path = '/' + '/'.join(parts[1:] if lang != 'ko' else parts).removesuffix('index.html')
    if path == '/': return lang, path, 'home'
    if path.startswith('/watch/'): return lang, path, 'watch'
    if path == '/fall-707/': return lang, path, 'series'
    if path == '/fall-707/world/': return lang, path, 'world'
    if path in ('/actors/', '/notes/', '/tutorials/', '/lounge/'):
        return lang, path, path.strip('/')
    if path == '/fall-707/characters/': return lang, path, 'characters'
    for prefix, kind in (('/actors/', 'actor'), ('/notes/', 'note'),
                         ('/tutorials/', 'tutorial'), ('/fall-707/characters/', 'character')):
        if path.startswith(prefix): return lang, path, kind
    return lang, path, 'menu'

def local_asset(out, value, base_path=''):
    path = unquote(urlsplit(value).path)
    if base_path and path.startswith(base_path + '/'):
        path = path[len(base_path):]
    file = (out / path.lstrip('/')).resolve()
    if not file.is_relative_to(out.resolve()) or not file.is_file():
        raise ValueError(f'Missing local OG source: {value}')
    return file

@lru_cache(maxsize=128)
def font(lang, size):
    name = 'NotoSansJP-Regular.ttf' if lang == 'ja' else 'NotoSansKR-Regular.ttf'
    return ImageFont.truetype(str(ROOT / 'build-assets/fonts' / name), size)

def wrap(text, face, width):
    # Keep Latin words together while allowing natural CJK line breaks.
    tokens = re.findall(r'[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9:+.\-]*|\s+|.', text)
    lines = []; line = ''
    for token in tokens:
        if line and face.getlength(line + token) > width:
            lines.append(line.rstrip()); line = token.lstrip()
        else: line += token
    if line.strip(): lines.append(line.rstrip())
    return lines

def title(draw, value, lang, box, maximum=62, minimum=30):
    x, y, w, h = box
    for size in range(maximum, minimum - 1, -1):
        face = font(lang, size); lines = wrap(value, face, w)
        step = round(size * 1.42)
        if len(lines) * step <= h and all(face.getlength(line) <= w for line in lines): break
    else: raise ValueError(f'OG title does not fit: {value}')
    for i, line in enumerate(lines):
        draw.text((x, y + i * step), line, font=face, fill=WHITE, stroke_width=1)
    return {'font_size': size, 'lines': lines}

def contain(canvas, file, box):
    with Image.open(file) as source:
        im = ImageOps.exif_transpose(source).convert('RGB')
        im.thumbnail((box[2], box[3]), Image.Resampling.LANCZOS)
        canvas.paste(im, (box[0] + (box[2] - im.width)//2, box[1] + (box[3] - im.height)//2))

def footer(canvas):
    d = ImageDraw.Draw(canvas)
    d.line((44, 584, 1156, 584), fill='#323237', width=1)
    text = 'DRA9ON CINEMA'; face = font('en', 19)
    d.text(((1200-face.getlength(text))/2, 594), text, font=face, fill='#bbb8bd')

def render(file, kind, heading, subtitle, lang, sources, names):
    canvas = Image.new('RGB', SIZE, BG); d = ImageDraw.Draw(canvas)
    if kind in ('series','home','watch'):
        # The existing FALL 707 key visual remains the actual artwork.
        contain(canvas, sources[0], (0, 0, 1200, 630))
        layout = {'existing_key_visual': True}
    elif kind == 'actors':
        d.rectangle((44, 37, 78, 42), fill=RED)
        layout = title(d, heading, lang, (44, 50, 1112, 100), maximum=62)
        d.text((46, 143), subtitle, font=font(lang, 23), fill=MUTED)
        for i, (source, name) in enumerate(zip(sources, names)):
            # Entire owner-watermarked photo; no cropping or text over the photo.
            x = 44 + i * 280
            contain(canvas, source, (x, 190, 268, 350))
            face = font(lang, 22)
            d.text((x+(268-face.getlength(name))/2, 544), name, font=face, fill=WHITE)
    elif kind in ('lounge', 'characters'):
        d.rectangle((44, 37, 78, 42), fill=RED)
        layout = title(d, heading, lang, (44, 55, 1112, 110), maximum=68)
        cell = 1112 // len(sources)
        for i, source in enumerate(sources):
            contain(canvas, source, (44+i*cell, 197, cell-14, 350))
    else:
        d.rectangle((44, 80, 78, 85), fill=RED)
        label = subtitle if kind in ('actor', 'character') else LABELS.get(kind+'s', tr('DRA9ON CINEMA','DRA9ON CINEMA','DRA9ON CINEMA','DRA9ON CINEMA'))[lang]
        # Notes use the plural section label rather than a generated category.
        if kind == 'note': label = LABELS['notes'][lang]
        if kind == 'tutorial': label = LABELS['tutorials'][lang]
        if kind in ('notes', 'tutorials', 'world'): label = 'DRA9ON CINEMA'
        for i, line in enumerate(wrap(label, font(lang, 22), 465)):
            d.text((44, 103+i*31), line, font=font(lang, 22), fill=MUTED)
        layout = title(d, heading, lang, (44, 188, 468, 334), maximum=66)
        contain(canvas, sources[0], (546, 36, 610, 514))
    footer(canvas)
    # Keep the approved picture intact; stamp the share-sized composition only.
    watermark=Image.new('RGBA',SIZE,(0,0,0,0));wd=ImageDraw.Draw(watermark)
    face=font('en',44);text='DRA9ON CINEMA'
    wd.text((600,315),text,font=face,anchor='mm',fill=(255,255,255,92),stroke_width=1,stroke_fill=(0,0,0,65))
    canvas=Image.alpha_composite(canvas.convert('RGBA'),watermark).convert('RGB')
    canvas.save(file, 'JPEG', quality=88, optimize=True, subsampling=0)
    if file.stat().st_size > 300000:
        canvas.save(file, 'JPEG', quality=80, optimize=True, subsampling=0)
    assert file.stat().st_size <= 300000, file
    return layout

def metadata(document, values):
    # Replace exactly one tag, remove duplicates, and add missing tags to head.
    for key, value in values.items():
        attr = 'property' if key.startswith('og:') else 'name'
        tag = f'<meta {attr}="{key}" content="{escape(str(value), quote=True)}">'
        pattern = r'<meta\b(?=[^>]*(?:name|property)=[\"\x27]'+re.escape(key)+r'[\"\x27])[^>]*>'
        document = re.sub(pattern, '', document, flags=re.I)
        document = document.replace('</head>', tag+'</head>', 1)
    return document

def build_social_cards(out, origin, base_path=''):
    out = Path(out); dest = out/'assets/og/pages'; dest.mkdir(parents=True, exist_ok=True)
    actor_config = json.loads((ROOT/'actors_config.json').read_text(encoding='utf-8'))
    from actors_content import ACTORS
    actor_names = {p['slug']: p['name'] for p in ACTORS}
    photo_sources = [out/'assets/actors'/actor_config['photos'][s]['fullbody']
                     for s in ('min-seoa', 'yeonhwa', 'yuna', 'haseul')]
    group_sources = [out/'assets/characters'/f'{s}-1.webp' for s in ('min-seoa', 'yeonhwa', 'yuna')]
    # This approved portrait contains no action, reveal or ending.
    hyeolmaek = out/'assets/actors/haseul-s3-2.webp'
    records = []
    for page in sorted(out.rglob('index.html')):
        info = route_info(page.relative_to(out).as_posix())
        if info is None: continue
        lang, route, kind = info
        document = page.read_text(encoding='utf-8'); parsed = Page(document)
        if 'noindex' in parsed.meta.get('robots','') and route!='/questions/': continue
        warning = ''
        heading = parsed.heading or parsed.meta.get('og:title', '').split(' | ')[0]
        subtitle = LABELS.get(kind, LABELS['characters'])[lang]
        desc = parsed.meta.get('description', parsed.meta.get('og:description', ''))
        names = []
        if kind in ('actors', 'notes', 'tutorials', 'lounge', 'world', 'characters'):
            heading = LABELS[kind][lang]
        if kind in ('home','watch'):
            sources=[local_asset(out,parsed.meta['og:image'],base_path)]
        elif kind in ('series', 'world'):
            sources = [out/'assets/og'/('og-ko.jpg' if lang == 'ko' else 'og-en.jpg')]
            if kind == 'series': heading = 'FALL 707: REBOOT'
        elif kind == 'actors':
            sources = photo_sources; subtitle = LABELS['original'][lang]
            names = [actor_names[s][lang] for s in ('min-seoa', 'yeonhwa', 'yuna', 'haseul')]
        elif kind in ('lounge', 'characters'): sources = group_sources
        elif kind == 'notes': sources = [out/'assets/notes/creator-workflow.png']
        elif kind == 'tutorials':
            sources = [out/'assets/tutorials/lighting-contrast/gpt-rembrandt.webp']
            desc = TUTORIAL_INTRO[lang]
        elif route == '/stickers/': sources = [out/'assets/notes/min-stickers-12-center-soft-wm.webp']
        elif kind == 'actor':
            slug = route.strip('/').split('/')[-1]
            sources = [out/'assets/actors'/actor_config['photos'][slug]['fullbody']]
            subtitle = LABELS['actor'][lang]
        else:
            candidates = [local_asset(out, p, base_path) for p in parsed.images]
            candidates = [p for p in candidates if p.suffix.lower() in ('.png','.webp','.jpg','.jpeg')]
            # First <main> image is the editorial representative, before related cards.
            # SVG tutorial covers already have a rasterized, original share version.
            if route == '/tutorials/claude-mcp-newtake/':
                candidates = [out/'assets/notes/claude-mcp-newtake-share-v1.jpg']
            if route == '/fall-707/characters/hyeolmaek/': candidates = [hyeolmaek]
            if not candidates:
                sources_for_menu={'/links/','/press/','/questions/','/privacy/','/terms/'}
                if route not in sources_for_menu:
                    warning=f'OG representative image missing: {lang}{route}; using an explicit branded fallback.'
                    warnings.warn(warning,RuntimeWarning)
                candidates=[out/'assets/press/dra9on-logo-dark-background.png']
            sources = candidates[:1]
            if kind == 'character': subtitle = LABELS['character'][lang]
        assert heading and desc, (page, 'Missing localized heading or description')
        fingerprint = sha256((LAYOUT+lang+kind+heading+subtitle+json.dumps(names,ensure_ascii=False)).encode())
        for source in sources: fingerprint.update(source.read_bytes())
        render_key = fingerprint.hexdigest()[:12]
        slug = route.strip('/').replace('/','-') or 'home'
        file = dest/f'{slug}-{lang}-{render_key}.jpg'
        layout = render(file, kind, heading, subtitle, lang, sources, names) if not file.exists() else {}
        version = sha256(file.read_bytes()).hexdigest()[:12]
        url = origin+'/assets/og/pages/'+file.name+'?v='+version
        og_title = parsed.meta.get('og:title') or heading+' | DRA9ON CINEMA'
        image_alt=parsed.meta.get('og:image:alt',heading) if kind=='home' else heading+(' · '+LABELS['actor'][lang] if kind=='actor' else '')
        document = metadata(document, {
            'og:image': url, 'twitter:image': url,
            'og:image:width': 1200, 'og:image:height': 630,
            'og:image:alt': image_alt, 'twitter:image:alt': image_alt,
            'og:title': og_title, 'twitter:title': og_title,
            'og:description': desc, 'twitter:description': desc,
            'twitter:card': 'summary_large_image',
            'og:type': 'article' if kind in ('note','tutorial') else 'website'})
        if kind == 'tutorials': document = metadata(document, {'description': desc})
        page.write_text(document, encoding='utf-8')
        records.append({'route': route, 'language': lang, 'kind': kind, 'title': heading,
                        'image': '/assets/og/pages/'+file.name, 'url': url,
                        'sources': [s.relative_to(out).as_posix() for s in sources],
                        'bytes': file.stat().st_size, 'layout': layout, 'warning': warning})
    (dest/'manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    return records
