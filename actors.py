"""Review-gated original AI actor agency. Only compressed owner photos are copied."""
import json
import os
import re
import shutil
from pathlib import Path
from html import escape as e
from urllib.parse import urlencode
from hashlib import sha256
from actors_content import ACTORS, LANGS, UI, row
from site_config import CONTACT_EMAIL, OG_ALT
from actor_rights import notice_html, with_copyright

HERE=Path(__file__).resolve().parent
MENU=row('AI 배우','AI Actors','AI俳優','Actores IA')

def settings():
 return json.loads((HERE/'actors_config.json').read_text(encoding='utf-8'))

def enabled():
 return os.getenv('D9_ACTORS_PREVIEW')=='1' or settings()['approved_for_publication']

def routes():
 return ['/actors/',*['/actors/'+a['slug']+'/' for a in ACTORS]] if enabled() else []

def prefix(lang):return '' if lang=='ko' else '/'+lang

def profile_navigation(actor,lang,base_path=''):
 index=ACTORS.index(actor);previous=ACTORS[(index-1)%len(ACTORS)];following=ACTORS[(index+1)%len(ACTORS)];pre=base_path+prefix(lang)
 back=row('이전 배우','Previous actor','前の俳優','Actor anterior')[lang];forward=row('다음 배우','Next actor','次の俳優','Siguiente actor')[lang]
 return '<nav class="actor-profile-nav" aria-label="'+e(row('배우 프로필 탐색','Browse actor profiles','俳優プロフィールの閲覧','Explorar perfiles')[lang],quote=True)+'"><a rel="prev" href="'+pre+'/actors/'+previous['slug']+'/" aria-label="'+e(back+' · '+previous['name'][lang],quote=True)+'"><span aria-hidden="true">←</span><span><small>'+back+'</small>'+e(previous['name'][lang])+'</span></a><a class="actor-all" href="'+pre+'/actors/">'+e(UI['back'][lang])+'<small>'+str(index+1).zfill(2)+' / '+str(len(ACTORS)).zfill(2)+'</small></a><a rel="next" href="'+pre+'/actors/'+following['slug']+'/" aria-label="'+e(forward+' · '+following['name'][lang],quote=True)+'"><span><small>'+forward+'</small>'+e(following['name'][lang])+'</span><span aria-hidden="true">→</span></a></nav>'

