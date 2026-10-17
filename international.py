"""Selected public routes in Japanese and Spanish, with real alternate URLs."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from hashlib import sha256
from urllib.parse import urlsplit
from copy import deepcopy
import json,re,xml.etree.ElementTree as ET
from international_content import LANGUAGES,ABOUT,SEASONS,WORKS,UI,PRESS,STILL_CAPTIONS,text
from localization import english_work
from site_config import CONTACT_EMAIL,ABOUT_PARAGRAPHS

ROUTES=['/fall-707/','/fall-707/world/']
TRANSLATIONS={'FALL 707 회차 안내':'FALL 707 episode guide','시즌별 회차와 몰아보기를 한곳에서. 처음이라면 시즌 1의 첫 회차부터 시작하세요.':'Episodes and full seasons in one place. New to the series? Start with Season 1, Episode 1.','← 홈으로':'← Home'}
WORLD_ENABLED=True
def local_work(work,lang):
 result=deepcopy(work);en=english_work(work)
 name,summary=WORKS.get(work['id'],{}).get(lang,(en['name'],en['summary']))
 if work['season'] and work['id'] not in WORKS:
  name=f'FALL 707 · S{work["season"]} EP.{work["episode"]:02}'
  summary='時代を越えた兵士の戦いを描くFALL 707の新エピソード。' if lang=='ja' else 'Un nuevo episodio de FALL 707, la historia de una soldado atrapada en otra época.'
 result.update(name=name,summary=summary,title=name+' | FALL 707: REBOOT',path=('/'+lang if work['season'] else '/en')+work['path'],searchText=' '.join((name,summary,work['name'],en['name'])))
 return result

def build_series_index(out,origin,works,head,header,footer):
 title='FALL 707 회차 안내';desc='시즌별 회차와 몰아보기를 한곳에서. 처음이라면 시즌 1의 첫 회차부터 시작하세요.'
 cards='<a class="text-button" href="/fall-707/world/">FALL 707 세계관 살펴보기 →</a>'
 for season in sorted({w['season'] for w in works if w['season']}):
  cards+=f'<section class="editorial-section"><h2>FALL 707 · 시즌 {season}</h2><div class="series-grid">'
  for w in sorted([w for w in works if w['category']==f's{season}'],key=lambda w:w['episode']):cards+=card(w)
  cards+='</div></section>'
 cards+='<section class="editorial-section"><h2>FALL 707 몰아보기</h2><div class="series-grid">'+''.join(card(w) for w in works if w['category']=='full')+'</div></section>'
 body='<body class="watch-page">'+header()+'<main id="main" class="editorial-main"><a class="editorial-back" href="/">← 홈으로</a><header class="editorial-hero"><p class="section-eyebrow">FALL 707 / EPISODES</p><h1>'+title+'</h1><p>'+desc+'</p></header>'+cards+'</main>'+footer()+'</body></html>'
 schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,'description':desc,'url':origin+'/fall-707/'}
 target=out/'fall-707';target.mkdir(exist_ok=True)
 (target/'index.html').write_text(head(title+' | DRA9ON CINEMA',desc,'/fall-707/',schema).replace('</head>','<link rel="stylesheet" href="/editorial.css"></head>')+body,encoding='utf-8')

def card(w):
 return f'<article class="card"><a class="card-open" href="{w["path"]}"><img src="{w["image"]}" width="1280" height="720" alt="{escape(w["name"],quote=True)}" loading="lazy"><p class="card-label">{w["label"]} · {w.get("duration") or ""}</p><h3 class="card-name">{escape(w["name"])}</h3></a></article>'

def dictionary(lang,out):
 pos=0 if lang=='ja' else 1
 d={key:values[pos] for key,values in {**UI,**PRESS}.items()}
 from localization import UI as EN_UI
 d['주 메뉴']='メインナビゲーション' if lang=='ja' else 'Navegación principal'
 from world import COPY
 for row in COPY:
  d[row[0]]=d[row[1]]=row[2 if lang=='ja' else 3]
 for ko,en in EN_UI.items():
  if en in d:d[ko]=d[en]
 for ko,en in {'홈':'Home','작품집':'Films','제작 비하인드':'Behind the scenes','튜토리얼':'Tutorials','질문과 답변':'Questions and answers','협업 문의':'Collaborate','사이트 메뉴':'Site menu','메뉴':'Menu','닫기 ×':'Close ×','DRA9ON CINEMA 홈':'DRA9ON CINEMA Home','콘텐츠로 바로 가기':'Skip to content'}.items():d[ko]=d.get(en,en)
 from site_config import OG_ALT
 d[OG_ALT['ko']]=d[OG_ALT['en']]='FALL 707: REBOOT 公式キービジュアル' if lang=='ja' else 'Imagen principal oficial de FALL 707: REBOOT'
 for ko,en in zip(ABOUT_PARAGRAPHS['ko'],ABOUT_PARAGRAPHS['en']):d[ko]=d[en]=ABOUT[lang][ABOUT_PARAGRAPHS['ko'].index(ko)]
 from presskit import SEASONS as PRESS_SEASONS
 for index,season in enumerate(PRESS_SEASONS[:2]):
  for key,index2 in [('logline',0),('synopsis',1)]:
   for source in season[key]:d[source]=SEASONS[lang][index][index2]
 stills=json.loads((out/'assets/press/stills.json').read_text(encoding='utf-8'))
 for s,translated in zip(stills,STILL_CAPTIONS):
  for source in s['caption'].values():d[source]=translated[pos]
 for source,ja,es in [('회차 안내','エピソードガイド','Guía de episodios'),('FALL 707 회차 안내','FALL 707 エピソードガイド','FALL 707 · Guía de episodios'),('시즌별 회차와 몰아보기를 한곳에서. 처음이라면 시즌 1의 첫 회차부터 시작하세요.','各シーズンのエピソードと一挙上映をまとめて。初めての方は、シーズン1の第1話から。','Todos los episodios y temporadas completas en un mismo lugar. Si es tu primera visita, empieza por el primer episodio de la temporada 1.'),('사이트 방문 통계','サイト訪問統計','Estadísticas de visitas'),('오늘 방문','本日の訪問','Visitas de hoy'),('누적 방문','累計訪問','Visitas totales'),('집계 기준','集計について','Cómo se cuentan las visitas'),('이용약관','利用規約','Términos de uso'),('개인정보처리방침','プライバシーポリシー','Política de privacidad'),('외부 콘텐츠 설정','外部動画の設定','Ajustes de videos externos'),('채널 문의','お問い合わせ','Contacto'),('AI로 세계관을 실사화하는 크리에이터.','AIで、想像を映像へ。','Dando vida a mundos imaginados con cine creado con IA.'),('작품·이미지·텍스트의 무단 복제, 재업로드 및 상업적 이용을 금합니다. 이용 문의는 이메일로 연락해 주세요.','作品・画像・文章の無断複製、再投稿、商用利用は禁止です。利用の際はメールでお問い合わせください。','No se permite copiar, volver a publicar ni usar comercialmente películas, imágenes o textos sin autorización. Para consultas de uso, escríbenos por correo.')]:d[source]=ja if lang=='ja' else es
 # Short dynamic UI labels still go through the same catalog-independent map.
 d.update({'YouTube views ': 'YouTube再生回数 ' if lang=='ja' else 'Reproducciones de YouTube ', 'YouTube subscribers':'YouTube登録者' if lang=='ja' else 'Suscriptores de YouTube'})
 return d

class PageLanguage(HTMLParser):
 def __init__(self,lang,mapping,origin,base_path,routes,assets):
  super().__init__(convert_charrefs=False);self.lang=lang;self.mapping=sorted(mapping.items(),key=lambda x:len(x[0]),reverse=True);self.origin=origin;self.base=base_path;self.routes=routes;self.assets=assets;self.parts=[];self.json_script=False
 def tr(self,value):
  # One replacement pass prevents a translation from being translated twice.
  if not value:return value
  exact=dict(self.mapping).get(value)
  if exact is not None:return exact
  pattern='|'.join(re.escape(source) for source,_ in self.mapping if source)
  lookup=dict(self.mapping)
  return re.sub(pattern,lambda m:lookup[m.group(0)],value) if pattern else value
 def href(self,value):
  if not value.startswith('/'):return value
  path=value[len(self.base):] if self.base and value.startswith(self.base+'/') else value
  if path.startswith('/assets/'):return self.base+path
  path=re.sub(r'^/(?:en|ja|es)(?=/)','',path)
  route,sep,fragment=path.partition('#')
  prefix='/'+self.lang if route in self.routes else '/en'
  if route.startswith('/library/'):prefix=''
  return self.base+prefix+route+(sep+fragment if sep else '')
 def handle_decl(self,value):self.parts.append('<!'+value+'>')
 def handle_starttag(self,tag,pairs):
  a=dict(pairs)
  if tag=='html':a['lang']=self.lang
  if tag=='script':self.json_script=a.get('type')=='application/ld+json'
  for key in ('alt','title','aria-label','placeholder','content'):
   if key in a:a[key]=self.tr(a[key])
  if tag=='a' and a.get('href','').startswith('/'):a['href']=self.href(a['href'])
  if tag=='meta' and a.get('property')=='og:locale':a['content']=LANGUAGES[self.lang][2]
  if (tag=='link' and a.get('rel')=='canonical') or (tag=='meta' and a.get('property')=='og:url'):
   key='href' if tag=='link' else 'content';tail=a[key][len(self.origin):];tail=re.sub(r'^/(?:en|ja|es)(?=/)','',tail);a[key]=self.origin+'/'+self.lang+tail
  if tag=='script' and re.search(r'/(?:en-)?catalog(?:[./])',a.get('src','')):a['src']=self.base+'/'+self.lang+'/catalog.js?v='+self.assets['catalog-version']
  for key in ('src','href'):
   if key in a and a[key] in self.assets:a[key]=self.assets[a[key]]
  if tag=='script' and 'portfolio.' in a.get('src',''):
   self.parts.append('<script src="'+self.base+'/'+self.lang+'/locale.js?v='+self.assets['locale-version']+'" defer></script>')
  self.parts.append('<'+tag+''.join(' '+k+('="'+escape(str(v),quote=True)+'"' if v is not None else '') for k,v in a.items())+'>')
 def handle_endtag(self,tag):
  self.parts.append('</'+tag+'>')
  if tag=='script':self.json_script=False
 def handle_data(self,value):
  if self.json_script:
   def transform(item):
    if isinstance(item,dict):return {k:(self.origin+'/'+self.lang+re.sub(r'^/(?:en|ja|es)(?=/)','',v[len(self.origin):]) if k=='url' and isinstance(v,str) and v.startswith(self.origin+'/') else transform(v)) for k,v in item.items()}
    if isinstance(item,list):return [transform(v) for v in item]
    return self.tr(item) if isinstance(item,str) else item
   self.parts.append(json.dumps(transform(json.loads(value)),ensure_ascii=False).replace('</','<\\/'))
  else:self.parts.append(escape(self.tr(value),quote=False))
 def handle_entityref(self,value):self.parts.append('&'+value+';')
 def handle_charref(self,value):self.parts.append('&#'+value+';')

def supported_routes(works):return {'/','/fall-707/','/press/',*[w['path'] for w in works if w['season']],*(['/fall-707/world/'] if WORLD_ENABLED else [])}

def build_languages(out,origin,works,data,head,header,footer,base_path=''):
 routes=supported_routes(works)
 for lang in ('ja','es'):
  records=[local_work(w,lang) for w in works];by_id={w['id']:w for w in records}
  folder=out/lang;folder.mkdir(exist_ok=True)
  for w in records:w['path']=base_path+w['path'];w['image']=base_path+w['image']
  catalog='window.PORTFOLIO = '+json.dumps(records,ensure_ascii=False).replace('</','<\\/')+';\n';(folder/'catalog.js').write_text(catalog,encoding='utf-8')
  d=dictionary(lang,out)
  for original in works:
   translated=local_work(original,lang)
   for field in ('name','summary','title'):
    d[original[field]]=translated[field]
    d[english_work(original)[field]]=translated[field]
  for season in range(1,max(w['season'] for w in works)+1):
   d['Season '+str(season)]=('シーズン' if lang=='ja' else 'Temporada ')+str(season)
  d['Seasons 1–3']='シーズン1–3' if lang=='ja' else 'Temporadas 1–3'
  locale='window.D9Locale={translate:(ko,en)=>{const d='+json.dumps(d,ensure_ascii=False).replace('</','<\\/')+';if(d[en]||d[ko])return d[en]||d[ko];return en.replace(/Season (\\d+)/g,"'+('シーズン$1' if lang=='ja' else 'Temporada $1')+'").replace(/Results for [“]([^”]+)[”]/g,"'+('「$1」の検索結果' if lang=='ja' else 'Resultados de «$1»')+'");}};'
  (folder/'locale.js').write_text(locale,encoding='utf-8')
  assets={'catalog-version':sha256(catalog.encode()).hexdigest()[:12],'locale-version':sha256(locale.encode()).hexdigest()[:12]}
  for filename in ('styles.css','portfolio.css','collaboration.css','portfolio.js','editorial.css'):
   stem,ext=filename.rsplit('.',1);assets['/'+filename]=base_path+'/assets/build/'+stem+'.'+sha256((out/filename).read_bytes()).hexdigest()[:12]+'.'+ext
  pages={}
  pages['/']=(out/'en/index.html').read_text(encoding='utf-8')
  index_desc=d['시즌별 회차와 몰아보기를 한곳에서. 처음이라면 시즌 1의 첫 회차부터 시작하세요.']
  listing='<main id="main" class="editorial-main"><a class="editorial-back" href="/">'+PRESS['← Home'][0 if lang=='ja' else 1]+'</a><header class="editorial-hero"><p class="section-eyebrow">FALL 707 / EPISODES</p><h1>'+d['FALL 707 회차 안내']+'</h1><p>'+index_desc+'</p></header>'
  for season in sorted({w['season'] for w in records if w['season']}):listing+='<section class="editorial-section"><h2>'+('シーズン ' if lang=='ja' else 'Temporada ')+str(season)+'</h2><div class="series-grid">'+''.join(card(w) for w in records if w['category']==f's{season}')+'</div></section>'
  listing+='<section class="editorial-section"><h2>'+text('Full movies',lang)+'</h2><a class="text-button" href="/fall-707/world/">'+d['Explore the world of FALL 707 →']+'</a><div class="series-grid">'+''.join(card(w) for w in records if w['category']=='full')+'</div></section></main>'
  pages['/fall-707/']=head(d['FALL 707 회차 안내']+' | DRA9ON CINEMA',index_desc,'/fall-707/',{'@context':'https://schema.org','@type':'CollectionPage','name':d['FALL 707 회차 안내'],'description':index_desc,'url':origin+'/fall-707/'})+'<body class="watch-page">'+header()+listing+footer()+'</body></html>'
  for original in [w for w in works if w['season']]:
   w=by_id[original['id']];siblings=sorted([v for v in records if v['category']==w['category']],key=lambda x:x['episode']);pos=siblings.index(w)
   next_work=siblings[pos+1] if pos+1<len(siblings) else next((v for v in records if v['category']==f's{w["season"]+1}' and v['episode']==1),None)
   frame=f'https://www.youtube-nocookie.com/embed/{w["id"]}?rel=0&amp;playsinline=1&amp;enablejsapi=1&amp;origin={escape(origin,quote=True)}&amp;hl={lang}'
   screen=f'<div class="watch-screen"><iframe src="{frame}" title="{escape(w["name"],quote=True)}" allow="accelerometer; autoplay; encrypted-media; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
   view='<main id="main" class="watch-main"><nav class="breadcrumb"><a href="/fall-707/">FALL 707</a><span>/</span><span>'+w['label']+'</span></nav><div class="watch-layout"><div class="watch-primary">'+screen+'<div class="watch-heading"><div><p class="section-eyebrow">'+w['label']+' · '+str(w.get('duration') or '')+'</p><h1>'+escape(w['name'])+'</h1></div></div><p class="watch-description">'+escape(w['summary'])+'</p><div class="watch-meta"><span>DRA9ON CINEMA</span><span>'+str(w.get('uploadDate') or '')[:10]+'</span></div><div class="watch-actions"><a class="button button-white" href="https://www.youtube.com/watch?v='+w['id']+'" target="_blank" rel="noopener noreferrer">'+text('Watch on YouTube',lang)+'</a></div>'
   if next_work:view+='<a class="next-episode" href="'+next_work['path']+'"><img src="'+next_work['image']+'" width="160" height="90" alt=""><div><p class="section-eyebrow">'+text('Up next',lang)+'</p><h2>'+escape(next_work['name'])+'</h2></div></a>'
   view+='</div><aside class="watch-episodes" aria-label="'+text('Episodes',lang)+'"><h2>'+text('Episodes',lang)+'</h2>'
   for v in siblings:view+='<a class="episode-item'+(' active' if v['id']==w['id'] else '')+'" href="'+v['path']+'"'+(' aria-current="page"' if v['id']==w['id'] else '')+'><img src="'+v['image']+'" width="160" height="90" alt="" loading="lazy"><div><span>'+v['label']+'</span><strong>'+escape(v['name'])+'</strong></div></a>'
   view+='</aside></div></main>'
   schema={'@context':'https://schema.org','@type':'VideoObject','name':w['name'],'description':w['summary'],'url':origin+original['path'],'thumbnailUrl':[origin+original['image']],'embedUrl':'https://www.youtube-nocookie.com/embed/'+w['id'],'uploadDate':w['uploadDate'],'duration':'PT'+str(w['seconds'])+'S'}
   pages[original['path']]=head(w['name']+' | DRA9ON CINEMA',w['summary'],original['path'],schema)+f'<body class="watch-page" data-page="watch" data-id="{w["id"]}">'+header()+view+footer()+'</body></html>'
  pages['/press/']=(out/'en/press/index.html').read_text(encoding='utf-8')
  pages['/fall-707/world/']=(out/'en/fall-707/world/index.html').read_text(encoding='utf-8')
  for route,source in pages.items():
   source=re.sub(r'<link rel="alternate" hreflang="[^"]+"[^>]*>','',source)
   source=re.sub(r'<nav class="language-switch".*?</nav>','',source,flags=re.S)
   source=source.replace('</head>','<link rel="stylesheet" href="/editorial.css"></head>') if '/editorial.css' not in source else source
   parser=PageLanguage(lang,d,origin,base_path,routes,assets);parser.feed(source);document=''.join(parser.parts)
   target=folder/route.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(document,encoding='utf-8')
 update_language_links(out,origin,works,base_path)

def update_language_links(out,origin,works,base_path=''):
 routes=supported_routes(works)
 for page in out.rglob('*.html'):
  rel=page.relative_to(out).as_posix();code=rel.split('/',1)[0] if rel.startswith(('en/','ja/','es/')) else 'ko';plain=re.sub(r'^(?:en|ja|es)/','',rel);route='/'+plain.removesuffix('index.html')
  if rel.startswith('library/'):continue
  doc=page.read_text(encoding='utf-8');available=['ko','en','ja','es'] if route in routes else ['ko','en']
  doc=re.sub(r'<link rel="alternate" hreflang="[^"]+"[^>]*>','',doc)
  alternate=''.join(f'<link rel="alternate" hreflang="{language}" href="{origin}{"" if language=="ko" else "/"+language}{route}">' for language in available)+f'<link rel="alternate" hreflang="x-default" href="{origin}/en{route}">'
  doc=doc.replace('</head>',alternate+'</head>',1)
  switch='<nav class="language-switch" aria-label="Language">'
  for language,(display,label,locale) in LANGUAGES.items():
   target=route if language in available else '/';href=base_path+('' if language=='ko' else '/'+language)+target
   switch+=f'<a href="{href}" lang="{language}" hreflang="{language}" data-language="{language}" aria-label="{label}"'+(' aria-current="page"' if code==language else '')+f'>{display}</a>'
  switch+='</nav>'
  if 'class="language-switch"' in doc:doc=re.sub(r'<nav class="language-switch".*?</nav>',switch,doc,count=1,flags=re.S)
  else:doc=doc.replace('<div class="header-actions">','<div class="header-actions">'+switch,1)
  page.write_text(doc,encoding='utf-8')
 ns='http://www.sitemaps.org/schemas/sitemap/0.9';xhtml='http://www.w3.org/1999/xhtml';ET.register_namespace('',ns);ET.register_namespace('xhtml',xhtml)
 tree=ET.parse(out/'sitemap.xml');root=tree.getroot()
 existing={entry.find('{'+ns+'}loc').text:entry for entry in root}
 for route in routes:
  for code in LANGUAGES:
   url=origin+('' if code=='ko' else '/'+code)+route
   if url not in existing:entry=ET.SubElement(root,'{'+ns+'}url');ET.SubElement(entry,'{'+ns+'}loc').text=url;existing[url]=entry
   entry=existing[url]
   for child in list(entry):
    if child.tag=='{'+xhtml+'}link':entry.remove(child)
   for language in [*LANGUAGES,'x-default']:ET.SubElement(entry,'{'+xhtml+'}link',{'rel':'alternate','hreflang':language,'href':origin+('' if language=='ko' else '/en' if language=='x-default' else '/'+language)+route})
 tree.write(out/'sitemap.xml',encoding='utf-8',xml_declaration=True)
