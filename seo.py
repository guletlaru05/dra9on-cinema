"""Keep existing routes and metadata, removing only missing/duplicate copy."""
from collections import Counter
from html import escape, unescape
from html.parser import HTMLParser
import json
import re
from urllib.parse import urlsplit

BRAND='드래곤시네마 DRA9ON CINEMA'
ALIASES=['드래곤시네마','드래곤 시네마','dragon cinema','드래곤나인']
MAJOR={'index.html','fall-707/index.html','fall-707/world/index.html','actors/index.html','notes/index.html','tutorials/index.html','lounge/index.html','press/index.html','about/index.html','links/index.html'}
BRAND_DESCRIPTION={
 'ko':'드래곤나인의 드래곤시네마(DRA9ON CINEMA) — 낙하 707(FALL 707)과 오리지널 AI 영화.',
 'en':'DRA9ON CINEMA (드래곤시네마), by 드래곤나인: original AI films and FALL 707 (낙하 707).',
 'ja':'ドゥレゴンナイン（드래곤나인）のDRA9ON CINEMA（드래곤시네마）。FALL 707（낙하 707）とオリジナルAI映画。',
 'es':'DRA9ON CINEMA (드래곤시네마), de 드래곤나인: cine original con IA y FALL 707 (낙하 707).',
}
HOME_DESCRIPTION={
 'ko':'드래곤나인이 만드는 드래곤시네마(DRA9ON CINEMA). 〈낙하 707: 리부트〉(FALL 707: REBOOT) 시즌 1–3와 오리지널 AI 영화, 배우 프로필·제작 비하인드를 만나보세요.',
 'en':'Discover DRA9ON CINEMA (드래곤시네마) by 드래곤나인: FALL 707: REBOOT (낙하 707), Seasons 1–3, original AI films, AI actor profiles and filmmaking notes.',
 'ja':'드래곤나인が手がけるDRA9ON CINEMA（드래곤시네마）。FALL 707: REBOOT（낙하 707）シーズン1〜3、オリジナルAI映画、AI俳優と制作の舞台裏をご覧ください。',
 'es':'Descubre DRA9ON CINEMA (드래곤시네마), de 드래곤나인: FALL 707: REBOOT (낙하 707), temporadas 1–3, cine original con IA, actores y notas de rodaje.',
}

def organization(origin):
    return {'@type':'Organization','@id':origin+'/#organization','name':BRAND,'alternateName':ALIASES.copy(),
            'url':origin+'/','description':BRAND_DESCRIPTION['ko'],'sameAs':['https://www.youtube.com/@dra9oncinema']}

def brand_schemas(source,origin):
    found=False
    def enhance(value):
        nonlocal found
        if isinstance(value,list):return [enhance(v) for v in value]
        if not isinstance(value,dict):return value
        result={k:enhance(v) for k,v in value.items()}
        if result.get('@type')=='Organization' and result.get('name') in ('DRA9ON CINEMA',BRAND):
            result.update(organization(origin));found=True
        return result
    def update(match):
        nonlocal found
        schema=enhance(json.loads(match[1]))
        if not found and isinstance(schema,dict):schema['publisher']=organization(origin);found=True
        return '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>'
    source=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update,source,flags=re.S)
    if not found:
        schema={'@context':'https://schema.org',**organization(origin)}
        source=source.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script></head>',1)
    return source


class Metadata(HTMLParser):
    def __init__(self, source):
        super().__init__();self.title='';self.description='';self.in_title=False;self.noindex=False;self.feed(source)
    def handle_starttag(self, tag, pairs):
        attrs=dict(pairs)
        if tag=='title':self.in_title=True
        if tag=='meta' and attrs.get('name')=='description':self.description=attrs.get('content','')
        if tag=='meta' and attrs.get('name')=='robots':self.noindex='noindex' in attrs.get('content','')
    def handle_endtag(self, tag):
        if tag=='title':self.in_title=False
    def handle_data(self, value):
        if self.in_title:self.title+=value