def build(out,origin,works,head,base_path=''):
 if not enabled():return
 config=settings();preview=os.getenv('D9_ACTORS_PREVIEW')=='1'
 if not preview and not (config['photos_approved'] and config['profiles_approved']):
  raise ValueError('AI actor photos and fictional profiles require owner review before publication.')
 if not preview and any(config.get(key) for key in ('lookbook','screen_stills')) and not (config.get('additional_photos_approved') and config.get('screen_stills_approved')):
  raise ValueError('Additional looks and production stills require owner review before publication.')
 if not preview and (config.get('behind_scenes') or config.get('behind_scenes_group')) and not config.get('behind_scenes_approved'):
  raise ValueError('Behind-the-scenes images require owner selection before publication.')
 source=Path(os.getenv('D9_ACTORS_PHOTOS',str(HERE/'site-assets/assets/actors'))).resolve()
 destination=out/'assets/actors';destination.mkdir(parents=True,exist_ok=True)
 photos={}
 for actor in ACTORS:
  record=config['photos'].get(actor['slug'],{})
  filename=record.get('fullbody')
  if not filename:raise ValueError('Missing owner-selected actor photograph: '+actor['slug'])
  # Never copy a directory or high-resolution source originals into the public build.
  names=[record.get(key) for key in ('fullbody','small','portrait')]
  names.extend(item['file'] for key in ('lookbook','screen_stills','behind_scenes') for item in config.get(key,{}).get(actor['slug'],[]))
  if config.get('behind_scenes_group'):names.append(config['behind_scenes_group']['file'])
  for name in names:
   if not name:continue
   if Path(name).name!=name or not re.fullmatch(r'[a-z0-9-]+\.webp',name):raise ValueError('Expected a web-only actor asset filename')
   file=source/name
   if not file.is_file() or file.stat().st_size>250_000:raise ValueError('Missing or oversized web-only actor photo: '+name)
   (destination/name).write_bytes(with_copyright(file.read_bytes()))
  photos[actor['slug']]=record
 css='/actors.css?v='+sha256((out/'actors.css').read_bytes()).hexdigest()[:12]
 script='/actors.js?v='+sha256((out/'actors.js').read_bytes()).hexdigest()[:12]
 tr=lambda key,lang:e(UI[key][lang])
 def asset(name):return base_path+'/assets/actors/'+name
 def photo(actor,lang,large=False):
  record=photos[actor['slug']];path=asset(record.get('portrait') or record['fullbody'])
  alt=actor['name'][lang]+' · '+UI['ai_keyword'][lang]+' · '+UI['fullbody'][lang]
  sizes='(max-width: 700px) 100vw, 54vw' if large else '(max-width: 600px) 46vw, (max-width: 1000px) 46vw, 23vw'
  srcset=(asset(record['small'])+' 400w, '+path+' 800w') if record.get('small') and not record.get('portrait') else path+' 800w'
  image='<img data-actor-image src="'+e(path,quote=True)+'" srcset="'+e(srcset,quote=True)+'" sizes="'+sizes+'" width="800" height="1200" alt="'+e(alt,quote=True)+'" draggable="false" '+('fetchpriority="high"' if large or actor==ACTORS[0] else 'loading="lazy"')+' decoding="async">'
  if large:return '<button class="actor-photo" type="button" data-actor-photo="'+e(path,quote=True)+'" aria-label="'+e(actor['name'][lang]+' · '+row('사진 크게 보기','Enlarge photo','写真を拡大','Ampliar foto')[lang],quote=True)+'">'+image+'</button>'
  return image
 def inquiry(actor,lang):
  return base_path+prefix(lang)+'/?'+urlencode({'inquiry':'ai-actor','actor':actor['slug']})+'#collaboration-inquiry'
 def behind_photo(item,lang,actor=None):
  path=asset(item['file']);label=item['label'][lang]
  disclosure=row('AI 캐릭터 · 촬영장 비하인드(연출 이미지)','AI characters · Behind the scenes (staged AI image)','AIキャラクター・撮影舞台裏（演出画像）','Personajes de IA · Detrás de cámaras (imagen escenificada con IA)')[lang]
  alt=label+' · '+disclosure
  cast=[actor] if actor else ACTORS
  cast_links='<span class="actor-behind-cast">'+''.join('<a href="'+base_path+prefix(lang)+'/actors/'+a['slug']+'/">'+e(a['name'][lang])+' <span aria-hidden="true">↗</span></a>' for a in cast)+'</span>'
  return '<figure class="actor-behind-photo"><button type="button" class="actor-photo" data-actor-photo="'+e(path,quote=True)+'" aria-label="'+e(label+' · '+row('사진 크게 보기','Enlarge photo','写真を拡大','Ampliar foto')[lang],quote=True)+'"><img data-actor-image src="'+e(path,quote=True)+'" width="'+str(item['width'])+'" height="'+str(item['height'])+'" alt="'+e(alt,quote=True)+'" loading="lazy" decoding="async" draggable="false"></button><figcaption>'+cast_links+'<span>'+e(label)+'</span><small>'+e(disclosure)+'</small></figcaption></figure>'
 def behind(lang):
  items=[(actor,item) for actor in ACTORS for item in config.get('behind_scenes',{}).get(actor['slug'],[])]
  group=config.get('behind_scenes_group')
  if not items and not group:return ''
  title=row('촬영장 비하인드','BEHIND THE SCENES','撮影の舞台裏','DETRÁS DE CÁMARAS')[lang]
  featured='<div class="actors-group-behind">'+behind_photo(group,lang)+'</div>' if group else ''
  return '<section id="behind-the-scenes" class="actor-gallery-section actor-behind-section" aria-label="'+e(title,quote=True)+'"><p class="section-eyebrow">BEHIND THE SCENES</p><h2>'+e(title)+'</h2>'+featured+'<div class="actor-gallery actor-behind-gallery">'+''.join(behind_photo(item,lang,actor) for actor,item in items)+'</div></section>'
 def photo_dialog(lang,title,filename):
  close=row('사진 닫기','Close photo','写真を閉じる','Cerrar foto')[lang]
  return '<dialog id="actor-photo-dialog" aria-label="'+e(title,quote=True)+'"><button type="button" data-actor-close aria-label="'+close+'">'+close+' ×</button><img data-actor-image src="'+e(asset(filename),quote=True)+'" draggable="false" alt="'+e(title+' · '+UI['ai_keyword'][lang],quote=True)+'"><p data-actor-dialog-caption hidden></p></dialog>'
 def gallery(actor,lang,screen=False):
  key='screen_stills' if screen else 'lookbook';items=config.get(key,{}).get(actor['slug'],[])
  if not items:return ''
  title=row('출연작','Screen work','出演作','Filmografía')[lang] if screen else UI['book'][lang]
  role={
   'min-seoa':row('민서아 대위 (707 특임단 팀장)','Captain Min Seo-a (707 team leader)','ミン・ソア大尉（707特殊任務団チーム長）','Capitana Min Seo-a (jefa del equipo 707)'),
   'yeonhwa':row('연화 (통제사의 딸)','Yeonhwa (the commander’s daughter)','ヨンファ（統制使の娘）','Yeonhwa (hija del comandante)'),
   'yuna':row('유나 (염력소녀)','Yuna (the telekinetic girl)','ユナ（念動力を持つ少女）','Yuna (la chica con telequinesis)'),
   'haseul':row('혈맥선생','Master Hyeolmaek','ヒョルメク先生','Maestra Hyeolmaek'),
  }[actor['slug']][lang]
  result='<section class="actor-gallery-section" aria-label="'+e(title,quote=True)+'"><p class="section-eyebrow">'+('ON SCREEN' if screen else 'LOOKBOOK')+'</p><h2>'+e(title)+'</h2>'
  if screen:result+='<p class="actor-role">'+e(role)+'</p>'
  result+='<div class="actor-gallery '+('actor-stills' if screen else 'actor-looks')+'">'
  for i,item in enumerate(items,1):
   path=asset(item['file'])
   if screen:
    work=next((w for w in works if w['season']==item['season'] and w['episode']==item['episode'] and w['category']==f"s{item['season']}"),None)
    if not work:raise ValueError('Unknown episode for actor still: '+item['file'])
    caption='FALL 707: REBOOT · S'+str(item['season'])+' EP.'+str(item['episode'])
    alt=actor['name'][lang]+' · '+row('AI 캐릭터 · FALL 707 장면','AI character · FALL 707 scene','AIキャラクター・FALL 707の場面','Personaje de IA · escena de FALL 707')[lang]+' · '+caption
    start='<a href="'+base_path+prefix(lang)+work['path']+'">';end='</a>'
   else:
    caption=item['label'][lang]
    alt=actor['name'][lang]+' · '+UI['ai_keyword'][lang]+' · '+caption
    start='<button type="button" class="actor-photo" data-actor-photo="'+e(path,quote=True)+'" aria-label="'+e(caption+' · '+row('사진 크게 보기','Enlarge photo','写真を拡大','Ampliar foto')[lang],quote=True)+'">';end='</button>'
   img='<img data-actor-image src="'+e(path,quote=True)+'" width="'+str(item['width'])+'" height="'+str(item['height'])+'" alt="'+e(alt,quote=True)+'" loading="lazy" decoding="async" draggable="false">'
   result+='<figure>'+start+img+end+'<figcaption>'+('<a href="'+base_path+prefix(lang)+work['path']+'">'+e(caption)+' ↗</a>' if screen else e(caption))+'</figcaption></figure>'
  return result+'</div></section>'
 def card(actor,lang):
  return '<article class="actor-card"><a class="actor-card-link" href="'+base_path+prefix(lang)+'/actors/'+actor['slug']+'/"><div class="actor-card-photo">'+photo(actor,lang)+'</div><div class="actor-card-caption"><p class="section-eyebrow">FALL 707: REBOOT</p><h2>'+e(actor['name'][lang])+'<span aria-hidden="true">↗</span></h2><p>'+e(actor['line'][lang])+'</p><small class="actor-disclosure">'+tr('disclosure',lang)+'</small></div></a></article>'
 def page(lang,path,title,description,body):
  home=(out/prefix(lang).strip('/')/'index.html').read_text(encoding='utf-8')
  nav=re.search(r'<header class="header"[\s\S]*?</header>',home).group()
  foot=re.search(r'<footer[\s\S]*?</footer>',home).group()
  schema={'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'inLanguage':lang,'url':origin+prefix(lang)+path,'publisher':{'@type':'Organization','name':'DRA9ON CINEMA'}}
  def creative(actor):
   return {'@type':'CreativeWork','@id':origin+'/actors/'+actor['slug']+'/#ai-character',
    'name':actor['name'][lang],'url':origin+prefix(lang)+'/actors/'+actor['slug']+'/',
    'description':actor['line'][lang]+' '+UI['disclosure'][lang],
    'genre':'Original fictional AI character; not a real person',
    'keywords':['AI character','fictional',*actor['keywords'][lang]],
    'creator':{'@type':'Organization','name':'DRA9ON CINEMA'},
    'copyrightHolder':{'@type':'Organization','name':'DRA9ON CINEMA'},
    'license':origin+prefix(lang)+'/terms/#ai-actors',
    'image':origin+asset(photos[actor['slug']]['fullbody']),
    'isBasedOn':{'@type':'CreativeWorkSeries','name':'FALL 707: REBOOT','url':origin+prefix(lang)+'/fall-707/'}}
  if path=='/actors/':
   schema['@type']='CollectionPage'
   schema['mainEntity']={'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'item':creative(actor)} for i,actor in enumerate(ACTORS,1)]}
  else:
   actor=next(actor for actor in ACTORS if path=='/actors/'+actor['slug']+'/')
   schema['mainEntity']=creative(actor)
  doc=head(title+' | DRA9ON CINEMA',description,prefix(lang)+path,schema)
  doc=doc.replace('<html lang="ko">','<html lang="'+lang+'">').replace('property="og:type" content="video.episode"','property="og:type" content="website"').replace('property="og:locale" content="ko_KR"','property="og:locale" content="'+{'ko':'ko_KR','en':'en_US','ja':'ja_JP','es':'es_ES'}[lang]+'"')
  doc=doc.replace(e(OG_ALT['ko'],quote=True),e('DRA9ON CINEMA · '+UI['title'][lang],quote=True))
  if preview:doc=doc.replace('content="index,follow,max-image-preview:large,max-video-preview:-1"','content="noindex,nofollow,noarchive"')
  if lang!='ko':doc=doc.replace('src="/catalog.js"','src="/'+lang+'/catalog.js"')
  doc=doc.replace('</head>','<link rel="stylesheet" href="'+base_path+css+'"><script src="'+base_path+script+'" defer></script></head>')
  banner='<aside class="actor-draft">'+tr('draft',lang)+'</aside>' if preview else ''
  folder=out/prefix(lang).strip('/')/path.strip('/');folder.mkdir(parents=True,exist_ok=True)
  (folder/'index.html').write_text(doc+'<body class="watch-page actor-page"><a class="skip-link" href="#main">'+tr('profile',lang)+'</a>'+nav+banner+body+foot+'</body></html>',encoding='utf-8')
 for lang in LANGS:
  pre=base_path+prefix(lang)
  listing='<main id="main" class="actors-main"><header class="actors-intro"><p class="section-eyebrow">DRA9ON CINEMA / ORIGINAL TALENT</p><div><h1>'+tr('title',lang)+'</h1><p>'+tr('intro',lang)+'</p></div></header><section class="actors-grid" aria-label="'+tr('back',lang)+'">'+''.join(card(a,lang) for a in ACTORS)+'</section>'+notice_html(lang,base_path)+'</main>'
  behind_gallery=behind(lang)
  if behind_gallery:
   listing=listing.replace(notice_html(lang,base_path),behind_gallery+notice_html(lang,base_path),1)
   first_photo=config.get('behind_scenes_group') or next(item for actor in ACTORS for item in config.get('behind_scenes',{}).get(actor['slug'],[]))
   listing+=photo_dialog(lang,UI['title'][lang],first_photo['file'])
  page(lang,'/actors/',UI['title'][lang],UI['intro'][lang],listing)
  for actor in ACTORS:
   name=e(actor['name'][lang]);role=e(actor['role'][lang])
   facts='<dl class="actor-facts">'
   for key,value in [('age',actor['age'][lang]),('height',str(actor['height_cm'])+' cm'),('skills',actor['skills'][lang])]:facts+='<div><dt>'+tr(key,lang)+'</dt><dd>'+e(value)+'</dd></div>'
   facts+='</dl><ul class="actor-keywords" aria-label="'+tr('keywords',lang)+'">'+''.join('<li>'+e(k)+'</li>' for k in actor['keywords'][lang])+'</ul>'
   credits='<section class="actor-credits"><h2>'+tr('credits',lang)+'</h2><p>FALL 707: REBOOT · '+role+'</p><div class="actor-episode-links">'
   for season,episode in actor['episodes']:
    work=next((w for w in works if w['season']==season and w['episode']==episode and w['category']==f's{season}'),None)
    if work:credits+='<a href="'+pre+work['path']+'">S'+str(season)+' EP.'+str(episode).zfill(2)+' ↗</a>'
   credits+='</div></section>'
   review='<p class="actor-settings-note">'+tr('fictional_settings',lang)+'</p>'
   body='<main id="main" class="actors-main"><a class="actor-back" href="'+pre+'/actors/">← '+tr('back',lang)+'</a><div class="actor-profile"><figure class="actor-hero-photo">'+photo(actor,lang,True)+'<figcaption>'+tr('fullbody',lang)+'</figcaption></figure><div class="actor-profile-copy"><p class="section-eyebrow">DRA9ON CINEMA / ORIGINAL TALENT</p><h1>'+name+'</h1><p class="actor-lead">'+e(actor['line'][lang])+'</p><p class="actor-disclosure">'+tr('disclosure',lang)+'</p>'+facts+review+credits+'<a class="actor-inquire" href="'+e(inquiry(actor,lang),quote=True)+'">'+tr('inquire',lang)+' <span aria-hidden="true">↗</span></a></div></div><section class="actor-screen-work"><p class="section-eyebrow">ON SCREEN</p><h2>'+tr('series',lang)+'</h2><p>'+role+'</p><a class="text-button" href="'+pre+'/fall-707/characters/'+actor['story_slug']+'/">'+row('작품 속 캐릭터 보기','Meet the character','作品の登場人物を見る','Conoce al personaje')[lang]+' →</a></section><p class="actor-copyright">'+tr('copyright',lang)+'</p></main>'
   body+=photo_dialog(lang,actor['name'][lang],photos[actor['slug']]['fullbody'])
   body=body.replace('<p class="actor-copyright">'+tr('copyright',lang)+'</p>',notice_html(lang,base_path))
   body=body.replace('<a class="actor-back" href="'+pre+'/actors/">← '+tr('back',lang)+'</a>',profile_navigation(actor,lang,base_path),1)
   behind_link='<p class="actor-behind-link"><a class="text-button" href="'+pre+'/actors/#behind-the-scenes">'+e(row('비하인드 사진 보기','View behind-the-scenes photos','舞台裏の写真を見る','Ver fotos detrás de cámaras')[lang])+' →</a></p>' if behind_gallery else ''
   body=body.replace('<section class="actor-screen-work">',gallery(actor,lang)+gallery(actor,lang,True)+behind_link+'<section class="actor-screen-work">',1)
   page(lang,'/actors/'+actor['slug']+'/',actor['name'][lang]+' · '+UI['title'][lang],actor['line'][lang]+' '+UI['disclosure'][lang],body)
 # Add the same entry points to the already-localised site without moving board data.
 for file in out.rglob('*.html'):
  rel=file.relative_to(out).as_posix();lang=rel.split('/')[0] if rel.startswith(('en/','ja/','es/')) else 'ko'
  doc=file.read_text(encoding='utf-8');pre=base_path+prefix(lang);target=pre+'/actors/'
  footer='<a data-actors-footer href="'+target+'">'+e(MENU[lang])+'</a>'
  doc=doc.replace('<div class="footer-links">','<div class="footer-links">'+footer,1)
  def add_menu(m):
   menu=m[0]
   return re.sub(r'(<a\b[^>]*>FALL 707</a>)',lambda a:a[0]+'<a class="nav-link" href="'+target+'">'+e(MENU[lang])+'</a>',menu,count=1)
  doc=re.sub(r'<nav class="nav"[\s\S]*?</nav>',add_menu,doc,count=1)
  plain=re.sub(r'^(?:en|ja|es)/','',rel)
  link='<a class="text-button" data-actor-entry href="'+target+'">'+tr('profile',lang)+' →</a>'
  if plain=='press/index.html':doc=doc.replace('</main>','<section class="editorial-section"><p class="section-eyebrow">ORIGINAL TALENT</p><h2>'+tr('title',lang)+'</h2><p>'+tr('intro',lang)+'</p>'+link+'</section></main>',1)
  if plain=='lounge/index.html':doc=re.sub(r'(<section id="characters"[\s\S]*?)(</section>)',lambda m:m[1]+link+m[2],doc,count=1)
  for actor in ACTORS:
   if plain=='fall-707/characters/'+actor['story_slug']+'/index.html':
    doc=doc.replace('</main>','<p class="character-actions"><a class="button button-white" data-actor-entry href="'+pre+'/actors/'+actor['slug']+'/">'+tr('profile',lang)+' · '+e(actor['name'][lang])+' →</a></p></main>',1)
  if plain=='index.html':
   form=contact_form(lang)
   doc=re.sub(r'(<section\b[^>]*\bid="collaboration"[\s\S]*?)(</section>)',lambda m:m[1]+form+m[2],doc,count=1)
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+base_path+css+'"><script src="'+base_path+script+'" defer></script></head>',1)
  file.write_text(doc,encoding='utf-8')

def contact_form(lang):
 t=lambda k:e(UI[k][lang]);options='<option value="">'+t('actor_none')+'</option>'+''.join('<option value="'+a['slug']+'">'+e(a['name'][lang])+'</option>' for a in ACTORS)
 labels={k:UI[k][lang] for k in ('type','actor','project','message','type_general','type_actor')}
 return '<div id="collaboration-inquiry" class="actor-contact"><h3>'+t('contact_title')+'</h3><form data-actor-enquiry data-email="'+e(CONTACT_EMAIL,quote=True)+'" data-labels="'+e(json.dumps(labels,ensure_ascii=False),quote=True)+'"><div class="actor-contact-fields"><label>'+t('type')+'<select name="inquiry"><option value="general">'+t('type_general')+'</option><option value="ai-actor">'+t('type_actor')+'</option></select></label><label>'+t('actor')+'<select name="actor">'+options+'</select></label></div><label>'+t('project')+'<input name="project" maxlength="160" autocomplete="off"></label><label>'+t('message')+'<textarea name="message" rows="4" maxlength="3000"></textarea></label><a class="button button-white" data-actor-compose href="mailto:'+e(CONTACT_EMAIL,quote=True)+'">'+t('mail')+' ↗</a><p class="actor-mail-note">'+t('mail_note')+'</p></form></div>'
