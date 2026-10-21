"""Shared, public section navigation, including the signed-out library shell."""
from hashlib import sha256
from html import escape
from pathlib import Path
import re

LANGS=('ko','en','ja','es')
def labels(*values):return dict(zip(LANGS,values))
LINKS=[
 ('/fall-707/',labels('FALL 707','FALL 707','FALL 707','FALL 707'),True),
 ('/notes/',labels('제작 비하인드','Behind the scenes','制作の舞台裏','Entre bastidores'),True),
 ('/tutorials/',labels('튜토리얼','Tutorials','チュートリアル','Tutoriales'),True),
 ('/lounge/',labels('팬 라운지','Fan Lounge','ファンラウンジ','Salón de fans'),True),
 ('/fall-707/world/',labels('세계관','Story world','作品世界','Universo'),False),
 ('/#originals',labels('작품집','Originals','作品集','Obras'),False),
 ('/stickers/',labels('이모티콘','Stickers','ステッカー','Stickers'),False),
 ('/#collaboration',labels('협업 문의','Collaborate','コラボのお問い合わせ','Colaboraciones'),False),
 ('/#about',labels('소개','About','紹介','Acerca de'),False),
]

def navigation(out,lang,path,base_path=''):
 from actors import enabled as actors_enabled, MENU
 prefix='' if lang=='ko' else '/'+lang
 local_path=path[len(prefix):] if prefix and path.startswith(prefix+'/') else path
 links=list(LINKS)
 if actors_enabled():links.insert(1,('/actors/',MENU,True))
 matches=[route for route,_,_ in links if '#' not in route and local_path.startswith(route)]
 active=max(matches,key=len) if matches else None
 if local_path.startswith('/watch/fall-707-'):active='/fall-707/'
 if local_path.startswith('/watch/film-'):active='/#originals'
 primary=[];secondary=[];secondary_active=False
 for route,names,main in links:
  target=prefix+route
  if not (out/(target.split('#')[0].strip('/')+'/index.html').lstrip('/')).is_file():
   target=('/en' if (out/('en'+route.split('#')[0]+'index.html')).is_file() else '')+route
  current=(' aria-current="'+('page' if local_path==route else 'location')+'"') if route==active else ''
  link='<a href="'+escape(base_path+target,quote=True)+'"'+current+'>'+escape(names[lang])+'</a>'
  (primary if main else secondary).append(link)
  secondary_active=secondary_active or bool(current and not main)
 more=labels('더 보기','More','もっと見る','Más')[lang]
 name=labels('사이트 둘러보기','Explore DRA9ON CINEMA','サイトを探す','Explora DRA9ON CINEMA')[lang]
 return '<nav class="home-explore" data-site-navigation aria-label="'+name+'"><div class="home-explore-bar"><div class="home-explore-primary">'+''.join(primary)+'</div><details class="home-explore-more"'+(' data-current-section' if secondary_active else '')+'><summary>'+more+'<span aria-hidden="true">+</span></summary><div class="home-explore-secondary">'+''.join(secondary)+'</div></details></div></nav>'

def inject_navigation(out,base_path=''):
 css=(out/'site-navigation.css').read_text(encoding='utf-8')
 version=sha256(css.encode()).hexdigest()[:12]
 for file in out.rglob('*.html'):
  doc=file.read_text(encoding='utf-8')
  lang=re.search(r'<html\b[^>]*\blang="([^"]+)"',doc)
  lang=lang[1] if lang and lang[1] in LANGS else 'ko'
  relative=file.relative_to(out).as_posix()
  path='/'+relative.removesuffix('index.html')
  doc=re.sub(r'<nav class="home-explore"[\s\S]*?</nav>','',doc)
  nav=navigation(out,lang,path,base_path)
  if relative.startswith('pwa/offline-'):
   # Keep the offline fallback self-contained; never depend on a network stylesheet.
   doc=doc.replace('<body>','<body class="site-offline">',1)
   doc=doc.replace('</strong>','</strong>'+nav,1)
   doc=doc.replace('</head>','<style>'+css+'</style></head>',1)
  else:
   if '</header>' not in doc:raise ValueError('Missing navigation insertion point: '+relative)
   if relative in ('index.html','en/index.html','ja/index.html','es/index.html'):
    doc=doc.replace('<main id="main">','<main id="main">'+nav,1)
   else:doc=doc.replace('</header>','</header>'+nav,1)
   doc=doc.replace('</head>','<link rel="stylesheet" href="'+base_path+'/site-navigation.css?v='+version+'"></head>',1)
  file.write_text(doc,encoding='utf-8')