TUTORIAL_DESCRIPTION={
 'ko':'캐릭터 시트부터 조명·연출·영상 제작까지, DRA9ON CINEMA의 실습 튜토리얼을 둘러보세요.',
 'en':'Explore DRA9ON CINEMA tutorials, from character sheets and lighting to directing and making AI films.',
 'ja':'キャラクターシートから照明・演出・AI映像制作まで、DRA9ON CINEMAの実践チュートリアルをご覧ください。',
 'es':'Explora los tutoriales de DRA9ON CINEMA: fichas de personajes, iluminación, dirección y creación de películas con IA.',
}


def optimize(out):
    documents=[]
    for file in out.rglob('*.html'):
        source=file.read_text(encoding='utf-8')
        if file.name=='404.html':
            source=re.sub(r'<meta name="robots"[^>]*>','<meta name="robots" content="noindex,nofollow">',source)
            file.write_text(source,encoding='utf-8')
        meta=Metadata(source)
        if not meta.noindex:documents.append((file,source,meta))
    titles=Counter(meta.title for _,_,meta in documents)
    descriptions=Counter(meta.description for _,_,meta in documents)
    changes=[]
    for file,source,meta in documents:
        relative=file.relative_to(out).as_posix()
        lang=relative.split('/')[0] if relative.startswith(('en/','ja/','es/')) else 'ko'
        route=re.sub(r'^(?:en|ja|es)/','',relative)
        title=meta.title
        if not title:
            heading=re.search(r'<h1\b[^>]*>(.*?)</h1>',source,re.S)
            title=unescape(re.sub('<[^>]+>','',heading[1]))+' | DRA9ON CINEMA' if heading else 'DRA9ON CINEMA · '+route
        if titles[title]>1:
            labels=({'ko':'등장인물','en':'Character','ja':'登場人物','es':'Personaje'} if route.startswith('fall-707/characters/') else {'ko':'작품','en':'Film','ja':'作品','es':'Película'} if route.startswith('watch/') else {'ko':'한국어','en':'English','ja':'日本語','es':'Español'})
            label=labels[lang]
            title=label+' · '+title
        description=meta.description
        if route=='tutorials/index.html':description=TUTORIAL_DESCRIPTION[lang]
        elif not description or descriptions[description]>1:
            description=title.removesuffix(' | DRA9ON CINEMA')+' — '+description
        if route=='index.html':
            title=BRAND+' | 드래곤나인 · 낙하 707 · FALL 707'+(' · '+{'en':'English','ja':'日本語','es':'Español'}[lang] if lang!='ko' else '')
        else:
            title=title.replace('드래곤시네마 DRA9ON CINEMA', 'DRA9ON CINEMA').replace('DRA9ON CINEMA',BRAND)
            if route in MAJOR:title+=' · 드래곤나인 · 낙하 707'
        if route=='index.html':description=HOME_DESCRIPTION[lang]
        elif route in MAJOR:description=description.rstrip()+' '+BRAND_DESCRIPTION[lang]
        canonical=re.search(r'<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"',source)
        if not canonical:raise ValueError('Missing canonical for organization: '+relative)
        parts=urlsplit(unescape(canonical[1]));origin=parts.scheme+'://'+parts.netloc
        source=brand_schemas(source,origin)
        source=re.sub(r'<title>.*?</title>','<title>'+escape(title)+'</title>',source,count=1,flags=re.S)
        for key,value in [('description',description),('og:title',title),('twitter:title',title),('og:description',description),('twitter:description',description)]:
            kind='property' if key.startswith('og:') else 'name'
            replacement='<meta '+kind+'="'+key+'" content="'+escape(value,quote=True)+'">'
            pattern=r'<meta\b[^>]*'+kind+'="'+re.escape(key)+r'"[^>]*>'
            if re.search(pattern,source):source=re.sub(pattern,lambda m:replacement,source,count=1)
            elif key=='description':source=source.replace('</head>',replacement+'</head>',1)
        def schema_copy(match):
            schema=json.loads(match[1])
            if schema.get('@type')=='VideoObject' and description!=meta.description:schema['description']=description
            return '<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>'
        source=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema_copy,source,flags=re.S)
        file.write_text(source,encoding='utf-8');changes.append(relative)
    (out/'seo-audit.json').write_text(json.dumps({'metadataUpdated':changes,'existingRoutesPreserved':True},ensure_ascii=False,indent=2),encoding='utf-8')
