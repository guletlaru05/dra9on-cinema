"""Build-only media variants and local subset fonts. Originals stay untouched."""
from hashlib import sha256
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parent
COPYRIGHT = '© DRA9ON CINEMA. All rights reserved.'
RIGHTS_XMP = ('<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:rights>'+COPYRIGHT+'</dc:rights></rdf:Description></rdf:RDF></x:xmpmeta>').encode()


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.text = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip: self.text.append(data)


def attributes(markup):
    parser = HTMLParser(); result = {}
    parser.handle_starttag = lambda tag, attrs: result.update(attrs)
    parser.feed(markup)
    return result


def img_tag(attrs):
    return '<img ' + ' '.join(key if value is None else key+'="'+escape(str(value), quote=True)+'"' for key, value in attrs.items()) + '>'


def optimize(out, base_path=''):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    pages = list(out.rglob('*.html'))
    cache = ROOT / '.cache/performance'; cache.mkdir(parents=True, exist_ok=True)
    assets = out / 'assets/optimized'; assets.mkdir(parents=True, exist_ok=True)
    assert assets.resolve().is_relative_to(out.resolve())
    for old in assets.iterdir():
        if old.is_file() and re.fullmatch(r'[a-f0-9]{14}-[0-9]+\.(webp|avif)', old.name): old.unlink()
    records = {}

    def variants(url):
        path = unescape(urlsplit(url).path)
        if base_path and path.startswith(base_path+'/'): path = path[len(base_path):]
        if path in records: return records[path]
        if not path.startswith(('/assets/actors/','/assets/portfolio/','/assets/characters/')): return None
        source = out / path.lstrip('/')
        if not path.startswith('/assets/') or source.suffix.lower() not in ('.jpg','.jpeg','.png','.webp') or not source.is_file(): return None
        image = Image.open(source)
        if getattr(image, 'n_frames', 1) != 1 or image.width < 300: return None
        image = image.convert('RGB') if image.mode not in ('RGB','RGBA') else image
        original_bytes=source.read_bytes()
        key = sha256(original_bytes+b'optimized-v3-q88-avif76-xmp').hexdigest()[:14]
        legacy_key = sha256(original_bytes+b'optimized-v2-q88-avif76-rights').hexdigest()[:14]
        widths = sorted(set([w for w in (320,480,800,1200,1600) if w < image.width] + [min(image.width,1600)]))
        result = {'width':image.width,'height':image.height,'webp':[],'avif':[]}
        for width in widths:
            resized = image.resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS) if width != image.width else image
            for fmt in ('webp','avif'):
                name = key+'-'+str(width)+'.'+fmt
                stored = cache/name
                legacy=cache/(legacy_key+'-'+str(width)+'.webp')
                if fmt=='webp' and not stored.exists() and legacy.is_file():stored.write_bytes(legacy.read_bytes())
                compiled = ROOT/'build-assets/performance-cache'/name
                if not stored.exists() and compiled.is_file(): stored.write_bytes(compiled.read_bytes())
                if not stored.exists():
                    if fmt == 'webp':
                        resized.save(stored,format='WEBP',quality=88,method=6,
                                     xmp=RIGHTS_XMP)
                    else:
                        rights=Image.Exif();rights[33432]=COPYRIGHT
                        resized.save(stored,format='AVIF',quality=76,speed=8,exif=rights,xmp=RIGHTS_XMP)
                (assets/name).write_bytes(stored.read_bytes())
                result[fmt].append((base_path+'/assets/optimized/'+name,width))
        result['src'] = result['webp'][-1][0]
        result['srcset'] = ', '.join(url+' '+str(width)+'w' for url,width in result['webp'])
        result['avifset'] = ', '.join(url+' '+str(width)+'w' for url,width in result['avif'])
        records[path] = result
        return result

    # Provide the same local thumbnails for dynamically filtered cards and hero slides.
    media = {}
    catalog = out/'catalog.js'
    if catalog.exists():
        videos = json.loads(catalog.read_text(encoding='utf-8').split(' = ',1)[1].rstrip(';\n'))
        for video in videos:
            record = variants(video['image'])
            if record: media[video['id']] = {key:record[key] for key in ('src','srcset')}
    mapping = ('window.D9ResponsiveImages='+json.dumps(media,separators=(',',':'))+';').encode()
    mapping_name = 'responsive-media.'+sha256(mapping).hexdigest()[:12]+'.js'
    (out/'assets/build'/mapping_name).write_bytes(mapping)
    texts = {lang:set(chr(i) for i in range(32,127)) for lang in ('ko','en','ja','es')}
    documents = {}
    for page in pages:
        doc = page.read_text(encoding='utf-8')
        lang = re.search(r'<html[^>]*lang="([^"]+)"',doc)[1]
        parser = Text(); parser.feed(doc); texts.setdefault(lang,set()).update(''.join(parser.text))
        def image_replacement(match):
            attrs = attributes(match[0]); src = attrs.get('src',''); record = variants(src)
            local = out/urlsplit(unescape(src)).path.removeprefix(base_path).lstrip('/')
            if local.is_file() and local.suffix.lower() in ('.jpg','.jpeg','.png','.webp','.avif'):
                with Image.open(local) as image:
                    attrs['width'],attrs['height'] = str(image.width),str(image.height)
            if doc.rfind('<dialog',0,match.start()) > doc.rfind('</dialog',0,match.start()):
                attrs['loading']='lazy';return img_tag(attrs)
            if not record: return img_tag(attrs)
            attrs.update(src=record['src'],srcset=record['srcset'],decoding='async')
            attrs.setdefault('sizes','(max-width: 700px) 100vw, 800px')
            if 'hero' in attrs.get('id','') or 'hero-image' in attrs.get('class','').split() or attrs.get('fetchpriority')=='high':
                attrs.pop('loading',None); attrs['fetchpriority']='high'
            else: attrs.setdefault('loading','lazy')
            # Hero images change with carousel state; do not retain a stale picture source.
            if 'hero' in attrs.get('id','') or 'hero-image' in attrs.get('class','').split(): return img_tag(attrs)
            return '<picture><source type="image/avif" srcset="'+escape(record['avifset'],quote=True)+'" sizes="'+escape(attrs['sizes'],quote=True)+'">'+img_tag(attrs)+'</picture>'
        doc = re.sub(r'<img\b[^>]*>',image_replacement,doc)
        def frame_replacement(match):
            markup = match[0]
            found = re.search(r'/embed/([A-Za-z0-9_-]{11})',markup)
            if not found or found[1] not in media:return markup
            record = media[found[1]]
            return markup[:-1]+' data-external-poster="'+record['src']+'" data-poster-srcset="'+record['srcset']+'" data-poster-sizes="'+('(max-width:600px) 100vw, 400px' if 'data-home-player' in markup else '100vw')+'">'
        doc = re.sub(r'<iframe\b[^>]*>',frame_replacement,doc)
        doc = doc.replace('<meta charset="utf-8">','<meta charset="utf-8"><script src="'+base_path+'/assets/build/'+mapping_name+'" defer></script>',1) if media and ('data-page="home"' in doc or '<iframe' in doc) else doc
        # This stylesheet is needed by the home collaboration area only.
        if 'id="collaboration"' not in doc:
            doc = re.sub(r'<link[^>]*href="[^"]*/collaboration(?:\.[a-f0-9]+)?\.css[^\"]*"[^>]*>','',doc)
        documents[page] = (lang,doc)

    # Font files are local, language-specific and regenerated from visible public text.
    font_dir = out/'assets/fonts'; font_dir.mkdir(parents=True,exist_ok=True)
    latin = set().union(*texts.values()); latin = {c for c in latin if ord(c)<0x250}
    font_css = {}
    for lang,chars in texts.items():
        faces=[]
        files=[('NotoSansJP-Variable.ttf' if lang=='ja' else 'NotoSansKR-Variable.ttf','Noto Sans KR','normal','100 900',chars)]
        files += [(name,'Barlow Condensed','italic' if 'Italic' in name else 'normal',str(weight),latin) for name,weight in [('BarlowCondensed-SemiBold.ttf',600),('BarlowCondensed-Bold.ttf',700),('BarlowCondensed-ExtraBold.ttf',800),('BarlowCondensed-BoldItalic.ttf',700),('BarlowCondensed-ExtraBoldItalic.ttf',800)]]
        for name,family,style,weight,glyphs in files:
            source=ROOT/'build-assets/fonts'/name
            key=sha256(source.read_bytes()+''.join(sorted(glyphs)).encode()).hexdigest()[:16]
            stored=cache/(key+'.woff2')
            compiled=ROOT/'build-assets/performance-cache'/stored.name
            if not stored.exists() and compiled.is_file():stored.write_bytes(compiled.read_bytes())
            if not stored.exists():
                options=subset.Options();options.flavor='woff2';options.recalc_timestamp=False
                font=TTFont(source);subsetter=subset.Subsetter(options=options);subsetter.populate(text=''.join(sorted(glyphs)));subsetter.subset(font)
                font.flavor='woff2';font.save(stored)
            (font_dir/stored.name).write_bytes(stored.read_bytes())
            faces.append('@font-face{font-family:"'+family+'";font-style:'+style+';font-weight:'+weight+';font-display:swap;src:url("'+base_path+'/assets/fonts/'+stored.name+'") format("woff2")}')
        css=''.join(faces).encode();name='fonts-'+lang+'.'+sha256(css).hexdigest()[:12]+'.css';(font_dir/name).write_bytes(css);font_css[lang]=base_path+'/assets/fonts/'+name
    for page,(lang,doc) in documents.items():
        doc=re.sub(r'<link[^>]*href="https://fonts\.(?:googleapis|gstatic)\.com[^\"]*"[^>]*>','',doc)
        doc=doc.replace('</head>','<link rel="stylesheet" href="'+font_css[lang]+'"></head>')
        page.write_text(doc,encoding='utf-8')
    for name in ('OFL.txt','OFL-NotoSansJP.txt','OFL-BarlowCondensed.txt'):
        (font_dir/name).write_bytes((ROOT/'build-assets/fonts'/name).read_bytes())
    # Compact CSS without changing quoted content or calc operator spacing.
    for css in out.rglob('*.css'):
        chunks=re.split(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')',css.read_text(encoding='utf-8'))
        for i in range(0,len(chunks),2):
            chunks[i]=re.sub(r'\s+',' ',re.sub(r'/\*.*?\*/','',chunks[i],flags=re.S))
            chunks[i]=re.sub(r'\s*([{};,])\s*',r'\1',chunks[i])
        css.write_text(''.join(chunks).strip(),encoding='utf-8')
    (out/'performance-assets.json').write_text(json.dumps({'images':len(records),'variants':len(list(assets.iterdir())),'fontFiles':len(list(font_dir.glob('*.woff2'))),'originalsPreserved':True}),encoding='utf-8')
